---
name: code-continuation
description: >
  Protocolo para retomar código existente com contexto completo e coerência
  arquitetural. Garante que o agente entenda o estado atual antes de escrever
  qualquer linha. Use sempre que implementar features em código já existente.
  Triggers: "continue", "implemente", "adicione", "extenda", referência a arquivo.
allowed-tools: Read, Grep, Glob, Write, Edit
---

# Code Continuation — Retomada de Código com Contexto

> "Nunca escreva uma linha de código sem primeiro entender o que já existe."

---

## Protocolo Obrigatório (antes de qualquer código)

### Passo 1: Leitura de Contexto

```
1. Ler .agent/project/CONTEXT.md
   → Qual feature está em andamento?
   → Quais constraints estão ativos?
   → Qual é o estado atual?

2. Identificar arquivo(s) envolvido(s)
   → Ler o arquivo completo (não apenas trechos)
   → Mapear: imports, dependências, padrões usados

3. Mapear contratos existentes
   → Ler arquivos de teste relacionados (tests.py, *.test.ts, etc.)
   → Entender: o que já está testado? o que é contrato?
```

### Passo 2: Análise de Coerência

Antes de propor qualquer código, verificar:

| Check | Verificação |
|-------|-------------|
| **Padrão arquitetural** | O código segue o padrão do projeto? (ex: service pattern, clean arch) |
| **Naming conventions** | Nomes seguem o padrão existente? |
| **Imports** | Usa as libs já instaladas, não adiciona novas sem motivo |
| **Async/sync** | Consistente com o restante do arquivo |
| **Error handling** | Segue o padrão de erro do projeto |
| **Typing** | Tipagem consistente (TypeScript strict? Python type hints?) |

### Passo 3: Proposta Antes de Escrever

```markdown
## 📋 Plano de Implementação

**Feature**: [nome]
**Arquivos afetados**: [lista]
**Abordagem**: [descrição de 2-3 linhas]
**Dependências novas necessárias**: [nenhuma / ou lista]

**Deseja prosseguir? (S para implementar / N para ajustar plano)**
```

> ⚠️ Aguardar aprovação antes de escrever código em mudanças que afetam 3+ arquivos.

### Passo 4: Implementação Incremental

```
Para cada arquivo a modificar:
1. Mostrar o diff do que será mudado (não o arquivo inteiro)
2. Implementar
3. Verificar se a mudança quebra algum teste existente
4. Sinalizar quando um novo teste é necessário
```

---

## Regras de Qualidade de Código

### Sempre
- ✅ Seguir o padrão arquitetural já estabelecido no projeto
- ✅ Usar as mesmas libs e abstrações já presentes
- ✅ Adicionar tipagem consistente com o restante
- ✅ Sinalizar quando um teste é necessário
- ✅ Manter comentários existentes — nunca apagar sem motivo

### Nunca
- ❌ Instalar nova dependência sem perguntar
- ❌ Mudar padrão arquitetural sem ADR
- ❌ Escrever código síncrono em projeto async (e vice-versa)
- ❌ Usar `any` em TypeScript ou omitir type hints em Python
- ❌ Implementar lógica de negócio em Views/Controllers

---

## Sinais de que é Preciso Parar e Perguntar

| Sinal | Ação |
|-------|------|
| Arquivo não existe (criar do zero) | Verificar estrutura de diretórios + perguntar localização |
| Feature cross-cutting (afeta 5+ arquivos) | Propor plano e aguardar aprovação |
| Necessidade de nova dependência | Justificar alternativa + aguardar aprovação |
| Possível breaking change | Sinalizar e aguardar instrução |
| Conflito com constraint ativo | Sinalizar conflito antes de implementar |

---

## Integração com Domínio Científico

Se o código implementa lógica que envolve dados de saúde:

```
ANTES de implementar:
→ Verificar se existe constraint científico relevante no CONTEXT.md
→ Se não existe: acionar especialista científico via conductor
→ Receber constraints → implementar dentro dos limites validados
```

Exemplo:
```python
# constraint recebido do endocrinologist:
# cortisol sérico normal: 6-23 µg/dL (manhã), 2-11 µg/dL (tarde)
# qualquer valor fora deste range deve acionar alerta, não erro de validação

CORTISOL_RANGES = {
    "morning": {"min": 6, "max": 23, "unit": "µg/dL"},
    "afternoon": {"min": 2, "max": 11, "unit": "µg/dL"},
}
```
