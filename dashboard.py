import os
import glob
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

console = Console()

def list_reports():
    """Lista todos os arquivos markdown na pasta resultados."""
    files = glob.glob("resultados/*.md")
    return sorted(files, reverse=True)

def render_styled_markdown(content):
    """Renderiza o Markdown com alertas visuais baseados na tendência."""
    lines = content.split('\n')
    styled_content = ""
    
    for line in lines:
        if "|" in line and "Quanto maior" in line:
            # Lógica de Cores baseada nos emojis que o app.py insere
            if "aumenta" in line:
                # Se aumenta o alvo, marcamos em vermelho (Atenção/Risco)
                line = f"[red]{line}[/red]"
            elif "diminui" in line:
                # Se diminui o alvo, marcamos em verde (Oportunidade/Fidelização)
                line = f"[green]{line}[/green]"
        styled_content += line + "\n"
    
    console.print(Markdown(styled_content))

def show_dashboard():
    console.clear()
    console.print(Panel.fit(
        "📊 [bold blue]Dashboard de Insights Spark Clone[/bold blue]\n[italic]Análise de Tendências e Descobertas Relacionais[/italic]", 
        border_style="blue"
    ))
    
    while True:
        reports = list_reports()
        
        if not reports:
            console.print("[red]Nenhum relatório encontrado na pasta /resultados.[/red]")
            break
        
        # Criar uma tabela simples para o menu
        menu_table = Table(show_header=True, header_style="bold magenta", box=None)
        menu_table.add_column("ID", style="cyan")
        menu_table.add_column("Relatórios Disponíveis", style="white")
        
        for i, path in enumerate(reports, 1):
            filename = os.path.basename(path)
            menu_table.add_row(str(i), filename)
        
        console.print(menu_table)
        console.print("[cyan]0.[/cyan] Sair")
        
        choice = Prompt.ask("\nVisualizar relatório nº", choices=[str(i) for i in range(len(reports) + 1)])
        
        if choice == '0':
            console.print("[yellow]Encerrando Dashboard...[/yellow]")
            break
        
        selected_file = reports[int(choice) - 1]
        with open(selected_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        console.clear()
        # Aqui usamos a nossa nova função de renderização inteligente
        render_styled_markdown(content)
        
        Prompt.ask("\n[bold cyan]Pressione [Enter] para voltar ao menu[/bold cyan]")
        console.clear()
        console.print(Panel.fit("📊 [bold blue]Dashboard de Insights Spark Clone[/bold blue]", border_style="blue"))

if __name__ == "__main__":
    show_dashboard()