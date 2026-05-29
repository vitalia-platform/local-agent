#!/usr/bin/env bash
# Gestor de Configuração de Sessão (/session-config)
# Permite visualizar e gerenciar o vínculo da sessão com o repositório remoto.

set -e

KIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd)"
TARGET_DIR="${PWD}"
SESSION_DIR="${TARGET_DIR}/.agent/session"
LOCK_FILE="${SESSION_DIR}/.sync_lock"

show_help() {
    echo "Uso: bash kit/scripts/session-config.sh [comando]"
    echo ""
    echo "Comandos:"
    echo "  --show    Mostra a configuração atual da sessão (Remote URL, Lock ETag)"
    echo "  --clear   Limpa o arquivo de sincronia (.sync_lock)"
    echo "  --help    Mostra esta mensagem"
}

if [ "$1" == "--show" ]; then
    echo "--- Configuração de Sessão ---"
    if [ -d "$SESSION_DIR/.git" ]; then
        cd "$SESSION_DIR"
        URL=$(git remote get-url origin 2>/dev/null || echo "Nenhum remoto configurado")
        echo "🔗 Repositório: $URL"
        if [ -f ".sync_lock" ]; then
            ETAG=$(cat .sync_lock)
            echo "🔒 Lock ETag:   $ETAG"
        else
            echo "🔒 Lock ETag:   Ausente (Nunca sincronizado)"
        fi
        echo ""
        python3 "${KIT_DIR}/scripts/lib_machine.py" --status-report "$SESSION_DIR"
    else
        echo "❌ Erro: Diretório .agent/session não inicializado ou não é um repositório Git."
    fi

elif [ "$1" == "--clear" ]; then
    if [ -f "$LOCK_FILE" ]; then
        rm "$LOCK_FILE"
        echo "✅ Arquivo .sync_lock removido. A próxima sincronia forçará um novo registro."
    else
        echo "ℹ️  O arquivo .sync_lock já não existia."
    fi

else
    show_help
fi
