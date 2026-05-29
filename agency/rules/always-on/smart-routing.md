---
name: rule-smart-routing
description: Ativa roteamento contextual automático em todas as solicitações.
trigger: always_on
---

# Regra: Smart Routing Ativo

Esta regra ativa a skill `smart-router` como comportamento padrão.

## Comportamento

Em **toda** solicitação de trabalho:

1. Analisar silenciosamente: domínio(s) detectado(s)
2. Selecionar agente(s) conforme tabela de roteamento em `skills/core/smart-router/SKILL.md`
3. Informar brevemente qual expertise está sendo aplicada
4. Executar com o contexto do especialista selecionado

## Prioridade

```
GEMINI.md explícito > Override manual do usuário (@agente) > Smart Router automático
```

## Override pelo Usuário

O usuário pode sempre sobrescrever com:
- `@nome-do-agente` na mensagem
- "Como [especialista], faça..."
- Menção explícita a um workflow: `/session-start`, `/continue`, etc.
