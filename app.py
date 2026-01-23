import os
import argparse
import warnings
import pandas as pd
import featuretools as ft
import numpy as np
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

# Suprime avisos específicos do woodwork e featuretools
warnings.filterwarnings('ignore', message='Could not infer format')
warnings.filterwarnings('ignore', message='pkg_resources is deprecated')
warnings.filterwarnings('ignore', category=FutureWarning, module='featuretools')

# Configuração de interface
console = Console()

def formatar_impacto(valor):
    """
    Formata valores de impacto de forma inteligente:
    - Para valores >= 0.01: mostra como porcentagem com 2 casas decimais
    - Para valores entre 0.001 e 0.01: mostra como porcentagem com 4 casas decimais
    - Para valores entre 0.0001 e 0.001: mostra como porcentagem com 6 casas decimais
    - Para valores < 0.0001: mostra em notação científica
    """
    if valor >= 0.01:
        return f"{valor:.2%}"
    elif valor >= 0.001:
        return f"{valor:.4%}"
    elif valor >= 0.0001:
        return f"{valor:.6%}"
    else:
        return f"{valor:.2e}"

def setup_environment():
    """Garante a existência das pastas do projeto."""
    for folder in ['datasets', 'mapeamento', 'resultados']:
        if not os.path.exists(folder):
            os.makedirs(folder)

def parse_mapping_file():
    """Interpreta a lógica: tabela:pai|id#tabela:filho|id"""
    try:
        with open("mapeamento/mapeamento.txt", "r") as f:
            line = f.readline().strip()
            if not line: return None
        
        tables_raw = line.split('#')
        parsed = []
        for item in tables_raw:
            info, keys_raw = item.split('|')
            name, role = info.split(':')
            keys = keys_raw.split(';')
            parsed.append({'name': name, 'role': role, 'keys': keys})
        return parsed
    except Exception as e:
        console.print(f"[red]Erro ao ler mapeamento.txt: {e}[/red]")
        return None

def traduzir_feature(nome_tecnico):
    """Converte termos técnicos do Featuretools para linguagem de negócios."""
    traducoes = {
        "SUM": "Soma total de",
        "MEAN": "Média de",
        "COUNT": "Quantidade total de",
        "MAX": "Valor máximo de",
        "MIN": "Valor mínimo de",
        "STD": "Variação de",
        "DAY": "Dia do evento",
        "MONTH": "Mês do evento",
        "WEEKDAY": "Dia da semana"
    }
    nome = nome_tecnico
    for eng, pt in traducoes.items():
        if eng in nome:
            nome = nome.replace(eng, pt)
    nome = nome.replace("(", " ").replace(")", "")
    if "." in nome:
        partes = nome.split(".")
        nome = f"{partes[1]} em {partes[0]}"
    return nome.capitalize()

def validate_targets(df, target_string):
    """Valida se os targets especificados são apropriados para análise."""
    if ',' in target_string:
        targets = [t.strip() for t in target_string.split(',')]
    else:
        targets = [target_string.strip()]
    
    # Identifica chaves comuns (campos que são tipicamente identificadores)
    common_keys = {'id_', '_id', 'cod_', '_cod', 'key', '_key', 'numero', '_numero', 'cpf', 'cnpj', 'matricula'}
    
    inappropriate_targets = []
    appropriate_targets = []
    
    for t in targets:
        if t not in df.columns:
            inappropriate_targets.append(f"{t} (não encontrado no dataset)")
        else:
            # Verifica se parece ser uma chave
            is_key = any(keyword in t.lower() for keyword in common_keys)
            
            # Verifica se tem muitos valores únicos (característica de chave)
            unique_ratio = df[t].nunique() / len(df)
            many_unique = unique_ratio > 0.8  # Mais de 80% valores únicos
            
            if is_key or many_unique:
                inappropriate_targets.append(f"{t} (parece ser uma chave/identificador)")
            else:
                appropriate_targets.append(t)
    
    return appropriate_targets, inappropriate_targets

def suggest_appropriate_targets(df):
    """Sugere targets apropriados para análise baseado nas características do dataset."""
    suggestions = []
    
    for col in df.columns:
        # Ignora colunas que são chaves
        common_keys = {'id_', '_id', 'cod_', '_cod', 'key', '_key', 'numero', '_numero', 'cpf', 'cnpj', 'matricula'}
        if any(keyword in col.lower() for keyword in common_keys):
            continue
        
        # Verifica tipo de dados
        dtype = df[col].dtype
        
        # Para colunas numéricas
        if pd.api.types.is_numeric_dtype(dtype):
            unique_ratio = df[col].nunique() / len(df)
            std_val = df[col].std()
            
            # Prioridade 1: Valores contínuos com boa variação (regressão)
            # Critério mais flexível: ou tem boa variação (std > 0) E (unique_ratio > 0.05 OU muitos valores únicos > 1000)
            if std_val > 0 and (unique_ratio > 0.05 or df[col].nunique() > 1000):
                priority = 1
                suggestions.append({
                    'coluna': col,
                    'tipo': 'Regressão',
                    'razao': f'Valores contínuos (variação: {std_val:.2f}, {df[col].nunique()} valores únicos)',
                    'priority': priority,
                    'std': std_val
                })
            # Prioridade 2: Poucas categorias (classificação)
            elif df[col].nunique() <= 10:
                priority = 2
                suggestions.append({
                    'coluna': col,
                    'tipo': 'Classificação',
                    'razao': f'{df[col].nunique()} categorias distintas',
                    'priority': priority,
                    'unique_count': df[col].nunique()
                })
            # Prioridade 3: Outras colunas numéricas
            else:
                priority = 3
                suggestions.append({
                    'coluna': col,
                    'tipo': 'Regressão/Classificação',
                    'razao': f'Valores numéricos ({df[col].nunique()} valores únicos)',
                    'priority': priority
                })
    
    # Ordena por prioridade (1 = melhor, 3 = pior) e desempata por desvio padrão (para regressão)
    suggestions.sort(key=lambda x: (x['priority'], -x.get('std', 0) if 'std' in x else 0, -x.get('unique_count', 0) if 'unique_count' in x else 0))
    
    return suggestions[:5]  # Retorna até 5 sugestões

def run_analytics(df, target):
    # Primeiro valida os targets
    appropriate_targets, inappropriate_targets = validate_targets(df, target)
    
    if inappropriate_targets:
        console.print(f"\n[bold yellow]⚠️  Atenção: Alguns targets podem não ser apropriados para análise:[/bold yellow]")
        for t in inappropriate_targets:
            console.print(f"  • {t}")
        
        # Sugere targets apropriados
        suggestions = suggest_appropriate_targets(df)
        
        if suggestions:
            console.print(f"\n[bold cyan]💡 Sugestões de targets apropriados:[/bold cyan]")
            for i, s in enumerate(suggestions, 1):
                console.print(f"  {i}. {s['coluna']} ({s['tipo']}) - {s['razao']}")
        
        # Oferece opções interativas ao usuário
        console.print(f"\n[bold]📋 Opções disponíveis:[/bold]")
        console.print(f"[cyan]1.[/cyan] Continuar com os targets informados (apesar da advertência)")
        
        if suggestions:
            # Cria opções para cada sugestão
            for i, s in enumerate(suggestions, 2):
                console.print(f"[cyan]{i}.[/cyan] Usar target: [bold]{s['coluna']}[/bold] ({s['tipo']})")
            
            # Opção para usar todas as sugestões
            last_option = len(suggestions) + 2
            console.print(f"[cyan]{last_option}.[/cyan] Usar todos os targets sugeridos")
            console.print(f"[cyan]{last_option + 1}.[/cyan] Cancelar análise")
            
            console.print(f"\n[bold]Escolha uma opção (1-{last_option + 1}):[/bold] ", end="")
            
            try:
                choice = input().strip()
                if choice == str(last_option + 1):  # Cancelar
                    console.print("[red]❌ Análise cancelada pelo usuário.[/red]")
                    return None, "Cancelado"
                elif choice == str(last_option):  # Usar todos os targets sugeridos
                    new_targets = [s['coluna'] for s in suggestions]
                    console.print(f"[green]✓ Usando todos os targets sugeridos: {', '.join(new_targets)}[/green]")
                    target = ','.join(new_targets)
                elif choice.isdigit() and 2 <= int(choice) <= last_option - 1:  # Usar uma sugestão específica
                    idx = int(choice) - 2
                    new_target = suggestions[idx]['coluna']
                    console.print(f"[green]✓ Usando target sugerido: {new_target}[/green]")
                    target = new_target
                elif choice == "1":  # Continuar com targets informados
                    console.print(f"[yellow]⚠️  Continuando com targets informados: {target}[/yellow]")
                else:
                    console.print(f"[yellow]⚠️  Opção inválida. Continuando com targets informados: {target}[/yellow]")
            except KeyboardInterrupt:
                console.print("[red]❌ Análise cancelada pelo usuário.[/red]")
                return None, "Cancelado"
            except Exception as e:
                console.print(f"[yellow]⚠️  Erro na seleção: {e}. Continuando com targets informados: {target}[/yellow]")
        else:
            console.print(f"[cyan]2.[/cyan] Cancelar análise")
            console.print(f"\n[bold]Escolha uma opção (1-2):[/bold] ", end="")
            
            try:
                choice = input().strip()
                if choice == "2":
                    console.print("[red]❌ Análise cancelada pelo usuário.[/red]")
                    return None, "Cancelado"
                elif choice != "1":
                    console.print(f"[yellow]⚠️  Opção inválida. Continuando com targets informados: {target}[/yellow]")
            except KeyboardInterrupt:
                console.print("[red]❌ Análise cancelada pelo usuário.[/red]")
                return None, "Cancelado"
            except Exception as e:
                console.print(f"[yellow]⚠️  Erro na seleção: {e}. Continuando com targets informados: {target}[/yellow]")
    
    # Verifica se target contém múltiplos campos separados por vírgula
    if ',' in target:
        targets = [t.strip() for t in target.split(',')]
        console.print(f"\n[bold yellow]🔍 Analisando relevância e direção para {len(targets)} targets: {', '.join(targets)}...[/bold yellow]")
        
        # Análise individual para cada target
        all_results = {}
        for single_target in targets:
            console.print(f"\n[cyan]▶️  Analisando individualmente: {single_target}[/cyan]")
            ranking, tipo = _run_single_analytics(df, single_target)
            all_results[single_target] = {'ranking': ranking, 'tipo': tipo}
        
        # Análise multivariada - interações entre targets
        console.print(f"\n[bold magenta]🔗 Analisando interações entre {len(targets)} targets...[/bold magenta]")
        multivariate_results = _run_multivariate_analytics(df, targets)
        
        return {
            'individual': all_results,
            'multivariate': multivariate_results
        }, "Múltiplos"
    else:
        # Caso único target (compatibilidade com versão anterior)
        console.print(f"\n[bold yellow]🔍 Analisando relevância e direção para: {target}...[/bold yellow]")
        ranking, tipo = _run_single_analytics(df, target)
        return {target: {'ranking': ranking, 'tipo': tipo}}, tipo

def _run_single_analytics(df, target):
    """Função auxiliar para análise de um único target."""
    # 1. Verifica se o target existe no DataFrame original
    if target not in df.columns:
        # Tenta encontrar colunas similares
        similar_cols = [col for col in df.columns if target.lower() in col.lower()]
        if similar_cols:
            console.print(f"[yellow]⚠️  Target '{target}' não encontrado. Usando coluna similar: {similar_cols[0]}[/yellow]")
            target = similar_cols[0]
        else:
            raise ValueError(f"Target '{target}' não encontrado no DataFrame")
    
    # 2. Verifica o tipo da coluna target e dá feedback ao usuário
    target_dtype = df[target].dtype
    is_numeric = pd.api.types.is_numeric_dtype(target_dtype)
    is_integer = pd.api.types.is_integer_dtype(target_dtype)
    
    console.print(f"[cyan]📊 Tipo da coluna '{target}': {target_dtype}[/cyan]")
    
    if is_numeric:
        if is_integer:
            console.print(f"[green]✓ Coluna '{target}' é numérica (inteiro)[/green]")
        else:
            console.print(f"[green]✓ Coluna '{target}' é numérica (decimal)[/green]")
    else:
        console.print(f"[yellow]⚠️  Coluna '{target}' não é numérica[/yellow]")
        console.print(f"[cyan]Valores únicos (primeiros 5): {df[target].unique()[:5]}[/cyan]")
        console.print(f"\n[bold green]� RECOMENDAÇÃO:[/bold green]")
        console.print(f"Para melhor análise, considere transformar '{target}' em uma coluna numérica:")
        console.print(f"1. Crie uma nova coluna numérica baseada em '{target}'")
        console.print(f"2. Use uma coluna já existente que seja numérica")
        console.print(f"3. Transforme '{target}' em uma coluna numérica usando:")
        console.print(f"   - Códigos numéricos para categorias")
        console.print(f"   - Contagens ou frequências")
        console.print(f"   - Valores binários (0/1)")
        console.print(f"\n[bold yellow]📝 O programa tentará converter automaticamente para análise...[/bold yellow]")
    
    # 3. Cria uma cópia do DataFrame para processamento
    df_ml = df.copy()
    
    # 4. Garante que o target seja numérico (transforma categóricos)
    if df_ml[target].dtype == 'object' or df_ml[target].dtype == 'string' or df_ml[target].nunique() <= 20:
        # Abordagem robusta: cria uma nova coluna com IDs numéricos
        # Isso evita o erro "Cannot setitem on a Categorical with a new category"
        unique_vals = df_ml[target].astype(str).unique()
        mapping = {val: i for i, val in enumerate(unique_vals)}
        
        # Cria uma nova coluna com sufixo '_id' para manter a original
        new_target_name = f"{target}_id"
        
        # Usa .replace() em vez de .map() para evitar NaN
        # .replace() substitui valores que não estão no mapeamento por NaN, então preenchemos depois
        df_ml[new_target_name] = df_ml[target].astype(str).replace(mapping)
        
        # Remove a coluna original e renomeia a nova para o nome do target
        df_ml = df_ml.drop(columns=[target])
        df_ml = df_ml.rename(columns={new_target_name: target})
        
        console.print(f"[green]✓ Target '{target}' transformado em IDs numéricos ({len(mapping)} categorias)[/green]")
    
    # 4. Filtra apenas colunas numéricas para análise (exclui o target da filtragem)
    # Primeiro mantemos o target transformado (cria uma cópia explícita para evitar referências)
    target_series = df_ml[target].copy()
    
    # Depois filtramos as features (todas as outras colunas)
    features_df = df_ml.drop(columns=[target]).select_dtypes(include=['number', 'bool']).copy()
    
    # Recria o DataFrame com features numéricas + target transformado
    df_ml = pd.concat([features_df, target_series], axis=1)
    
    # 5. Limpeza de dados (essencial para correlação não dar NaN)
    df_ml = df_ml.fillna(0)
    
    X = df_ml.drop(columns=[target])
    y = df_ml[target]

    # 6. Treino do Modelo
    if y.nunique() <= 2:
        model = RandomForestClassifier(n_estimators=100, random_state=123)
        tipo = "Classificação"
    else:
        model = RandomForestRegressor(n_estimators=100, random_state=123)
        tipo = "Regressão"

    model.fit(X, y)

    # 7. Cálculo de Importância + Direção usando função segura
    ranking_data = []
    for i, col in enumerate(X.columns):
        # Usa função segura para evitar warnings
        corr = _safe_correlation(X[col], y)
        
        ranking_data.append({
            'Feature': col,
            'Importance': model.feature_importances_[i],
            'Correlation': corr
        })
    
    ranking = pd.DataFrame(ranking_data)
    ranking = ranking.sort_values(by='Importance', ascending=False).head(10)
    return ranking, tipo

def _safe_correlation(x, y):
    """Cálculo seguro de correlação que evita warnings de divisão por zero."""
    # Limpa dados
    x_clean = x.replace([np.inf, -np.inf], np.nan).fillna(0)
    y_clean = y.replace([np.inf, -np.inf], np.nan).fillna(0)
    
    # Calcula desvio padrão
    std_x = x_clean.std()
    std_y = y_clean.std()
    
    # Se algum desvio padrão for zero, retorna 0
    if std_x == 0 or std_y == 0:
        return 0.0
    
    # Calcula covariância
    covariance = ((x_clean - x_clean.mean()) * (y_clean - y_clean.mean())).mean()
    
    # Calcula correlação
    correlation = covariance / (std_x * std_y)
    
    # Garante que não seja NaN
    return 0.0 if pd.isna(correlation) else correlation

def _run_multivariate_analytics(df, targets):
    """Análise multivariada - identifica padrões complexos entre múltiplos targets."""
    # 1. Prepara os dados
    df_ml = df.copy()
    
    # 2. Garante que todos os targets sejam numéricos
    for target in targets:
        if target not in df_ml.columns:
            continue
            
        if df_ml[target].dtype == 'object' or df_ml[target].dtype == 'string' or df_ml[target].nunique() <= 20:
            unique_vals = df_ml[target].astype(str).unique()
            mapping = {val: i for i, val in enumerate(unique_vals)}
            new_target_name = f"{target}_id"
            df_ml[new_target_name] = df_ml[target].astype(str).replace(mapping)
            df_ml = df_ml.drop(columns=[target])
            df_ml = df_ml.rename(columns={new_target_name: target})
    
    # 3. Filtra apenas colunas numéricas (exclui os targets temporariamente)
    target_series = df_ml[targets].copy()
    features_df = df_ml.drop(columns=targets).select_dtypes(include=['number', 'bool']).copy()
    
    # 4. Recria DataFrame com features + targets
    df_ml = pd.concat([features_df, target_series], axis=1)
    
    # 5. Limpeza robusta de dados para evitar NaN/Inf
    # Remove infinitos e substitui NaN por 0
    df_ml = df_ml.replace([np.inf, -np.inf], np.nan)
    df_ml = df_ml.fillna(0)
    
    # 6. Análise de correlação entre targets com tratamento de erros robusto
    try:
        # Verifica se há colunas com desvio padrão zero antes do cálculo
        targets_data = df_ml[targets].copy()
        
        # Remove colunas com desvio padrão zero (causam divisão por zero)
        valid_targets = []
        for target in targets:
            if target in targets_data.columns:
                std_val = targets_data[target].std()
                if std_val == 0 or pd.isna(std_val):
                    console.print(f"[yellow]⚠️  Target '{target}' tem desvio padrão zero, removendo da análise multivariada[/yellow]")
                else:
                    valid_targets.append(target)
        
        if len(valid_targets) >= 2:
            # Calcula correlação apenas com targets válidos
            correlation_matrix = targets_data[valid_targets].corr()
            # Substitui NaN na matriz de correlação por 0
            correlation_matrix = correlation_matrix.fillna(0)
            
            # Se removemos alguns targets, preenche a matriz completa com zeros
            if len(valid_targets) < len(targets):
                # Cria matriz com tipo float para evitar warning de tipo
                full_matrix = pd.DataFrame(0.0, index=targets, columns=targets, dtype=float)
                for i, t in enumerate(targets):
                    full_matrix.loc[t, t] = 1.0
                # Copia os valores calculados para os targets válidos
                for t1 in valid_targets:
                    for t2 in valid_targets:
                        full_matrix.loc[t1, t2] = float(correlation_matrix.loc[t1, t2])
                correlation_matrix = full_matrix
        else:
            console.print(f"[yellow]⚠️  Não há targets suficientes com variância para análise multivariada[/yellow]")
            correlation_matrix = pd.DataFrame(0.0, index=targets, columns=targets, dtype=float)
            for i, t in enumerate(targets):
                correlation_matrix.loc[t, t] = 1.0
                
    except Exception as e:
        console.print(f"[yellow]⚠️  Erro ao calcular correlações: {e}[/yellow]")
        # Cria matriz de correlação vazia com tipo float
        correlation_matrix = pd.DataFrame(0.0, index=targets, columns=targets, dtype=float)
        for i, t in enumerate(targets):
            correlation_matrix.loc[t, t] = 1.0
    
    # 6. Identifica features que influenciam múltiplos targets simultaneamente
    multivariate_insights = []
    
    for feature in features_df.columns:
        # Calcula correlação com cada target usando função segura
        correlations = {}
        for target in targets:
            if feature in df_ml.columns and target in df_ml.columns:
                # Usa função segura que evita warnings
                corr = _safe_correlation(df_ml[feature], df_ml[target])
                correlations[target] = corr
        
        # Identifica padrões:
        # 1. Features que influenciam todos os targets na mesma direção
        # 2. Features que têm efeitos opostos em diferentes targets
        # 3. Features com forte influência em pelo menos 2 targets
        
        if len(correlations) >= 2:
            # Verifica se influencia na mesma direção
            positive_count = sum(1 for corr in correlations.values() if corr > 0.1)
            negative_count = sum(1 for corr in correlations.values() if corr < -0.1)
            strong_count = sum(1 for corr in correlations.values() if abs(corr) > 0.3)
            
            if strong_count >= 2 or (positive_count >= 2) or (negative_count >= 2):
                # Calcula impacto médio
                avg_impact = sum(abs(corr) for corr in correlations.values()) / len(correlations)
                
                # Determina padrão
                if positive_count >= 2 and negative_count == 0:
                    pattern = "Influencia positiva múltipla"
                elif negative_count >= 2 and positive_count == 0:
                    pattern = "Influencia negativa múltipla"
                elif positive_count >= 1 and negative_count >= 1:
                    pattern = "Efeito misto (oposto)"
                else:
                    pattern = "Influencia forte múltipla"
                
                multivariate_insights.append({
                    'Feature': feature,
                    'Pattern': pattern,
                    'AvgImpact': avg_impact,
                    'Correlations': correlations,
                    'StrongTargets': strong_count
                })
    
    # 7. Ordena por impacto e número de targets afetados
    multivariate_insights.sort(key=lambda x: (x['StrongTargets'], x['AvgImpact']), reverse=True)
    
    return {
        'correlation_matrix': correlation_matrix,
        'multivariate_insights': multivariate_insights[:20],  # Top 20 insights
        'target_interactions': _analyze_target_interactions(correlation_matrix, targets)
    }

def _analyze_target_interactions(correlation_matrix, targets):
    """Analisa interações entre os próprios targets."""
    interactions = []
    
    for i, target1 in enumerate(targets):
        for j, target2 in enumerate(targets):
            if i < j:  # Evita duplicatas
                corr = correlation_matrix.loc[target1, target2]
                
                if abs(corr) > 0.5:
                    strength = "Forte"
                elif abs(corr) > 0.3:
                    strength = "Moderada"
                elif abs(corr) > 0.1:
                    strength = "Fraca"
                else:
                    continue
                
                direction = "Positiva" if corr > 0 else "Negativa"
                
                interactions.append({
                    'Target1': target1,
                    'Target2': target2,
                    'Correlation': corr,
                    'Strength': strength,
                    'Direction': direction,
                    'Interpretation': f"{target1} e {target2} têm relação {direction.lower()} {strength.lower()}"
                })
    
    return interactions

def export_to_markdown(results, tipo_ml, projeto, target, ts):
    """Gera um arquivo .md com tratamento robusto de erros e codificação."""
    filename = f"result_{projeto}_{ts}.md"
    filepath = os.path.join("resultados", filename)
    
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# Relatorio de Inteligencia: {projeto.upper()}\n\n")
            f.write(f"**Alvos Analisados:** {target} | **Tipo:** {tipo_ml}\n\n")
            
            # Se for análise múltipla, mostra um sumário executivo primeiro
            if tipo_ml == "Múltiplos":
                # Extrai targets da string
                targets = [t.strip() for t in target.split(',')]
                
                f.write("## 📊 Sumário Executivo - Análise Multivariada\n\n")
                f.write(f"Foram analisados {len(targets)} targets simultaneamente:\n\n")
                
                # Análise individual
                if 'individual' in results:
                    for target_name, result_data in results['individual'].items():
                        f.write(f"- **{target_name}**: {result_data['tipo']} (Top 10 insights)\n")
                
                # Análise multivariada
                if 'multivariate' in results:
                    multivariate = results['multivariate']
                    f.write(f"\n**🔗 Interações entre targets:**\n")
                    
                    if multivariate['target_interactions']:
                        f.write(f"- Foram identificadas {len(multivariate['target_interactions'])} interações significativas entre targets\n")
                    
                    if multivariate['multivariate_insights']:
                        f.write(f"- {len(multivariate['multivariate_insights'])} features influenciam múltiplos targets simultaneamente\n")
                
                f.write("\n---\n\n")
                
                # Seção de análise multivariada
                if 'multivariate' in results:
                    multivariate = results['multivariate']
                    
                    # 1. Interações entre targets
                    if multivariate['target_interactions']:
                        f.write("## 🔗 Interações entre Targets\n\n")
                        f.write("| Target 1 | Target 2 | Correlação | Força | Direção |\n")
                        f.write("| :--- | :--- | :--- | :--- | :--- |\n")
                        
                        for interaction in multivariate['target_interactions']:
                            f.write(f"| {interaction['Target1']} | {interaction['Target2']} | {interaction['Correlation']:.3f} | {interaction['Strength']} | {interaction['Direction']} |\n")
                        
                        f.write("\n")
                    
                    # 2. Insights multivariados
                    if multivariate['multivariate_insights']:
                        f.write("## 🧩 Insights Multivariados (Padrões Complexos)\n\n")
                        f.write("Features que influenciam múltiplos targets simultaneamente:\n\n")
                        f.write("| Feature | Padrão | Impacto Médio | Targets Fortes | Correlações |\n")
                        f.write("| :--- | :--- | :--- | :--- | :--- |\n")
                        
                        for insight in multivariate['multivariate_insights'][:10]:  # Top 10
                            traducao = traduzir_feature(insight['Feature'])
                            correlations_str = ", ".join([f"{t}: {c:.2f}" for t, c in insight['Correlations'].items()])
                            f.write(f"| {traducao} | {insight['Pattern']} | {insight['AvgImpact']:.3f} | {insight['StrongTargets']} | {correlations_str} |\n")
                        
                        f.write("\n---\n\n")
                
                # Análise individual para cada target
                if 'individual' in results:
                    for target_name, result_data in results['individual'].items():
                        ranking = result_data['ranking']
                        target_tipo = result_data['tipo']
                        
                        f.write(f"## 🎯 Análise Individual para: {target_name} ({target_tipo})\n\n")
                        
                        f.write("| Rank | Insight | Impacto | Tendencia |\n")
                        f.write("| :--- | :--- | :--- | :--- |\n")
                        
                        for i, row in enumerate(ranking.itertuples(), 1):
                            traducao = traduzir_feature(row.Feature)
                            seta = "(+)" if row.Correlation > 0 else "(-)"
                            relacao = "aumenta" if row.Correlation > 0 else "diminui"
                            tendencia = f"{seta} Quanto maior, mais {relacao} o(a) {target_name}"
                            
                            f.write(f"| #{i} | {traducao} | {formatar_impacto(row.Importance)} | {tendencia} |\n")
                        
                        f.write("\n")
            else:
                # Caso único target
                for target_name, result_data in results.items():
                    ranking = result_data['ranking']
                    target_tipo = result_data['tipo']
                    
                    f.write("## Top 10 Insights e Tendencias\n\n")
                    
                    f.write("| Rank | Insight | Impacto | Tendencia |\n")
                    f.write("| :--- | :--- | :--- | :--- |\n")
                    
                    for i, row in enumerate(ranking.itertuples(), 1):
                        traducao = traduzir_feature(row.Feature)
                        seta = "(+)" if row.Correlation > 0 else "(-)"
                        relacao = "aumenta" if row.Correlation > 0 else "diminui"
                        tendencia = f"{seta} Quanto maior, mais {relacao} o(a) {target_name}"
                        
                        f.write(f"| #{i} | {traducao} | {formatar_impacto(row.Importance)} | {tendencia} |\n")
                    
                    f.write("\n")
            
            f.write(f"\n\n--- \n*Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}*")
        return filename
    except Exception as e:
        console.print(f"[red]Erro ao gravar Markdown: {e}[/red]")
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--projeto", required=True)
    parser.add_argument("--target", required=True)
    args = parser.parse_args()

    rules = parse_mapping_file()
    if not rules: return

    console.print(Panel(f"🚀 [bold]DiscoverySpark Engine[/bold] v3.0\nProjeto: {args.projeto}", style="blue"))
    
    es = ft.EntitySet(id=args.projeto)
    parent_table = ""

    # 1. Carga
    for r in rules:
        df = pd.read_csv(f"datasets/{r['name']}.csv")
        for col in df.columns:
            if 'data' in col.lower() or 'date' in col.lower():
                df[col] = pd.to_datetime(df[col], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        
        # Featuretools 1.31.0+ requer woodwork obrigatoriamente
        # Abordagem direta: inicializa woodwork explicitamente
        
        # Debug: mostra tipos de dados
        console.print(f"[yellow]Tipos de dados para {r['name']}:[/yellow]")
        for col in df.columns:
            console.print(f"  {col}: {df[col].dtype}")
        
        # Converte tipos problemáticos para garantir compatibilidade
        for col in df.columns:
            if df[col].dtype == 'object' or df[col].dtype == 'string':
                df[col] = df[col].astype('str')
        
        # Abordagem: cria uma cópia limpa do DataFrame e remove woodwork
        # O featuretools 1.31.0 requer woodwork, mas podemos trabalhar com cópias limpas
        df_clean = df.copy()
        
        # Remove qualquer atributo woodwork que possa existir
        if hasattr(df_clean, 'ww'):
            # Cria um novo DataFrame a partir de um dicionário para evitar woodwork
            data_dict = {}
            for col in df_clean.columns:
                data_dict[col] = df_clean[col].values
            
            df_clean = pd.DataFrame(data_dict)
        
        console.print(f"[green]✓ DataFrame limpo criado para {r['name']}[/green]")
        
        if r['role'] == 'pai':
            parent_table = r['name']
            # Para tabelas pai, usa a chave existente
            try:
                es.add_dataframe(dataframe_name=r['name'], dataframe=df_clean, index=r['keys'][0])
                console.print(f"[green]✓[/green] Tabela '{r['name']}' carregada.")
            except Exception as e:
                console.print(f"[red]❌ Erro ao adicionar tabela '{r['name']}': {e}[/red]")
                raise
        else:
            # Para tabelas filhas, cria um índice manualmente ANTES de adicionar
            index_name = f"id_auto_{r['name']}"
            df_clean[index_name] = range(len(df_clean))
            try:
                es.add_dataframe(dataframe_name=r['name'], dataframe=df_clean, index=index_name)
                console.print(f"[green]✓[/green] Tabela '{r['name']}' carregada.")
            except Exception as e:
                console.print(f"[red]❌ Erro ao adicionar tabela '{r['name']}': {e}[/red]")
                raise

    # 2. Relacionamentos
    pai = [r for r in rules if r['role'] == 'pai'][0]
    for f in [r for r in rules if r['role'] == 'filho']:
        es.add_relationship(pai['name'], pai['keys'][0], f['name'], f['keys'][0])
    
    # 3. DFS
    console.print("\n[bold magenta]⚙️  Sintetizando variáveis...[/bold magenta]")
    feature_matrix, _ = ft.dfs(entityset=es, target_dataframe_name=parent_table, max_depth=2)

# 4. Analytics
    results, tipo_ml = run_analytics(feature_matrix, args.target)
    
    # Verifica se o usuário cancelou a análise
    if results is None:
        console.print("[yellow]📝 Análise não realizada (cancelada pelo usuário).[/yellow]")
        return

    # 5. Saída (Invertemos a ordem para garantir a tentativa do MD)
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    
    console.print("[yellow]💾 Gravando arquivos de saída...[/yellow]")
    
    # Tenta MD primeiro
    md_file = export_to_markdown(results, tipo_ml, args.projeto, args.target, ts)
    if md_file:
        console.print(f"[green]✓ Relatório MD criado: {md_file}[/green]")
    
    # Tenta CSV depois
    csv_path = f"resultados/result_{args.projeto}_{ts}.csv"
    feature_matrix.to_csv(csv_path)
    console.print(f"[green]✓ Dataset CSV criado: {csv_path}[/green]")

    # Exibe resultados no terminal
    if tipo_ml == "Múltiplos":
        # Análise individual para cada target
        if 'individual' in results:
            for target_name, result_data in results['individual'].items():
                ranking = result_data['ranking']
                target_tipo = result_data['tipo']
                
                res_table = Table(title=f"Resumo de Impacto para: {target_name} ({target_tipo})")
                res_table.add_column("Insight", style="white")
                res_table.add_column("Impacto", style="green")
                res_table.add_column("Tendência", style="cyan")
                
                for row in ranking.itertuples():
                    traducao = traduzir_feature(row.Feature)
                    seta = "↗️" if row.Correlation > 0 else "↘️"
                    relacao = "aumenta" if row.Correlation > 0 else "diminui"
                    tendencia = f"{seta} {relacao} {target_name}"
                    
                    res_table.add_row(traducao, formatar_impacto(row.Importance), tendencia)
                
                console.print(res_table)
        
        # Análise multivariada
        if 'multivariate' in results:
            multivariate = results['multivariate']
            
            # Interações entre targets
            if multivariate['target_interactions']:
                inter_table = Table(title="🔗 Interações entre Targets")
                inter_table.add_column("Target 1", style="cyan")
                inter_table.add_column("Target 2", style="cyan")
                inter_table.add_column("Correlação", style="yellow")
                inter_table.add_column("Força", style="green")
                inter_table.add_column("Direção", style="magenta")
                
                for interaction in multivariate['target_interactions']:
                    inter_table.add_row(
                        interaction['Target1'],
                        interaction['Target2'],
                        f"{interaction['Correlation']:.3f}",
                        interaction['Strength'],
                        interaction['Direction']
                    )
                
                console.print(inter_table)
            
            # Insights multivariados
            if multivariate['multivariate_insights']:
                multi_table = Table(title="🧩 Insights Multivariados (Top 5)")
                multi_table.add_column("Feature", style="white")
                multi_table.add_column("Padrão", style="cyan")
                multi_table.add_column("Impacto Médio", style="green")
                multi_table.add_column("Targets Fortes", style="yellow")
                
                for insight in multivariate['multivariate_insights'][:5]:
                    traducao = traduzir_feature(insight['Feature'])
                    multi_table.add_row(
                        traducao,
                        insight['Pattern'],
                        f"{insight['AvgImpact']:.3f}",
                        str(insight['StrongTargets'])
                    )
                
                console.print(multi_table)
    else:
        # Caso único target
        for target_name, result_data in results.items():
            ranking = result_data['ranking']
            target_tipo = result_data['tipo']
            
            res_table = Table(title=f"Resumo de Impacto para: {target_name} ({target_tipo})")
            res_table.add_column("Insight", style="white")
            res_table.add_column("Impacto", style="green")
            res_table.add_column("Tendência", style="cyan")
            
            for row in ranking.itertuples():
                traducao = traduzir_feature(row.Feature)
                seta = "↗️" if row.Correlation > 0 else "↘️"
                relacao = "aumenta" if row.Correlation > 0 else "diminui"
                tendencia = f"{seta} {relacao} {target_name}"
                
                res_table.add_row(traducao, formatar_impacto(row.Importance), tendencia)
            
            console.print(res_table)

    console.print(f"\n[bold green]✅ Relatórios gerados em /resultados![/bold green]")

if __name__ == "__main__":
    setup_environment()
    try:
        main()
    except Exception as e:
        console.print(f"[red]Erro fatal: {e}[/red]")