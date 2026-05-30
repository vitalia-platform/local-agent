#!/usr/bin/env bash

set -e

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================================${NC}"
echo -e "${BLUE}🚀 INICIANDO SETUP DO NOTEBOOK VITALIA (NÓ 1)${NC}"
echo -e "${BLUE}======================================================${NC}\n"

echo -e "${YELLOW}[1/5] Sincronizando Agent Kit e Sessão Remota...${NC}"
bash agency/scripts/install.sh
cd .agent/session
git pull origin main 2>/dev/null || echo "   ⚠️  Não foi possível puxar as últimas configurações do servidor (Talvez ainda não commitadas)."
cd ../../

echo -e "\n${YELLOW}[2/5] Lendo Configurações do Servidor e Auto-Preenchendo .env...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env
fi

CONFIG_FILE=".agent/session/server_config.json"
if [ -f "$CONFIG_FILE" ]; then
    # Usa Python para ler o JSON e atualizar o .env sem precisar instalar jq
    python3 -c "
import json
import re

try:
    with open('$CONFIG_FILE', 'r') as f:
        data = json.load(f)
    
    server_ip = data.get('server_ip')
    if server_ip:
        with open('.env', 'r') as f:
            env_content = f.read()
        
        # Substitui ou adiciona NO2_SERVER_IP
        if 'NO2_SERVER_IP=' in env_content:
            env_content = re.sub(r'NO2_SERVER_IP=.*', f'NO2_SERVER_IP={server_ip}', env_content)
        else:
            env_content += f'\nNO2_SERVER_IP={server_ip}\n'
            
        with open('.env', 'w') as f:
            f.write(env_content)
        print(f'✅ IP do servidor ({server_ip}) injetado no .env com sucesso!')
except Exception as e:
    print(f'❌ Erro ao auto-configurar IP: {e}')
"
else
    echo -e "${YELLOW}⚠️ Arquivo de configuração de sessão não encontrado. O IP terá que ser configurado manualmente no .env.${NC}"
fi

echo -e "\n${YELLOW}[3/5] Subindo containers locais (OpenHands e DB)...${NC}"
docker compose -f docker-compose.notebook.yml up -d

echo -e "\n${YELLOW}[4/5] Configurando o Banco de Dados Local...${NC}"
# Passamos explicitamente o nome do container do notebook para o script de init_db
DB_CONTAINER_NAME=vitalia_db_local DB_NAME=vitalia_db DB_USER=vitalia_admin bash scripts/init_db.sh

echo -e "\n${YELLOW}[5/5] Preparando ambiente Python Global (PyTorch Otimizado CUDA)...${NC}"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
echo -e "   - Instalando PyTorch..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128 > /dev/null
echo -e "   - Instalando Requisitos..."
pip install -r requirements.txt > /dev/null

echo -e "\n${BLUE}======================================================${NC}"
echo -e "${GREEN}🎉 SETUP DO NOTEBOOK CONCLUÍDO!${NC}"
echo -e "${BLUE}======================================================${NC}"
echo -e "O OpenHands está rodando em http://localhost:3000\n"
echo -e "Para abrir o Dashboard de Monitoramento Colorido, execute:\n"
echo -e "  ${YELLOW}source .venv/bin/activate${NC}"
echo -e "  ${YELLOW}python scripts/runner.py --node notebook${NC}"
