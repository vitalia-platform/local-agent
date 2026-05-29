---
name: clinical-safety
description: >
  Regras de segurança clínica para software de saúde. Define limites de atuação
  da IA, protocolos de crise, disclaimers obrigatórios e quando escalar para
  profissional humano. Aplicar em qualquer feature de saúde personalizada.
  Triggers: "segurança clínica", "limite da IA em saúde", "quando escalar",
  "protocolo de crise", "disclaimer médico", "responsabilidade legal em saúde".
allowed-tools: Read
---

# Clinical Safety — Segurança Clínica em Software de Saúde

> "A IA é uma ferramenta educacional e de suporte, nunca um substituto ao profissional de saúde."

---

## Limites de Atuação da IA (Inegociáveis)

### ✅ O que a IA PODE fazer
- Fornecer informações educacionais baseadas em evidências
- Exibir valores de referência populacionais com contexto
- Sugerir que o usuário procure um profissional
- Registrar dados inseridos pelo usuário
- Alertar quando valores estão fora do range de referência
- Facilitar comunicação entre usuário e profissional

### 🛑 O que a IA NUNCA pode fazer
- Diagnosticar condições médicas
- Prescrever ou recomendar medicamentos ou dosagens
- Interpretar exames de forma individualizada sem profissional
- Substituir consulta médica para decisões de tratamento
- Fazer afirmações terapêuticas ("vai curar", "vai tratar")
- Ignorar sinais de crise ou emergência

---

## Protocolos de Crise

### Crise de Saúde Mental
```python
MENTAL_CRISIS_KEYWORDS = [
    "suicídio", "me matar", "não quero viver", "me machucar",
    "autolesão", "cutting", "overdose intencional"
]

def handle_mental_crisis(user_id: int, message: str) -> CrisisResponse:
    """NUNCA processar com IA — escalar imediatamente."""
    CrisisLog.create(user_id=user_id, trigger=message)
    notify_safety_team(user_id)
    return CrisisResponse(
        message="Estou aqui. O que você está sentindo importa. "
                "Por favor, ligue agora para o CVV: 188 (24h, gratuito).",
        resources=[{"name": "CVV", "phone": "188", "available": "24/7"}],
        escalated=True
    )
```

### Emergência Médica (Valores Críticos)
```python
CRITICAL_LAB_VALUES = {
    "glucose": {"panic_low": 54, "panic_high": 500, "unit": "mg/dL"},
    "systolic_bp": {"panic_low": 80, "panic_high": 180, "unit": "mmHg"},
    "heart_rate": {"panic_low": 40, "panic_high": 150, "unit": "bpm"},
    "spo2": {"panic_low": 90, "unit": "%"},
}

def check_critical_value(biomarker: str, value: float) -> Optional[Alert]:
    """Se valor crítico: alertar e recomendar avaliação imediata."""
    limits = CRITICAL_LAB_VALUES.get(biomarker)
    if limits and is_critical(value, limits):
        return Alert(
            severity="CRITICAL",
            message=f"Seu valor de {biomarker} ({value}) requer atenção imediata. "
                    "Por favor, procure atendimento médico ou ligue para o SAMU (192).",
            action_required=True
        )
```

---

## Disclaimers Obrigatórios

### Para Conteúdo Educacional
```
"Esta informação tem caráter educacional e não substitui a orientação 
de um profissional de saúde qualificado."
```

### Para Dados e Biomarcadores
```
"Os valores de referência apresentados são populacionais. 
A interpretação dos seus resultados deve ser feita pelo seu médico, 
considerando seu histórico e contexto individual."
```

### Para Recomendações de Bem-Estar
```
"As sugestões apresentadas são baseadas em evidências científicas gerais 
e não consideram condições médicas individuais. Consulte um profissional 
de saúde antes de fazer mudanças significativas em sua rotina."
```

---

## Classificação de Features por Risco

| Risco | Exemplos | Requisitos |
|-------|----------|-----------|
| **Baixo** | Conteúdo educacional, dicas gerais | Disclaimer básico |
| **Médio** | Rastreamento de biomarcadores, notificações | Disclaimer + validação científica |
| **Alto** | Interpretação personalizada, planos | Disclaimer + revisão humana + HITL |
| **Crítico** | Triagem, alertas de emergência | Protocolo de crise + equipe humana |
