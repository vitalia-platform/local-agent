---
name: adr-writing
description: >
  Architecture Decision Records. Documenta decisões arquiteturais com contexto,
  opções consideradas, decisão tomada e consequências. Triggers: "ADR",
  "decisão arquitetural", "por que escolhemos", "documentar decisão",
  "registrar escolha técnica", "trade-off", "/adr".
allowed-tools: Read, Write, Edit, Glob
---

# ADR Writing — Architecture Decision Records

> "O código diz o quê. O ADR diz o porquê."

## Quando Criar

| Situação | ADR? |
|----------|------|
| Escolha de framework/biblioteca principal | ✅ |
| Decisão de arquitetura (padrão, estrutura) | ✅ |
| Mudança de convenção de código | ✅ |
| Fix de bug simples | ❌ |

## Template

Salvar em: `docs/adr/ADR-NNN-titulo.md`

```markdown
# ADR-[NNN]: [Título]

**Status**: Aceita | Proposta | Substituída por ADR-NNN
**Data**: [YYYY-MM-DD]

## Contexto
[O problema. Forças em jogo. Restrições existentes.]

## Opções Consideradas

### Opção A: [Nome]
- ✅ Prós: [lista]
- ❌ Contras: [lista]

### Opção B: [Nome]
- ✅ Prós: [lista]
- ❌ Contras: [lista]

## Decisão
Escolhemos **[Opção X]** porque [justificativa honesta].

## Consequências
- ✅ [benefício]
- ⚠️ [trade-off honesto]
- 🔲 Dívida técnica: [o que ficou para depois]
```

## Protocolo do `/adr`

```
1. "Qual é a decisão a documentar?"
2. "Quais opções foram consideradas?"
3. "Qual foi escolhida e por quê?"
4. "Quais são os trade-offs honestos?"
5. Gerar ADR com número sequencial
6. Salvar em docs/adr/
7. Registrar referência no CONTEXT.md
```

## Regras
- Nunca deletar ADRs — apenas marcar como substituída
- Ser honesto sobre pressões de tempo ou custo
- ADR-001 substituída → muda status, ADR-002 referencia a anterior
