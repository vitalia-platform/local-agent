---
name: git-flow
description: >
  Convenções de Git: Conventional Commits, branching strategy, PR templates
  e changelog automático. Use ao fazer commits, criar branches, abrir PRs
  ou preparar releases. Triggers: "commit", "mensagem de commit", "branch",
  "PR", "pull request", "changelog", "tag", "semver", "conventional commits".
allowed-tools: Read, Bash
---

# Git Flow — Convenções de Git

> "Um histórico de commits bem escrito é documentação gratuita."

---

## Conventional Commits

Formato obrigatório: `tipo(escopo): descrição`

| Tipo | Quando usar | Bump SemVer |
|------|------------|-------------|
| `feat` | Nova funcionalidade | MINOR |
| `fix` | Correção de bug | PATCH |
| `security` | Correção de segurança | PATCH urgente |
| `docs` | Documentação | — |
| `refactor` | Refatoração sem mudança de comportamento | — |
| `test` | Adição/correção de testes | — |
| `chore` | Manutenção, deps, CI | — |
| `perf` | Melhoria de performance | PATCH |
| `BREAKING CHANGE` | Mudança incompatível (no footer) | MAJOR |

**Exemplos:**
```
feat(biometrics): adicionar monitoramento de cortisol com alertas críticos
fix(auth): corrigir expiração de refresh token em timezone UTC
security: atualizar django 5.0.3→5.0.4 (CVE-2024-1234)
docs(api): documentar endpoint de biometria com exemplos OpenAPI
refactor(services): extrair lógica de cálculo HOMA-IR para BiometricCalculator
BREAKING CHANGE: endpoint /api/biometrics/ agora requer organization_id no header
```

---

## Branching Strategy

```
main              ← produção, sempre estável
  └── develop     ← integração (se time grande) ou diretamente main (solo/small)
        ├── feat/biometric-monitoring   ← feature branch
        ├── fix/cortisol-range-alert    ← bug fix
        ├── security/token-rotation     ← security fix
        └── chore/update-dependencies   ← manutenção
```

**Nomenclatura de branches:**
```bash
feat/nome-da-feature-em-kebab
fix/descricao-do-bug
security/descricao-da-vulnerabilidade
chore/o-que-esta-sendo-mantido
release/v1.2.0
```

---

## Template de Commit para o Agente

Ao fazer commit, usar sempre:
```bash
git add [arquivos específicos]  # nunca git add .
git commit -m "tipo(escopo): descrição

[corpo opcional — o que e por quê, não como]

[footer: BREAKING CHANGE, closes #issue]"
```

---

## PR Template

Salvar em: `.github/pull_request_template.md`

```markdown
## O que esta PR faz
[Descrição clara e objetiva]

## Tipo de mudança
- [ ] feat: nova funcionalidade
- [ ] fix: correção de bug
- [ ] security: correção de segurança
- [ ] refactor: sem mudança de comportamento
- [ ] BREAKING CHANGE

## Checklist
- [ ] Testes passando localmente
- [ ] Sem secrets no código
- [ ] Multi-tenancy: filtros por organization_id presentes
- [ ] Constraints científicos respeitados (se aplicável)
- [ ] CONTEXT.md atualizado
- [ ] ADR criado se decisão arquitetural foi tomada

## Validação Científica (se aplicável)
- [ ] Ranges de biomarcadores validados por especialista
- [ ] Disclaimer HITL presente onde necessário
```
