"""
ollama_client.py — Cliente de Comunicação com API Local do Ollama

Responsabilidades:
- Conectar via requisições HTTP (POST) à API local do Ollama
- Implementar pre-flight check de conexão
- Retry automático com backoff exponencial e log/report terminal de tentativas
- Forçar liberação de VRAM (keep_alive: 0)
"""

import time
import requests
import json
import os
import sys

def check_ollama_alive(api_url: str) -> bool:
    """Verifica se o servidor Ollama está ativo e respondendo na porta."""
    try:
        base_url = api_url.rsplit("/api/", 1)[0]
        response = requests.get(base_url, timeout=2.0)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def query_ollama(
    prompt: str,
    api_url: str,
    model: str,
    options: dict | None = None,
    log_file_path: str = "execution_log.txt"
) -> dict:
    """
    Envia prompt para o Ollama com retry de 3 tentativas, backoff exponencial e liberação de VRAM.
    
    Exibe reports amarelos no terminal e grava falhas de conexão no execution_log.txt.
    """
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model,
        "prompt": prompt,
        "format": "json",
        "stream": False,
        "options": options or {}
    }
    
    # 3 Tentativas silenciosas com backoff exponencial antes do menu interativo
    max_retries = 3
    wait_times = [5, 15, 30]
    
    # Registra no log de execuções
    def _log_attempt(attempt: int, error_msg: str, title_hint: str = ""):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [RETRY {attempt}/{max_retries}] Erro: {error_msg} | Artigo: {title_hint}\n"
        try:
            with open(log_file_path, "a", encoding="utf-8") as lf:
                lf.write(log_line)
        except Exception:
            pass

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=120)
            if response.status_code == 200:
                return response.json()
            else:
                err_msg = f"HTTP {response.status_code}: {response.text}"
                print(f"\033[93m[RETRY {attempt}/{max_retries}] Ollama retornou erro {response.status_code}. Aguardando {wait_times[attempt-1]}s...\033[0m")
                _log_attempt(attempt, err_msg)
        except requests.exceptions.RequestException as e:
            err_msg = str(e)
            print(f"\033[93m[RETRY {attempt}/{max_retries}] Falha de conexão com Ollama. Aguardando {wait_times[attempt-1]}s...\033[0m")
            _log_attempt(attempt, err_msg)
            
        if attempt < max_retries:
            time.sleep(wait_times[attempt - 1])
            
    # Se todas falharem, levanta exceção para ser tratada no menu principal de triagem
    raise ConnectionError("Falha de conexão com o Ollama após 3 tentativas.")

def unload_model(api_url: str, model: str) -> None:
    """Força o descarregamento da VRAM (keep_alive: 0)."""
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model,
        "prompt": "",
        "keep_alive": 0,
        "stream": False
    }
    try:
        requests.post(api_url, headers=headers, json=payload, timeout=5)
    except Exception:
        pass
