---
description: "Protocolo socrático para estruturar features ou requisitos complexos antes da execução."
---

# /brainstorming — Estruturação Socrática

$ARGUMENTS

---

## Propósito

Forçar uma pausa reflexiva antes da execução. O agente fará perguntas cruciais (com trade-offs e consequências) sobre arquitetura, requisitos e escala antes de tocar em qualquer código.

## Comportamento

Quando ativado, o agente segue as regras estritas da skill `core/brainstorming`:
1. **Nenhum código é gerado no primeiro passo.**
2. O agente analisa o pedido e identifica pontos cegos.
3. Apresenta opções de decisão com Prós e Contras.
4. Aguarda a definição do usuário para criar um plano.

## Exemplos
```
/brainstorming criar nova fase de processamento paralelo
/brainstorming mudar a estrutura do banco de dados
```
