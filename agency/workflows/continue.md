---
description: >
  Retoma implementação de uma feature ou arquivo específico com contexto completo.
  Lê o código existente, entende o estado atual e propõe o próximo passo antes
  de escrever qualquer linha. Use para continuar código entre sessões.
---

# /continue — Retomada de Código

$ARGUMENTS

---

## Propósito

Continua a implementação de onde você parou — com contexto completo, sem inconsistências e sem perguntas desnecessárias.

---

## Comportamento

Quando `/continue [feature ou arquivo]` for acionado:

### Fase 1: Reconhecimento (silencioso)

```
1. Ler CONTEXT.md → estado atual + constraints
2. Identificar arquivo(s) relevante(s):
   → Se mencionado explicitamente: ler esse arquivo
   → Se não mencionado: ler o arquivo da "feature em andamento" no CONTEXT.md
3. Ler testes relacionados (se existirem)
4. Verificar se o domínio envolve dados de saúde
   → Se sim: verificar constraints científicos antes de propor
```

### Fase 2: Diagnóstico

```markdown
## 🔍 Estado Atual — [feature/arquivo]

**O que existe**: [descrição do código atual]
**O que foi feito até aqui**: [baseado no CONTEXT.md]
**O que falta**: [gap entre atual e objetivo]
**Constraints ativos**: [lista relevante]
```

### Fase 3: Proposta

```markdown
## 📋 Próximo passo

**Implementar**: [descrição clara e específica]
**Arquivos**: [lista]
**Estratégia**: [abordagem em 2-3 linhas]

Posso prosseguir? (S / N / ajustar)
```

### Fase 4: Implementação incremental

- Implementar em chunks lógicos
- Sinalizar quando teste é necessário
- Reportar o que foi feito após cada chunk
- Sugerir próximo chunk

### Fase 5: Atualização de contexto

```
Após implementar:
→ Perguntar se quer atualizar CONTEXT.md com o progresso
→ Sugerir o próximo item na fila
```

---

## Exemplos de Uso

```
/continue
/continue endpoint de biometria
/continue backend/core/services/biometric_service.py
/continue feature de plano de saúde personalizado
```

---

## Casos Especiais

| Situação | Comportamento |
|----------|--------------|
| Feature envolve dados de saúde sem constraint | Acionar especialista científico antes de implementar |
| Feature afeta 5+ arquivos | Propor plano completo e aguardar aprovação |
| Código existente tem padrão diferente do kit | Seguir padrão do projeto, não do kit |
| Bug em vez de feature | Aplicar protocolo de debug: hipótese → reproduce → fix → test |
| Contexto ambíguo | Fazer 1-2 perguntas de clarificação antes de propor |
