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

A infraestrutura do Servidor agora é provisionada quase que integralmente por um único script, que orquestra a inicialização do Docker, o download pesado de modelos no Ollama e a injeção do banco de dados (schema do RAG).

1. Clone o repositório dentro do WSL2:
   ```bash
   git clone git@github.com:vitalia-platform/local-agent.git
   cd local-agent
   ```

2. Execute o Script Automático de Instalação:
   O script configurará seu `.env`, lerá o IP local e o **sincronizará magicamente** através do nosso repositório de sessão isolado (`.agent/session`), além de inicializar todo o ecossistema de Inteligência Artificial:
   ```bash
   bash scripts/setup_server.sh
   ```

3. **Configuração de Rede (Crucial):**
   Como o IP do WSL muda a cada reinício, execute o script do port proxy como **Administrador no PowerShell do Windows Server** (para que o notebook consiga alcançar a porta do Ollama):
   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts/wsl-port-proxy.ps1
   ```

---

## 4. Setup do NÓ 1 (Notebook)

O notebook consumirá a sessão que o servidor acabou de "publicar" no `.agent/session`, auto-configurando sua conexão de rede de forma totalmente invisível.

1. Clone o mesmo repositório dentro do WSL2 do notebook:
   ```bash
   git clone git@github.com:vitalia-platform/local-agent.git
   cd local-agent
   ```

2. Execute o Script Automático de Instalação:
   Ele baixará os dados da sessão via pull, preencherá o `NO2_SERVER_IP` no seu `.env` automaticamente, e instalará as dependências globais de Python (como PyTorch otimizado para CUDA) e o OpenHands.
   ```bash
   bash scripts/setup_notebook.sh
   ```

---

## 5. Inicialização e Testes

O sistema permite duas abordagens principais:

### 5.1 Chat via Open WebUI (Servidor)
Pode ser acessado de qualquer lugar da rede pela porta `4000`:
- **Acesse:** `http://192.168.0.254:4000`
- Crie a primeira conta (que será o Admin) e selecione o modelo `qwen2.5-coder-vitalia`.

### 5.2 Agentic IDE via OpenHands + AG2 (Notebook)
No notebook, você possui a suíte completa de orquestração e monitoramento.
- **Acesse o OpenHands:** `http://localhost:3000` (Esta interface usará o Ollama remoto configurado).
- **Acompanhe os Serviços Locais (Dashboard):**
  ```bash
  source .venv/bin/activate
  python scripts/runner.py --node notebook
  ```
- **Inicie o Orquestrador Manualmente:**
  ```bash
  source .venv/bin/activate
  python orchestrator/orchestrator.py "Execute uma varredura de telemetria no servidor."
  ```

---

> Desenvolvido com as diretrizes do **Vitalia Platform Agent Kit** 🧬
