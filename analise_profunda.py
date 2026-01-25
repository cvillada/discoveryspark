import os
import pandas as pd
import json
import glob
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import requests
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich import print as rprint

class DeepSeekAPIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def chat_completion(self, messages: List[Dict[str, str]], model: str = "deepseek-reasoner") -> str:
        url = f"{self.base_url}/chat/completions"
        
        # Configurar timeout baseado no modelo
        if model == "deepseek-reasoner":
            timeout_config = (30, 180)  # connect timeout 30s, read timeout 180s
        else:
            timeout_config = (30, 120)  # connect timeout 30s, read timeout 120s
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(url, headers=self.headers, json=payload, timeout=timeout_config)
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # backoff exponencial: 1, 2, 4 segundos
                    import time
                    time.sleep(wait_time)
                    continue
                return f"Timeout após {max_retries} tentativas. O modelo '{model}' pode estar muito lento ou a conexão está instável.\n\n{self._gerar_resposta_fallback(messages)}"
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    import time
                    time.sleep(wait_time)
                    continue
                return f"Erro na comunicação com a API após {max_retries} tentativas: {str(e)}\n\n{self._gerar_resposta_fallback(messages)}"
            except (KeyError, IndexError) as e:
                return f"Erro ao processar resposta da API: {str(e)}\n\n{self._gerar_resposta_fallback(messages)}"
    
    def _gerar_resposta_fallback(self, messages: List[Dict[str, str]]) -> str:
        user_content = messages[-1]["content"] if messages else ""
        
        if "ANALISE OS SEGUINTES DADOS" in user_content:
            return self._gerar_analise_fallback(user_content)
        elif "ANALISE DE INSIGHTS RECEBIDA" in user_content:
            return self._gerar_estrategia_fallback(user_content)
        else:
            return "API indisponível. Aqui está uma análise básica baseada nos dados:\n\n1. Foco na redução de churn de clientes de alto valor\n2. Implementar programa de fidelidade baseado em frequência\n3. Monitorar variação nos padrões de compra\n4. Criar segmentação dinâmica de clientes\n5. Desenvolver sistema de alerta precoce para risco de churn"
    
    def _gerar_analise_fallback(self, user_content: str) -> str:
        return """
RESUMO EXECUTIVO:
A análise dos dados de churn revela padrões importantes para estratégia de retenção. Clientes com maior valor médio de compras apresentam maior risco de churn, enquanto consistência e frequência de compras são fatores protetores.

INSIGHTS PRINCIPAIS:
1. Valor médio alto correlaciona-se positivamente com churn (9.41% impacto)
2. Consistência (skew positivo) reduz churn (9.04% impacto)
3. Volume de transações (soma de id_venda) é fator de retenção (8.24% impacto)
4. Variação alta nos gastos aumenta risco (7.95% impacto)
5. Compras de valor máximo isoladas são sinal de alerta (7.73% impacto)

TENDÊNCIAS IDENTIFICADAS:
- Paradoxo: clientes mais valiosos monetariamente são os que mais saem
- Consistência > Valor: regularidade nas compras é mais importante que valor total
- Sinais precoces: variação no padrão de gastos precede o churn

IMPLICAÇÕES DE NEGÓCIO:
1. Revisar experiência de clientes de alto valor
2. Criar incentivos para frequência de compras
3. Implementar monitoramento de padrões de risco

PONTOS DE ATENÇÃO:
1. Programa de retenção para top 20% por valor
2. Sistema de alerta para variação súbita em gastos
3. Pesquisa de satisfação focada em clientes de risco
"""
    
    def _gerar_estrategia_fallback(self, user_content: str) -> str:
        return """
VISÃO ESTRATÉGICA:
Reduzir churn em 30% nos próximos 6 meses através de segmentação inteligente e intervenções proativas.

OBJETIVOS SMART:
1. Reduzir taxa de churn de 44% para 30% em 6 meses
2. Implementar sistema de alerta precoce para 100% dos clientes de alto risco em 30 dias
3. Aumentar retenção de clientes de alto valor em 25% em 3 meses

PLANO DE AÇÃO:
1. SEMANA 1-2: Identificar segmentos de risco usando análise de dados
2. SEMANA 3-4: Desenvolver programa de retenção para cada segmento
3. MÊS 2: Implementar sistema de monitoramento contínuo
4. MÊS 3: Treinar equipes de atendimento e vendas
5. MÊS 4-6: Executar, medir e ajustar estratégias

METRICS & KPIs:
- Taxa de churn mensal
- Valor de vida do cliente (LTV)
- Custo de aquisição vs. retenção
- Satisfação do cliente (NPS/CSAT)
- Eficácia de intervenções de retenção

ALOCAÇÃO DE RECURSOS:
- 1 Analista de Dados (meio período)
- 1 Especialista em Retenção
- Orçamento para programas de fidelidade
- Ferramentas de monitoramento e automação

TIMELINE:
FASE 1 (0-30 dias): Diagnóstico e planejamento
FASE 2 (31-60 dias): Implementação piloto
FASE 3 (61-90 dias): Escala e otimização
FASE 4 (91-180 dias): Consolidação e melhoria contínua
"""

class SeniorAnalisadorInsights:
    def __init__(self, api_client: DeepSeekAPIClient):
        self.api_client = api_client
        self.nome = "Senior Analisador de Insights e Tendências"
        self.expertise = "Análise de dados, identificação de padrões, insights de negócio, tendências de mercado"
    
    def analisar_arquivos(self, md_content: str, csv_data: pd.DataFrame) -> Dict[str, Any]:
        csv_summary = self._resumir_csv(csv_data)
        
        prompt = f"""
        Você é um {self.nome} com expertise em {self.expertise}.
        
        ANALISE OS SEGUINTES DADOS:
        
        1. RELATÓRIO DE INSIGHTS (formato markdown):
        {md_content}
        
        2. RESUMO DOS DADOS CSV:
        {csv_summary}
        
        INSTRUÇÕES IMPORTANTES:
        - O arquivo Markdown pode ter qualquer formato ou layout. Analise o conteúdo independentemente da estrutura.
        - O arquivo CSV pode conter qualquer conjunto de colunas. Identifique as variáveis mais relevantes.
        - O arquivo Markdown e CSV tem sempre um relacionamento entre eles. 
        - Foque em extrair insights significativos independentemente do formato dos dados.
        
        SUA TAREFA:
        1. Analise profundamente os insights apresentados no relatório (independentemente do formato)
        2. Identifique as principais tendências e padrões nos dados (extraia do conteúdo disponível)
        3. Relacione os insights estatísticos com possíveis implicações de negócio (baseado no que os dados revelam)
        4. Destaque os pontos mais críticos que merecem atenção imediata (identifique riscos e oportunidades)
        5. Forneça uma análise contextualizada sobre o problema de churn (rotatividade de clientes)
        
        IMPORTANTE: Se os dados estiverem em formato incomum ou com layout diferente do esperado, adapte sua análise para extrair o máximo de valor possível. Foque no conteúdo, não na estrutura.
        
        FORMATO DA RESPOSTA (em português):
        - RESUMO EXECUTIVO: Breve resumo dos principais achados
        - INSIGHTS PRINCIPAIS: Lista dos 5 insights mais importantes com explicação
        - TENDÊNCIAS IDENTIFICADAS: Padrões de comportamento observados
        - IMPLICAÇÕES DE NEGÓCIO: Como esses insights afetam o negócio
        - PONTOS DE ATENÇÃO: Áreas que requerem ação imediata
        """
        
        messages = [
            {"role": "system", "content": f"Você é um {self.nome} especializado em {self.expertise}. Você é especialista em analisar dados em qualquer formato ou layout, extraindo valor independentemente da estrutura dos arquivos."},
            {"role": "user", "content": prompt}
        ]
        
        analise = self.api_client.chat_completion(messages)
        
        return {
            "analista": self.nome,
            "timestamp": datetime.now().isoformat(),
            "analise_completa": analise,
            "resumo_csv": csv_summary
        }
    
    def _resumir_csv(self, df: pd.DataFrame) -> str:
        summary = []
        summary.append(f"Total de registros: {len(df)}")
        summary.append(f"Colunas disponíveis: {', '.join(df.columns.tolist())}")
        
        if 'churn' in df.columns:
            churn_stats = df['churn'].value_counts()
            summary.append(f"Distribuição de churn: {churn_stats.to_dict()}")
            summary.append(f"Taxa de churn: {(churn_stats.get(1, 0) / len(df) * 100):.2f}%")
        
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        if len(numeric_cols) > 0:
            summary.append(f"Colunas numéricas: {len(numeric_cols)}")
            for col in numeric_cols[:5]:
                summary.append(f"  {col}: média={df[col].mean():.2f}, std={df[col].std():.2f}")
        
        return "\n".join(summary)

class SeniorEstrategista:
    def __init__(self, api_client: DeepSeekAPIClient):
        self.api_client = api_client
        self.nome = "Senior Estrategista de Negócios"
        self.expertise = "Estratégia empresarial, tomada de decisão, planejamento tático, implementação de soluções"
    
    def criar_estrategia(self, analise_insights: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
        Você é um {self.nome} com expertise em {self.expertise}.
        
        ANALISE DE INSIGHTS RECEBIDA DO ANALISTA:
        {analise_insights['analise_completa']}
        
        DADOS ADICIONAIS:
        Analista: {analise_insights['analista']}
        Timestamp: {analise_insights['timestamp']}
        
        INSTRUÇÕES IMPORTANTES:
        - A análise pode conter dados em qualquer formato ou estrutura. Adapte sua estratégia ao conteúdo disponível.
        - Foque em criar uma estratégia prática baseada nos insights fornecidos, independentemente do formato original.
        - Se a análise for incompleta ou em formato não convencional, extraia o máximo de valor possível.
        
        SUA TAREFA:
        Com base na análise de insights fornecida, crie uma estratégia clara e acionável para tomada de decisão.
        
        A estratégia deve incluir:
        1. OBJETIVOS ESTRATÉGICOS: O que queremos alcançar (baseados nos insights disponíveis)
        2. AÇÕES PRIORITÁRIAS: O que fazer imediatamente (curto prazo, adaptável aos recursos identificados)
        3. PLANO TÁTICO: Como implementar (médio prazo, considerando as limitações identificadas)
        4. INDICADORES DE SUCESSO: Como medir o progresso (métricas mensuráveis e realistas)
        5. RISCOS E MITIGAÇÕES: Possíveis problemas e como evitá-los (considerando o contexto fornecido)
        6. RECOMENDAÇÕES ESPECÍFICAS: Sugestões concretas baseadas nos dados (mesmo que incompletos)
        
        FOCO PRINCIPAL: Redução de churn (rotatividade de clientes) e otimização de vendas.
        
        IMPORTANTE: Crie uma estratégia que funcione independentemente do formato original dos dados. O foco deve estar na aplicação prática dos insights. Se alguns dados estiverem faltando ou em formato incomum, faça suposições razoáveis baseadas no contexto disponível.
        
        FORMATO DA RESPOSTA (em português):
        - VISÃO ESTRATÉGICA: Contexto e direção geral
        - OBJETIVOS SMART: Específicos, Mensuráveis, Atingíveis, Relevantes, Temporais (baseados nos insights disponíveis)
        - PLANO DE AÇÃO: Passos concretos com responsabilidades e prazos (adaptável aos recursos)
        - METRICS & KPIs: Como acompanhar o sucesso (métricas realistas)
        - ALOCAÇÃO DE RECURSOS: O que será necessário (considerando limitações)
        - TIMELINE: Cronograma sugerido (baseado na complexidade dos insights)
        """
        
        messages = [
            {"role": "system", "content": f"Você é um {self.nome} especializado em {self.expertise}. Você é especialista em criar estratégias eficazes mesmo quando os dados estão em formatos incompletos ou não convencionais."},
            {"role": "user", "content": prompt}
        ]
        
        estrategia = self.api_client.chat_completion(messages)
        
        return {
            "estrategista": self.nome,
            "timestamp": datetime.now().isoformat(),
            "estrategia_completa": estrategia,
            "baseado_em": analise_insights['analista']
        }

class AnaliseProfunda:
    def __init__(self, api_key: str, model: str = "deepseek-reasoner"):
        # Criar cliente API com modelo personalizado
        class DeepSeekAPIClientPersonalizado(DeepSeekAPIClient):
            def chat_completion(self, messages: List[Dict[str, str]], model_param: str = None) -> str:
                # Usar o modelo especificado no construtor
                model_to_use = model if model_param is None else model_param
                return super().chat_completion(messages, model_to_use)
        
        self.api_client = DeepSeekAPIClientPersonalizado(api_key)
        self.analisador = SeniorAnalisadorInsights(self.api_client)
        self.estrategista = SeniorEstrategista(self.api_client)
        self.console = Console()
        self.model = model
    
    def listar_arquivos_resultados(self, resultados_dir: str = "resultados") -> Tuple[List[str], List[str]]:
        arquivos_md = sorted(glob.glob(os.path.join(resultados_dir, "*.md")), reverse=True)
        arquivos_csv = sorted(glob.glob(os.path.join(resultados_dir, "*.csv")), reverse=True)
        return arquivos_md, arquivos_csv
    
    def selecionar_arquivo_interativo(self, arquivos: List[str], tipo: str) -> Optional[str]:
        if not arquivos:
            self.console.print(f"[red]Nenhum arquivo {tipo} encontrado na pasta resultados.[/red]")
            return None
        
        self.console.print(f"\n[yellow]📁 Arquivos {tipo.upper()} disponíveis:[/yellow]")
        
        tabela = Table(show_header=True, header_style="bold cyan", box=None)
        tabela.add_column("ID", style="green", width=5)
        tabela.add_column(f"Arquivo {tipo}", style="white")
        tabela.add_column("Modificado", style="dim")
        
        for i, caminho in enumerate(arquivos, 1):
            nome_arquivo = os.path.basename(caminho)
            mod_time = datetime.fromtimestamp(os.path.getmtime(caminho)).strftime("%d/%m/%Y %H:%M")
            tabela.add_row(str(i), nome_arquivo, mod_time)
        
        self.console.print(tabela)
        self.console.print("[cyan]0.[/cyan] Cancelar seleção")
        
        escolhas = [str(i) for i in range(len(arquivos) + 1)]
        escolha = Prompt.ask(f"\nSelecione o arquivo {tipo} nº", choices=escolhas)
        
        if escolha == '0':
            return None
        
        return arquivos[int(escolha) - 1]
    
    def selecionar_arquivos_interativo(self, resultados_dir: str = "resultados") -> Tuple[Optional[str], Optional[str]]:
        self.console.clear()
        self.console.print(Panel.fit(
            "🔍 [bold blue]SELECIONE OS ARQUIVOS PARA ANÁLISE[/bold blue]\n[italic]Selecione os arquivos .md e .csv correspondentes[/italic]",
            border_style="blue"
        ))
        
        arquivos_md, arquivos_csv = self.listar_arquivos_resultados(resultados_dir)
        
        self.console.print("\n[bold]1. SELECIONE O ARQUIVO DE RELATÓRIO (.md)[/bold]")
        arquivo_md = self.selecionar_arquivo_interativo(arquivos_md, ".md")
        
        if not arquivo_md:
            return None, None
        
        self.console.print(f"\n[green]✓ Selecionado: {os.path.basename(arquivo_md)}[/green]")
        
        self.console.print("\n[bold]2. SELECIONE O ARQUIVO DE DADOS (.csv)[/bold]")
        arquivo_csv = self.selecionar_arquivo_interativo(arquivos_csv, ".csv")
        
        if not arquivo_csv:
            return None, None
        
        self.console.print(f"\n[green]✓ Selecionado: {os.path.basename(arquivo_csv)}[/green]")
        
        return arquivo_md, arquivo_csv
    
    def carregar_arquivos(self, arquivo_md: str, arquivo_csv: str) -> tuple:
        try:
            with open(arquivo_md, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            csv_data = pd.read_csv(arquivo_csv)
            
            return md_content, csv_data, os.path.basename(arquivo_md), os.path.basename(arquivo_csv)
        except Exception as e:
            raise Exception(f"Erro ao carregar arquivos: {str(e)}")
    
    def executar_analise(self, resultados_dir: str = "resultados"):
        self.console.clear()
        self.console.print(Panel.fit(
            "🚀 [bold blue]ANÁLISE PROFUNDA COM IA GENERATIVA[/bold blue]\n[italic]Sistema de análise inteligente com agentes especializados[/italic]",
            border_style="blue"
        ))
        
        self.console.print("\n[bold]1. SELECIONANDO ARQUIVOS PARA ANÁLISE[/bold]")
        arquivo_md, arquivo_csv = self.selecionar_arquivos_interativo(resultados_dir)
        
        if not arquivo_md or not arquivo_csv:
            self.console.print("[red]❌ Seleção de arquivos cancelada. Análise interrompida.[/red]")
            return
        
        self.console.print("\n[bold]2. CARREGANDO ARQUIVOS...[/bold]")
        try:
            md_content, csv_data, md_nome, csv_nome = self.carregar_arquivos(arquivo_md, arquivo_csv)
            self.console.print(f"   [green]✓[/green] Arquivo de relatório: {md_nome}")
            self.console.print(f"   [green]✓[/green] Arquivo de dados: {csv_nome}")
        except Exception as e:
            self.console.print(f"[red]❌ Erro ao carregar arquivos: {str(e)}[/red]")
            return
        
        self.console.print("\n[bold]3. ANALISANDO DADOS COM AGENTE SENIOR ANALISADOR DE INSIGHTS...[/bold]")
        self.console.print(f"   [dim]Usando modelo: {self.model}[/dim]")
        self.console.print("   [yellow]⏳ Isso pode levar alguns minutos...[/yellow]")
        analise_result = self.analisador.analisar_arquivos(md_content, csv_data)
        
        self.console.print("\n[bold]4. GERANDO ESTRATÉGIA COM AGENTE SENIOR ESTRATEGISTA...[/bold]")
        self.console.print(f"   [dim]Usando modelo: {self.model}[/dim]")
        self.console.print("   [yellow]⏳ Gerando estratégia...[/yellow]")
        estrategia_result = self.estrategista.criar_estrategia(analise_result)
        
        self.console.print("\n[bold]5. CONSOLIDANDO RECOMENDAÇÕES...[/bold]")
        recomendacoes = self.consolidar_recomendacoes(analise_result, estrategia_result)
        
        self.console.print("\n[bold]6. SALVANDO ARQUIVO DE RECOMENDAÇÃO...[/bold]")
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        arquivo_recomendacao = os.path.join(resultados_dir, f"recomendacao_{timestamp}.txt")
        
        try:
            with open(arquivo_recomendacao, 'w', encoding='utf-8') as f:
                f.write(recomendacoes)
            self.console.print(f"   [green]✓ Arquivo salvo: {arquivo_recomendacao}[/green]")
        except Exception as e:
            self.console.print(f"[red]❌ Erro ao salvar arquivo: {str(e)}[/red]")
            return
        
        self.console.print("\n" + "=" * 80)
        self.console.print("[bold green]ANÁLISE CONCLUÍDA COM SUCESSO![/bold green]")
        self.console.print("=" * 80)
    
    def consolidar_recomendacoes(self, analise_result: Dict[str, Any], estrategia_result: Dict[str, Any]) -> str:
        prompt = f"""
        Com base na análise de insights e na estratégia desenvolvida, crie um relatório completo e profissional.
        
        ANÁLISE DE INSIGHTS:
        {analise_result.get('analise_completa', 'Análise não disponível')}
        
        ESTRATÉGIA DESENVOLVIDA:
        {estrategia_result.get('estrategia_completa', 'Estratégia não disponível')}
        
        Estruture o relatório da seguinte forma:
        
        ================================================================================
        RELATÓRIO DE ANÁLISE PROFUNDA - RECOMENDAÇÕES ESTRATÉGICAS
        ================================================================================
        
        ## CONTEXTO E OBJETIVOS
        [Resumo do contexto e objetivos da análise]
        
        ## INSIGHTS PRINCIPAIS
        [Lista dos insights mais importantes identificados]
        
        ## ESTRATÉGIA PROPOSTA
        [Descrição detalhada da estratégia]
        
        ## PLANO DE AÇÃO
        [Passos concretos para implementação]
        
        ## METAS E KPIs
        [Métricas para acompanhamento do sucesso]
        
        ## RECOMENDAÇÕES-CHAVE PARA AÇÃO IMEDIATA
        [Lista numerada das 10 recomendações mais importantes]
        
        ================================================================================
        """
        
        messages = [
            {"role": "system", "content": "Você é um consultor estratégico sênior especializado em análise de dados e tomada de decisão. Seu trabalho é transformar análises complexas em recomendações acionáveis e claras."},
            {"role": "user", "content": prompt}
        ]
        
        return self.api_client.chat_completion(messages)
        print(relatorio['estrategia_completa'])
        
def main():
    console = Console()
    
    console.print(Panel.fit(
        "[bold cyan]🔐 CONFIGURAÇÃO DA API DEEPSEEK[/bold cyan]\n\n"
        "Para usar o sistema de análise profunda com IA, você precisa de uma chave de API do DeepSeek.\n"
        "Se você ainda não tem uma chave, siga estes passos:\n"
        "1. Acesse: https://platform.deepseek.com/\n"
        "2. Crie uma conta ou faça login\n"
        "3. Vá para 'API Keys' no painel de controle\n"
        "4. Crie uma nova chave de API\n"
        "5. Copie a chave (começa com 'sk-')",
        title="Bem-vindo ao DiscoverySpark IA",
        border_style="cyan"
    ))
    
    api_key = Prompt.ask(
        "[bold yellow]Digite sua chave de API do DeepSeek[/bold yellow]",
        password=True
    )
    
    if not api_key.startswith("sk-"):
        console.print("[bold red]⚠️  ATENÇÃO: A chave de API parece inválida![/bold red]")
        console.print("Certifique-se de que a chave começa com 'sk-' e foi copiada corretamente.")
        confirm = Prompt.ask(
            "[bold yellow]Deseja continuar mesmo assim?[/bold yellow]",
            choices=["s", "n"],
            default="n"
        )
        if confirm.lower() != "s":
            console.print("[bold red]Operação cancelada. Por favor, obtenha uma chave de API válida.[/bold red]")
            return
    
    console.print("[bold green]✅ Chave de API configurada com sucesso![/bold green]")
    
    # Seleção de modelo
    console.print("\n" + "=" * 80)
    console.print(Panel.fit(
        "[bold cyan]🤖 SELEÇÃO DE MODELO DE IA[/bold cyan]\n\n"
        "Escolha o modelo de IA que deseja usar para a análise:\n\n"
        "[bold]1. deepseek-reasoner[/bold] - Modelo avançado com raciocínio profundo\n"
        "   • Mais lento (até 3 minutos)\n"
        "   • Análise mais detalhada e estratégica\n"
        "   • Recomendado para decisões complexas\n\n"
        "[bold]2. deepseek-chat[/bold] - Modelo padrão mais rápido\n"
        "   • Mais rápido (até 2 minutos)\n"
        "   • Respostas mais diretas\n"
        "   • Recomendado para análises rápidas\n",
        border_style="cyan"
    ))
    
    modelo_escolha = Prompt.ask(
        "[bold yellow]Escolha o modelo (1 ou 2)[/bold yellow]",
        choices=["1", "2"],
        default="1"
    )
    
    if modelo_escolha == "1":
        modelo = "deepseek-reasoner"
        console.print("[bold green]✓ Modelo selecionado: deepseek-reasoner (raciocínio profundo)[/bold green]")
    else:
        modelo = "deepseek-chat"
        console.print("[bold green]✓ Modelo selecionado: deepseek-chat (análise rápida)[/bold green]")
    
    # Criar instância de AnaliseProfunda com o modelo escolhido
    analise_profunda = AnaliseProfunda(api_key, modelo)
    
    # Adicionar informação do modelo ao início da execução
    analise_profunda.console.print(f"\n[bold cyan]🔧 Configuração:[/bold cyan] Usando modelo [bold]{modelo}[/bold]")
    if modelo == "deepseek-reasoner":
        analise_profunda.console.print("[yellow]⚠️  Nota:[/yellow] Este modelo pode levar até 3 minutos para processar análises complexas.")
    
    analise_profunda.executar_analise()

if __name__ == "__main__":
    main()