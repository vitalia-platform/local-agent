<!-- kit/workflows/review.md | Atualizado em: 21-05-2026 12:12:00(GMT-04:00) -->
---
description: >
  Audita a qualidade, arquitetura e segurança de um arquivo ou diretório.
  Valida se o código atende às 21 diretrizes da Constituição do Arquiteto.
---

# /review — Revisão de Código e Arquitetura

$ARGUMENTS

---

## Propósito

Identificar proativamente violações arquiteturais, más práticas, vulnerabilidades de segurança ou desvios de design system antes que o código entre em revisão humana ou produção.

---

## Comportamento

Quando ativado, o agente realiza a varredura do arquivo ou diretório especificado, aplicando a skill `dev/code-review-checklist` e as regras de `dev/clean-code`:

### Passo 1: Seleção do Modo de Execução
*   **Modo Pair Programming (Padrão):** O agente apresenta os problemas encontrados por seção e discute com o desenvolvedor as possíveis alternativas de correção.
*   **Modo Autônomo (via flag `--autonomous` ou `--auto`):** O agente revisa todo o arquivo/diretório em lote e gera uma tabela Markdown estruturada pronta de melhorias.

### Passo 2: Dimensões da Revisão
O agente valida rigorosamente:
1.  **Constituição do Arquiteto:** Conformidade estrita com os princípios P1 a P21 (como isolamento de dados, injeção de segredos via `.env` e selo de data e hora).
2.  **Clean Code & SOLID:** Legibilidade, responsabilidade única das funções, nomes expressivos e ausência de hardcodes.
3.  **Segurança e Privacidade:** Checagem de IPs locais expostos, credenciais ou falhas de vazamento de dados.

---

## Exemplos de Uso

```bash
/review scripts/review_pipeline/core/config_manager.py
/review scripts/review_pipeline/core/ --autonomous
/review --auto
```
