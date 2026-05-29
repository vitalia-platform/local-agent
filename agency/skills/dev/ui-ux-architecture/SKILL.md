---
name: ui-ux-architecture
description: Skill de Arquitetura de UI/UX unificando as regras anti-clichê e o conceito de Tech-Warmth da Vitalia.
---

# UI/UX Architecture & Tech-Warmth

Esta skill define os princípios de design de interface, unificando a quebra de padrões (anti-clichê) com o design acolhedor exigido para saúde (Tech-Warmth).

## 1. O Conceito de Tech-Warmth (Vitalia)
- **Design Afetivo**: Interfaces médicas não devem ser "frias como um hospital". Use cores quentes e tipografia acolhedora.
- **Friction for Safety (Lei P9)**: Fluxos perigosos (ex: deletar prontuário, aprovar plano) devem ter "atrito intencional" e exigir ações conscientes.
- **Acessibilidade Absoluta**: Contraste AA+, navegação por teclado e suporte a leitores de tela são inegociáveis. O sistema deve ser usável por uma avó e poderoso para um médico.

## 2. Quebra de Padrões (Anti-Clichê)
- **Fuja do "SaaS Genérico"**: Não use layouts 50/50 por padrão, não abuse de Bento Grids sem necessidade, evite Mesh Gradients genéricos.
- **Purple Ban**: Nunca use roxo, violeta ou índigo como cor principal (clichê de IA), a menos que explicitamente solicitado.
- **Tipografia Brutalista ou Assimétrica**: Tente layouts onde a tipografia é 80% do peso visual. Quebre o grid intencionalmente para criar hierarquia visual única.

## 3. Implementação Técnica Frontend
- **Framework**: Next.js (App Router).
- **Estado**: TanStack Query (Server State) e Zustand/Redux (Client State).
- **Estilo**: Tailwind CSS v4 + `shadcn/ui` (customizado com tokens de Tech-Warmth).
- **Performance**: Evite waterfalls em client-side fetching. Otimize re-renderizações. Prefira Server Components para conteúdo estático.

## 4. O Teste "Maestro" (Validação Final)
Antes de dar uma UI como pronta, pergunte-se:
1. *"Isso parece um template genérico da Vercel?"* Se sim, refaça.
2. *"As animações (micro-interações) estão presentes?"* UI estática é uma UI morta. Adicione spring physics, hover states profundos e feedback visual.
3. *"A interface passa segurança clínica sem parecer intimidadora?"* Equilíbrio perfeito entre Tech e Warmth.
