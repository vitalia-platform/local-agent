---
name: agent-factory
description: >
  Templates e protocolo para criação de novos agentes, skills e workflows.
  Use quando o knowledge-curator precisar criar um novo componente para o kit.
  Triggers: "criar agente", "novo agente", "template de agente", "criar skill",
  "adicionar ao kit", "factory de agentes".
allowed-tools: Read, Write, Edit, Glob
---

# Agent Factory — Criação Dinâmica de Componentes

> "Um agente bem projetado se ativa sozinho, no momento certo."

---

## Regra de Ouro: O Trigger é Tudo

A `description` de um agente/skill é o **único mecanismo de ativação contextual**. Investir tempo aqui é o que faz o roteamento funcionar sem nomeação explícita.

**Anatomia de uma description perfeita:**
```
[Papel principal em 1 frase]. [Use quando: casos de uso principais].
Triggers: "[palavra1]", "[frase2]", "[contexto3]", "[padrão4]", "[situação5]".
```

---

## Template: Novo Agente

Localização: `templates/agent.template.md`
Salvar em: `kit/agents/[categoria]/[nome-do-agente].md`

```markdown
---
name: [nome-kebab-case]
description: >
  [Papel principal — 1 frase clara].
  [Quando usar — casos de uso específicos].
  Triggers: "[palavra-chave-1]", "[palavra-chave-2]", "[frase-ativadora-1]",
  "[contexto-1]", "[situação-1]".
tools: Read, Write, Edit, Grep, Glob, Bash
skills: [skill-1], [skill-2]
---

# [Nome Legível] — [Subtítulo/Especialidade]

> **Persona**: [Descrição da persona em 1-2 frases. Quem é este agente?]

## Missão

[O que este agente garante? Qual problema ele resolve? 2-3 frases.]

---

## Domínios de Expertise

| Área | Detalhes |
|------|---------|
| [área 1] | [descrição] |
| [área 2] | [descrição] |

---

## Protocolo de Execução

[Passo a passo do que o agente faz quando acionado]

1. [Passo 1]
2. [Passo 2]
3. [Passo 3]

---

## Regras de Ferro

| Regra | Descrição |
|-------|-----------|
| [Regra 1] | [O que nunca fazer / sempre fazer] |
| [Regra 2] | [O que nunca fazer / sempre fazer] |

---

## Integração com o Time

[Como este agente interage com outros agentes do kit]
```

---

## Template: Nova Skill

Localização: `templates/skill.template.md`
Salvar em: `kit/skills/[categoria]/[nome-da-skill]/SKILL.md`

```markdown
---
name: [nome-kebab-case]
description: >
  [O que esta skill fornece]. [Quando ativar].
  Triggers: "[palavra-chave-1]", "[frase-2]", "[contexto-3]".
version: 1.0.0
allowed-tools: Read, Grep
---

# [Nome Legível] — [Subtítulo]

> [Citação ou princípio central desta skill]

---

## Visão Geral

[O que esta skill encapsula. Por que existe. Qual problema resolve.]

---

## [Seção Principal]

[Conteúdo da skill — regras, padrões, valores de referência, exemplos]

---

## Como Usar

[Instruções para o agente de como aplicar este conhecimento]

---

## Referências

[Links ou arquivos em references/ com detalhes adicionais]
```

---

## Template: Novo Workflow

Localização: `templates/workflow.template.md`
Salvar em: `kit/workflows/[nome-do-comando].md`

```markdown
---
description: >
  [O que este workflow faz em 1-2 frases].
  [Quando usar].
---

# /[comando] — [Título Descritivo]

$ARGUMENTS

---

## Propósito

[Por que este workflow existe. Qual problema resolve.]

---

## Comportamento

Quando `/[comando]` for acionado:

### Fase 1: [Nome da Fase]
[O que acontece]

### Fase 2: [Nome da Fase]
[O que acontece]

---

## Exemplos de Uso

```
/[comando]
/[comando] [argumento-exemplo]
```

---

## Saída Esperada

[O que o usuário recebe ao final]
```

---

## Checklist de Qualidade (antes de adicionar ao kit)

Para agentes:
- [ ] Description inclui "Use quando" + pelo menos 5 triggers
- [ ] Protocolo de execução é claro e sequencial
- [ ] Regras de ferro estão definidas
- [ ] Skills necessárias estão listadas no frontmatter

Para skills:
- [ ] Description é específica o suficiente para não ativar por engano
- [ ] Conteúdo é reutilizável entre projetos diferentes
- [ ] Referências externas estão linkadas, não embutidas
- [ ] Não duplica uma skill existente

Para workflows:
- [ ] Comportamento é determinístico e previsível
- [ ] Tem saída clara e verificável
- [ ] Inclui exemplos de uso
