#!/usr/bin/env python3
"""
Validador do Kit de Agentes
Audita a infraestrutura local (.agent) e invoca o guardião de sincronia.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def print_header(title):
    print(f"\n{'='*50}\n{title}\n{'='*50}")

def check_symlinks(agent_dir):
    print_header("1. Validação Estrutural (Symlinks)")
    expected_links = ["agents", "rules", "skills", "workflows", "templates"]
    all_ok = True
    
    for item in expected_links:
        path = agent_dir / item
        if not path.exists():
            print(f"❌ FALHA: Symlink {item} não encontrado ou quebrado.")
            all_ok = False
        elif not path.is_symlink():
            print(f"⚠️ AVISO: {item} existe, mas não é um symlink.")
        else:
            target = os.readlink(path)
            print(f"✅ OK: {item} -> {target}")
            
    return all_ok

def check_session_context(agent_dir, kit_dir):
    print_header("2. Saúde do Contexto de Sessão")
    session_dir = agent_dir / "session"
    
    if not session_dir.exists():
        print("❌ FALHA: Diretório .agent/session não encontrado.")
        return False
        
    shards_dir = session_dir / "shards"
    if not shards_dir.exists():
        print("⚠️  AVISO: Diretório shards/ não encontrado. Criando...")
        shards_dir.mkdir(parents=True, exist_ok=True)
        
    context_file = session_dir / "CONTEXT.md"
    if context_file.exists():
        size = context_file.stat().st_size
        print(f"📄 CONTEXT.md: Encontrado ({size} bytes)")
    else:
        print("⚠️ CONTEXT.md: Não encontrado no diretório de sessão.")
        
    history_file = session_dir / "SESSION_HISTORY.md"
    if history_file.exists():
        print(f"📚 SESSION_HISTORY.md: Encontrado ({history_file.stat().st_size} bytes)")
        
    print("\n[+] Acionando lib_sync_guard.py para verificação de ETags (Timestamp)")
    guard_script = kit_dir / "scripts" / "lib_sync_guard.py"
    
    try:
        result = subprocess.run(
            ["python3", str(guard_script), "--action", "check", "--session-dir", str(session_dir)],
            capture_output=True, text=True
        )
        
        output = result.stdout.strip()
        print(output)
        
        if "NOT_GIT_REPO" in output:
            print("🚨 ERRO ESTRUTURAL: O controle de versão do contexto (.git) foi perdido.")
            print("👉 AÇÃO REQUERIDA: Execute 'bash kit/scripts/session-resolve.sh' para restaurar a estrutura.")
            return False
            
        if result.returncode == 0:
            print("✅ Sincronia de contexto aprovada ou repositório não-linkado.")
            # Se deu sucesso, atualiza o ETag silenciosamente
            subprocess.run(
                ["python3", str(guard_script), "--action", "update", "--session-dir", str(session_dir)],
                capture_output=True
            )
            return True
        else:
            print("🚨 CONFLITO DETECTADO 🚨")
            print("O repositório remoto possui atualizações de contexto mais recentes que o seu ETag local.")
            print("👉 AÇÃO REQUERIDA: Execute 'bash kit/scripts/session-resolve.sh' antes de iniciar seus trabalhos.")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao invocar guardião: {e}")
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default=os.getcwd(), help="Diretório raiz do projeto alvo")
    parser.add_argument("--skip-session", action="store_true", help="Pular validação de contexto de sessão (útil para CI do Kit)")
    args = parser.parse_args()
    
    target_dir = Path(args.target).resolve()
    agent_dir = target_dir / ".agent"
    
    # Descobre o próprio kit dir assumindo que o script está em kit/scripts/
    kit_dir = Path(__file__).resolve().parent.parent

    if not agent_dir.exists():
        # Se estamos no root do próprio kit, o .agent não existirá da forma padrão
        if (target_dir / "agents").exists() and (target_dir / "scripts").exists():
            print("ℹ️  Detectado diretório raiz do Kit. Rodando em modo standalone.")
            agent_dir = None
        else:
            print(f"❌ ERRO: Diretório .agent não encontrado em {target_dir}")
            print("Execute o install.sh primeiro.")
            sys.exit(1)
        
    links_ok = True
    if agent_dir:
        links_ok = check_symlinks(agent_dir)
    
    context_ok = True
    if not args.skip_session:
        if agent_dir:
            context_ok = check_session_context(agent_dir, kit_dir)
        else:
            print("⚠️  Aviso: Verificação de sessão pulada (Diretório .agent ausente).")
    else:
        print("⏭️  Pulo solicitado: Validação de sessão ignorada.")
    
    print_header("RESULTADO FINAL")
    if links_ok and context_ok:
        print("🟢 KIT AUDITADO E PRONTO PARA USO.")
        sys.exit(0)
    else:
        print("🔴 FORAM ENCONTRADOS PROBLEMAS NA VALIDAÇÃO.")
        if not context_ok and sys.stdin.isatty():
            print("\n💡 DICA: Tente rodar 'bash kit/scripts/session-resolve.sh' para corrigir problemas de sessão.")
        sys.exit(1)

if __name__ == "__main__":
    main()
