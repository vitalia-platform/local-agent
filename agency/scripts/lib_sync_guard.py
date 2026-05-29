#!/usr/bin/env python3
"""
Módulo Guardião de Sincronia (.sync_lock)
Usado para garantir a integridade da sincronização de contexto.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def get_git_remote_timestamp(session_dir):
    """Executa git fetch e retorna o timestamp do origin/main. Retorna 0 se repo vazio ou sem remote."""
    try:
        # Puxa atualizações do remoto silenciosamente
        subprocess.run(["git", "fetch", "origin", "main"], cwd=session_dir, check=False, capture_output=True)
        # Extrai o timestamp (unix epoch) do último commit do origin/main
        result = subprocess.run(["git", "log", "-1", "--format=%ct", "origin/main"], 
                                cwd=session_dir, check=True, capture_output=True, text=True)
        ts = result.stdout.strip()
        return int(ts) if ts else 0
    except Exception:
        # Pode ocorrer se origin/main não existir ainda (repositório recém criado ou sem remote)
        return 0

def get_local_timestamp(session_dir):
    """Retorna o timestamp do HEAD local. Retorna 0 se repo sem commits."""
    try:
        result = subprocess.run(["git", "log", "-1", "--format=%ct", "HEAD"], 
                                cwd=session_dir, check=True, capture_output=True, text=True)
        ts = result.stdout.strip()
        return int(ts) if ts else 0
    except Exception:
        return 0

def read_sync_lock(lock_file):
    if not lock_file.exists():
        return 0
    try:
        with open(lock_file, "r") as f:
            return int(f.read().strip())
    except ValueError:
        return 0

def write_sync_lock(lock_file, timestamp):
    with open(lock_file, "w") as f:
        f.write(str(timestamp))

def main():
    parser = argparse.ArgumentParser(description="Guardião de sincronia do contexto da IA.")
    parser.add_argument("--action", choices=["check", "update"], required=True, help="Ação a executar")
    parser.add_argument("--session-dir", required=True, help="Caminho para .agent/session")
    
    args = parser.parse_args()
    session_dir = Path(args.session_dir)
    lock_file = session_dir / ".sync_lock"
    git_dir = session_dir / ".git"

    if not git_dir.exists():
        print("STATUS: NOT_GIT_REPO")
        print("AVISO: Diretório de sessão não é um repositório git. Operações de sync desativadas.")
        sys.exit(0)  # Não é erro impeditivo para continuar trabalhando, só não tem sync.

    remote_ts = get_git_remote_timestamp(session_dir)
    lock_ts = read_sync_lock(lock_file)

    if args.action == "update":
        write_sync_lock(lock_file, remote_ts)
        print(f"LOCK UPDATED: {remote_ts}")
        sys.exit(0)

    elif args.action == "check":
        # Se remote_ts é 0, não tem histórico remoto (ex: novo repo)
        if remote_ts == 0:
            print("STATUS: OK (No remote history)")
            sys.exit(0)
            
        if remote_ts > lock_ts:
            print(f"STATUS: CONFLICT (Remote {remote_ts} > Lock {lock_ts})")
            sys.exit(1)
        else:
            print("STATUS: OK")
            sys.exit(0)

if __name__ == "__main__":
    main()
