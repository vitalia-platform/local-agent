"""
prisma_logger.py — Rastreabilidade, Estatísticas em Tempo Real e JSON Sharding

Responsabilidades:
- Escrever decisões da triagem direto no PRISMA_LOG.csv
- Salvar logs de auditoria detalhados e rastreáveis por artigo (JSON Sharding)
- Monitorar estatísticas de progresso em tempo real
"""

import csv
import json
import os
import sys
import time

class PrismaLogger:
    """Orquestrador de persistência de triagem com escrita no PRISMA_LOG.csv e JSON sharding."""
    
    def __init__(
        self,
        prisma_log_path: str,
        shards_dir: str = "saida/shards",
        log_file_path: str = "execution_log.txt"
    ):
        self.prisma_log_path = prisma_log_path
        self.shards_dir = shards_dir
        self.log_file_path = log_file_path
        
        # Garante as pastas
        os.makedirs(os.path.dirname(prisma_log_path) if os.path.dirname(prisma_log_path) else ".", exist_ok=True)
        os.makedirs(shards_dir, exist_ok=True)
        
        # Mapeia colunas canônicas
        self.fieldnames = [
            "Title", "Authors", "Year", "Journal", "DOI",
            "Abstract", "Status", "Exclusion_Reason", "Source"
        ]
        
    def get_stats(self) -> dict:
        """Calcula estatísticas de progresso lendo o PRISMA_LOG.csv em tempo real."""
        stats = {
            "total": 0,
            "aguardando": 0,
            "incluidos": 0,
            "excluidos": 0,
            "erros": 0
        }
        
        if not os.path.exists(self.prisma_log_path):
            return stats
            
        try:
            with open(self.prisma_log_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    stats["total"] += 1
                    status = row.get("Status", "").strip()
                    if status == "Aguardando Fase 1":
                        stats["aguardando"] += 1
                    elif status == "Incluido Fase 1":
                        stats["incluidos"] += 1
                    elif status == "Excluido Fase 1":
                        stats["excluidos"] += 1
                    elif "Erro" in status:
                        stats["erros"] += 1
        except Exception as e:
            print(f"\033[91m[ERRO] Falha ao ler estatísticas do PRISMA_LOG: {e}\033[0m")
            
        return stats

    def show_progress_bar(self, stats: dict) -> None:
        """Exibe uma barra de progresso formatada com detalhes estatísticos no terminal."""
        total = stats["total"]
        if total == 0:
            return
            
        concluidos = total - stats["aguardando"]
        porcentagem = (concluidos / total) * 100
        bar_length = 30
        filled_length = int(round(bar_length * concluidos / float(total)))
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        
        sys.stdout.write(
            f"\r\033[94mProgresso: [{bar}] {porcentagem:.1f}% ({concluidos}/{total}) "
            f"| Incluídos: \033[92m{stats['incluidos']}\033[94m | Excluídos: \033[91m{stats['excluidos']}\033[94m "
            f"| Erros: \033[93m{stats['erros']}\033[94m\033[0m"
        )
        sys.stdout.flush()

    def save_decision(
        self,
        article_title: str,
        decision: str,
        exclusion_reason: str,
        raw_response: dict,
        article_data: dict
    ) -> None:
        """
        Salva o resultado da triagem:
        1. Atualiza a linha correspondente no PRISMA_LOG.csv
        2. Salva um shard JSON robusto e auditável para este artigo
        """
        # 1. JSON Sharding (Rastreabilidade Absoluta)
        safe_filename = "".join([c if c.isalnum() else "_" for c in article_title[:80]]) + ".json"
        shard_path = os.path.join(self.shards_dir, safe_filename)
        
        audit_payload = {
            "title": article_title,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "article_metadata": article_data,
            "llm_response": raw_response
        }
        
        try:
            with open(shard_path, "w", encoding="utf-8") as jf:
                json.dump(audit_payload, jf, indent=2, ensure_ascii=False)
        except Exception as e:
            self.write_execution_log(f"Erro ao salvar shard para '{article_title}': {e}")
            
        # 2. Atualização atômica do CSV
        self.update_csv_row(article_title, decision, exclusion_reason)

    def update_csv_row(self, article_title: str, status: str, exclusion_reason: str) -> None:
        """Atualiza uma linha específica no PRISMA_LOG.csv baseado no Título."""
        if not os.path.exists(self.prisma_log_path):
            return
            
        rows = []
        updated = False
        
        with open(self.prisma_log_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("Title", "").strip().lower() == article_title.strip().lower():
                    row["Status"] = status
                    row["Exclusion_Reason"] = exclusion_reason
                    updated = True
                rows.append(row)
                
        if updated:
            with open(self.prisma_log_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()
                writer.writerows(rows)

    def write_execution_log(self, message: str) -> None:
        """Grava uma mensagem com timestamp no execution_log.txt."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(self.log_file_path, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {message}\n")
        except Exception:
            pass
