"""
prompt_engine.py — Montador Dinâmico de Prompts (Zero Hardcoding)

Lê exclusivamente as configurações passadas em criteria_config.yaml para
construir prompts agnósticos e livres de contaminação de domínio.
"""

import json

def build_prompt(
    title: str,
    abstract: str,
    prompt_config: dict
) -> str:
    """
    Constrói o prompt dinâmico baseado na configuração YAML.
    
    Lê:
    - prompt_configuration.cot_questions (para perguntas do Chain-of-Thought)
    - prompt_configuration.decision_rule (para regras de inclusão/exclusão)
    - prompt_configuration.extraction_fields (para campos de extração adicionais)
    - prompt_configuration.few_shot_examples (exemplos estruturados negativos/positivos)
    """
    
    # 1. Instruções básicas do Agente Screener
    instruction = (
        "Você é um assistente de pesquisa científica altamente preciso e rigoroso.\n"
        "Sua tarefa é analisar o Título e o Resumo (Abstract) de um artigo acadêmico e determinar "
        "se ele atende aos critérios de inclusão definidos.\n\n"
        "INSTRUÇÕES OBRIGATÓRIAS:\n"
        "1. Analise cada pergunta do Chain-of-Thought detalhadamente no seu raciocínio.\n"
        "2. Aplique estritamente a Regra de Decisão.\n"
        "3. Extraia com precisão as variáveis solicitadas.\n"
        "4. A resposta DEVE ser estritamente no formato JSON definido, sem blocos markdown adicionais.\n"
    )
    
    # 2. Definição das perguntas do CoT
    cot_section = "PERGUNTAS CHAIN-OF-THOUGHT (CoT):\n"
    cot_questions = prompt_config.get("cot_questions", [])
    for q in cot_questions:
        q_id = q.get("id", "")
        q_text = q.get("question", "")
        cot_section += f"- {q_id}: {q_text}\n"
        
    # 3. Regra de Decisão
    decision_section = f"\nREGRA DE DECISÃO:\n{prompt_config.get('decision_rule', '')}\n"
    
    # 4. Campos de extração
    extraction_section = "\nCAMPOS ADICIONAIS A EXTRAIR (se incluído):\n"
    extraction_fields = prompt_config.get("extraction_fields", [])
    for f in extraction_fields:
        f_id = f.get("id", "")
        f_desc = f.get("description", "")
        extraction_section += f"- {f_id}: {f_desc}\n"
        
    # 5. Formato de saída esperado (Schema JSON)
    schema_cot_dict = {q.get("id", "q"): "Yes/No (Justifique brevemente)" for q in cot_questions}
    schema_extraction_dict = {f.get("id", "field"): "Valor extraído ou 'N/A'" for f in extraction_fields}
    
    schema_dict = {
        "cot_analysis": schema_cot_dict,
        "final_decision": "INCLUIR ou EXCLUIR",
        "reasoning": "Resumo metodológico da decisão baseada nos critérios e CoT.",
        "extractions": schema_extraction_dict
    }
    
    format_section = (
        f"\nFORMATO JSON DE SAÍDA OBRIGATÓRIO:\n"
        f"{json.dumps(schema_dict, indent=2, ensure_ascii=False)}\n"
    )
    
    # 6. Few-shot Examples
    few_shot_section = "\nEXEMPLOS DE REFERÊNCIA (FEW-SHOT):\n"
    few_shots = prompt_config.get("few_shot_examples", [])
    for i, ex in enumerate(few_shots, 1):
        few_shot_section += f"\n--- EXEMPLO {i} ---\n"
        few_shot_section += f"Título: {ex.get('title', '')}\n"
        few_shot_section += f"Resumo: {ex.get('abstract', '')}\n"
        few_shot_section += f"Resposta esperada:\n{json.dumps(ex.get('expected_response', {}), indent=2, ensure_ascii=False)}\n"
        
    # 7. Dados do artigo a ser triado
    target_section = (
        f"\n=========================================\n"
        f"ARTIGO A SER ANALISADO AGORA:\n"
        f"=========================================\n"
        f"Título: {title}\n"
        f"Resumo: {abstract}\n"
        f"=========================================\n"
        f"Sua resposta JSON contendo cot_analysis, final_decision, reasoning e extractions:"
    )
    
    # Montagem completa do Prompt
    prompt = (
        f"{instruction}\n"
        f"{cot_section}"
        f"{decision_section}"
        f"{extraction_section}"
        f"{format_section}"
        f"{few_shot_section}"
        f"{target_section}"
    )
    
    return prompt
