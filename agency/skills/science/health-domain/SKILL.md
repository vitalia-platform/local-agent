---
name: health-domain
description: >
  Vocabulário, ontologias e conceitos fundamentais de saúde. Fornece
  terminologia padronizada (ICD-11, SNOMED, LOINC), hierarquias de conceitos
  médicos e contexto clínico para agentes de desenvolvimento.
  Triggers: "terminologia médica", "ICD", "CID", "código de diagnóstico",
  "ontologia de saúde", "vocabulário clínico", "padronizar termos de saúde".
allowed-tools: Read, Grep
---

# Health Domain — Vocabulário e Ontologias de Saúde

> Terminologia padronizada para garantir consistência entre código, conteúdo e comunicação científica.

---

## Sistemas de Classificação Principais

| Sistema | Uso | Versão Atual |
|---------|-----|-------------|
| **ICD-11 / CID-11** | Diagnósticos e condições | ICD-11 (WHO, 2022+) |
| **SNOMED CT** | Terminologia clínica abrangente | Atualização semestral |
| **LOINC** | Exames laboratoriais e observações | v2.76+ |
| **RxNorm** | Medicamentos e substâncias | Mensal |
| **NCI Thesaurus** | Oncologia e pesquisa | |

---

## Áreas de Saúde & Wellness do Projeto

### Biomarcadores Comuns (LOINC + Unidades Padrão)

| Biomarcador | Código LOINC | Unidade SI | Unidade Comum |
|-------------|-------------|-----------|---------------|
| Glicemia | 2339-0 | mmol/L | mg/dL |
| HbA1c | 4548-4 | % ou mmol/mol | % |
| Cortisol sérico | 2143-6 | nmol/L | µg/dL |
| TSH | 3016-3 | mUI/L | mUI/L |
| Frequência cardíaca | 8867-4 | /min | bpm |
| Pressão arterial sistólica | 8480-6 | mmHg | mmHg |
| Saturação O2 | 2708-6 | % | % |

### Conversões de Unidade Frequentes

```python
# Conversões padrão para biomarcadores
def cortisol_ug_to_nmol(ug_per_dl: float) -> float:
    """µg/dL para nmol/L. Fator: x 27.59"""
    return ug_per_dl * 27.59

def glucose_mg_to_mmol(mg_per_dl: float) -> float:
    """mg/dL para mmol/L. Fator: x 0.0555"""
    return mg_per_dl * 0.0555
```

---

## Princípios de Modelagem de Dados de Saúde

### Observação (padrão FHIR-inspired)

```python
class HealthObservation(models.Model):
    """Modelo base para qualquer observação de saúde."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    
    # Identificação padronizada
    loinc_code = models.CharField(max_length=20)   # ex: "2339-0"
    display_name = models.CharField(max_length=200) # ex: "Glicemia"
    
    # Valor
    value_quantity = models.DecimalField(max_digits=10, decimal_places=4)
    unit = models.CharField(max_length=50)           # ex: "mg/dL"
    unit_ucum = models.CharField(max_length=50)      # UCUM: "mg/dL"
    
    # Contexto
    effective_datetime = models.DateTimeField()
    method = models.CharField(max_length=200, blank=True)  # ex: "Capilar"
    
    # Interpretação
    interpretation = models.CharField(
        choices=[("N", "Normal"), ("L", "Baixo"), ("H", "Alto"), ("C", "Crítico")],
        max_length=1, blank=True
    )
    reference_range_low = models.DecimalField(null=True, blank=True, ...)
    reference_range_high = models.DecimalField(null=True, blank=True, ...)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'loinc_code', 'effective_datetime']),
            models.Index(fields=['organization', 'effective_datetime']),
        ]
```

---

## Referências Externas

Para consultas a ontologias completas:
- LOINC Search: https://loinc.org/search/
- ICD-11 Browser: https://icd.who.int/browse11
- SNOMED Browser: https://browser.ihtsdotools.org/
- FHIR R4 Spec: https://hl7.org/fhir/R4/
