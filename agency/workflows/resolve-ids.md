<!-- kit/workflows/resolve-ids.md | Atualizado em: 21-05-2026 12:12:00(GMT-04:00) -->
---
description: >
  Busca e resolve metadados científicos complexos (DOIs, PMIDs, PMCID)
  e valida a rastreabilidade da literatura.
---

# /resolve-ids — Resolução de Identificadores Acadêmicos

$ARGUMENTS

---

## Propósito

Garantir que nenhum artigo sofra de "links quebrados" ou falsas citações. Resolve identificadores diretamente contra as APIs de referência (PubMed, Crossref, Unpaywall).

---

## Comportamento

Quando ativado, o agente invoca a skill `science/academic-id-resolver` para cruzar dados e buscar registros limpos:

### Passo 1: Seleção do Modo de Execução
*   **Modo Pair Programming (Padrão):** O agente exibe os dados recuperados de APIs externas para cada identificador e pede que você confirme a indexação ou a correspondência aproximada encontrada.
*   **Modo Autônomo (via flag `--autonomous` ou `--auto`):** O agente busca em lote, tenta resolver desvios de grafia nos nomes de autores e títulos de forma autônoma e atualiza diretamente a planilha `PRISMA_LOG.csv` ou os Shards correspondentes.

### Passo 2: Procedimento
1.  **Busca Federada:** Dispara consultas nas APIs da literatura médica/científica.
2.  **Validação de Metadados:** Certifica que o ano de publicação, autores e journal estão consistentes com a amostra.
3.  **Enriquecimento:** Adiciona metadados de acesso aberto (Open Access) e links de PDFs quando disponíveis.

---

## Exemplos de Uso

```bash
/resolve-ids doi:10.2196/34526
/resolve-ids --autonomous Buscar DOIs para todos os artigos sem ID no PRISMA_LOG
/resolve-ids "Digital health interventions in physical education"
```
