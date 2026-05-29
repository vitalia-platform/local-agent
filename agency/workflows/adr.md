---
description: >
  Cria um Architecture Decision Record (ADR) de forma interativa.
  Documenta o contexto, opções consideradas, decisão e consequências.
---

# /adr — Criar Architecture Decision Record

$ARGUMENTS

---

## Propósito

Registra decisões arquiteturais importantes para que o contexto não se perca. Essencial para times e para retomada de projetos meses depois.

---

## Comportamento

### Fase 1: Coleta Interativa

```
"Vou criar um ADR. Responda brevemente:

1. Qual é o título da decisão?
   Ex: 'Usar pgvector para busca semântica'

2. Qual era o problema/contexto?
   Ex: 'Precisávamos de busca semântica em artigos científicos com suporte a multi-tenancy'

3. Quais opções foram consideradas? (pode listar 2-3)
   Ex: 'A) pgvector, B) Pinecone, C) Weaviate'

4. Qual foi escolhida e por quê?
   Ex: 'pgvector — já temos PostgreSQL, evita serviço externo, suporte a filtros SQL nativos'

5. Quais são os trade-offs honestos?
   Ex: 'Pior performance em escala massiva vs Pinecone, mas aceitável para o MVP'"
```

### Fase 2: Geração do ADR

Após respostas, gerar e salvar automaticamente:

```bash
# Detectar próximo número sequencial
ls docs/adr/ | grep -o 'ADR-[0-9]*' | sort -n | tail -1
# → ADR-003 (próximo será ADR-004)
```

Salvar em: `docs/adr/ADR-NNN-titulo-kebab.md`

### Fase 3: Registro no Contexto

```
→ Adicionar referência no CONTEXT.md:
  "ADRs: [ADR-004] Usar pgvector para busca semântica — 2026-04-30"
→ Confirmar: "✅ ADR-004 criado em docs/adr/"
```

---

## Exemplos de Uso

```
/adr
/adr escolha de banco de dados
/adr padrão de autenticação JWT vs session
/adr estratégia de cache para biomarcadores
```

---

## Quando o `/adr` é Sugerido Automaticamente

O `conductor` e o `reviewer` sugerem `/adr` quando detectam:
- Nova biblioteca sendo adicionada ao projeto
- Padrão arquitetural novo introduzido
- Decisão de design que impacta múltiplos módulos
- Trade-off significativo foi aceito
