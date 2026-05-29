# Skill: LLM Screener (`llm-screener`)

Este agente é especializado no screening/triagem de artigos acadêmicos em larga escala utilizando o Ollama local e prompts dinâmicos baseados no `criteria_config.yaml`.

## Diretrizes de Ação

1. **Instanciação e Preparação**:
   - Copie a pasta do pipeline de revisão do kit para a pasta correspondente no projeto playground:
     ```bash
     cp -r kit/scripts/review_pipeline/ ./scripts/review_pipeline/
     ```
2. **Execução do Processamento**:
   - Dispare a triagem de Fase 1 via:
     ```bash
     python3 scripts/review_pipeline/run_fase1.py --config ./criteria_config.yaml
     ```
3. **Interpretação e Verificações**:
   - O script lerá automaticamente o `PRISMA_LOG.csv` existente e iniciará o lote.
   - Em caso de erros persistentes ou travamentos do Ollama, o script exibirá um menu interativo no terminal. Aguarde e coordene a escolha do usuário ou selecione a ação adequada.
   - Verifique a saúde do processamento consultando os shards JSON gerados em `saida/shards/` e as estatísticas exibidas na barra de progresso.
