<!-- kit/rules/always-on/architect-constitution.md | Atualizado em: 21-05-2026 11:31:00(GMT-04:00) -->
## Constituição do Arquiteto (Princípios de Desenvolvimento)

Estas são as **21 diretrizes invioláveis** que governam todo o desenvolvimento, garantindo que a Vitalia seja segura, escalável e auditável.

### I. Metodologia e Governança
-   **(P1) Decomposição Atômica:** Transformar épicos em tarefas granulares, sequenciais e testáveis. Nunca commitar código que quebre o build.
-   **(P2) Análise de Impacto Holística (A Lei Zero):** Antes de escrever uma linha de código, validar o impacto em: **Multi-Tenancy** (Isolamento), **RBAC** (Permissões), **LGPD** (Privacidade), **Performance** e **Segurança**.
-   **(P3) Documentação Como Artefato de Entrega:** O código não está pronto se o `README.md` e o `.env.example` não refletirem as mudanças. A documentação é viva e contínua.
-   **(P4) Carimbo de Tempo e Auditoria Absoluta:** O selo de data e hora no formato `DD-MM-YYYY HH:MM:SS(GMT-04:00)` deve ser aplicado OBRIGATORIAMENTE a toda e qualquer alteração realizada em qualquer arquivo do projeto, sem exceções. O selo `(GMT-04:00)` é mandatório para alinhar ao fuso horário do usuário (America/Cuiaba). No caso de arquivos de código, a alteração deve incluir também um comentário (geralmente no topo) contendo o caminho relativo do arquivo e o selo de data e hora atualizado.
-   **(P4.1) Regra de ordem de histórico:** Todos os arquivos de histórico, logs de sessão e arquivos de auditoria legíveis por humanos devem manter a entrada mais recente no topo do arquivo (ordem decrescente por data), com o registro mais antigo no final do arquivo. Implementações que gravem mensagens deverão preferencialmente preparar o conteúdo novo e gravá-lo no início do arquivo para garantir leitura rápida das informações mais recentes.
-   **(P5) Entrega de Código Completo:** Ao modificar arquivos, entregar o conteúdo completo para substituição, garantindo integridade e evitando erros de "colagem".
-   **(P6) Automação como Guardiã:** Utilizar scripts (`.sh`) para tarefas repetitivas (backup, restore, setup). Se o processo é manual, ele é falho.

### II. Segurança e Dados (Data Vault)
-   **(P6) Gerenciamento Estrito de Segredos:** Segredos nunca entram no Git. `.env` é exclusivo para desenvolvimento local; Produção usa injeção de variáveis seguras.
-   **(P7) Soberania do Dado (Data Vault):** O dado de saúde pertence ao **Participante**, não à Organização. O acesso é concedido temporariamente via `DataAccessGrant`. Nenhuma query deve ignorar essa verificação.
-   **(P8) Migrações Defensivas:** Alterações no banco de dados devem ser não-destrutivas e idempotentes. Dados sensíveis exigem migrações de dados separadas das de schema.

### III. Inteligência Artificial e Ética
-   **(P9) Friction for Safety (Atrito de Segurança):** Em fluxos de **Alto Risco** (ex: aprovação de plano de saúde), a UX deve impedir a "aprovação cega". Exigir ação explícita do profissional (HITL - Human-in-the-Loop).
-   **(P10) Rastreabilidade de Evidência:** Toda decisão sugerida pela IA deve ter seu "raciocínio" (Chain of Thought) registrado no `AuditLog` para explicabilidade jurídica e clínica.

### IV. Arquitetura de Software
-   **(P11) Desacoplamento Limpo:**
    -   *Services:* Lógica de Negócio Pura.
    -   *Clients:* Comunicação Externa (Ollama, APIs).
    -   *Views/Tasks:* Orquestração.
-   **(P12) API-First:** O contrato (DRF Serializers) é a fonte da verdade. O Frontend e o Backend se alinham através dele antes da implementação.
-   **(P13) Serializers Dedicados:** Separar explicitamente `ReadSerializer` (com dados aninhados para exibição) de `WriteSerializer` (com validação estrita para entrada).

### V. Qualidade e Testes
-   **(P14) Testes como Contrato da Realidade:** Nenhuma funcionalidade crítica (especialmente as médicas e de segurança) é considerada pronta sem testes de unidade e integração (Pytest + FactoryBoy).
-   **(P15) Dependências Estritas:** Versionamento de bibliotecas travado (`requirements.txt`, `package.json`) para garantir builds reprodutíveis e auditáveis.
-   **(P16) Validação Externa Ativa:** Não confiar cegamente em documentação de terceiros; validar o comportamento real das APIs e bibliotecas antes da implementação.

### VI. Performance e Frontend
-   **(P17) Otimização Proativa (Anti-N+1):** O uso de `select_related` e `prefetch_related` é obrigatório em queries relacionais. Processamento pesado vai para filas dedicadas (`ai_reasoning`).
-   **(P18) Ambiente Local-First:** O ambiente de desenvolvimento (Docker) deve ser um espelho fiel da produção para evitar o "funciona na minha máquina".
-   **(P19) Autonomia de Ferramentas:** Preferir soluções conteinerizadas e agnósticas a serviços proprietários de nuvem ("Vendor Lock-in").
-   **(P20) Gestão de Estado Estratégica:**
    -   *Server State:* TanStack Query (Cache e Sincronização).
    -   *Client State:* Redux Toolkit (Sessão, UI Global).
-   **(P21) Lançamentos Graduais:** Funcionalidades complexas devem ser desenvolvidas atrás de *Feature Flags* para permitir deploy contínuo sem quebrar a produção.
