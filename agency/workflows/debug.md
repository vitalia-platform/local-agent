<!-- kit/workflows/debug.md | Atualizado em: 21-05-2026 12:12:00(GMT-04:00) -->
---
description: >
  Inicia o fluxo sistemático de depuração. Ajuda a isolar falhas,
  identificar a causa raiz usando os 5 Whys e validar correções de forma segura.
---

# /debug — Depuração Sistemática

$ARGUMENTS

---

## Propósito

Identificar, isolar e corrigir bugs ou comportamentos inesperados sem adivinhação. A IA usará a metodologia estruturada de 4 fases para documentar a causa raiz antes de tocar no código.

---

## Comportamento

Quando ativado, o agente interage com o usuário para carregar e executar a skill `dev/systematic-debugging`:

### Passo 1: Seleção do Modo de Execução
O agente perguntará explicitamente qual modo utilizar (caso não tenha sido fornecido via argumento):
*   **Modo Pair Programming (Padrão):** O agente investiga cada fase, propõe suas observações e aguarda aprovação explícita do usuário para prosseguir.
*   **Modo Autônomo (via flag `--autonomous` ou `--auto`):** O agente realiza a reprodução, o isolamento e a identificação do bug diretamente, gerando um relatório detalhado.

### Passo 2: Execução das Fases de Depuração
1.  **Phase 1: Reproduce:** Tenta reproduzir o bug a partir de logs, mensagens de erro fornecidas ou reprodução local.
2.  **Phase 2: Isolate:** Isola a causa examinando alterações recentes de código (`git log`) e configurações.
3.  **Phase 3: Understand (Os 5 Porquês):** Monta a análise de causa raiz usando o método socrático dos 5 Porquês.
4.  **Phase 4: Fix & Verify:** Propõe o patch completo, aplica-o defensivamente e roda os testes correspondentes para atestar a correção.

---

## Exemplos de Uso

```bash
/debug Erro de Timeout na chamada à API do Ollama
/debug falha no parsing do PDF na fase 2
/debug --autonomous Erro de importação em run_fase1.py
```
