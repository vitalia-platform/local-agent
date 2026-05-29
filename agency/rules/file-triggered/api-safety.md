---
name: rule-api-safety
description: Segurança obrigatória em rotas de API. Autenticação, rate limiting e validação de input.
trigger:
  files: ["**/api/**", "**/routes/**", "**/views.py", "**/controllers/**", "**/endpoints/**"]
---

# Regra: Segurança de API

## Checklist Obrigatório para Toda Rota/Endpoint

Antes de finalizar qualquer endpoint, verificar:

- [ ] **Autenticação**: Rota protegida por `@login_required`, JWT ou similar?
- [ ] **Autorização**: Usuário tem permissão para o recurso específico (não apenas estar logado)?
- [ ] **Rate Limiting**: Rota sensível tem limite de requisições?
- [ ] **Validação de Input**: Serializer/schema valida todos os campos antes de processar?
- [ ] **Multi-Tenancy**: Query filtra por `organization_id` quando aplicável?
- [ ] **Dados de saúde**: Se retorna dados sensíveis, aplica health-data-guard?

## Padrões Obrigatórios

```python
# ✅ View com todos os requisitos
class BiometricDataView(APIView):
    permission_classes = [IsAuthenticated, HasOrganizationAccess]
    throttle_classes = [UserRateThrottle]

    async def get(self, request):
        serializer = BiometricQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        # Multi-tenancy filtrado
        data = await BiometricService.get_for_user(
            user_id=request.user.id,
            organization_id=request.user.organization_id,
            **serializer.validated_data
        )
        return Response(data)
```

## Erros Que Nunca Devem Vazar

```python
# ❌ NUNCA expor stack trace ou detalhes internos
return Response({"error": str(exception)}, status=500)

# ✅ Log interno + resposta genérica ao cliente
logger.exception(f"Unexpected error in BiometricDataView: {exception}")
return Response({"error": "Internal server error"}, status=500)
```
