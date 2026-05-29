---
name: academic-id-resolver
description: Protocolo de resolução, normalização e fallback de Identificadores Acadêmicos (DOI, PMID, PMCID, Scopus ID) para assegurar automação estável no processamento de literatura.
---

# Skill: Academic ID Resolver

Quando manipular bancos de dados brutos exportados de portais científicos (como Web of Science, PubMed ou Scopus), o agente `data-librarian` deve seguir este protocolo de normalização para evitar que o download de PDFs completos falhe futuramente por quebra de links.

## 1. A Hierarquia de Chaves
Na estruturação do dataset limpo, aplique a seguinte prioridade de chaves (Primary Keys) para os artigos:
1. **DOI** (Digital Object Identifier) — O padrão Ouro absoluto.
2. **PMID** (PubMed ID)
3. **PMCID** (PubMed Central ID)
4. **Scopus EID / WoS UT** — Identificadores proprietários.

## 2. Resolução de DOI Ausente
Em arquivos exportados da PubMed ou Scopus, é frequente que o DOI venha vazio, mas o PMID esteja presente.
Se houver PMIDs sem DOI associado no CSV, **não descarte o artigo**. 

**Estratégia de Fallback (NCBI API):**
Escreva um script Python usando a [NCBI ID Converter API](https://www.ncbi.nlm.nih.gov/pmc/tools/id-converter-api/).
- **Endpoint**: `https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids=[LISTA_DE_PMIDS]&format=json`
- Parse o JSON para encontrar a chave `doi`.
- Atualize a linha correspondente no CSV com o DOI descoberto.

## 3. Limpeza de Strings
Para a coluna de DOI no CSV resultante:
- Remova prefixos URL se existirem (ex: `https://doi.org/10.1111/abc` vira estritamente `10.1111/abc`).
- Isso é mandatório porque APIs de recuperação de metadados como Unpaywall ou CrossRef falham se o DOI tiver fragmentos HTTP injetados.
