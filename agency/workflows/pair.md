---
description: >
  Ativa o modo pair programming estruturado. O agente propõe cada chunk
  de implementação e aguarda sua aprovação antes de escrever qualquer código.
---

# /pair — Pair Programming

$ARGUMENTS

---

## Propósito

Trabalhar junto, chunk a chunk, com aprovação explícita em cada passo. Nenhum código é escrito sem você revisar a proposta primeiro.

---

## Comportamento

### Ativação

```markdown
## 👥 Pair Programming — [Objetivo]

**Regras do par:**
1. Proponho um chunk → você aprova antes de implementar
2. "ok" ou "aprovado" → avanço
3. "ajuste: [o que]" → reviso a proposta
4. "pause" → salvo progresso e encerro
5. "skip" → pulo este chunk

Vou propor o primeiro chunk agora.
```

### Loop de Trabalho

Para cada chunk:

```markdown
---
## 💭 Chunk [N]: [Nome]

**Implementarei**: [descrição clara]
**Arquivo(s)**: `[caminho]`

```[linguagem]
[código proposto]
```

**Impacto**: [baixo/médio/alto]
**Teste necessário**: [sim/não — motivo]

✅ ok para implementar? (ok / ajuste: ... / pause / skip)
```

### Após Implementação

```markdown
✅ Chunk [N] feito.
[O que foi implementado em 1-2 linhas]

---
## 💭 Chunk [N+1]: [Nome]
[próxima proposta]
```

### Encerramento

```markdown
## 🏁 Sessão de Pair Encerrada

**Chunks concluídos**: [N]
**Pausado em**: Chunk [X] — [descrição]
**Testes pendentes**: [lista]

Atualizo o CONTEXT.md com o progresso?
```

---

## Exemplos

```
/pair implementar endpoint de biometria
/pair refatorar serviço de autenticação
/pair adicionar alertas críticos de glicemia
```

---

## Integração com Especialistas

Se um chunk tocar dado clínico, o par faz pausa automática:

```
💭 Chunk N toca [dado de saúde].
Antes de propor: consultando @endocrinologist...
[recebe constraint]
Proposta atualizada com constraint validado ↓
```
