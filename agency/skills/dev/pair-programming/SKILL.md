---
name: pair-programming
description: >
  Protocolo de pair programming estruturado. Define o ritmo de trabalho em
  pares: proposta → revisão → aprovação → implementação → próximo chunk.
  Use quando o usuário quer trabalhar junto, revisando cada passo antes de
  avançar. Triggers: "pair", "trabalhar juntos", "em pares", "vamos juntos",
  "me mostre antes de implementar", "quero revisar cada passo".
allowed-tools: Read, Write, Edit, Grep, Glob
---

# Pair Programming — Protocolo de Trabalho em Pares

> "Dois olhos no código, zero surpresas no resultado."

---

## O que é Pair Programming no Kit

Modo de trabalho onde o agente (`coder`) e o usuário colaboram em loop constante:

```
coder propõe → usuário revisa → usuário aprova → coder implementa → coder reporta → próximo chunk
```

A diferença para o modo normal: **nenhum chunk é implementado sem aprovação explícita.**

---

## Ativação do Modo Pair

Quando `/pair [objetivo]` é acionado:

```markdown
## 👥 Modo Pair Programming Ativado

**Objetivo**: [descrição do objetivo]
**Agentes**: você + coder [+ especialista científico se relevante]

**Regras do par:**
1. Cada proposta espera sua aprovação antes de implementar
2. Você pode pedir ajuste antes de aprovar
3. Use "ok" ou "aprovado" para avançar
4. Use "pause" para parar o loop
5. Use "revise [o que]" para ajustar a proposta

Pronto para começar? Vou propor o primeiro chunk.
```

---

## O Loop de Pair

### Estrutura de cada iteração

```markdown
## 💭 Chunk [N]: [Nome do Chunk]

**O que farei:**
[Descrição clara e específica do que será implementado]

**Arquivo(s):**
- `caminho/do/arquivo.py` — [o que será mudado]

**Código proposto:**
```[linguagem]
[trecho de código que será implementado]
```

**Impacto:** [baixo/médio/alto — o que pode ser afetado]

---
✅ Aprovar e implementar? (ok / ajuste: [o que mudar] / pause)
```

### Após aprovação e implementação

```markdown
## ✅ Chunk [N] Implementado

**O que foi feito:** [resumo]
**Teste necessário:** [sim — sugiro escrever X / não para este chunk]

---
## 💭 Chunk [N+1]: [Próximo Chunk]
[continua o loop]
```

---

## Tamanho Ideal de Chunk

| Complexidade | Tamanho do Chunk |
|-------------|-----------------|
| Simples | 1 função / 1 método |
| Médio | 1 classe / 1 endpoint |
| Complexo | 1 arquivo / 1 camada |

> Regra de ouro: cada chunk deve ser implementável em < 5 minutos.

---

## Papéis no Par

| Papel | Responsabilidade |
|-------|----------------|
| **Coder (agente)** | Propõe, analisa dependências, implementa, reporta |
| **Usuário (você)** | Aprova, ajusta, questiona, decide prioridade |
| **Reviewer (se invocado)** | Questiona decisões arquiteturais entre chunks |

---

## Especialista Científico no Par

Quando a feature envolve dados de saúde:

```
coder propõe chunk com dado clínico
→ coder sinaliza: "Este valor precisa validação científica"
→ conductor aciona especialista
→ especialista emite constraint
→ coder revisa proposta com constraint
→ usuário aprova versão validada
```

---

## Encerramento do Pair

```markdown
## 🏁 Pair Programming Encerrado

**Objetivo**: [original]
**Status**: ✅ Concluído / ⏸️ Pausado em: [chunk N]

**Chunks implementados:**
1. [chunk 1] ✅
2. [chunk 2] ✅
...

**Pendentes:**
- [chunk X] — próxima sessão

**Testes sugeridos:** [lista]

Deseja que eu atualize o CONTEXT.md com o progresso?
```
