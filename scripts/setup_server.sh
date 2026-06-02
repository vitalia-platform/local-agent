#!/usr/bin/env bash

set -e

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================================${NC}"
echo -e "${BLUE}🚀 INICIANDO SETUP DO SERVIDOR VITALIA (NÓ 2)${NC}"
echo -e "${BLUE}======================================================${NC}\n"

echo -e "${YELLOW}[1/7] Instalando o Agent Kit e inicializando sessão...${NC}"
bash agency/scripts/install.sh

echo -e "\n${YELLOW}[2/7] Configurando Variáveis de Ambiente (.env)...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✅ .env criado a partir do .env.example.${NC}"
    echo -e "${YELLOW}⚠️  Atenção: Revise as senhas do .env mais tarde!${NC}"
else
    echo -e "${GREEN}✅ .env já existe.${NC}"
fi

# Puxa os dados do env para uso no script
source .env

echo -e "\n${YELLOW}[3/7] Sincronizando Configurações via .agent/session...${NC}"
# Descobre o IP principal do WSL/Servidor (Exemplo simples, adaptação se tiver multi-nics)
SERVER_IP=$(hostname -I | awk '{print $1}')
OLLAMA_PORT=${NO2_OLLAMA_PORT:-11434}
TELEMETRY_PORT=${NO2_TELEMETRY_PORT:-8001}

CONFIG_FILE=".agent/session/server_config.json"
cat <<EOF > "$CONFIG_FILE"
{
  "server_ip": "$SERVER_IP",
  "ollama_port": "$OLLAMA_PORT",
  "telemetry_port": "$TELEMETRY_PORT"
}
EOF

echo -e "${GREEN}✅ Configuração gravada em $CONFIG_FILE${NC}"
# Tentativa de push para os nós clientes (ignora se der erro de repo vazio/sem remoto)
cd .agent/session
git add server_config.json
git commit -m "chore: sync server connection config" || true
git push origin main || echo -e "${YELLOW}⚠️ Não foi possível fazer push da sessão. (Normal se for um repo local isolado)${NC}"
cd ../../

echo -e "\n${YELLOW}[4/7] Subindo containers Docker...${NC}"
docker compose up -d

echo -e "\n${YELLOW}[5/7] Configurando o Banco de Dados RAG...${NC}"
bash scripts/init_db.sh

echo -e "\n${YELLOW}[6/7] Baixando e configurando Modelos no Ollama (Pode demorar!)...${NC}"
OLLAMA_CONTAINER=${OLLAMA_CONTAINER_NAME:-vitalia_ollama}

echo -e "   - Puxando nomic-embed-text..."
docker exec "$OLLAMA_CONTAINER" ollama pull nomic-embed-text

echo -e "   - Puxando qwen2.5-coder:7b..."
docker exec "$OLLAMA_CONTAINER" ollama pull qwen2.5-coder:7b

echo -e "   - Criando modelo customizado vitalia (sem Flash Attention)..."
if [ -f "Modelfile.qwen" ]; then
    docker cp Modelfile.qwen "$OLLAMA_CONTAINER":/tmp/Modelfile.qwen
    docker exec "$OLLAMA_CONTAINER" ollama create qwen2.5-coder-vitalia -f /tmp/Modelfile.qwen
    echo -e "${GREEN}✅ Modelo customizado criado com sucesso!${NC}"
else
    echo -e "${YELLOW}⚠️ Modelfile.qwen não encontrado. Pulando criação customizada.${NC}"
fi

echo -e "\n${YELLOW}[7/7] Preparando ambiente Python Global...${NC}"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install -r requirements.txt > /dev/null

echo -e "\n${BLUE}======================================================${NC}"
echo -e "${GREEN}🎉 SETUP DO SERVIDOR CONCLUÍDO!${NC}"
echo -e "${BLUE}======================================================${NC}"
echo -e "Para iniciar a API de Telemetria e o Dashboard de Monitoramento Colorido, execute:\n"
echo -e "  ${YELLOW}source .venv/bin/activate${NC}"
echo -e "  ${YELLOW}python scripts/runner.py --node server${NC}"
echo -e "\nIsso garantirá rastreabilidade visual e salvará logs contínuos em logs/vitalia.log."
