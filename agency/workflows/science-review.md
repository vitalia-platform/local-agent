---
description: >
  Coordena revisão científica de features antes de publicar. Identifica o
  domínio científico relevante, aciona o(s) especialista(s) adequado(s) e
  produz um parecer consolidado com constraints para implementação.
---

# /science-review — Revisão Científica de Feature

$ARGUMENTS

---

## Propósito

Antes de publicar qualquer feature que envolva dados ou conteúdo de saúde, um especialista científico valida os claims, ranges e abordagens — e fornece constraints claros para o time de dev.

---

## Comportamento

### Fase 1: Identificação de Domínios

O `conductor` analisa a feature e identifica domínios científicos:

```
Biologia/Fisiologia geral → biologist
Hormônios/Metabolismo → endocrinologist  
Nutrição/Alimentação → nutritionist
Saúde mental/Comportamento → psychologist
Múltiplos domínios → todos relevantes em paralelo
```

### Fase 2: Briefing para Especialistas

```
Para cada especialista acionado:
→ Descrever a feature em linguagem clara
→ Listar os claims ou valores que precisam de validação
→ Indicar o público-alvo (médico / paciente / usuário geral)
→ Indicar se é conteúdo educacional ou recomendação personalizada
```

### Fase 3: Pareceres Individuais

Cada especialista emite seu parecer no formato:
```markdown
## [Especialidade] — Status: ✅ / ⚠️ / 🛑

[Análise dos claims e valores]
[Constraints para implementação]
[Classificação HITL]
```

### Fase 4: Síntese do Conductor

```markdown
## 📋 Parecer Consolidado — [Feature]

### Status Geral: ✅ Aprovado / ⚠️ Aprovado com ajustes / 🛑 Bloqueado

### Por Especialidade
| Especialista | Status | Principal ajuste |
|-------------|--------|-----------------|
| Biologist | ✅ | — |
| Endocrinologist | ⚠️ | Ajustar range de cortisol |

### Constraints para Implementação
[Lista consolidada de todos os constraints recebidos]

### Próximos Passos
- [ ] [ação 1 para o coder]
- [ ] [ação 2]
- [ ] Revisão humana: [sim/não — e por quê]
```

---

## Exemplos de Uso

```
/science-review feature de monitoramento de cortisol
/science-review módulo de plano alimentar personalizado
/science-review conteúdo do artigo sobre sono e hormônios
/science-review calculadora de HOMA-IR
```

---

## Quando Bloquear

A feature é bloqueada (`🛑`) até revisão humana quando:
- Envolve diagnóstico (mesmo que "sugestivo")
- Fornece dosagem de suplemento ou medicamento
- Usa linguagem terapêutica ("trata", "cura", "reverte")
- Acessa dados de menores de 18 sem protocolo específico
- Detecta risco de crise (suicídio, autolesão, etc.)
