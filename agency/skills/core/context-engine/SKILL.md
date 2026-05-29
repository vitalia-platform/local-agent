---
name: context-engine
description: >
  Gerencia contexto entre sessões de trabalho. Lê, atualiza e serializa o
  estado do projeto em CONTEXT.md. Use quando iniciar sessão, encerrar sessão
  ou precisar saber onde o projeto está. Triggers: "contexto", "onde parei",
  "última sessão", "o que foi feito", "resumo do projeto".
allowed-tools: Read, Write, Edit, Glob
---

# Context Engine — Memória Entre Sessões

> Elimina o "cold start" de cada sessão. O agente sabe exatamente onde o projeto está.

---

## Localização do CONTEXT.md

```
<projeto-root>/
└── .agent/
    └── project/
        └── CONTEXT.md   ← arquivo de contexto do projeto
```

---

## Protocolo de Leitura (início de sessão)

```
1. Verificar se .agent/project/CONTEXT.md existe
   → NÃO existe: copiar template e pedir ao usuário para preencher campos básicos
   → EXISTE: ler e processar

2. Extrair campos obrigatórios:
   - Feature em andamento
   - Próximos passos (por prioridade)
   - Regras e constraints ativos
   - Branch atual

3. Apresentar resumo ao usuário:
   "📍 Contexto recuperado:
    Você estava trabalhando em: [feature]
    Último passo concluído: [item]
    Próximo: [P0 item]
    
    Deseja continuar com isso? (S/N ou outro foco)"
```

---

## Protocolo de Atualização (fim de sessão)

Ao executar `/session-end` ou quando o usuário pedir para encerrar:

```
1. Perguntar: "O que foi concluído nesta sessão?" (se não óbvio)
2. Atualizar seção "O que foi feito" com a sessão atual
3. Atualizar "Feature em andamento" se mudou
4. Atualizar "Próximos passos" — remover concluídos, reordenar
5. Atualizar "Última sessão" com data/hora atual
6. Perguntar: "Há alguma decisão arquitetural que devo registrar como ADR?"
7. Salvar o arquivo
8. Confirmar: "✅ Contexto salvo. Próxima sessão começa daqui."
```

---

## Protocolo de Criação (primeiro uso)

Quando CONTEXT.md não existe:

```
1. Copiar de templates/CONTEXT.template.md
2. Preencher automaticamente o que for possível:
   - Detectar tipo de projeto (package.json, requirements.txt, etc.)
   - Detectar stack (imports, config files)
   - Detectar branch (git)
3. Pedir ao usuário apenas os campos que não conseguiu detectar
4. Salvar em .agent/project/CONTEXT.md
```

---

## Campos do CONTEXT.md

| Campo | Obrigatório | Atualizado por |
|-------|-------------|----------------|
| Nome do projeto | ✅ | Usuário |
| Tipo | ✅ | Auto-detect ou usuário |
| Stack principal | ✅ | Auto-detect ou usuário |
| Objetivo | ✅ | Usuário |
| Status | ✅ | Usuário |
| Última sessão | ✅ | `context-engine` automaticamente |
| Feature em andamento | ✅ | `context-engine` após sessão |
| Arquivo principal | ⬜ | `context-engine` |
| Branch atual | ⬜ | Auto-detect via git |
| O que foi feito | ✅ | `context-engine` após sessão |
| Próximos passos | ✅ | Usuário + `context-engine` |
| Arquitetura | ⬜ | Usuário |
| ADRs | ⬜ | `adr-writing` skill |
| Regras e constraints | ⬜ | Usuário |
| Dependências externas | ⬜ | Usuário |
| Notas e aprendizados | ⬜ | `knowledge-curator` |

---

## Regras de Qualidade

- ✅ CONTEXT.md deve ser **legível por humano e por IA** — não use formatos exóticos
- ✅ Máximo de 100 linhas — seja conciso, não um diário
- ✅ Próximos passos devem ter **prioridade explícita** (P0, P1, P2)
- ✅ Cada sessão adiciona no topo da lista "O que foi feito" — não substitui
- ❌ Nunca deletar histórico de sessões anteriores — apenas arquivar se muito longo
