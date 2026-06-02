#!/usr/bin/env python3
import time
import subprocess
import os
import argparse
import sys
from datetime import datetime
from collections import deque
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.table import Table
from rich import box
from rich.align import Align
from rich.text import Text

from dotenv import load_dotenv

# Carrega Variáveis
load_dotenv()

# Configuração de Logs Reversos
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)
LOG_FILE = LOGS_DIR / "vitalia_runner.log"

# Mantém um buffer na memória para a UI (reverso: novos no topo)
ui_log_buffer = deque(maxlen=10)

def write_reverse_log(message: str, level: str = "INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}"
    
    # Adiciona ao topo do buffer da UI
    ui_log_buffer.appendleft(f"[dim]{timestamp}[/dim] [{level}] {message}")
    
    # Adiciona no topo do arquivo físico
    try:
        if LOG_FILE.exists():
            with open(LOG_FILE, 'r') as f:
                content = f.read()
        else:
            content = ""
            
        with open(LOG_FILE, 'w') as f:
            f.write(log_entry + "\n" + content)
    except Exception:
        pass

console = Console()

def get_service_status(container_name):
    if not container_name:
        return "[dim]N/A[/dim]"
    try:
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Status}}", container_name],
            capture_output=True, text=True, check=True
        )
        status = result.stdout.strip()
        if status == "running":
            return "[green]Online 🟢[/green]"
        return f"[yellow]{status}[/yellow]"
    except subprocess.CalledProcessError:
        return "[red]Offline 🔴[/red]"

def generate_layout(node_type, telemetry_process=None):
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="logs", size=12),
        Layout(name="footer", size=3)
    )
    layout["main"].split_row(
        Layout(name="services"),
        Layout(name="info")
    )
    
    # Header
    node_name = "Nó 2 (Servidor)" if node_type == "server" else "Nó 1 (Notebook)"
    layout["header"].update(
        Panel(Align.center(f"[bold cyan]Vitalia Local Agent[/bold cyan] - Status Dashboard | {node_name}"), box=box.ROUNDED)
    )
    
    # Services Table
    table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE)
    table.add_column("Serviço")
    table.add_column("Container")
    table.add_column("Status")
    
    if node_type == "notebook":
        services = [
            ("Orquestrador AG2 (Sandbox)", os.getenv("OPENHANDS_CONTAINER_NAME", "vitalia_openhands")),
            ("Banco de Dados Local (pgvector)", os.getenv("NOTEBOOK_DB_CONTAINER_NAME", "vitalia_db_local")),
        ]
    else:
        services = [
            ("Banco de Dados Principal", os.getenv("DB_CONTAINER_NAME", "vitalia_db")),
            ("Cache & Mensageria", os.getenv("REDIS_CONTAINER_NAME", "vitalia_redis")),
            ("Motor LLM (GPU)", os.getenv("OLLAMA_CONTAINER_NAME", "vitalia_ollama")),
            ("Interface Chat", os.getenv("WEBUI_CONTAINER_NAME", "vitalia_open_webui")),
        ]
        
    for name, container in services:
        table.add_row(name, container, get_service_status(container))
        
    if node_type == "server":
        # Add Telemetry Status manually
        tel_status = "[green]Online 🟢[/green]" if telemetry_process and telemetry_process.poll() is None else "[red]Offline 🔴[/red]"
        table.add_row("API de Telemetria", "(subprocesso)", tel_status)
        
    layout["services"].update(
        Panel(table, title="[bold blue]Serviços em Execução[/bold blue]", border_style="blue")
    )
    
    # Info Panel
    if node_type == "notebook":
        info_text = f"""[bold]Instruções Rápidas:[/bold]
- OpenHands IDE: [underline]http://localhost:3000[/underline]
- Sincronizado com: [cyan]{os.getenv('NO2_SERVER_IP', 'N/A')}[/cyan]

Para rodar o orquestrador:
[green]python orchestrator/orchestrator.py "Sua query"[/green]
        """
    else:
        info_text = f"""[bold]Instruções Rápidas:[/bold]
- WebUI Chat: [underline]http://{os.getenv('NO2_SERVER_IP', 'localhost')}:4000[/underline]
- Ollama Porta: [cyan]{os.getenv('NO2_OLLAMA_PORT', '11434')}[/cyan]
- Telemetria Porta: [cyan]{os.getenv('NO2_TELEMETRY_PORT', '8001')}[/cyan]

O servidor deve permanecer ligado para
atender as requisições do Notebook.
        """
        
    layout["info"].update(
        Panel(info_text, title="[bold yellow]Informações[/bold yellow]", border_style="yellow")
    )
    
    # Logs Panel (Mostra as últimas linhas do topo)
    log_text = Text()
    for line in ui_log_buffer:
        color = "white"
        if "[ERROR]" in line: color = "red"
        elif "[WARN]" in line: color = "yellow"
        elif "[INFO]" in line: color = "green"
        log_text.append(f"{line}\n")
        
    layout["logs"].update(
        Panel(log_text, title="[bold green]Logs Recentes (Ordenação: Mais Novos no Topo)[/bold green]", border_style="green")
    )
    
    # Footer
    layout["footer"].update(
        Panel(Align.center("Pressione [bold red]Ctrl+C[/bold red] para sair do dashboard e encerrar processos locais."), box=box.ROUNDED)
    )
    
    return layout

def main():
    parser = argparse.ArgumentParser(description="Vitalia Monitor")
    parser.add_argument("--node", choices=["server", "notebook"], help="Tipo do nó a monitorar")
    args = parser.parse_args()
    
    node_type = args.node or os.getenv("NODE_TYPE", "notebook")
    
    write_reverse_log(f"Iniciando Dashboard para nó do tipo: {node_type}")
    
    telemetry_proc = None
    
    if node_type == "server":
        write_reverse_log("Iniciando subprocesso da API de Telemetria...")
        try:
            # Roda a telemetria não bloqueante, capturando stderr/out se desejado (aqui deixamos livre)
            telemetry_proc = subprocess.Popen(["python3", "telemetry_api/telemetry_api.py"], 
                                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            # Para não bloquear, definimos a leitura como não bloqueante via fd, ou apenas confiamos que ela sobe
            os.set_blocking(telemetry_proc.stdout.fileno(), False)
            write_reverse_log("Telemetria iniciada na porta " + os.getenv("NO2_TELEMETRY_PORT", "8001"))
        except Exception as e:
            write_reverse_log(f"Falha ao iniciar Telemetria: {e}", "ERROR")

    try:
        with Live(generate_layout(node_type, telemetry_proc), refresh_per_second=2, screen=True) as live:
            while True:
                # Checa logs da telemetria, se rodando
                if telemetry_proc and telemetry_proc.stdout:
                    while True:
                        try:
                            line = telemetry_proc.stdout.readline()
                            if not line: break
                            write_reverse_log(f"Telemetria: {line.strip()}", "INFO")
                        except Exception:
                            break
                            
                live.update(generate_layout(node_type, telemetry_proc))
                time.sleep(1)
                
    except KeyboardInterrupt:
        write_reverse_log("Dashboard encerrado pelo usuário.")
        if telemetry_proc:
            write_reverse_log("Matando subprocesso da Telemetria...")
            telemetry_proc.terminate()
            telemetry_proc.wait()
        console.print("[bold green]Dashboard encerrado.[/bold green]")

if __name__ == "__main__":
    main()
