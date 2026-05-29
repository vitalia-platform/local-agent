---
description: >
  Encerra a sessão de trabalho: documenta o que foi feito, atualiza o contexto
  do projeto e prepara o próximo passo para a próxima sessão.
---

# /session-end — Encerramento de Sessão

$ARGUMENTS

---

## Propósito

Garante que nenhum aprendizado ou progresso se perca entre sessões. Em 2 minutos, o contexto está salvo e a próxima sessão começa exatamente de onde você parou.

---

## Comportamento

### Passo 1: Coleta de Progresso

```
Se não for óbvio pelo histórico da sessão, perguntar:
"O que foi concluído nesta sessão?"
```

### Passo 2: Verificar Aprendizados

```
"Houve algum padrão, descoberta ou decisão que devo registrar?"
→ Se sim: acionar knowledge-curator ou adr-writing
→ Se não: prosseguir
```

### Passo 3: Atualizar CONTEXT.md

```markdown
## Sessão [data/hora] — concluída

**Concluído:**
- [item 1]
- [item 2]

**Feature em andamento:** [atualizar se mudou]
**Próximo passo (P0):** [item mais prioritário]
```

### Passo 4: Revisar Próximos Passos

```
→ Remover itens concluídos
→ Reordenar por prioridade atual
→ Adicionar itens descobertos durante a sessão
```

### Passo 5: Confirmação e Histórico (Obrigatório)

```markdown
## ✅ Sessão Encerrada

**Salvo em**: .agent/session/CONTEXT.md
**Progresso registrado**: [resumo de 2-3 linhas]
**Próxima sessão começa em**: [P0 — descrição do próximo item]
```

**[AÇÃO DO AGENTE]:** Anexe o resumo gerado (o bloco markdown acima) ao final do arquivo `.agent/session/SESSION_HISTORY.md` incluindo a data e hora exatas. Isso garante o registro imutável.

### Passo 6: Controle de Concorrência e Nuvem

```
Pergunte ao usuário:
"Deseja enviar este contexto para a nuvem do GitHub agora? (Padrão: Não)"

→ Se o usuário responder SIM:
Execute o comando de sincronia passando o resumo da sessão:
$ bash .agent/scripts/session-sync.sh "Resumo da sessão: [progresso]"

→ O script bash cuidará do ETag (.sync_lock). Se o script falhar acusando conflito, avise o usuário para usar o session-resolve.sh.
```

Até a próxima. Use `/session-start` para retomar.

---

## Exemplos de Uso

```
/session-end
/session-end --resumo="Implementei o endpoint de biometria"
```
