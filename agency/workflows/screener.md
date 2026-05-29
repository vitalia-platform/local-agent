<!-- kit/workflows/screener.md | Atualizado em: 21-05-2026 12:12:00(GMT-04:00) -->
---
description: >
  Orquestra a triagem científica de artigos da amostra.
  Aplica critérios de inclusão/exclusão e gera evidência auditável.
---

# /screener — Triagem Científica e Elegibilidade

$ARGUMENTS

---

## Propósito

Garantir o rigor absoluto da triagem na Fase 1 (ou auditoria manual) com base em critérios explícitos, eliminando vieses e registrando provas irrefutáveis de elegibilidade para publicação.

---

## Comportamento

Quando ativado, o agente aciona o Esquadrão Science (`chief-reviewer`, `methodology-auditor`) usando as skills `science/llm-screener` e `science/clinical-safety`:

### Passo 1: Seleção do Modo de Execução
*   **Modo Pair Programming (Padrão):** O agente processa um artigo por vez, exibe a justificativa da IA baseada na pergunta norteadora e aguarda o seu veredito/validação humana (HITL) para salvar.
*   **Modo Autônomo (via flag `--autonomous` ou `--auto`):** O agente processa um lote inteiro de artigos (usando a flag `--overnight` no script), persistindo os shards de auditoria silenciosamente e apresentando o sumário de aceitação.

### Passo 2: Roteiro Científico
1.  **Leitura de Metadados:** Avalia título, abstract e palavras-chave.
2.  **Checagem de Elegibilidade:** Valida rigorosamente contra os limites temporais (ex: 2018-2026) e recorte tecnológico do estudo.
3.  **Persistência Forense:** Grava a decisão com chain-of-thought detalhado no shard JSON de auditoria.

---

## Exemplos de Uso

```bash
/screener Artigo ID 42 --pair
/screener --autonomous
/screener Validar triagem dos últimos 10 artigos da amostra
```
