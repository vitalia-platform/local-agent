---
name: rule-health-data-guard
description: Proteção de dados de saúde. Aplica LGPD/HIPAA e criptografia obrigatória.
trigger:
  files: ["**/health/**", "**/medical/**", "**/biometric/**", "**/wellness/**", "**/patient/**", "**/user_data/**"]
---

# Regra: Proteção de Dados de Saúde

> Dados de saúde são dados sensíveis por definição. LGPD Art. 11. Tolerância zero para exposição.

## Diretrizes Inegociáveis

### 1. Criptografia de Dados Sensíveis
Campos PII e de saúde DEVEM ser criptografados em repouso:
```python
# Usar biblioteca de criptografia de campo (ex: django-crypto-fields)
from django_crypto_fields.fields import EncryptedTextField

class HealthRecord(models.Model):
    diagnosis = EncryptedTextField()      # ✅ criptografado
    heart_rate = EncryptedIntegerField()  # ✅ criptografado
    notes = EncryptedTextField()          # ✅ criptografado
```

### 2. Acesso Multi-Tenant
TODA query em dados de saúde DEVE incluir filtro por `organization_id` ou `user_id`:
```python
# ✅ CORRETO
records = HealthRecord.objects.filter(
    user_id=request.user.id,
    organization_id=request.user.organization_id
)

# ❌ ERRADO — nunca buscar todos os registros sem filtro
records = HealthRecord.objects.all()
```

### 3. Logs Sanitizados
Logs NUNCA devem conter dados de saúde em texto puro:
```python
# ❌ ERRADO
logger.info(f"User {user.id} has diagnosis: {user.diagnosis}")

# ✅ CORRETO
logger.info(f"Health record accessed for user_id={user.id}, record_id={record.id}")
```

### 4. Retenção e Exclusão
Dados de saúde devem ter política de retenção definida e suporte a exclusão (LGPD Art. 18).
