"""
run_fase1.py — Orquestrador do Processamento LLM de Triagem (Fase 1)

Uso:
    python run_fase1.py [--config ./criteria_config.yaml]
"""

import argparse
import csv
import os
import sys
import time
import json

# Garante que o pacote core seja encontrado
sys.path.insert(0, os.path.dirname(__file__))

from core.config_manager import load_config
from core.ollama_client import query_ollama, check_ollama_alive, unload_model
from core.prompt_engine import build_prompt
from core.prisma_logger import PrismaLogger

def handle_error_menu(article_title: str, error_message: str) -> str:
    """Exibe menu de tratamento de erro no terminal."""
    print("\n\n\033[91m╔══════════════════════════════════════════════════════════╗")
    print("║                ERRO NO PROCESSAMENTO DO ARTIGO           ║")
    print("╚══════════════════════════════════════════════════════════╝\033[0m")
    print(f"Artigo: {article_title}")
    print(f"Erro: {error_message}")
    print("\n\033[93mSelecione a ação:\033[0m")
    print("  [1] Tentar novamente imediatamente")
    print("  [2] Pular este artigo e marcá-lo como 'Erro'")
    print("  [3] Pausar processamento e sair")
    
    while True:
        choice = input("\nEscolha [1/2/3]: ").strip()
        if choice in ["1", "2", "3"]:
            return choice
        print("Opção inválida.")

def run_screening(config: dict, config_path: str):
    # 1. Configurar caminhos e parâmetros
    paths = config.get("paths", {})
    prisma_log_path = os.path.join(paths.get("output_prisma", "saida"), "PRISMA_LOG.csv")
    shards_dir = os.path.join(paths.get("output_prisma", "saida"), "shards")
    
    ollama_cfg = config.get("ollama", {})
    base_url = ollama_cfg.get("base_url", "http://localhost:11434")
    api_url = ollama_cfg.get("api_url", f"{base_url.rstrip('/')}/api/generate")
    model = ollama_cfg.get("model", "llama3")
    options = ollama_cfg.get("options", {})
    
    prompt_config = config.get("prompt_configuration", {})
    
    # 2. Inicializar loggers
    logger = PrismaLogger(prisma_log_path, shards_dir)
    
    # Pre-flight check do Ollama
    print("\nVerificando conexão com Ollama...")
    if not check_ollama_alive(api_url):
        print(f"\033[91m[ERRO] Ollama não está rodando no endpoint: {api_url}\033[0m")
        print("Certifique-se de que o Ollama está ativo (ollama serve) e tente novamente.")
        sys.exit(1)
    print("\033[92mOllama ativo! Iniciando triagem...\033[0m")
    
    # 3. Ler artigos que precisam de triagem
    if not os.path.exists(prisma_log_path):
        print(f"\033[91m[ERRO] PRISMA_LOG.csv não encontrado em {prisma_log_path}.\033[0m")
        print("Rode o script run_ingestion.py primeiro para consolidar suas buscas.")
        sys.exit(1)
        
    articles_to_process = []
    with open(prisma_log_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("Status", "").strip() == "Aguardando Fase 1":
                articles_to_process.append(row)
                
    total_to_process = len(articles_to_process)
    if total_to_process == 0:
        print("\n\033[92m✔ Nenhum artigo aguardando triagem no PRISMA_LOG.csv!\033[0m")
        sys.exit(0)
        
    print(f"\nArtigos aguardando triagem nesta rodada: \033[92m{total_to_process}\033[0m")
    time.sleep(1)
    
    # 4. Loop de Processamento
    processed_count = 0
    try:
        for idx, article in enumerate(articles_to_process, 1):
            title = article.get("Title", "").strip()
            abstract = article.get("Abstract", "").strip()
            
            stats = logger.get_stats()
            logger.show_progress_bar(stats)
            
            # Constrói o prompt dinamicamente
            prompt = build_prompt(title, abstract, prompt_config)
            
            success = False
            while not success:
                try:
                    response_json = query_ollama(
                        prompt=prompt,
                        api_url=api_url,
                        model=model,
                        options=options
                    )
                    
                    # Parsear a resposta JSON retornada pelo Ollama
                    raw_text = response_json.get("response", "").strip()
                    # Limpa possíveis blocos markdown do modelo
                    if raw_text.startswith("```json"):
                        raw_text = raw_text.split("```json", 1)[1]
                    if "```" in raw_text:
                        raw_text = raw_text.split("```", 1)[0]
                    raw_text = raw_text.strip()
                    
                    parsed_res = json.loads(raw_text)
                    decision = parsed_res.get("final_decision", "EXCLUIR").strip().upper()
                    
                    # Determina o status canônico
                    status_log = "Incluido Fase 1" if decision == "INCLUIR" else "Excluido Fase 1"
                    reason = parsed_res.get("reasoning", "Sem justificativa")
                    
                    # Salva decisão
                    logger.save_decision(title, status_log, reason, parsed_res, article)
                    success = True
                    processed_count += 1
                    
                except Exception as e:
                    # Envia erro ao menu do pesquisador
                    choice = handle_error_menu(title, str(e))
                    if choice == "1":
                        # Tentar novamente (reinicia o laço success)
                        continue
                    elif choice == "2":
                        # Pula e registra erro
                        logger.update_csv_row(title, f"Erro: {str(e)[:150]}", "Falha de processamento")
                        success = True
                    elif choice == "3":
                        print("\nProcessamento pausado pelo usuário.")
                        return
                        
    finally:
        # 5. Sempre forçar liberação de VRAM ao encerrar
        print("\n\nLiberando recursos de VRAM do Ollama...")
        unload_model(api_url, model)
        
        # Relatório Final
        final_stats = logger.get_stats()
        print(f"\n\033[94m{'═'*60}\033[0m")
        print(f"\033[92m  TRIAGEM DA FASE 1 CONCLUÍDA\033[0m")
        print(f"\033[94m{'═'*60}\033[0m")
        print(f"  Artigos triados nesta rodada:   {processed_count}")
        print(f"  Total Incluídos na Fase 1:     \033[92m{final_stats['incluidos']}\033[0m")
        print(f"  Total Excluídos na Fase 1:     \033[91m{final_stats['excluidos']}\033[0m")
        print(f"  Aguardando processamento:       {final_stats['aguardando']}")
        print(f"\033[94m{'═'*60}\033[0m\n")

def main():
    parser = argparse.ArgumentParser(
        description="Fase 1 Screening: processamento inteligente via Ollama"
    )
    parser.add_argument(
        "--config",
        default="./criteria_config.yaml",
        help="Caminho para o criteria_config.yaml (default: ./criteria_config.yaml)",
    )
    args = parser.parse_args()
    
    config = load_config(args.config)
    run_screening(config, args.config)

if __name__ == "__main__":
    main()
