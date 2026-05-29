# Vitalia Local Agent (Cross-WSL Distribuído)

Este é o repositório principal do ecossistema de agentes da Vitalia. Trata-se de uma arquitetura 100% local, autônoma e distribuída, otimizada para superar gargalos de VRAM usando múltiplos nós (Notebook + Servidor) coordenados pelo orquestrador **AG2** com inferência via **Ollama**.

## 1. Arquitetura Conceitual

O sistema distribui a carga pesada para o servidor e a lógica ágil para o notebook, coordenando o estado através de um barramento do **Redis** e sincronizando memórias semânticas no **pgvector**.

```
REDE LOCAL / VPN
┌──────────────────────────────────────────────┐   ┌──────────────────────────────────────────────┐
│          NÓ 2 — SERVIDOR                     │   │          NÓ 1 — NOTEBOOK                     │
│  Win Server 2025 / WSL2 Ubuntu               │   │  Win 11 Pro / WSL2 Ubuntu                    │
│                                              │   │                                              │
│  ┌─ docker-compose.yml ─────────────────┐    │   │  ┌─ docker-compose.notebook.yml ──────────┐  │
│  │  db (pgvector:pg16)    :5432         │    │   │  │  openhands    :3000                    │  │
│  │  redis (alpine)        :6379 ←───────┼────┼───┼─→│  (sandbox IDE do AG2)                  │  │
│  │  ollama (GTX 1060)     :11434 ←──────┼────┼───┼─→└────────────────────────────────────────┘  │
│  │  open-webui            :4000         │    │   │                                              │
│  │  telemetry_api         :8001 ←───────┼────┼───┼─→┌─ Python venv (AG2) ────────────────────┐  │
│  └──────────────────────────────────────┘    │   │  │  orchestrator.py                       │  │
│                                              │   │  │  Docling (MX450 CUDA)                  │  │
│  Modelfile.qwen (num_ctx 8192, FA=0)         │   │  │  pgvector local  :5432                 │  │
└──────────────────────────────────────────────┘   └──────────────────────────────────────────────┘
```

- **Redis:** Serve como pub/sub para replicação do RAG (pgvector), armazenamento do estado da Sprint e semáforos de controle distribuído.
- **Ollama:** A GTX 1060 (Servidor) roda os modelos pesados (`qwen2.5-coder-vitalia`), enquanto a MX450 (Notebook) gerencia embeddings e processamento local.
- **Docling:** Processamento massivo de PDFs na GPU do Notebook via PyTorch/CUDA, com semáforo rigoroso para descarregar o Ollama local quando ativado.

---

## 2. Requisitos Prévios

> [!WARNING]
> Certifique-se de que sua **VPN** está ativada e que as regras de **Firewall** do Windows Server permitem acesso às portas TCP 5432, 6379, 11434, 4000 e 8001.

### Nó 2 (Servidor)
- Windows Server 2025 com driver NVIDIA atualizado (GPU Paravirtualization).
- WSL2 instalado (`wsl --update`).
- Docker instalado dentro do WSL2 ou Docker Desktop integrado ao WSL2.
- `nvidia-smi` respondendo dentro do terminal do Ubuntu (WSL2).

### Nó 1 (Notebook)
- Windows 11 com WSL2 e driver NVIDIA atualizado.
- Docker instalado (integrado com o WSL2).
- Python 3.11+.

---

## 3. Setup do NÓ 2 (Servidor)

1. Clone o repositório dentro do WSL2:
   ```bash
   git clone git@github.com:vitalia-platform/local-agent.git
   cd local-agent
   ```

2. Crie e configure o `.env`:
   ```bash
   cp .env.example .env
   # Edite o .env e insira senhas seguras para o PostgreSQL e Redis.
   ```

3. Suba os serviços principais:
   ```bash
   docker compose up -d
   ```

4. Habilite o pgvector:
   ```bash
   sleep 10
   docker exec vitalia_db psql -U vitalia_admin -d vitalia_db -c "CREATE EXTENSION IF NOT EXISTS vector;"
   ```

5. Baixe os modelos no Ollama:
   ```bash
   docker exec vitalia_ollama ollama pull qwen2.5-coder:7b
   docker exec vitalia_ollama ollama pull nomic-embed-text
   
   # Crie o modelo customizado para a GTX 1060 (Sem Flash Attention e num_ctx=8192)
   docker cp Modelfile.qwen vitalia_ollama:/tmp/Modelfile.qwen
   docker exec vitalia_ollama ollama create qwen2.5-coder-vitalia -f /tmp/Modelfile.qwen
   ```

6. Inicie a API de Telemetria e Sync:
   ```bash
   cd telemetry_api
   pip install -r requirements.txt
   python telemetry_api.py &
   ```

7. **Configuração de Rede (Crucial):**
   Como o IP do WSL muda a cada reinício, execute o script do port proxy como **Administrador no PowerShell do Windows Server**:
   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts/wsl-port-proxy.ps1
   ```

---

## 4. Setup do NÓ 1 (Notebook)

1. Clone o mesmo repositório dentro do WSL2 do notebook:
   ```bash
   git clone git@github.com:vitalia-platform/local-agent.git
   cd local-agent
   ```

2. Inicie e estruture a Agency local:
   O comando abaixo irá formatar a pasta `.agent` criando os symlinks para os agentes e inicializando o repositório git aninhado de sessão (`.agent/session`). Responda com "s" para configurar o repositório remoto caso seja perguntado.
   ```bash
   bash agency/scripts/install.sh
   ```

3. Configure o `.env`:
   ```bash
   cp .env.example .env
   # Edite o .env, preenchendo as MESMAS SENHAS criadas no servidor e apontando o IP:
   # NO2_SERVER_IP=192.168.0.254
   ```

4. Suba o ambiente OpenHands (Sandbox):
   ```bash
   docker compose -f docker-compose.notebook.yml up -d
   ```

5. Configure o ambiente Python do Orquestrador:
   ```bash
   cd orchestrator
   python3 -m venv .venv
   source .venv/bin/activate
   
   # PyTorch com CUDA 12.8 (Compatível com driver 12.9)
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
   pip install -r requirements.txt
   ```

6. Suba o banco de dados pgvector local (para RAG descentralizado):
   ```bash
   source ../.env
   docker run -d --name vitalia_db_local \
     -p 5432:5432 \
     -e POSTGRES_DB=${POSTGRES_DB} \
     -e POSTGRES_USER=${POSTGRES_USER} \
     -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
     -v vitalia_local_data:/var/lib/postgresql/data \
     pgvector/pgvector:pg16

   docker exec vitalia_db_local psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "CREATE EXTENSION IF NOT EXISTS vector;"
   ```

---

## 5. Inicialização e Testes

O sistema permite duas abordagens principais:

### 5.1 Chat via Open WebUI (Servidor)
Pode ser acessado de qualquer lugar da rede pela porta `4000`:
- **Acesse:** `http://192.168.0.254:4000`
- Crie a primeira conta (que será o Admin) e selecione o modelo `qwen2.5-coder-vitalia`.

### 5.2 Agentic IDE via OpenHands + AG2 (Notebook)
No notebook, você possui a suíte completa de orquestração.
- **Acesse o OpenHands:** `http://localhost:3000` (Esta interface usará o Ollama remoto configurado).
- **Inicie o Orquestrador:**
  ```bash
  cd orchestrator
  source .venv/bin/activate
  python orchestrator.py "Execute uma varredura de telemetria no servidor."
  ```

---

> Desenvolvido com as diretrizes do **Vitalia Platform Agent Kit** 🧬
