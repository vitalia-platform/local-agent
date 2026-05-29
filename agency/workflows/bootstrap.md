<!-- .agent/workflows/bootstrap.md | Atualizado em: 21-05-2026 11:31:00(GMT-04:00) -->
---
description: >
  Inicializa um novo projeto do zero com estrutura padronizada, convenções
  e kit de agentes instalado. Pronto para trabalhar na primeira sessão.
---

# /bootstrap — Novo Projeto

$ARGUMENTS

---

## Propósito

Configura um projeto completo em minutos: estrutura, Docker, Git, `.env.example`, kit de agentes e CONTEXT.md — tudo pronto para começar a codar.

---

## Comportamento

### Fase 1: Coleta de Dados

```
"Vou criar o projeto. Responda rapidamente:

1. Nome: (ex: vitalia-api)
2. Tipo: api / web-app / mobile / cli / full-stack
3. Stack: (ex: Django + PostgreSQL / Next.js / React Native + Expo)
4. Envolve dados de saúde? S/N
5. Diretório: (padrão: ./[nome])"
```

### Fase 2: Geração de Estrutura

Com base no tipo, gerar a estrutura de diretórios e arquivos base:
- Diretórios principais
- `.gitignore` completo
- `.env.example` sem valores reais
- `docker-compose.yml` básico
- `Makefile` com comandos dev
- `docs/adr/` para decisões

### Fase 3: Instalação do Kit

```bash
bash [kit-path]/scripts/install.sh [projeto-path]
```

### Fase 4: Git Init + Primeiro Commit

```bash
git init && git add . && git commit -m "chore: bootstrap [nome]"
```

### Fase 5: CONTEXT.md

Criar com dados do briefing. Usuário valida antes de salvar.

### Fase 5.5: Validação de Segurança e .env

Instruir o usuário a:
1. Copiar o `.env.example` para `.env`
2. Executar o script de sanitização: `bash scripts/sanitize_for_cloud.sh`

### Fase 6: Entrega

```markdown
## ✅ Projeto [nome] pronto!

📁 Estrutura criada
🤖 Kit de agentes instalado
🐙 Git inicializado
📋 CONTEXT.md pronto

Próximo passo: /session-start
```

---

## Exemplos

```
/bootstrap
/bootstrap vitalia-api
/bootstrap --tipo=full-stack --stack="Django + Next.js"
```
