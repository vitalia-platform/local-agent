# orchestrator.py
# Criado em: 29-05-2026 14:52:00(GMT-04:00)
# Caminho: /home/andre/projetos/assistidos/servidor-ia/orchestrator/orchestrator.py

import os
import sys
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
# CONFIGURAÇÃO MULTI-LLM E FALLBACK
# -------------------------------------------------------------

def load_agent_config(profile_env_var: str, default_profile: str) -> dict:
    """
    Lê o perfil do .env (ex: ROUTER_LLM_PROFILE) e retorna o llm_config correto.
    Em caso de falha de credencial, faz graceful exit com mensagem amigável no terminal.
    """
    profile = os.getenv(profile_env_var, default_profile).strip().lower()
    
    if profile == "ollama_server":
        return {
            "config_list": [{"model": "qwen2.5-coder-vitalia", "client_host": f"http://{NO2_SERVER_IP}:{NO2_OLLAMA_PORT}", "api_type": "ollama"}],
            "temperature": 0.2, "cache_seed": None
        }
    elif profile == "ollama_local":
        return {
            "config_list": [{"model": "qwen2:1.5b", "client_host": NO1_LOCAL_OLLAMA_URL, "api_type": "ollama"}],
            "temperature": 0.1, "cache_seed": None
        }
    elif profile == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error(f"❌ ERRO CRÍTICO: Perfil '{profile}' escolhido para {profile_env_var}, mas GEMINI_API_KEY está vazio no .env.")
            sys.exit(1)
        return {
            "config_list": [{"model": "gemini-1.5-pro", "api_key": api_key, "api_type": "google"}],
            "temperature": 0.2, "cache_seed": None
        }
    elif profile == "claude":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.error(f"❌ ERRO CRÍTICO: Perfil '{profile}' escolhido para {profile_env_var}, mas ANTHROPIC_API_KEY está vazio no .env.")
            sys.exit(1)
        return {
            "config_list": [{"model": "claude-3-5-sonnet-20241022", "api_key": api_key, "api_type": "anthropic"}],
            "temperature": 0.2, "cache_seed": None
        }
    elif profile == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error(f"❌ ERRO CRÍTICO: Perfil '{profile}' escolhido para {profile_env_var}, mas OPENAI_API_KEY está vazio no .env.")
            sys.exit(1)
        return {
            "config_list": [{"model": "gpt-4o", "api_key": api_key}],
            "temperature": 0.2, "cache_seed": None
        }
    else:
        logger.error(f"❌ ERRO CRÍTICO: Perfil '{profile}' desconhecido para {profile_env_var}.")
        sys.exit(1)

llm_config_triage = load_agent_config("ROUTER_LLM_PROFILE", "gemini")
llm_config_server = load_agent_config("DEVELOPER_LLM_PROFILE", "ollama_server")
llm_config_local = load_agent_config("INFRA_LLM_PROFILE", "ollama_local")

# -------------------------------------------------------------
# CRIAÇÃO DOS AGENTES DO AUTOGEN
# -------------------------------------------------------------

triage = AssistantAgent(
    name="Triage_Agent",
    llm_config=llm_config_triage,
    description="Agente principal de roteamento. O primeiro a receber o pedido do usuário para decidir a intenção.",
    system_message="""Você é o Triage Agent da Vitalia. Seu único objetivo é analisar o pedido do usuário e repassar para o agente correto.
Regras de Roteamento:
1. Problemas de lentidão, queda de recursos, verificações de telemetria ou hardware: repasse para o Infrastructure_Agent.
2. Criação de código, buscas na web ou funcionalidades: repasse para o Developer_Agent.
Apenas declare para quem você está direcionando a tarefa e por quê."""
)

developer = AssistantAgent(
    name="Developer_Agent",
    llm_config=llm_config_server,
    description="Especialista em software. Acione APENAS para resolver problemas de código, criar arquivos ou realizar buscas na web.",
    system_message="""Você é o Lead Developer da Vitalia, operando sob a nossa Constituição de Eficiência.
Regras de ouro:
1. NUNCA reescreva arquivos inteiros se puder retornar apenas a função ou bloco modificado.
2. A ferramenta `save_to_rag` deve ser acionada APENAS quando você considerar que uma funcionalidade completa (ou arquivo inteiro) foi concluída e testada.
3. Use a ferramenta `web_search` DEPOIS do RAG, levando o contexto dele para otimizar sua busca na web. Inicialmente nenhuma tarefa é proibida, vasculhe a web na busca de boas práticas.
"""
)

infra = AssistantAgent(
    name="Infrastructure_Agent",
    llm_config=llm_config_local,
    description="Especialista em infraestrutura. Acione APENAS para monitorar telemetria, hardware e atualizar o estado da sprint.",
    system_message="""Você é o Guardião de Recursos da Vitalia.
Regras de ouro:
1. Use `get_node2_telemetry` periodicamente ou sob demanda, especialmente quando o Triage_Agent relatar problemas de lentidão ou solicitar varredura.
2. Use `update_sprint_state` a CADA TURNO para garantir o sincronismo do estado.
3. Se a VRAM do servidor estiver acima de 5500MB, avise imediatamente a equipe.
"""
)

user_proxy = UserProxyAgent(
    name="User_Proxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").strip().endswith("TERMINAR"),
    code_execution_config={"work_dir": "workspace_run", "use_docker": False},
)

# -------------------------------------------------------------
# SHIELD ANTI-OOM (COMPRESSÃO DE CONTEXTO DINÂMICA)
# -------------------------------------------------------------
token_limiter = MessageTokenLimiter(max_tokens=6000, model="gpt-3.5-turbo")
context_transformer = transform_messages.TransformMessages(transforms=[token_limiter])
context_transformer.add_to_agent(developer)
logger.info("Capacidade de compressão de contexto TransformMessages acoplada ao Developer Agent.")

# -------------------------------------------------------------
# REGISTRO DE TOOLS E DESCRIÇÕES MELHORADAS
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

autogen.register_function(
    save_to_rag,
    caller=developer,
    executor=user_proxy,
    name="save_to_rag",
    description="MANDATÓRIO: Salva código/arquivos no banco vetorial. USE APENAS quando considerar que uma funcionalidade completa (ou arquivo inteiro) foi concluído e testado. Não use para modificações triviais em andamento."
)

autogen.register_function(
    update_sprint_state,
    caller=infra,
    executor=user_proxy,
    name="update_sprint_state",
    description="MANDATÓRIO: Grava o estado atual da sprint. Execute esta ferramenta A CADA TURNO para garantir a consistência do acompanhamento do projeto."
)

autogen.register_function(
    web_search,
    caller=developer,
    executor=user_proxy,
    name="web_search",
    description="Executa busca na web. Use apenas DEPOIS de esgotar o RAG, levando o contexto para buscar boas práticas. Não acione repetitivamente a mesma busca."
)

autogen.register_function(
    get_node2_telemetry,
    caller=infra,
    executor=user_proxy,
    name="get_node2_telemetry",
    description="MANDATÓRIO: Consulta hardware. Use sempre que o usuário ou Triage reportarem lentidão, queda de recursos ou solicitarem varredura. Rode periodicamente."
)
autogen.register_function(
    get_node2_telemetry,
    caller=developer,
    executor=user_proxy,
    name="get_node2_telemetry",
    description="Consulta hardware (VRAM). Acione se precisar confirmar disponibilidade de recursos no servidor antes de gerar código muito pesado."
)

# -------------------------------------------------------------
# FLUXO DE INICIALIZAÇÃO
# -------------------------------------------------------------

def run_orchestration(user_prompt: str):
    logger.info("Instanciando chat de grupo de agentes (Swarm/Triage mode)...")
    
    groupchat = autogen.GroupChat(
        agents=[user_proxy, triage, developer, infra],
        messages=[],
        max_round=12,
        speaker_selection_method="auto"
    )
    
    # Manager agora usa a inteligência do Triage/Router (ex: Gemini) para decidir com precisão
    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config_triage)
    
    logger.info(f"Disparando prompt inicial: {user_prompt}")
    user_proxy.initiate_chat(
        manager,
        message=f"{user_prompt}\n\nAo finalizar com sucesso sua tarefa, responda com a palavra 'TERMINAR' no final."
    )

if __name__ == "__main__":
    import sys
    prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Verifique o status da telemetria do servidor e reporte a disponibilidade de VRAM."
    run_orchestration(prompt)
