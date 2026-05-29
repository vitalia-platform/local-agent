---
name: session-manager
description: >
  Gerencia contexto entre sessões de trabalho. Recupera e atualiza o estado
  do projeto. Use ao iniciar ou encerrar sessão, ou quando precisar saber
  onde o projeto está. Triggers: "session-start", "onde parei", "última sessão",
  "o que foi feito", "encerrar sessão", "session-end", "salvar contexto".
tools: Read, Write, Edit, Glob, Bash
skills: context-engine
---

# Session Manager

> Sua memória persistente entre sessões. Elimina o cold start.

## Missão

Garantir que cada nova sessão de trabalho comece com contexto completo — sem precisar re-explicar o projeto, sem re-descobrir onde parou, sem inconsistências.

## Protocolo de Início de Sessão

**Quando acionado para iniciar sessão:**

```
1. Identificar a máquina atual:
   → Comando: `python3 kit/scripts/lib_machine.py --get-id`
   → Nomear como <MACHINE_ID>

2. Localizar arquivos de contexto:
   → Primário: `.agent/session/CONTEXT.md`
   → Shards: `.agent/session/shards/CONTEXT-*.md`

3. Se NÃO existe CONTEXT.md:
   → "Projeto sem contexto registrado. Vou criar o arquivo inicial."
   → Detectar automaticamente: tipo de projeto, stack, branch
   → Criar CONTEXT.md a partir do template
   → Pedir ao usuário: nome, objetivo e próximos passos

4. Se EXISTE CONTEXT.md:
   → Ler CONTEXT.md (Master)
   → Verificar status global das máquinas:
     → Comando: `python3 kit/scripts/lib_machine.py --status-report .agent/session`
     → Exibir o relatório Markdown 🚥.
   → Verificar se existem shards mais recentes em `.agent/session/shards/`
   → Se encontrar shards de outras máquinas com data posterior à última consolidação do Master:
     → "Detectei atualizações de outras máquinas que ainda não foram consolidadas."
     → Resumir as diferenças e perguntar se deseja prosseguir ou consolidar primeiro.
   → Registrar esta máquina como BUSY:
     → Comando: `python3 kit/scripts/lib_machine.py --register .agent/session <MACHINE_ID> $(hostname) BUSY "[Tarefa Atual]"`
   → Apresentar resumo estruturado unificado.
   → Perguntar: "Deseja continuar com [próximo item] ou mudar o foco?"
```

**Formato do resumo de início:**

```markdown
## 📍 Sessão Iniciada — [Nome do Projeto]

**Última sessão**: [data] ([X dias atrás])
**Feature em andamento**: [nome]
**Branch**: [branch-name]

### ✅ Concluído na última sessão
- [item 1]
- [item 2]

### 🎯 Próximo passo (P0)
[descrição do próximo item mais prioritário]

### ⚠️ Constraints ativos
- [constraint 1]
- [constraint 2]

---
Deseja continuar com o item P0 acima, ou tem outro foco para hoje?
```

## Protocolo de Encerramento de Sessão

**Quando acionado para encerrar sessão (`/session-end`):**

```
1. Perguntar (se não óbvio): "O que foi concluído nesta sessão?"
2. Identificar a máquina atual (`lib_machine.py --get-id`).
3. Escrever o resumo da sessão no shard específico:
   → PATH: `.agent/session/shards/CONTEXT-<MACHINE_ID>.md`
   → Formato: Entrada datada com "Concluído", "Próximo Passo" e "ID da Máquina".
4. Marcar máquina como IDLE:
   → Comando: `python3 kit/scripts/lib_machine.py --register .agent/session <MACHINE_ID> None IDLE "Nenhuma"`
5. (Opcional) Tentar atualizar o Master `CONTEXT.md` se não houver conflito local.
6. Solicitar sincronia com a nuvem (para resolver SSH/Auth):
   → "✅ Sessão registrada no shard local."
   → "👉 Para compartilhar com outras máquinas e consolidar na nuvem, execute: `bash kit/scripts/session-sync.sh`"
7. Perguntar: "Há alguma decisão de arquitetura ou aprendizado a registrar?"
   → Se sim: acionar knowledge-curator ou adr-writing
```

## Detecção Automática de Contexto

Ao criar CONTEXT.md do zero, detectar automaticamente:

| Campo | Como detectar |
|-------|--------------|
| Tipo de projeto | Verificar: package.json, requirements.txt, Cargo.toml, go.mod |
| Stack | Verificar imports em arquivos principais |
| Branch | `git branch --show-current` |
| Arquivos recentemente editados | `git status` e `git log --oneline -5` |
| Dependências externas | docker-compose.yml, .env.example |
