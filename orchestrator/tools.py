# tools.py
# Criado em: 29-05-2026 14:48:00(GMT-04:00)
# Caminho: /home/andre/projetos/assistidos/servidor-ia/tools.py

import os
import ast
import uuid
import time
import json
import logging
import requests
import redis
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
from duckduckgo_search import DDGS

# Configura o Logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("VitaliaTools")

# Carrega as variáveis de ambiente do .env
load_dotenv()

NO2_SERVER_IP = os.getenv("NO2_SERVER_IP", "192.168.0.254")
NO2_OLLAMA_PORT = os.getenv("NO2_OLLAMA_PORT", "11434")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
NO1_LOCAL_OLLAMA_URL = os.getenv("NO1_LOCAL_OLLAMA_URL", "http://localhost:11434")

POSTGRES_DB = os.getenv("POSTGRES_DB", "vitalia_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "vitalia_admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "altere_este_segredo_123")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
# No notebook (Nó 1), o postgres roda localmente
POSTGRES_HOST = "localhost" 

def get_db_connection():
    """Retorna conexão local do pgvector (Nó 1)."""
    return psycopg2.connect(
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT
    )

def get_redis_client():
    """Conecta no Redis centralizado no Servidor (Nó 2)."""
    return redis.Redis(host=NO2_SERVER_IP, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True)

# -------------------------------------------------------------
# SEMÁFORO DE GPU LOCAL (MX450 - 2GB)
# -------------------------------------------------------------

def acquire_local_gpu_lock(timeout_seconds: int = 40) -> bool:
    """
    Tenta descarregar todos os modelos do Ollama local da MX450 e aguarda a liberação total da VRAM.
    Se não liberar a GPU dentro do timeout, levanta uma exceção para evitar rodar em CPU.
    """
    logger.info("Solicitando liberação de GPU local (MX450) para o Docling...")
    
    # 1. Consulta o Ollama local para saber quais modelos estão na memória
    try:
        ps_response = requests.get(f"{NO1_LOCAL_OLLAMA_URL}/api/ps", timeout=5)
        if ps_response.status_code == 200:
            models = ps_response.json().get("models", [])
            if not models:
                logger.info("Nenhum modelo carregado na GPU local. GPU livre.")
                return True
                
            # Envia comando keep_alive: 0 para cada modelo ativo
            for model in models:
                model_name = model.get("name")
                logger.info(f"Sinalizando descarregamento do modelo '{model_name}'...")
                # Chamamos /api/generate para descarregar o modelo
                requests.post(
                    f"{NO1_LOCAL_OLLAMA_URL}/api/generate",
                    json={"model": model_name, "keep_alive": 0},
                    timeout=5
                )
        else:
            logger.warning(f"Ollama local retornou status {ps_response.status_code}. Prosseguindo sob risco.")
    except Exception as e:
        logger.warning(f"Não foi possível falar com Ollama local: {str(e)}. Assumindo GPU ocupada ou inexistente.")

    # 2. Loop de espera ativa (Polling) para aguardar a VRAM esvaziar
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        try:
            ps_response = requests.get(f"{NO1_LOCAL_OLLAMA_URL}/api/ps", timeout=3)
            if ps_response.status_code == 200:
                models = ps_response.json().get("models", [])
                if not models:
                    logger.info("GPU liberada com sucesso do Ollama local!")
                    return True
                logger.info(f"Aguardando liberação da GPU... {len(models)} modelo(s) ainda ativo(s).")
            time.sleep(2)
        except Exception:
            time.sleep(2)
            
    # Se estourar o timeout, lança exceção para não forçar processamento no CPU
    raise RuntimeError(
        "TIMEOUT: A GPU local (MX450) continua ocupada pelo Ollama local. "
        "A operação de parsing do Docling foi abortada para evitar sobrecarga da CPU."
    )

# -------------------------------------------------------------
# PARSING AST & CODE CHUNKING
# -------------------------------------------------------------

def chunk_python_code(code: str) -> list:
    """Quebra código Python de forma semântica (AST), isolando funções e classes."""
    try:
        tree = ast.parse(code)
    except Exception as e:
        # Se falhar a sintaxe, fallback para o bloco todo
        return [{"chunk_type": "code_block", "name": "raw_content", "start_line": 1, "end_line": len(code.split("\n")), "content": code}]

    chunks = []
    lines = code.split("\n")

    class CodeVisitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node):
            start = node.lineno
            end = node.end_lineno if hasattr(node, 'end_lineno') else len(lines)
            func_code = "\n".join(lines[start-1:end])
            chunks.append({
                "chunk_type": "function",
                "name": node.name,
                "start_line": start,
                "end_line": end,
                "content": func_code
            })
            self.generic_visit(node)

        def visit_ClassDef(self, node):
            start = node.lineno
            end = node.end_lineno if hasattr(node, 'end_lineno') else len(lines)
            class_code = "\n".join(lines[start-1:end])
            chunks.append({
                "chunk_type": "class",
                "name": node.name,
                "start_line": start,
                "end_line": end,
                "content": class_code
            })
            self.generic_visit(node)

    visitor = CodeVisitor()
    visitor.visit(tree)

    if not chunks:
        chunks.append({
            "chunk_type": "code_block",
            "name": "module",
            "start_line": 1,
            "end_line": len(lines),
            "content": code
        })

    return chunks

def chunk_generic_code(content: str) -> list:
    """Chunker genérico para linguagens não-Python (splits simples por linhas)."""
    lines = content.split("\n")
    chunks = []
    chunk_size = 50
    for i in range(0, len(lines), chunk_size):
        chunk_lines = lines[i:i+chunk_size]
        chunks.append({
            "chunk_type": "code_block",
            "name": f"block_{i // chunk_size}",
            "start_line": i + 1,
            "end_line": min(i + chunk_size, len(lines)),
            "content": "\n".join(chunk_lines)
        })
    return chunks

# -------------------------------------------------------------
# INGESTÃO & SINCRONIZAÇÃO DE RAG (LOCAL + REDIS PUB/SUB)
# -------------------------------------------------------------

def get_embedding(text: str) -> list:
    """Gera embeddings ligando para o Ollama do Servidor (Nó 2) como fonte primária."""
    # Chama o servidor
    url = f"http://{NO2_SERVER_IP}:{NO2_OLLAMA_PORT}/api/embeddings"
    try:
        response = requests.post(url, json={"model": "nomic-embed-text", "prompt": text}, timeout=10)
        if response.status_code == 200:
            return response.json().get("embedding", [])
    except Exception as e:
        logger.warning(f"Falha ao gerar embedding no Servidor: {str(e)}. Tentando Ollama local.")
    
    # Fallback local
    local_url = f"{NO1_LOCAL_OLLAMA_URL}/api/embeddings"
    try:
        response = requests.post(local_url, json={"model": "nomic-embed-text", "prompt": text}, timeout=10)
        if response.status_code == 200:
            return response.json().get("embedding", [])
    except Exception as e:
        logger.error(f"Falha crítica nos embeddings locais e remotos: {str(e)}")
        
    return [0.0] * 1536  # Retorna vetor dummy em caso de falha crítica total

def save_to_rag(filepath: str, content: str = None) -> str:
    """
    Lógica unificada de Ingestão de Código (AST) e Documentos (Docling local na MX450 GPU).
    Salva localmente no pgvector e transmite reativamente para o servidor via Redis Pub/Sub.
    """
    chunks_to_insert = []
    
    # CASO A: Documento PDF (Aciona Docling local na GPU MX450)
    if filepath.lower().endswith(".pdf"):
        # Executa semáforo de GPU
        acquire_local_gpu_lock()
        
        # Imports tardios (Lazy Imports) para evitar carregar o PyTorch no boot do AutoGen
        try:
            import torch
            from docling.document_converter import DocumentConverter
            from docling.datamodel.base_models import InputFormat
            from docling.datamodel.pipeline_options import PdfPipelineOptions
            from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
            
            logger.info(f"Inicializando Docling na GPU (CUDA) para o arquivo: {filepath}")
            
            # Força o Docling a rodar em CUDA
            pipeline_options = PdfPipelineOptions()
            pipeline_options.do_ocr = True  # Ativa OCR
            pipeline_options.accelerator_options = AcceleratorOptions(device=AcceleratorDevice.CUDA)
            
            converter = DocumentConverter(
                allowed_formats=[InputFormat.PDF],
                pipeline_options=pipeline_options
            )
            # Nota: O Docling roda em GPU se o PyTorch debaixo dele estiver configurado com CUDA.
            # Verificamos se o cuda está disponível no torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Docling usando dispositivo de hardware: {device}")
            
            # Faz a conversão
            result = converter.convert(filepath)
            doc_dict = result.document.export_to_dict()
            
            # Parseia os elementos extraídos (tabelas, figuras, parágrafos)
            # Para cada elemento no dicionário exportado, geramos um chunk estruturado
            elements = doc_dict.get("texts", [])
            for idx, elem in enumerate(elements[:150]): # Limite de chunks para evitar estouro
                page_no = elem.get("prov", [{}])[0].get("page_no", 1)
                text_content = elem.get("text", "").strip()
                if not text_content:
                    continue
                    
                chunks_to_insert.append({
                    "id": str(uuid.uuid4()),
                    "chunk_type": elem.get("label", "text"),
                    "page_number": page_no,
                    "content": text_content,
                    "bbox": elem.get("prov", [{}])[0].get("bbox", []),
                    "metadata": {"source": "docling_pdf"}
                })
                
            # Limpa cache CUDA do PyTorch e chama GC
            del converter
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            import gc
            gc.collect()
            logger.info("Docling finalizado. GPU local liberada.")
            
        except Exception as e:
            logger.error(f"Erro crítico no processamento com Docling: {str(e)}")
            raise e
            
    # CASO B: Arquivo de código ou texto (Processamento de CPU leve)
    else:
        if not content:
            # Lê o arquivo em disco
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                
        # AST Chunking para Python
        if filepath.endswith(".py"):
            raw_chunks = chunk_python_code(content)
        else:
            raw_chunks = chunk_generic_code(content)
            
        for chunk in raw_chunks:
            chunks_to_insert.append({
                "id": str(uuid.uuid4()),
                "chunk_type": chunk["chunk_type"],
                "page_number": 1,
                "content": f"Arquivo: {filepath}\nLinhas {chunk['start_line']}-{chunk['end_line']}\n\n{chunk['content']}",
                "bbox": [],
                "metadata": {
                    "name": chunk.get("name", ""),
                    "start_line": chunk["start_line"],
                    "end_line": chunk["end_line"]
                }
            })

    # 3. Gera os Embeddings e insere os dados
    if not chunks_to_insert:
        return "Nenhum conteúdo válido extraído."
        
    logger.info(f"Gerando embeddings para {len(chunks_to_insert)} chunks...")
    for idx, chunk in enumerate(chunks_to_insert):
        chunk["embedding"] = get_embedding(chunk["content"])
        
    # 4. Grava no pgvector local (Notebook)
    logger.info("Gravando chunks no pgvector local do Notebook...")
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
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

        query = """
            INSERT INTO document_chunks 
            (id, filepath, chunk_type, page_number, content, embedding, bbox, metadata)
            VALUES (%s, %s, %s, %s, %s, %s::vector, %s::jsonb, %s::jsonb)
            ON CONFLICT (id) DO UPDATE SET
                content = EXCLUDED.content,
                embedding = EXCLUDED.embedding,
                metadata = EXCLUDED.metadata;
        """
        data_tuples = [
            (
                c["id"],
                filepath,
                c["chunk_type"],
                c["page_number"],
                c["content"],
                c["embedding"],
                json.dumps(c.get("bbox", [])),
                json.dumps(c.get("metadata", {}))
            )
            for c in chunks_to_insert
        ]
        cur.executemany(query, data_tuples)
        conn.commit()
    except Exception as e:
        logger.error(f"Erro ao salvar localmente no pgvector: {str(e)}")
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

    # 5. Publica os chunks no Redis Pub/Sub do Servidor para sincronia reativa
    try:
        logger.info("Publicando chunks no Redis Pub/Sub para sincronização com o Servidor...")
        r = get_redis_client()
        payload = {
            "filepath": filepath,
            "chunks": chunks_to_insert
        }
        r.publish("vitalia:rag:sync", json.dumps(payload))
        logger.info("Publicado com sucesso no Redis canal 'vitalia:rag:sync'.")
    except Exception as e:
        logger.warning(f"Não foi possível publicar no Redis Pub/Sub (Servidor offline?): {str(e)}")

    return f"Sucesso! {len(chunks_to_insert)} chunks salvos no pgvector local e sincronizados via Redis."

# -------------------------------------------------------------
# OUTRAS TOOLS (SPRINT STATE & WEB SEARCH)
# -------------------------------------------------------------

def update_sprint_state(status_json: str) -> str:
    """
    Atualiza o estado quente da Sprint no Redis e gera o arquivo físico de log
    no repositório Git de sessão aninhado (.agent/session/sprint_atual.md).
    """
    try:
        # Tenta decodificar o JSON recebido
        data = json.loads(status_json)
    except Exception as e:
        return f"Erro: status_json inválido. {str(e)}"
        
    sprint_title = data.get("sprint_title", "Sprint Vitalia")
    status = data.get("status", "Em progresso")
    tasks = data.get("tasks", [])
    
    # 1. Converte em Markdown legível
    markdown_content = f"""# 📍 Estado Atual da Sprint: {sprint_title}
*Última Atualização: {time.strftime('%d-%m-%Y %H:%M:%S(GMT-04:00)')}*
**Status:** {status}

## 📋 Lista de Tarefas (Checklist)
"""
    for task in tasks:
        symbol = "[x]" if task.get("completed") else "[ ]"
        priority = f" (P{task.get('priority')})" if "priority" in task else ""
        markdown_content += f"- `{symbol}` {task.get('title')}{priority}\n"
        
    # 2. Grava no Redis (Quente)
    try:
        r = get_redis_client()
        r.hset("vitalia:sprint:state", mapping={
            "json": status_json,
            "markdown": markdown_content,
            "last_updated": time.time()
        })
    except Exception as e:
        logger.warning(f"Falha ao salvar no Redis quente: {str(e)}")

    # 3. Grava no Git de Sessão (Frio)
    session_dir = ".agent/session"
    if os.path.exists(session_dir):
        file_path = os.path.join(session_dir, "sprint_atual.md")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            logger.info("Sprint salva no repositório de sessão Git.")
        except Exception as e:
            return f"Erro ao escrever o arquivo físico de sessão: {str(e)}"
    else:
        logger.warning("Diretório de sessão .agent/session não encontrado. Estado salvo apenas no Redis.")

    return f"Sucesso! Sprint '{sprint_title}' atualizada no Redis e gravada no Git de sessão."

def web_search(query: str) -> str:
    """Executa busca na web via DuckDuckGo Search e retorna resumo estruturado."""
    logger.info(f"Buscando na Web por: '{query}'")
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=5)]
            if not results:
                return "Nenhum resultado encontrado."
                
            summary = f"Resultados da busca para: '{query}'\n\n"
            for idx, r in enumerate(results):
                summary += f"[{idx+1}] {r.get('title')}\nURL: {r.get('href')}\nSnippet: {r.get('body')}\n\n"
            return summary
    except Exception as e:
        logger.error(f"Erro na busca do DuckDuckGo: {str(e)}")
        return f"Falha na busca: {str(e)}"
