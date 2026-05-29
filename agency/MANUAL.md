# Manual da Agência Vitalia (Agency System)

Bem-vindo ao **Manual do Proprietário** da infraestrutura de inteligência artificial da Vitalia Platform.
Este documento detalha o funcionamento, as ferramentas disponíveis, a governança de contexto e os procedimentos de operação dos agentes que trabalham no projeto.

## 1. Visão Geral do Kit de Agentes

O Kit de Agentes é um ecossistema portátil projetado para atuar como uma "agência de desenvolvimento autônoma" com controle rigoroso. Ele implementa o conceito de **Smart Routing** (Roteamento Inteligente), onde a intenção do desenvolvedor é analisada em tempo real para ativar o especialista (agente) mais adequado para a tarefa solicitada.

### Os 4 Pilares da Agência
1. **Agentes:** As personas (ex: Coder, Biólogo, Arquiteto) que ditam o *comportamento* da IA.
2. **Workflows:** Os roteiros passo a passo (acionados via `/comando`) para processos padronizados.
3. **Regras:** Diretrizes de segurança que podem ser ativas permanentemente (*Always-on*) ou engatilhadas por arquivos específicos (*File-triggered*).
4. **Skills:** Habilidades técnicas detalhadas de desenvolvimento ou ciência que o agente consulta antes de implementar (ex: melhores práticas do Next.js, validação de evidência clínica).

---

## 2. Setup Inicial e Importação de Nuvem

### Instalação Básica
Para ativar a agência em um ambiente novo, execute o instalador na raiz do projeto:
```bash
bash kit/scripts/install.sh
```
Isso criará a pasta `.agent/` (que estará no `.gitignore`) e preparará os *symlinks* do kit.

### Importando Contexto da Nuvem
Se você já possui um repositório de contexto salvo na nuvem e quer trazê-lo para a sua máquina atual, siga estes passos:

1. **Acesse o repositório isolado de sessão:**
   ```bash
   cd .agent/session
   ```
2. **Adicione o seu repositório remoto:**
   ```bash
   git remote add origin <URL_DO_SEU_REPO_DE_CONTEXTO>
   ```
3. **Baixe o histórico:**
   ```bash
   git fetch origin
   ```
4. **Substitua o estado local pelo da nuvem (Recomendado):**
   ```bash
   git reset --hard origin/main
   ```
   *(Nota: Se houver contexto local valioso, use `git pull origin main --allow-unrelated-histories`)*
5. **Atualize o Guardião de Sincronia:**
   ```bash
   cd ../..
   python3 .agent/scripts/lib_sync_guard.py --action update --session-dir .agent/session
   ```
Após estes passos, basta rodar `/session-start` no seu chat para que a IA leia tudo o que foi importado.

---

## 3. Catálogo Completo da Agência

### 🤖 Agentes (`kit/agents/`)
Os agentes estão divididos em três camadas de atuação:

- **Desenvolvimento (Dev):**
  - `coder`: Focado em implementação de código limpo e resolução de bugs.
  - `conductor`: O maestro full-stack; orquestra tarefas complexas entre frontend e backend.
  - `reviewer`: Especialista em revisão de código, focado em segurança e padrões.
  - `shipper`: Especialista em deploy, integrações contínuas e infraestrutura.
  - `tester`: Arquiteto de qualidade; focado em Test-Driven Development (TDD) e automação.

- **Ciência e Saúde (Science):**
  - `biologist`: Análise de interações biológicas e fisiologia estrutural.
  - `endocrinologist`: Especialista em hormônios, marcadores e protocolos clínicos complexos.
  - `exercise-physiologist`: Fisiologia do exercício, prescrição de treino, zonas de FC, VO₂max e recuperação.
  - `longevity-specialist`: Medicina de longevidade, aging, epigenética e protocolos anti-aging — diferencial competitivo da Vitalia.
  - `nutritionist`: Focado em segurança alimentar (alérgenos) e prescrição nutricional baseada em evidência.
  - `psychologist`: Especialista em neurociência do comportamento e mudança de hábitos (eixos de bem-estar).
  - `research-analyst`: Análise de literatura científica e trabalho em par com todos os agentes — o elo entre ciência e engenharia.
  - `sleep-specialist`: Medicina do sono, cronobiologia aplicada, métricas de wearables e recovery.
  - `supplement-pharmacologist`: Suplementação baseada em evidências, interações e dosagens seguras (alto risco HITL).

- **Meta (Gerenciamento do Kit):**
  - `bootstrapper`: Inicializa e configura projetos novos do zero.
  - `knowledge-curator`: Garante que aprendizados da sessão virem "regras" ou "skills" reaproveitáveis.
  - `session-manager`: Responsável exclusivo por manter e proteger o estado do projeto.

### ⚡ Workflows (`kit/workflows/`)
Os workflows são acionados via chat (Slash Commands):
- `/session-start`: Lê o repositório, identifica onde o trabalho parou e prepara a IA para a sessão.
- `/session-end`: Faz o resumo do dia, salva no contexto e roda o script de sincronia.
- `/pair`: Ativa o Pair Programming (a IA sugere, o humano revisa e aprova, passo a passo).
- `/continue`: Retoma uma tarefa inacabada de forma cirúrgica (lê o código atual antes de modificar).
- `/science-review`: Paralisa a implementação técnica e aciona a camada `Science` para verificar uma regra clínica (HITL).
- `/release`: Processo padrão de documentação de changelog e empacotamento antes de deploy.
- `/adr`: Cria de forma interativa um *Architecture Decision Record*.
- `/bootstrap`: Inicia um projeto do zero a partir dos templates da Vitalia.

### 📜 Regras Ouro (`kit/rules/`)
As regras definem restrições intransponíveis:
- **Always-on:** `hitl-medical` (Humano no loop para qualquer dado clínico), `session-context` (obriga a leitura de contexto ao iniciar), `smart-routing` (roteamento ativo constante), `architect-constitution` (P21 regras base da Vitalia).
- **File-triggered:** `health-data-guard` (acionada ao mexer em PII ou dados de saúde), `api-safety` (acionada ao expor endpoints), `test-required` (bloqueio de commit de core/services sem testes atrelados).

### 🧠 Skills (`kit/skills/`)
As skills ensinam à IA *como pensar*, não apenas *como codar*. Estão agrupadas em:
- **Dev:** Melhores práticas de Node, React, Rust, Python, Bash, Tailwind, Git Flow e Banco de Dados (modelagem e índices).
- **Core:** Habilidades arquiteturais (MCP Builder, Context Engine, Agent Factory, etc).
- **Science:** Protocolos RAG em bases médicas (PubMed), hierarquia de evidência científica, e segurança clínica.

---

## 4. Gestão de Contexto e Concorrência

A infraestrutura foi projetada com um **Controle Otimista de Concorrência (ETags)**. Isso permite trabalhar na mesma plataforma usando IA em múltiplos computadores (ex: Notebook, Desktop) sem sobrescrever o racicionado da máquina anterior.

### O Modelo *Nested Git*
A memória da IA não polui o seu código principal. Durante o `install.sh`, o diretório oculto `.agent/session/` é criado e transformado em um **repositório Git independente**.

### O Guardião de Sincronia (`lib_sync_guard.py`)
Para evitar conflitos de merge silenciosos no contexto de IA, usamos uma trava (`.sync_lock`).
1. **Ao Iniciar:** O Guardião lê o ETag remoto. Se houver divergência, ele bloqueia o trabalho e exige sincronização. Se estiver tudo OK, ele salva o timestamp atual no `.sync_lock`.
2. **Ao Encerrar:** O Guardião verifica: *"O timestamp na nuvem hoje é igual ao timestamp do `.sync_lock` desta máquina?"*
3. **Se Sim:** O Push é feito com sucesso via `session-sync.sh`.
4. **Se Não:** Outra máquina empurrou dados de contexto antes de você. A sincronização aborta.

---

## 5. Troubleshooting e Comandos de Operação

Sempre execute os scripts de manutenção a partir da raiz do repositório principal do seu projeto (`vitalia-platform`).

| Comando / Script | Propósito |
| :--- | :--- |
| `bash kit/scripts/install.sh` | Restaura *symlinks* do kit e inicializa o repositório de sessão. |
| `python3 .agent/scripts/validate-kit.py --target .` | Faz auditoria para verificar se algum symlink do kit quebrou e se o ETag está válido. |
| `bash .agent/scripts/session-sync.sh` | O script que faz commit das mudanças na pasta `.agent/session` e sobe para a nuvem. Usado pelo `/session-end`. |
| `bash .agent/scripts/session-resolve.sh` | **A Ferramenta de Emergência.** Usada quando a IA avisa que houve um *Erro de Concorrência*. Ele te guiará para baixar do remoto ou forçar o push local. |

---
**Vitalia Platform** - *Tecnologia a serviço da vida.*
