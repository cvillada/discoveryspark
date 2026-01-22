import os
import argparse
import pandas as pd
import featuretools as ft
import numpy as np
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

# Configuração de interface
console = Console()

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

def run_analytics(df, target):
    console.print(f"\n[bold yellow]🔍 Analisando relevância e direção para: {target}...[/bold yellow]")
    
    # 1. Filtra apenas colunas numéricas
    df_ml = df.select_dtypes(include=['number', 'bool']).copy()
    
    # 2. Garante que o target seja numérico
    if df_ml[target].dtype == 'object' or df_ml[target].nunique() <= 20:
        le = LabelEncoder()
        df_ml[target] = le.fit_transform(df[target].astype(str))
    
    # 3. Limpeza de dados (essencial para correlação não dar NaN)
    df_ml = df_ml.fillna(0)
    
    X = df_ml.drop(columns=[target])
    y = df_ml[target]

    # 4. Treino do Modelo
    if y.nunique() <= 2:
        model = RandomForestClassifier(n_estimators=100, random_state=123)
        tipo = "Classificação"
    else:
        model = RandomForestRegressor(n_estimators=100, random_state=123)
        tipo = "Regressão"

    model.fit(X, y)

    # 5. Cálculo de Importância + Direção com Tratamento de Erro
    ranking_data = []
    for i, col in enumerate(X.columns):
        # Evita erro de correlação se a coluna for constante (std=0)
        if X[col].std() == 0:
            corr = 0
        else:
            # Usamos o método do pandas que é mais tolerante
            corr = X[col].corr(y)
        
        ranking_data.append({
            'Feature': col,
            'Importance': model.feature_importances_[i],
            'Correlation': 0 if pd.isna(corr) else corr
        })
    
    ranking = pd.DataFrame(ranking_data)
    ranking = ranking.sort_values(by='Importance', ascending=False).head(10)
    return ranking, tipo

def export_to_markdown(ranking, tipo_ml, projeto, target, ts):
    """Gera um arquivo .md com tratamento robusto de erros e codificação."""
    filename = f"result_{projeto}_{ts}.md"
    filepath = os.path.join("resultados", filename)
    
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# Relatorio de Inteligencia: {projeto.upper()}\n\n")
            f.write(f"**Alvo Analisado:** {target} | **Tipo:** {tipo_ml}\n\n")
            f.write("## Top 10 Insights e Tendencias\n\n")
            f.write("| Rank | Insight | Impacto | Tendencia |\n")
            f.write("| :--- | :--- | :--- | :--- |\n")
            
            for i, row in enumerate(ranking.itertuples(), 1):
                traducao = traduzir_feature(row.Feature)
                # Trocando emojis por texto simples para evitar erro de escrita
                seta = "(+)" if row.Correlation > 0 else "(-)"
                relacao = "aumenta" if row.Correlation > 0 else "diminui"
                tendencia = f"{seta} Quanto maior, mais {relacao} o(a) {target}"
                
                f.write(f"| #{i} | {traducao} | {row.Importance:.2%} | {tendencia} |\n")
            
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

    console.print(Panel(f"🚀 [bold]Spark Clone Engine[/bold] v3.0\nProjeto: {args.projeto}", style="blue"))
    
    es = ft.EntitySet(id=args.projeto)
    parent_table = ""

    # 1. Carga
    for r in rules:
        df = pd.read_csv(f"datasets/{r['name']}.csv")
        for col in df.columns:
            if 'data' in col.lower() or 'date' in col.lower():
                df[col] = pd.to_datetime(df[col], errors='coerce')

        if r['role'] == 'pai':
            parent_table = r['name']
            es.add_dataframe(dataframe_name=r['name'], dataframe=df, index=r['keys'][0])
        else:
            es.add_dataframe(dataframe_name=r['name'], dataframe=df, make_index=True, index=f"id_auto_{r['name']}")
        console.print(f"[green]✓[/green] Tabela '{r['name']}' carregada.")

    # 2. Relacionamentos
    pai = [r for r in rules if r['role'] == 'pai'][0]
    for f in [r for r in rules if r['role'] == 'filho']:
        es.add_relationship(pai['name'], pai['keys'][0], f['name'], f['keys'][0])
    
    # 3. DFS
    console.print("\n[bold magenta]⚙️  Sintetizando variáveis...[/bold magenta]")
    feature_matrix, _ = ft.dfs(entityset=es, target_dataframe_name=parent_table, max_depth=2)

# 4. Analytics
    ranking, tipo_ml = run_analytics(feature_matrix, args.target)

    # 5. Saída (Invertemos a ordem para garantir a tentativa do MD)
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    
    console.print("[yellow]💾 Gravando arquivos de saída...[/yellow]")
    
    # Tenta MD primeiro
    md_file = export_to_markdown(ranking, tipo_ml, args.projeto, args.target, ts)
    if md_file:
        console.print(f"[green]✓ Relatório MD criado: {md_file}[/green]")
    
    # Tenta CSV depois
    csv_path = f"resultados/result_{args.projeto}_{ts}.csv"
    feature_matrix.to_csv(csv_path)
    console.print(f"[green]✓ Dataset CSV criado: {csv_path}[/green]")

    # Exibe tabela rápida no terminal
    res_table = Table(title="Resumo de Impacto")
    res_table.add_column("Insight", style="white")
    res_table.add_column("Impacto", style="green")
    for row in ranking.itertuples():
        res_table.add_row(traduzir_feature(row.Feature), f"{row.Importance:.2%}")
    console.print(res_table)

    console.print(f"\n[bold green]✅ Relatórios gerados em /resultados![/bold green]")

if __name__ == "__main__":
    setup_environment()
    try:
        main()
    except Exception as e:
        console.print(f"[red]Erro fatal: {e}[/red]")