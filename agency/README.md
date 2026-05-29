<!-- kit/README.md | Atualizado em: 21-05-2026 12:12:00(GMT-04:00) -->
# Vitalia Agent Kit


> **Uma agência de IA portátil para plataformas de saúde & wellness.**  
> Agentes especialistas que trabalham em equipe — desenvolvem código, revisam ciência, gerenciam contexto e se expandem conforme o projeto cresce.

---

## O que é

O Vitalia Agent Kit é uma coleção de agentes de IA, skills e workflows projetada para ser instalada em qualquer projeto via **git submodule**. Ele implementa **Smart Routing** automático: a intenção do desenvolvedor é analisada em tempo real para acionar o especialista certo — sem nomeação explícita.

**Projetado para:**
- Plataformas de saúde, wellness & longevidade
- Times que combinam engenharia de software e expertise científica
- Qualquer projeto que exija rigor clínico + velocidade de desenvolvimento

---

## Instalação

### Pré-requisito
O kit é compatível com o **Antigravity (Gemini CLI)**. Qualquer ferramenta que suporte arquivos `.agent/` pode ser adaptada.

### Passo 1 — Adicionar como submódulo

```bash
# Na raiz do seu projeto:
git submodule add https://github.com/vitalia-platform/vitalia-agent-kit.git kit
git submodule update --init --recursive
```

### Passo 2 — Instalar (criar symlinks e repositório de sessão)

```bash
bash kit/scripts/install.sh
```

Este script cria o diretório `.agent/` com symlinks para o kit e inicializa o repositório isolado de contexto de sessão.

### Passo 3 — Ativar

Abra o projeto no Antigravity e execute:
```
/session-start
```

### Atualizar o kit

```bash
git submodule update --remote kit
```

---

## Estrutura

```
kit/
├── agents/               # Especialistas por domínio
│   ├── dev/              # Time de desenvolvimento (5 agentes)
│   ├── science/          # Especialistas científicos (9 agentes)
│   └── meta/             # Agentes de meta-trabalho (3 agentes)
├── skills/               # Conhecimento modular reutilizável
│   ├── core/             # Arquitetura, roteamento, contexto
│   ├── dev/              # Padrões de código e engenharia
│   └── science/          # Protocolos clínicos e evidência
├── workflows/            # Slash commands (/session-start, /pair, etc.)
├── rules/                # Regras automáticas (always-on e file-triggered)
├── scripts/              # install.sh, validate-kit.py
└── templates/            # Templates de projeto
```

---

## Agentes disponíveis (17)

### 🛠️ Dev (5)
| Agente | Especialidade |
|--------|--------------|
| `conductor` | Orquestração full-stack e tarefas multi-domínio |
| `coder` | Implementação limpa e resolução de bugs |
| `reviewer` | Code review com foco em segurança e padrões |
| `tester` | TDD, automação e cobertura de testes |
| `shipper` | Deploy, CI/CD e release management |

### 🔬 Science (9)
| Agente | Especialidade |
|--------|--------------|
| `biologist` | Fisiologia, anatomia, imunologia e cronobiologia |
| `endocrinologist` | Hormônios, metabolismo e biomarcadores endócrinos |
| `exercise-physiologist` | Prescrição de exercício, VO₂max e zonas de treino |
| `longevity-specialist` | Aging, epigenética e protocolos de longevidade |
| `nutritionist` | Nutrição baseada em evidência e segurança alimentar |
| `psychologist` | Neurociência comportamental e mudança de hábitos |
| `research-analyst` | Análise de literatura e parceiro de pair science/dev |
| `sleep-specialist` | Medicina do sono e cronobiologia aplicada |
| `supplement-pharmacologist` | Suplementação, dosagens e interações (HITL crítico) |

### ⚙️ Meta (3)
| Agente | Especialidade |
|--------|--------------|
| `bootstrapper` | Inicializa projetos do zero com estrutura padronizada |
| `knowledge-curator` | Extrai aprendizados e cria novos componentes |
| `session-manager` | Mantém e protege o estado do projeto entre sessões |

---

## Workflows e Comandos da Barra `/`

O kit expõe comandos interativos através da pasta `workflows/` (mapeada em `.agent/workflows/`). Eles podem ser acionados diretamente na barra `/` do chat do Antigravity.

| Comando | Tipo | Quando usar |
|---------|------|-------------|
| `/session-start` | Core | Ao iniciar a sessão de trabalho — recupera o contexto imutável e resume checklists. |
| `/session-end` | Core | Ao encerrar — consolida e documenta o progresso, salvando no histórico imutável. |
| `/continue [feature]` | Dev | Retoma código em andamento carregando o contexto cirúrgico de um arquivo. |
| `/pair [objetivo]` | Dev | Programa par a par (chunk-a-chunk) com revisões e aprovações humanas. |
| `/debug [erro/arquivo]` | Dev | **[Novo]** Inicia o fluxo sistemático de depuração (4 fases e os 5 Porquês). |
| `/review [arquivo]` | Dev | **[Novo]** Audita a qualidade/segurança contra as 21 regras da Constituição. |
| `/test [caminho/lógica]` | Dev | **[Novo]** Conduz o desenvolvimento guiado por testes (Red-Green-Refactor) em TDD. |
| `/screener [lote/id]` | Science | **[Novo]** Realiza triagem científica e elegibilidade estruturada com auditoria forense. |
| `/resolve-ids [query/doi]` | Science | **[Novo]** Busca e resolve metadados científicos (DOIs, PMIDs, OpenAccess) contra APIs. |
| `/science-review [feat]`| Science | Executa revisão científica estrita com o time acadêmico antes do deploy. |
| `/adr` | Meta | Registra decisões arquiteturais (ADR) de forma interativa. |
| `/bootstrap` | Meta | Inicializa um novo projeto a partir dos templates oficiais da Vitalia. |
| `/release` | Meta | Consolida changelog, aplica versionamento SemVer e cria tags de release. |

---

## 📖 Manual de Uso do Vitalia Agent Kit

Este guia prático ensina como tirar o máximo proveito da inteligência portátil do Kit no seu dia a dia de trabalho.

### 1. O Modo de Execução Dinâmico (Pair vs Autônomo)

Todos os comandos de engenharia e ciência (`/debug`, `/review`, `/test`, `/screener`, `/resolve-ids`) suportam dois modos de operação fundamentais:

*   **Modo Pair Programming (Padrão de Fábrica):**
    *   *Como acionar:* Chame o comando normalmente (Ex: `/review scripts/core/config_manager.py`).
    *   *Comportamento:* O agente agirá como um companheiro de equipe socrático. Ele dividirá a tarefa em pequenas partes, apresentará o raciocínio clínico/técnico e **aguardará sua aprovação explícita** antes de aplicar qualquer alteração física em seus arquivos.
*   **Modo Autônomo (Overnight):**
    *   *Como acionar:* Adicione as flags `--autonomous` ou `--auto` no seu comando (Ex: `/debug erro de timeout --auto`).
    *   *Comportamento:* O agente executará o ciclo completo de forma independente. Ele investigará arquivos, corrigirá lógicas, executará testes e gerará apenas o relatório final de sucesso ou falha, maximizando a velocidade.

---

### 2. Guia de Operação dos Novos Comandos

#### 🛠️ Resolvendo Bugs de Forma Científica com `/debug`
Esqueça a tentativa e erro. O comando `/debug` força o agente a executar uma investigação forense:
1.  **Reprodução:** Ele analisa logs, simula inputs e garante que o erro foi isolado.
2.  **Os 5 Porquês:** O agente formula uma cadeia de 5 perguntas e respostas para expor a causa raiz real do bug (ex: timeout ocorre porque a VRAM não foi liberada pelo modelo anterior).
3.  **Correção e Validação:** Ele propõe o patch mínimo necessário e só conclui o fluxo se validar que a regressão foi sanada.

#### 🕵️ Auditando Código e Segurança com `/review`
Antes de commitar, use o `/review` no seu arquivo. O agente fará uma análise lógica profunda contra a **Constituição do Arquiteto (P1 a P21)**:
*   Ele verificará se você expôs IPs locais (como `192.168.x.x`) ou credenciais e alertará para mover para o `.env`.
*   Validará a formatação do cabeçalho de auditoria (`DD-MM-YYYY HH:MM:SS(GMT-04:00)`) e do caminho relativo do arquivo.
*   Retornará um relatório formatado em tabela Markdown com o status de conformidade das diretrizes e o código corrigido.

#### 🧪 Construindo com Segurança Acadêmica usando `/test`
Invoque `/test` descrevendo a lógica que você deseja implementar. O agente instanciará o ciclo clássico de TDD:
*   **Red:** Ele escreve uma suíte de testes robusta na pasta correspondente que simula todos os casos de borda e falha.
*   **Green:** Implementa a lógica mínima exata para fazer os testes passarem.
*   **Refactor:** Limpa e embeleza a estrutura garantindo que a cobertura permaneça verde.

#### 🔬 Processando a Literatura com `/screener` e `/resolve-ids`
Estes comandos acionam os especialistas médicos da Vitalia para acelerar pesquisas científicas:
*   Use `/resolve-ids` passando um DOI ou título parcial de artigo para buscar a ficha de indexação limpa, cruzar dados e baixar automaticamente a cópia open access em PDF.
*   Use `/screener` para aplicar os critérios de inclusão/exclusão da sua Revisão Sistemática/Integrativa de forma irrefutável, gerando os shards de auditoria metodológica JSON essenciais para aprovação em periódicos.

---

### 3. Solução de Problemas (Troubleshooting)

*   **O autocomplete da barra `/` não exibe os novos comandos:**
    Execute `bash kit/scripts/install.sh`. Isso recriará os symlinks no diretório oculto `.agent/` e forçará a IDE a limpar o cache de comandos.
*   **Erro na saúde do contexto de sessão (Validação de ETag):**
    O validador acusará erro se o seu histórico de contexto estiver dessincronizado de outras máquinas. Para resolver, execute:
    ```bash
    bash kit/scripts/session-resolve.sh
    ```
*   **Erros de integridade no Kit:**
    A qualquer momento, você pode auditar a saúde de toda a infraestrutura rodando:
    ```bash
    python3 kit/scripts/validate-kit.py
    ```

---

## Segurança & HITL

O kit implementa **Human-in-the-Loop (HITL)** obrigatório para conteúdo clínico:

```
IA gera → DRAFT
Especialista científico revisa → REVIEW
Profissional de saúde humano aprova → ACTIVE (pode ir para produção)
```

Regras always-on: `hitl-medical`, `session-context`, `smart-routing`.

---

## Gestão de Contexto entre Sessões

O kit usa um modelo **Nested Git** para persistir contexto sem poluir o repositório principal:

- `.agent/session/` é um repositório Git **independente** (gitignored no projeto)
- Contexto pode ser sincronizado com qualquer repositório remoto privado
- Controle otimista de concorrência via ETags para uso em múltiplas máquinas

---

## Changelog

### v0.3.0 — 2026-05-21
- ✨ **5 novos workflows acionáveis na barra `/`**: `/debug`, `/review`, `/test`, `/screener`, `/resolve-ids`.
- ⚙️ **Modo de Execução Dinâmico**: Suporte nativo ao modo Pair (padrão socrático interativo) e modo Autônomo (`--auto`).
- 📝 **Manual de Uso Completo** injetado diretamente no README.md.
- 🕒 **Selo de Tempo e Carimbo do Fuso Horário** (`America/Cuiaba` / `GMT-04:00`) padronizado em todas as ferramentas do kit de acordo com a regra P4.

### v0.2.0 — 2026-05-11
- ✨ 5 novos agentes science: `exercise-physiologist`, `longevity-specialist`, `research-analyst`, `sleep-specialist`, `supplement-pharmacologist`
- 📝 MANUAL.md atualizado com catálogo completo
- 🔄 Estrutura preparada para distribuição como repositório independente

### v0.1.0 — 2026-04-30
- 🎉 Release inicial
- 12 agentes, 11 skills, 8 workflows, 6 rules
- `install.sh` e `validate-kit.py` funcionais
- Integração científica com HITL e RAG protocol

---

## Licença

MIT — use, modifique e distribua livremente.  
Contribuições bem-vindas via Pull Request.

