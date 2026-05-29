---
name: rule-test-required
description: Testes obrigatórios para services e lógica de negócio. TDD first.
trigger:
  files: ["**/services/**", "**/core/**", "**/domain/**", "**/use_cases/**", "**/usecases/**"]
---

# Regra: Testes Obrigatórios

> "Se não testa, não existe em produção."

## Princípio

Qualquer código em `services/`, `core/`, `domain/` ou `use_cases/` DEVE ter teste correspondente.

## Protocolo do `coder`

Ao criar ou modificar um service:

```
1. Escrever o teste ANTES ou JUNTO com o código (nunca depois)
2. Ao concluir a implementação, perguntar:
   "✅ Implementação concluída. Quer que eu escreva os testes agora?"
3. Se o usuário dizer sim: escrever testes de:
   - Caso de sucesso (happy path)
   - Caso de erro (exceções esperadas)
   - Edge cases (valores limites, nulls, etc.)
```

## Estrutura de Teste Padrão

```python
# tests/test_biometric_service.py
import pytest
from unittest.mock import AsyncMock, patch

class TestBiometricService:
    """Testes para BiometricService."""

    @pytest.mark.asyncio
    async def test_get_for_user_returns_correct_data(self, db, user_factory):
        """Happy path: retorna dados filtrados por user_id."""
        user = await user_factory()
        # ... arrange, act, assert

    @pytest.mark.asyncio
    async def test_get_for_user_raises_for_wrong_organization(self, db):
        """Security: não retorna dados de outra organization."""
        # ... arrange, act, assert

    @pytest.mark.asyncio
    async def test_get_for_user_handles_empty_result(self, db, user_factory):
        """Edge case: retorna lista vazia, não erro."""
        # ... arrange, act, assert
```

## Cobertura Mínima

| Tipo de código | Cobertura mínima |
|----------------|-----------------|
| Services (lógica de negócio) | 90% |
| Views/Controllers | 70% |
| Utilities/helpers | 80% |
| Models (apenas métodos customizados) | 85% |
