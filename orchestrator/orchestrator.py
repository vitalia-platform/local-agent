# orchestrator.py
# Criado em: 29-05-2026 14:52:00(GMT-04:00)
# Caminho: /home/andre/projetos/assistidos/servidor-ia/orchestrator.py

import os
import json
import logging
import requests
from dotenv import load_dotenv
import autogen
from autogen import AssistantAgent, UserProxyAgent
from autogen.agentchat.contrib.capabilities import transform_messages
from autogen.agentchat.contrib.capabilities.transforms import MessageTokenLimiter

# Configura o Logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("VitaliaOrchestrator")

# Carrega variáveis de ambiente
load_dotenv()

NO2_SERVER_IP = os.getenv("NO2_SERVER_IP", "192.168.0.254")
NO2_OLLAMA_PORT = os.getenv("NO2_OLLAMA_PORT", "11434")
NO1_LOCAL_OLLAMA_URL = os.getenv("NO1_LOCAL_OLLAMA_URL", "http://localhost:11434")

# Imports de ferramentas locais
from tools import save_to_rag, update_sprint_state, web_search

# -------------------------------------------------------------
# CONFIGURAÇÃO DE LLM POR NÓ (ROTEAMENTO INTELIGENTE)
# -------------------------------------------------------------

# Lead Engineer / Raciocínio Pesado (Servidor - GTX 1060 6GB)
# Aceita qwen2.5-coder:7b ou deepseek-r1-distill-qwen-7b
llm_config_server = {
    "config_list": [
        {
            "model": "qwen2.5-coder-vitalia",
            "client_host": f"http://{NO2_SERVER_IP}:{NO2_OLLAMA_PORT}",
            "api_type": "ollama",
        }
    ],
    "temperature": 0.2,
    "cache_seed": None,  # Desativa o cache local para garantir execução de testes limpos
}

# Linter / Triagem / Telemetria (Notebook - MX450 2GB CPU/GPU)
llm_config_local = {
    "config_list": [
        {
            "model": "qwen2:1.5b",
            "client_host": NO1_LOCAL_OLLAMA_URL,
            "api_type": "ollama",
        }
    ],
    "temperature": 0.1,
    "cache_seed": None,
}

# -------------------------------------------------------------
# CRIAÇÃO DOS AGENTES DO AUTOGEN
# -------------------------------------------------------------

# 1. Agente Desenvolvedor (GTX 1060)
developer = AssistantAgent(
    name="Developer_Agent",
    llm_config=llm_config_server,
    system_message="""Você é o Lead Developer da Vitalia, operando sob a nossa Constituição de Eficiência.
Seu motor executa em uma GTX 1060 (limite rígido de 8k tokens de contexto).
Regras de ouro:
1. Seja extremamente conciso. NUNCA reescreva arquivos inteiros se puder retornar apenas a função ou bloco modificado.
2. Sempre que criar ou refatorar lógica de código, execute a ferramenta `save_to_rag` para registrar a assinatura das funções e arquivos.
3. Se o histórico de conversas estiver muito longo, solicite um resumo ao Agente de Infraestrutura para economizar sua VRAM.
4. Responda apenas com o código modificado ou instruções diretas. Evite explicações textuais redundantes.
""",
)

# 2. Agente de Infraestrutura & Telemetria (Ollama Local)
infra = AssistantAgent(
    name="Infrastructure_Agent",
    llm_config=llm_config_local,
    system_message="""Você é o Guardião de Recursos da Vitalia. Seu trabalho é monitorar a integridade das GPUs (MX450 local e GTX 1060 remota).
Suas diretrizes:
1. Use a ferramenta `get_node2_telemetry` periodicamente para avaliar o uso de VRAM no Servidor.
2. Se a VRAM do servidor estiver acima de 5500MB, avise imediatamente a equipe para forçar um checkpoint e descarregar contextos.
3. Gerencie as sprints. Sempre que uma fase relevante for concluída ou um checkpoint for necessário, consolide as informações e chame a ferramenta `update_sprint_state` salvando no Redis e no Git de sessão.
4. Ajude o desenvolvedor a manter o foco em tarefas menores para economizar seu contexto de 8k tokens.
""",
)

# 3. User Proxy (Notebook - Executa as ferramentas fisicamente)
user_proxy = UserProxyAgent(
    name="User_Proxy",
    human_input_mode="NEVER",  # Roda de forma autônoma/semi-autônoma respondendo automaticamente
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").strip().endswith("TERMINAR"),
    code_execution_config={
        "work_dir": "workspace_run",
        "use_docker": False,  # OpenHands já executa dentro de um sandbox seguro
    },
)

# -------------------------------------------------------------
# SHIELD ANTI-OOM (COMPRESSÃO DE CONTEXTO DINÂMICA)
# -------------------------------------------------------------
# Garante que o payload enviado para o Servidor nunca exceda 6000 tokens.
token_limiter = MessageTokenLimiter(max_tokens=6000, model="gpt-3.5-turbo")
context_transformer = transform_messages.TransformMessages(transforms=[token_limiter])
context_transformer.add_to_agent(developer)

logger.info("Capacidade de compressão de contexto TransformMessages acoplada ao Developer Agent.")

# -------------------------------------------------------------
# REGISTRO DE TOOLS
# -------------------------------------------------------------

def get_node2_telemetry() -> str:
    """Consulta a API de telemetria no Nó 2 e retorna o status de VRAM/RAM/CPU."""
    url = f"http://{NO2_SERVER_IP}:8001/telemetry"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return json.dumps(response.json(), indent=2)
    except Exception as e:
        return f"Erro ao acessar API de Telemetria no Servidor ({NO2_SERVER_IP}): {str(e)}"
    return "Status desconhecido."

# Registra save_to_rag
autogen.register_function(
    save_to_rag,
    caller=developer,
    executor=user_proxy,
    name="save_to_rag",
    description="Salva arquivos de código (via AST) ou PDFs (via Docling local na GPU MX450) no pgvector local e retransmite para o servidor."
)

# Registra update_sprint_state
autogen.register_function(
    update_sprint_state,
    caller=infra,
    executor=user_proxy,
    name="update_sprint_state",
    description="Grava o estado atual da sprint em JSON no Redis e cria o arquivo de log Markdown em .agent/session/sprint_atual.md."
)

# Registra web_search
autogen.register_function(
    web_search,
    caller=developer,
    executor=user_proxy,
    name="web_search",
    description="Executa uma busca na web rápida e gratuita via DuckDuckGo Search."
)

# Registra get_node2_telemetry
autogen.register_function(
    get_node2_telemetry,
    caller=infra,
    executor=user_proxy,
    name="get_node2_telemetry",
    description="Consulta o status de hardware em tempo real da GTX 1060 (VRAM) e RAM do Servidor (Nó 2)."
)

# -------------------------------------------------------------
# FLUXO DE INICIALIZAÇÃO
# -------------------------------------------------------------

def run_orchestration(user_prompt: str):
    """Dispara a conversa de grupo entre o Desenvolvedor, o Infra e o Usuário."""
    logger.info("Instanciando chat de grupo de agentes...")
    
    groupchat = autogen.GroupChat(
        agents=[user_proxy, developer, infra],
        messages=[],
        max_round=12,
        speaker_selection_method="auto"  # AG2 gerencia dinamicamente o fluxo de conversa
    )
    
    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config_local)
    
    logger.info(f"Disparando prompt inicial: {user_prompt}")
    user_proxy.initiate_chat(
        manager,
        message=f"{user_prompt}\n\nAo finalizar com sucesso sua tarefa, responda com a palavra 'TERMINAR' no final."
    )

if __name__ == "__main__":
    # Exemplo de teste rápido do orquestrador
    import sys
    prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Verifique o status da telemetria do servidor e reporte a disponibilidade de VRAM."
    run_orchestration(prompt)
