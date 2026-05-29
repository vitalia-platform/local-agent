#!/usr/bin/env bash
# Sincronizador de Sessão Interativo (/session-sync)
# Lida com Git Pull/Push (incluindo SSH) e Consolidação de Contexto.

set -e

KIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd)"
TARGET_DIR="${PWD}"
SESSION_DIR="${TARGET_DIR}/.agent/session"
CONSOLIDATE_SCRIPT="${KIT_DIR}/scripts/session-consolidate.py"

if [ ! -d "$SESSION_DIR/.git" ]; then
    echo "❌ Erro: Diretório de sessão não é um repositório Git."
    exit 1
fi

cd "$SESSION_DIR"

echo "🔄 [1/4] Puxando atualizações da Nuvem..."
# Verifica se o remoto tem histórico antes de tentar pull
HAS_REMOTE=$(git ls-remote --heads origin main 2>/dev/null | wc -l | tr -d ' ')
if [ "$HAS_REMOTE" -gt "0" ]; then
    git pull origin main --rebase || { echo "❌ Falha no Pull. Verifique sua conexão e chaves SSH."; exit 1; }
else
    echo "   ℹ️  Remoto sem histórico (repositório vazio). Pulando pull."
fi

echo "🧩 [2/4] Consolidando contextos de todas as máquinas..."
python3 "$CONSOLIDATE_SCRIPT" "$SESSION_DIR"

echo "💾 [3/4] Salvando estado consolidado localmente..."
git add .
if ! git diff --staged --quiet; then
    git commit -m "chore: consolidated context shards [$(date +'%Y-%m-%d %H:%M')]"
else
    echo "   (Nenhuma mudança nova para commitar)"
fi

echo "⬆️  [4/4] Enviando para a Nuvem..."
# O git push pode pedir senha aqui
if git push origin main; then
    echo "✅ Sincronia Global Concluída!"
    # Atualiza o lock local
    python3 "${KIT_DIR}/scripts/lib_sync_guard.py" --action update --session-dir "$SESSION_DIR"
else
    echo "❌ Falha no Push. Verifique suas permissões."
    exit 1
fi
