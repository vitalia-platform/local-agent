---
name: backend-architecture
description: Skill de Arquitetura de Backend e Banco de Dados consolidando as regras ouro de Data Vault, API-First e Clean Architecture.
---

# Backend Architecture & Data Vault

Esta skill orienta o design e a implementação do backend (focado em Python/Django, Node ou equivalentes) com alta segurança e isolamento de dados de saúde.

## 1. Segurança e Data Vault (Obrigatório)
- **Soberania do Dado (Lei P7)**: O dado pertence ao Paciente/Participante. O acesso da organização é temporário (via `DataAccessGrant`).
- **Isolamento de Tenant**: Em arquiteturas multi-tenant, nenhuma query deve ignorar a validação do tenant atual ou do participante.
- **Gerenciamento Estrito de Segredos (Lei P6)**: Nenhum segredo no Git. `.env` é exclusivo para dev. Em produção, variáveis seguras via injeção.
- **Rastreabilidade (Lei P10)**: Especialmente em integrações com LLM, toda decisão sugerida pela IA deve ser guardada no `AuditLog` para explicabilidade jurídica/médica.

## 2. API-First e Contratos
- **Serializers Dedicados (Lei P13)**: Separe estritamente serializers de Leitura (com dados aninhados para views ricas) dos serializers de Escrita (validação estrita para payload de entrada).
- **Contrato Fonte de Verdade (Lei P12)**: O contrato da API (OpenAPI/Swagger/Serializers) dita as regras. Frontend e Backend não discutem, seguem o contrato.

## 3. Desacoplamento Limpo (Lei P11)
- **Services**: A regra de negócio pura mora aqui. Nenhuma lógica pesada em Views/Controllers.
- **Clients/Adapters**: Toda comunicação externa (Ollama, APIs de terceiros) isolada em clients testáveis.
- **Views/Tasks**: Apenas orquestram a chamada aos Services e Clients e cuidam do Response/Error HTTP.

## 4. Banco de Dados e Migrações
- **Otimização Proativa (Lei P17)**: Anti-N+1 obrigatório. Em ORMs, use joins (`select_related`, `prefetch_related`) em queries relacionais.
- **Migrações Defensivas (Lei P8)**: Alterações no banco não podem ser destrutivas. Migrações de dados sensíveis devem ser isoladas das migrações de schema.

## 5. Integração com Testes
- **O Contrato da Realidade (Lei P14)**: Nenhuma feature backend de saúde está pronta sem testes de unidade e integração (ex: Pytest + FactoryBoy). Mockar chamadas externas de LLM/Ollama nos testes rápidos.
