<!-- .agent/workflows/session-start.md | Atualizado em: 21-05-2026 11:31:00(GMT-04:00) -->
---
description: >
  Inicia sessão de trabalho recuperando contexto completo do projeto. 
  Apresenta estado atual, últimas atividades e próximo passo prioritário.
  Use ao começar qualquer sessão de trabalho.
---

# /session-start — Início de Sessão

$ARGUMENTS

---

## Propósito

Elimina o cold start de cada sessão. Em segundos você sabe exatamente onde o projeto está e o que fazer a seguir.

---

## Comportamento

Quando `/session-start` for acionado:

### Passo 1: Validar Ambiente e Sincronia (Obrigatório)

```
Execute o script de validação para checar integridade e conflitos de contexto:
$ python3 .agent/scripts/validate-kit.py --target .
```

**Se houver conflito de ETag (Remoto mais novo que o local):**
```
Pare imediatamente e oriente o usuário a resolver o conflito:
$ bash .agent/scripts/session-resolve.sh
Aguarde a resolução antes de prosseguir.
```

### Passo 2: Localizar contexto

```
Buscar: <workspace-root>/.agent/session/CONTEXT.md
```

---

#### 🆕 MODO TEMPLATE — Se `.agent/session/CONTEXT.md` NÃO existe

Isso indica um clone fresco do repositório template. Nenhuma revisão foi configurada ainda.
Apresente o seguinte guia de inicialização:

```
════════════════════════════════════════════════
🆕 MODO TEMPLATE — Repositório base detectado
Nenhuma revisão integrativa foi iniciada neste ambiente.
════════════════════════════════════════════════

Siga os 5 passos abaixo para configurar seu ambiente de trabalho:

─────────────────────────────────────────
PASSO 1 — Crie seu repositório de trabalho no GitHub
─────────────────────────────────────────
Crie um novo repositório VAZIO no GitHub (não inicialize com README).
Nome sugerido: revisao-[tema]-[ano]
Exemplo:      revisao-exercicio-digital-2026

─────────────────────────────────────────
PASSO 2 — Aponte este clone para o seu repositório
─────────────────────────────────────────
$ git remote set-url origin git@github.com:SEU_USUARIO/revisao-[tema]-[ano].git
$ git push -u origin main

─────────────────────────────────────────
PASSO 3 — Crie seu repositório de contexto de sessão
─────────────────────────────────────────
O contexto de sessão permite à IA retomar o trabalho entre máquinas e sessões.
É um repositório Git separado que armazena o estado da revisão.

  3a. Crie outro repositório VAZIO no GitHub:
      Nome sugerido: revisao-[tema]-contexto
      Exemplo:       revisao-exercicio-digital-contexto

  3b. Configure o contexto no projeto:
      $ bash kit/scripts/install.sh
      → Quando solicitado, informe a URL SSH do repositório de contexto:
        git@github.com:SEU_USUARIO/revisao-[tema]-contexto.git

  3c. Verifique a instalação:
      $ python3 .agent/scripts/validate-kit.py --target .

─────────────────────────────────────────
PASSO 4 — Prepare os dados de calibração
─────────────────────────────────────────
As pastas de trabalho serão criadas pelo /integrative-review com os nomes
que você definir no painel. Antes de invocá-lo, tenha em mãos:

  • PDFs dos artigos mais relevantes (baixados do portal Scopus)
  • CSV de metadados exportado da Web of Science
  • CSV bruto completo da busca nas bases de dados

─────────────────────────────────────────
PASSO 5 — Inicie a revisão
─────────────────────────────────────────
Com o ambiente configurado, invoque:

  /integrative-review

O workflow abrirá o painel interativo de setup, onde você definirá
o escopo, as pastas de trabalho e a infraestrutura de processamento.
════════════════════════════════════════════════
```

---

#### 📋 MODO TRABALHO — Se `CONTEXT.md` existe

Processar e apresentar resumo baseado também na leitura do `.agent/session/sprint_atual.md` para mapear os checklists em andamento:

```markdown
---

## 📍 [Nome do Projeto] — Sessão Iniciada

**Status**: [status do projeto]
**Branch**: [branch-name]
**Última sessão**: [data] — [X dias/horas atrás]

### 📋 Checklists Atuais (sprint_atual.md)
[Apresentar tarefas não concluídas ou em andamento baseadas no arquivo sprint_atual.md]

### ✅ Concluído recentemente
[lista dos últimos 3-5 itens concluídos]

### 🎯 Próximo passo (P0 — mais prioritário)
**[descrição clara do próximo item com base no sprint]**

### 📌 Outros pendentes
- P1: [item]
- P2: [item]

### ⚠️ Constraints ativos
[lista de regras/restrições em vigor para este projeto]

---
**Deseja continuar com o item P0, ou tem outro foco para hoje?**
```

### Passo 3: Preparar ambiente

Após o usuário confirmar o foco:
- Listar os arquivos principais envolvidos
- Verificar se há especialista científico relevante para o foco de hoje
- Ativar `coder` ou `conductor` conforme o foco

---

## Exemplos de Uso

```
/session-start
/session-start --foco="calibração de critérios PRISMA"
```

---

## Saída Esperada

- **Modo Template**: Guia de 5 passos até `/integrative-review`
- **Modo Trabalho**: Resumo do estado atual + próximo passo prioritário
