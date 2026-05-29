---
name: rag-protocol
description: >
  Protocolo para consulta a fontes externas via RAG (Retrieval-Augmented
  Generation) e bancos de dados científicos estruturados. Define como
  conectar a PubMed, bases de dados clínicas e DBs proprietários.
  Triggers: "consultar PubMed", "buscar evidência", "base de dados externa",
  "RAG", "retrieval", "busca semântica em base científica", "Ollama RAG".
allowed-tools: Read, Bash
---

# RAG Protocol — Consulta a Fontes Científicas Externas

> "IA sem grounding alucina. IA com RAG cita."

---

## Arquitetura de Fontes

```
Solicitação Científica
        ↓
[1] Knowledge Base Local (arquivos em skills/science/*/references/)
    → Resposta rápida, sem latência, sempre disponível
        ↓ (se não encontrado)
[2] Vector DB do Projeto (pgvector)
    → Knowledge Hub do projeto — artigos curados pela equipe
        ↓ (se precisar mais)  
[3] APIs Externas (PubMed, guidelines, DBs clínicos)
    → Fontes canônicas — via MCP ou requests diretos
```

---

## Fontes Externas Suportadas

### PubMed / NCBI

```python
# Busca básica via NCBI API (gratuita)
import httpx

async def search_pubmed(query: str, max_results: int = 10) -> list[dict]:
    """Busca artigos no PubMed. Sempre adicionar filtros de qualidade."""
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    # Adicionar filtro: apenas artigos em humanos, nos últimos 5 anos
    filtered_query = f"{query} AND (humans[MeSH]) AND (\"last 5 years\"[PDat])"
    
    # 1. Buscar IDs
    search_resp = await httpx.get(f"{base_url}/esearch.fcgi", params={
        "db": "pubmed", "term": filtered_query,
        "retmax": max_results, "retmode": "json"
    })
    ids = search_resp.json()["esearchresult"]["idlist"]
    
    # 2. Buscar detalhes
    fetch_resp = await httpx.get(f"{base_url}/efetch.fcgi", params={
        "db": "pubmed", "id": ",".join(ids),
        "retmode": "xml"  # ou "json" com rettype="abstract"
    })
    return parse_pubmed_response(fetch_resp.text)
```

### Configuração MCP para Fontes Externas

```json
// .agent/project/mcp_config.json — adicionar ao projeto
{
  "mcpServers": {
    "pubmed": {
      "command": "npx",
      "args": ["-y", "@mcp-servers/pubmed"],
      "config": { "apiKey": "${NCBI_API_KEY}" }
    },
    "clinical-guidelines": {
      "command": "python",
      "args": [".agent/scripts/guidelines_mcp.py"],
      "config": { "sources": ["who", "uptodate", "dynamed"] }
    }
  }
}
```

---

## Protocolo de Grounding para Agentes Científicos

Quando um agente científico precisar responder sobre tópico específico:

```
1. Verificar knowledge base local (skills/science/*/references/)
   → Encontrou resposta confiável: usar + citar arquivo
   
2. Verificar Vector DB do projeto (se configurado)
   → Busca semântica por termos-chave
   → Threshold de similaridade: > 0.75 cosine
   
3. Buscar em fonte externa (PubMed ou guidelines)
   → Sempre filtrar: humanos, últimos 5 anos, peer-reviewed
   → Citar: [Autores, Título, Periódico, Ano, DOI]
   
4. Se nenhuma fonte encontrada:
   → NUNCA inventar — dizer explicitamente:
      "Não encontrei evidência publicada sobre isto. 
       Recomendo consultar um especialista humano."
```

---

## Indexação no Vector DB do Projeto (pgvector)

```python
# Como indexar artigos curados no Knowledge Hub
async def index_article(article: dict, embedding_model: str = "nomic-embed-text"):
    """Indexa artigo no pgvector para busca semântica futura."""
    import ollama
    
    text = f"{article['title']}. {article['abstract']}"
    embedding = await ollama.embeddings(model=embedding_model, prompt=text)
    
    await KnowledgeArticle.objects.acreate(
        title=article['title'],
        authors=article['authors'],
        source=article['source'],         # "pubmed", "uptodate", etc.
        doi=article.get('doi'),
        published_date=article['date'],
        abstract=article['abstract'],
        embedding=embedding['embedding'],  # pgvector field
        tags=article.get('mesh_terms', []),
        quality_level=article.get('evidence_level', 'unknown')
    )
```

---

## Regras de Qualidade de Fonte

- ✅ Peer-reviewed em periódico indexado
- ✅ Publicado nos últimos 5 anos (ou clássico com validação atual)
- ✅ Estudo em humanos (quando aplicável)
- ✅ DOI disponível para rastreabilidade
- ❌ Blogs, sites de suplementos, fontes sem revisão
- ❌ Estudos em animais sem ressalva explícita
- ❌ Estudos financiados pela indústria sem declaração
