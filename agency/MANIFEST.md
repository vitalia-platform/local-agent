# Kit de Agentes — MANIFEST

> Coleção portátil de agentes, skills e workflows para projetos de saúde & wellness e além.

**Versão**: 0.3.0  
**Última atualização**: 2026-05-19  
**Compatível com**: Gemini CLI (Antigravity) — e qualquer ferramenta que suporte `.agent/` ou `.gemini/`

---

## 📦 Conteúdo

### Agentes (17)

| # | Categoria | Agente | Arquivo | Trigger Principal |
|---|-----------|--------|---------|-----------------|
| 1 | **Dev** | Conductor | `agents/dev/conductor.md` | full stack, orquestre, multiple domains |
| 2 | **Dev** | Coder | `agents/dev/coder.md` | continue, implemente, próximo passo |
| 3 | **Dev** | Reviewer | `agents/dev/reviewer.md` | revise, code review, checar qualidade |
| 4 | **Dev** | Tester | `agents/dev/tester.md` | testes, TDD, cobertura, pytest |
| 5 | **Dev** | Shipper | `agents/dev/shipper.md` | release, deploy, changelog, publicar |
| 6 | **Science** | Biologist | `agents/science/biologist.md` | fisiologia, anatomia, sistema nervoso |
| 7 | **Science** | Endocrinologist | `agents/science/endocrinologist.md` | hormônio, cortisol, metabolismo |
| 8 | **Science** | Exercise Physiologist | `agents/science/exercise-physiologist.md` | exercício, VO2max, zona de treino, HIIT |
| 9 | **Science** | Longevity Specialist | `agents/science/longevity-specialist.md` | longevidade, aging, epigenética, NAD+ |
| 10 | **Science** | Nutritionist | `agents/science/nutritionist.md` | nutrição, dieta, alérgenos |
| 11 | **Science** | Psychologist | `agents/science/psychologist.md` | ansiedade, comportamento, hábito |
| 12 | **Science** | Research Analyst | `agents/science/research-analyst.md` | analisar artigo, nível de evidência, paper |
| 13 | **Science** | Sleep Specialist | `agents/science/sleep-specialist.md` | sono, REM, insônia, ritmo circadiano |
| 14 | **Science** | Supplement Pharmacologist | `agents/science/supplement-pharmacologist.md` | suplemento, dosagem, interação, creatina |
| 15 | **Meta** | Session Manager | `agents/meta/session-manager.md` | session-start, onde parei, contexto |
| 16 | **Meta** | Knowledge Curator | `agents/meta/knowledge-curator.md` | aprendi, extraia padrão, crie agente |
| 17 | **Meta** | Bootstrapper | `agents/meta/bootstrapper.md` | novo projeto, bootstrap, do zero |

### Skills (13)

| # | Categoria | Skill | Diretório | Trigger |
|---|-----------|-------|-----------|---------|
| 1 | **Core** | Smart Router | `skills/core/smart-router/` | sempre ativo |
| 2 | **Core** | Context Engine | `skills/core/context-engine/` | contexto, sessão, CONTEXT.md |
| 3 | **Core** | Agent Factory | `skills/core/agent-factory/` | criar agente, template |
| 4 | **Dev** | Code Continuation | `skills/dev/code-continuation/` | continuar código, arquivo existente |
| 5 | **Dev** | Pair Programming | `skills/dev/pair-programming/` | pair, trabalhar juntos |
| 6 | **Dev** | ADR Writing | `skills/dev/adr-writing/` | ADR, decisão arquitetural |
| 7 | **Dev** | Git Flow | `skills/dev/git-flow/` | commit, branch, PR, semver |
| 8 | **Science** | Health Domain | `skills/science/health-domain/` | LOINC, ICD-11, dados de saúde |
| 9 | **Science** | Evidence Grading | `skills/science/evidence-grading/` | nível de evidência, RCT, meta-análise |
| 10 | **Science** | Clinical Safety | `skills/science/clinical-safety/` | segurança clínica, limite da IA |
| 11 | **Science** | RAG Protocol | `skills/science/rag-protocol/` | PubMed, base externa, retrieval |
| 12 | **Science** | Data Ingestion | `skills/science/data-ingestion/` | ingestion, run_ingestion, mapear CSV |
| 13 | **Science** | LLM Screener | `skills/science/llm-screener/` | screening, run_fase1, triagem |

### Workflows (9)

| Comando | Arquivo | Função |
|---------|---------|--------|
| `/session-start` | `workflows/session-start.md` | Recupera contexto ao iniciar sessão |
| `/session-end` | `workflows/session-end.md` | Salva contexto ao encerrar sessão |
| `/continue` | `workflows/continue.md` | Retoma código específico com contexto |
| `/pair` | `workflows/pair.md` | Ativa pair programming chunk-a-chunk |
| `/science-review` | `workflows/science-review.md` | Revisão científica de feature de saúde |
| `/adr` | `workflows/adr.md` | Cria Architecture Decision Record |
| `/bootstrap` | `workflows/bootstrap.md` | Inicializa novo projeto completo |
| `/release` | `workflows/release.md` | Prepara e executa release |
| `/integrative-review` | `workflows/integrative-review.md` | Orquestra pipeline de revisão de literatura |

### Rules (6)

| Escopo | Arquivo | Função |
|--------|---------|--------|
| always-on | `rules/always-on/session-context.md` | Verifica CONTEXT.md antes de agir |
| always-on | `rules/always-on/hitl-medical.md` | HITL obrigatório para conteúdo médico |
| always-on | `rules/always-on/smart-routing.md` | Ativa roteamento contextual automático |
| file-triggered | `rules/file-triggered/health-data-guard.md` | Proteção dados saúde (LGPD/HIPAA) |
| file-triggered | `rules/file-triggered/api-safety.md` | Segurança de endpoints |
| file-triggered | `rules/file-triggered/test-required.md` | TDD obrigatório em services |

### Scripts (2)

| Script | Função |
|--------|--------|
| `scripts/install.sh` | Instala kit no projeto via symlinks |
| `scripts/validate-kit.py` | Valida integridade da coleção |

---

## 📊 Estatísticas

| Componente | Quantidade |
|-----------|-----------|
| Agentes | 17 (5 dev + 9 science + 3 meta) |
| Skills | 13 |
| Workflows | 9 |
| Rules | 6 |
| Scripts | 2 |
| **Total** | **47 componentes** |

---

## 🚀 Instalação Rápida

```bash
# Em qualquer projeto:
bash /Ollama/root/projetos/assistidos/kit/scripts/install.sh

# Validar integridade do kit:
python /Ollama/root/projetos/assistidos/kit/scripts/validate-kit.py

# Após instalar, no Antigravity:
/session-start
```

---

## 🗺️ Arquitetura de Roteamento

```
Solicitação do usuário
        ↓
[Tier 0 — GEMINI.md] → regras always-on (HITL, session-context, smart-routing)
        ↓
[Smart Router] → detecta domínio → seleciona agente
        ↓
[Agente especialista] → usa skills relevantes → resposta
```

---

## 🔄 Changelog

### v0.3.0 — 2026-05-19
- ✨ Adicionado suporte ao Pipeline de Revisão Integrativa modular e agnóstico de domínio.
- 📦 Novas Skills científicas registradas: `data-ingestion` e `llm-screener`.
- ⚙️ Novo Workflow registrado: `/integrative-review` orquestrando setups, few-shots e ingestion.
- 🔧 Scripts Python de automação adicionados a `kit/scripts/review_pipeline/` com resolução de conflitos e retry.

### v0.2.0 — 2026-05-11
- ✨ 5 novos agentes science: `exercise-physiologist`, `longevity-specialist`, `research-analyst`, `sleep-specialist`, `supplement-pharmacologist`
- 📝 README.md reescrito para distribuição pública como repositório independente
- 🔧 Estrutura `.github/workflows/validate.yml` para CI
- 📋 MANUAL.md atualizado com catálogo completo (17 agentes)

### v0.1.0 — 2026-04-30
- 🎉 Release inicial
- 12 agentes, 11 skills, 8 workflows, 6 rules
- install.sh e validate-kit.py funcionais
- Integração científica com HITL e RAG protocol

---

## 📄 Licença

MIT — use, modifique e distribua livremente.  
Contribuições bem-vindas via Pull Request.
