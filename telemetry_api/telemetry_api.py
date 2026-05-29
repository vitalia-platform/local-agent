# telemetry_api.py
# Criado em: 29-05-2026 14:45:00(GMT-04:00)
# Caminho: /home/andre/projetos/assistidos/servidor-ia/telemetry_api.py

import os
import subprocess
import re
import json
import logging
import asyncio
import threading
from typing import Dict, Any
from fastapi import FastAPI, BackgroundTasks
import redis
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Configura o Logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("TelemetryAPI")

# Carrega as variáveis de ambiente
load_dotenv()

app = FastAPI(title="Vitalia Server Telemetry & Sync Bridge", version="1.0.0")

# Parametrização do Redis e DB a partir do .env
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

POSTGRES_DB = os.getenv("POSTGRES_DB", "vitalia_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "vitalia_admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "altere_este_segredo_123")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
# No servidor (Nó 2), o host do DB é 'db' se estiver na rede docker-compose, ou 'localhost'
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db") 

def get_db_connection():
    """Retorna uma conexão síncrona com o PostgreSQL/pgvector."""
    return psycopg2.connect(
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT
    )

def parse_nvidia_smi() -> Dict[str, Any]:
    """
    Executa o nvidia-smi e parseia o uso de VRAM de forma resiliente.
    Em caso de falha ou ausência de GPU NVIDIA, retorna dados em modo fallback.
    """
    try:
        # Comando para obter o uso de memória de GPU em formato limpo
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used,memory.total,utilization.gpu", "--format=csv,noheader,nounits"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        output = result.stdout.strip()
        if not output:
            raise ValueError("nvidia-smi retornou dados vazios")
            
        parts = [p.strip() for p in output.split(",")]
        vram_used = int(parts[0])
        vram_total = int(parts[1])
        gpu_util = int(parts[2])
        
        return {
            "status": "active",
            "vram_used_mb": vram_used,
            "vram_total_mb": vram_total,
            "vram_percent": round((vram_used / vram_total) * 100, 2),
            "gpu_utilization_percent": gpu_util
        }
    except Exception as e:
        logger.warning(f"Falha ao executar nvidia-smi: {str(e)}. Retornando fallback de GPU.")
        return {
            "status": "unavailable",
            "vram_used_mb": 0,
            "vram_total_mb": 0,
            "vram_percent": 0.0,
            "gpu_utilization_percent": 0
        }

def get_system_ram() -> Dict[str, int]:
    """Parseia /proc/meminfo ou roda free -m de forma portátil no Linux guest."""
    try:
        result = subprocess.run(
            ["free", "-m"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        lines = result.stdout.strip().split("\n")
        # Encontra a linha que começa com 'Mem:'
        for line in lines:
            if line.startswith("Mem:"):
                parts = re.split(r"\s+", line)
                total = int(parts[1])
                used = int(parts[2])
                free = int(parts[3])
                return {"total_mb": total, "used_mb": used, "free_mb": free}
    except Exception as e:
        logger.error(f"Erro ao ler RAM do sistema: {str(e)}")
    
    return {"total_mb": 0, "used_mb": 0, "free_mb": 0}

@app.get("/telemetry", response_model=Dict[str, Any])
def get_telemetry():
    """Endpoint principal de monitoramento de hardware do Nó 2."""
    gpu_data = parse_nvidia_smi()
    ram_data = get_system_ram()
    
    # Obtém carga de CPU de 1, 5, 15 min
    try:
        load1, load5, load15 = os.getloadavg()
    except Exception:
        load1, load5, load15 = 0.0, 0.0, 0.0

    return {
        "node": "Node 2 (Server)",
        "gpu": gpu_data,
        "ram": ram_data,
        "cpu": {
            "load_1m": load1,
            "load_5m": load5,
            "load_15m": load15
        }
    }

# -------------------------------------------------------------
# BRIDGE DE SINCRONIA REATIVA (RAG PUB/SUB LISTENER)
# -------------------------------------------------------------

def start_redis_sync_listener():
    """Loop síncrono executado em thread secundária para ouvir o Redis."""
    logger.info("Iniciando Listener de RAG do Redis...")
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True)
    pubsub = r.pubsub()
    pubsub.subscribe("vitalia:rag:sync")

    for message in pubsub.listen():
        if message["type"] == "message":
            try:
                data = json.loads(message["data"])
                filepath = data.get("filepath")
                chunks = data.get("chunks", [])
                
                logger.info(f"Recebida mensagem de sincronização para {filepath} ({len(chunks)} chunks)")
                sync_chunks_to_db(filepath, chunks)
            except Exception as e:
                logger.error(f"Falha ao processar mensagem do Redis Pub/Sub: {str(e)}")

def sync_chunks_to_db(filepath: str, chunks: list):
    """Grava os chunks recebidos no banco de dados pgvector local do servidor."""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Garante a existência da tabela de chunks caso não exista
        cur.execute("""
            CREATE EXTENSION IF NOT EXISTS vector;
            CREATE TABLE IF NOT EXISTS document_chunks (
                id UUID PRIMARY KEY,
                filepath TEXT,
                chunk_type VARCHAR(50),
                page_number INTEGER,
                content TEXT,
                embedding VECTOR(1536),
                bbox JSONB,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()

        # Prepara a query de inserção / atualização
        query = """
            INSERT INTO document_chunks 
            (id, filepath, chunk_type, page_number, content, embedding, bbox, metadata)
            VALUES (%s, %s, %s, %s, %s, %s::vector, %s::jsonb, %s::jsonb)
            ON CONFLICT (id) DO UPDATE SET
                content = EXCLUDED.content,
                embedding = EXCLUDED.embedding,
                metadata = EXCLUDED.metadata;
        """
        
        # Prepara os dados
        data_tuples = []
        for chunk in chunks:
            data_tuples.append((
                chunk["id"],
                filepath,
                chunk.get("chunk_type", "text"),
                chunk.get("page_number", 1),
                chunk["content"],
                chunk["embedding"],  # O pgvector aceita formato string '[val1, val2, ...]'
                json.dumps(chunk.get("bbox", [])),
                json.dumps(chunk.get("metadata", {}))
            ))
            
        # Executa inserção em lote
        if data_tuples:
            cur.executemany(query, data_tuples)
            conn.commit()
            logger.info(f"Sincronização concluída com sucesso para {filepath}: {len(chunks)} chunks inseridos/atualizados.")
        
    except Exception as e:
        logger.error(f"Falha crítica ao gravar chunks sincronizados no pgvector: {str(e)}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

# Dispara a thread do Redis na inicialização da aplicação FastAPI
@app.on_event("startup")
def startup_event():
    # Roda em thread separada para não bloquear o event loop assíncrono da API FastAPI
    thread = threading.Thread(target=start_redis_sync_listener, daemon=True)
    thread.start()
    logger.info("Thread do Redis RAG Sync Listener disparada em background.")

if __name__ == "__main__":
    import uvicorn
    # A API escuta na porta 8001 por padrão
    uvicorn.run("telemetry_api:app", host="0.0.0.0", port=8001, reload=False)
