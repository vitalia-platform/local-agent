---
description: >
  Prepara e executa o processo de release: checklist de qualidade, changelog,
  versionamento SemVer e tag Git. Use antes de publicar qualquer versão.
---

# /release — Preparar Release

$ARGUMENTS

---

## Propósito

Garante que nada vai para produção sem passar por checklist de qualidade, changelog atualizado e versionamento correto.

---

## Comportamento

### Fase 1: Determinar Versão

```
"Qual é o tipo de release?
- patch  → bug fixes (0.0.X)
- minor  → nova feature (0.X.0)
- major  → breaking change (X.0.0)

Versão atual: [lida do package.json, pyproject.toml ou MANIFEST.md]
Nova versão será: [calculada]"
```

### Fase 2: Checklist de Qualidade

```markdown
## 🔍 Checklist Pré-Release v[X.Y.Z]

- [ ] Testes passando: `pytest` / `npm test`
- [ ] Lint limpo: `ruff check .` / `npm run lint`
- [ ] Build sem erros: `npm run build` / `python -m py_compile`
- [ ] Sem secrets no código
- [ ] Migrations aplicadas (se Django)
- [ ] CONTEXT.md atualizado
```

> Bloqueia se qualquer item crítico falhar.

### Fase 3: Changelog

Analisar commits desde a última tag e gerar:

```markdown
## [X.Y.Z] — YYYY-MM-DD

### ✨ Features
[commits feat:]

### 🐛 Bug Fixes
[commits fix:]

### 🔒 Security
[commits security:]

### ♻️ Refactors
[commits refactor:]
```

### Fase 4: Tag e Push

```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z: [descrição resumida]"
git push origin main --tags
```

### Fase 5: Confirmação

```markdown
## ✅ Release vX.Y.Z Publicado

**Tag**: vX.Y.Z
**Changelog**: CHANGELOG.md atualizado
**Commit**: [hash]

Próximos passos:
- Deploy para staging para smoke test
- Comunicar equipe sobre o release
```

---

## Exemplos

```
/release
/release patch
/release minor
/release major --notes="Migração para Django 5"
```

---

## Release do Kit (pacote GitHub)

Quando usado no próprio kit:
```bash
# Valida integridade antes de publicar
python scripts/validate-kit.py
# Atualiza MANIFEST.md com nova versão
# Cria tag e push
```
