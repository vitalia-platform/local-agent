#!/usr/bin/env bash
# Resolução de Conflitos e Recuperação de Sessão (/session-resolve)
# Gerencia a sincronia entre a MÁQUINA LOCAL e a NUVEM (GitHub).

set -e

KIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd)"
TARGET_DIR="${PWD}"
AGENT_DIR="${TARGET_DIR}/.agent"
SESSION_DIR="${AGENT_DIR}/session"
GUARD_SCRIPT="${KIT_DIR}/scripts/lib_sync_guard.py"

echo "===================================================="
echo "🚨 GESTOR DE RESILIÊNCIA DE SESSÃO 🚨"
echo "===================================================="

# Verificação de Estado Inicial
if [ ! -d "$SESSION_DIR" ]; then
    echo "⚠️  ESTADO: Pasta de sessão AUSENTE nesta máquina."
    echo "Local sugerido: .agent/session"
else
    echo "📂 ESTADO: Pasta de sessão presente em .agent/session"
    if [ -d "$SESSION_DIR/.git" ]; then
        cd "$SESSION_DIR"
        REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "Não configurado")
        echo "🔗 NUVEM (Remote): $REMOTE_URL"
        
        # Mostrar timestamps de forma humana
        LOCAL_TS=$(git log -1 --format=%ct HEAD 2>/dev/null || echo "0")
        git fetch origin main --quiet 2>/dev/null || true
        REMOTE_TS=$(git log -1 --format=%ct origin/main 2>/dev/null || echo "0")
        
        if [[ "$OSTYPE" == "darwin"* ]]; then
            LOCAL_DATE=$(date -r "$LOCAL_TS" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || echo "N/A")
            REMOTE_DATE=$(date -r "$REMOTE_TS" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || echo "N/A")
        else
            LOCAL_DATE=$(date -d "@$LOCAL_TS" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || echo "N/A")
            REMOTE_DATE=$(date -d "@$REMOTE_TS" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || echo "N/A")
        fi
        
        echo "🕒 Sincronia Local:  $LOCAL_DATE"
        echo "🕒 Sincronia Nuvem:  $REMOTE_DATE"
        cd "$TARGET_DIR"
    else
        echo "⚠️  ESTADO: Pasta existe mas NÃO é um repositório Git."
    fi
fi

echo ""
echo "Escolha como deseja prosseguir:"
echo "1) [NUVEM -> MÁQUINA] Sincronizar (Pull/Merge): Traz novidades da Nuvem e mescla com seu Local."
echo "2) [MÁQUINA -> NUVEM] Sobrescrever Nuvem (Push): Envia seu Local para o GitHub, apagando o que estiver lá."
echo "3) [MÁQUINA] Reparar Git Local: Recria o controle de versão local se a pasta .git sumiu."
echo "4) [NUVEM -> MÁQUINA] Restaurar da Nuvem (Clone): Baixa um contexto existente do GitHub para esta máquina."
echo "5) [CANCELAR]"
echo ""
read -p "Digite a opção (1-5): " opcao

case $opcao in
    1)
        if [ ! -d "$SESSION_DIR/.git" ]; then echo "❌ Erro: Repositório Git não encontrado. Use a opção 3 ou 4 primeiro."; exit 1; fi
        cd "$SESSION_DIR"
        echo "⬇️  Iniciando Pull / Merge da Nuvem..."
        git config pull.rebase false
        if git pull origin main; then
            echo "✅ Sincronia concluída com sucesso."
            python3 "$GUARD_SCRIPT" --action update --session-dir "$SESSION_DIR"
        else
            echo "⚠️  CONFLITO: Ocorreram divergências no arquivo CONTEXT.md."
            echo "👉 Abra .agent/session/CONTEXT.md, resolva os conflitos, faça o commit e rode session-sync."
        fi
        ;;
    2)
        if [ ! -d "$SESSION_DIR/.git" ]; then echo "❌ Erro: Repositório Git não encontrado."; exit 1; fi
        echo "⚠️  CUIDADO: Isso apagará o histórico da NUVEM que for mais recente que seu LOCAL."
        read -p "Confirmar sobrescrita? (sim/N): " confirm
        if [ "$confirm" == "sim" ]; then
            cd "$SESSION_DIR"
            git add .
            git diff --staged --quiet || git commit -m "chore: force overwrite remote context"
            if git push -f origin main; then
                echo "✅ Nuvem atualizada com sucesso!"
                python3 "$GUARD_SCRIPT" --action update --session-dir "$SESSION_DIR"
            else
                echo "❌ Falha no Push. Verifique suas permissões no GitHub."
            fi
        fi
        ;;
    3)
        echo "🔨 Recriando estrutura Git local..."
        mkdir -p "$SESSION_DIR"
        cd "$SESSION_DIR"
        git init
        git branch -M main 2>/dev/null || true
        if [ ! -f "CONTEXT.md" ]; then echo "# Contexto de Sessão" > CONTEXT.md; fi
        git add .
        git commit -m "chore: repair/init session repository"
        echo "✅ Git local inicializado. Agora use a opção 2 para conectar ao remoto ou configure manualmente."
        ;;
    4)
        echo "🌐 Restaurando da Nuvem..."
        read -p "Digite a URL do repositório de contexto (Ex: git@github.com:user/repo.git): " repo_url
        if [ -z "$repo_url" ]; then echo "❌ URL inválida."; exit 1; fi
        
        if [ -d "$SESSION_DIR" ]; then
            echo "⚠️  A pasta .agent/session já existe. Deseja apagá-la para o novo clone?"
            read -p "(s/N): " del_confirm
            if [ "$del_confirm" == "s" ]; then rm -rf "$SESSION_DIR"; fi
        fi
        
        mkdir -p "$AGENT_DIR"
        if git clone "$repo_url" "$SESSION_DIR"; then
            echo "✅ Restauração concluída!"
            python3 "$GUARD_SCRIPT" --action update --session-dir "$SESSION_DIR"
        else
            echo "❌ Falha ao clonar. Verifique a URL e suas chaves SSH."
        fi
        ;;
    *)
        echo "Operação cancelada."
        ;;
esac
