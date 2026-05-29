---
name: rule-hitl-medical
description: HITL obrigatório para qualquer conteúdo médico ou de saúde destinado a usuários finais.
trigger: always_on
---

# Regra: HITL Médico (Human-in-the-Loop)

> "IA alucina. Em saúde, isso tem consequências. Humano no comando sempre."

## Quando Aplicar

Aplicar esta regra quando a resposta envolver **qualquer** dos seguintes:

- Diagnóstico, sintomas ou condições médicas
- Protocolos de tratamento ou suplementação
- Interpretação de exames ou biomarcadores
- Recomendações nutricionais específicas
- Dosagens de qualquer substância
- Conteúdo que será exibido a pacientes ou usuários finais
- Planos de saúde, wellness ou fitness personalizados

## Protocolo Obrigatório

### Para conteúdo técnico (entre agentes/devs):
```
→ Marcar como: [REVISÃO CIENTÍFICA PENDENTE]
→ Acionar especialista científico relevante antes de usar em produção
```

### Para conteúdo destinado a usuários finais:
```
→ Adicionar disclaimer: "Esta informação é educacional. Consulte um profissional de saúde."
→ Marcar status como DRAFT até revisão humana
→ Não publicar sem aprovação explícita
```

### Para ranges e valores clínicos no código:
```python
# SEMPRE documentar a fonte do range:
# Fonte: [nome do especialista / referência científica] — [data]
CORTISOL_MORNING_RANGE_UG_DL = {"min": 6, "max": 23}  # Ref: endocrinologist-review-2026
```

## Hierarquia de Aprovação

```
IA gera → DRAFT
Especialista científico revisa → REVIEW  
Profissional de saúde humano aprova → ACTIVE (pode ir para produção)
```
