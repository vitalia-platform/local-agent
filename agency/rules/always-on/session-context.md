---
name: rule-session-context
description: Verifica CONTEXT.md antes de qualquer ação no projeto.
trigger: always_on
---

# Regra: Verificar Contexto de Sessão

**ANTES de responder qualquer solicitação de trabalho:**

1. Verificar se `.agent/project/CONTEXT.md` existe no projeto
2. Se existe e **não foi lido nesta sessão**: lê-lo e incorporar os constraints ativos
3. Se **não existe**: sugerir `/session-start` para criar o contexto

> Esta regra não bloqueia respostas — apenas garante que o contexto está disponível quando relevante.

## Quando aplicar

- ✅ Ao receber a primeira solicitação de código em uma sessão
- ✅ Ao receber referência a arquivo ou feature do projeto
- ❌ Em perguntas conceituais ou conversas gerais — não aplicar
