<!-- kit/workflows/test.md | Atualizado em: 21-05-2026 12:12:00(GMT-04:00) -->
---
description: >
  Conduz o ciclo de Test-Driven Development (TDD) para novas features ou correções.
  Garante integridade e resiliência via ciclo Red-Green-Refactor.
---

# /test — TDD e Cobertura de Testes

$ARGUMENTS

---

## Propósito

Assegurar que toda lógica crítica (especialmente regras científicas, médicas e de segurança) seja suportada por testes robustos e livre de regressões antes de qualquer publicação.

---

## Comportamento

Quando ativado, o agente engaja o usuário no ciclo de TDD usando as skills `dev/tdd-workflow` e `dev/testing-patterns`:

### Passo 1: Seleção do Modo de Execução
*   **Modo Pair Programming (Padrão):** O agente conduz o ciclo passo a passo de forma guiada, mostrando o resultado de cada fase e aguardando aprovação para refatorar.
*   **Modo Autônomo (via flag `--autonomous` ou `--auto`):** O agente gera a suite de testes, implementa a lógica necessária, executa o runner (Pytest/Jest) de forma autônoma e apresenta o veredito final.

### Passo 2: O Ciclo TDD
1.  **Fase Vermelha (Red):** Criação/Atualização do arquivo de testes expressando a especificação desejada. Execução inicial para atestar a falha.
2.  **Fase Verde (Green):** Escrita do código mínimo necessário para fazer os testes passarem sem erros.
3.  **Fase de Refatoração (Refactor):** Melhoria da estrutura, legibilidade e performance do código implementado, mantendo todos os testes em verde.

---

## Exemplos de Uso

```bash
/test Testes unitários do carregador do .env no config_manager
/test --autonomous tests/test_ollama_resilience.py
/test Criar testes de isolamento para auditoria
```
