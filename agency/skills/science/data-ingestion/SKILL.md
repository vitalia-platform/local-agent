# Skill: Data Ingestion (`data-ingestion`)

Este agente é especializado em ingerir, mapear e unificar dados bibliográficos multi-fonte para a geração do `PRISMA_LOG.csv` sem perda de integridade metodológica.

## Diretrizes de Ação

1. **Regra de Ouro (Anti-Alucinação)**:
   - **NUNCA** determine cabeçalhos ou delimitadores baseado em seu conhecimento prévio.
   - Sempre que precisar mapear ou validar aliases de um export acadêmico, consulte as URLs oficiais listadas em `sources_config.yaml` realizando buscas na web via `search_web` e lendo os conteúdos com `read_url_content`.
2. **Execução do Pipeline**:
   - Inicie o processamento dos arquivos brutos depositados na pasta de exportação disparando:
     ```bash
     python3 scripts/review_pipeline/run_ingestion.py --config ./criteria_config.yaml --project-root .
     ```
3. **Resolução de Conflitos e Mapeamentos**:
   - O script detecta de forma automática o delimitador (`,`, `;`, `\t`) e o encoding do arquivo CSV.
   - Caso um arquivo de exportação não seja mapeado com os perfis conhecidos em `./scripts/review_pipeline/sources_config.yaml`, o script executará um fallback genérico baseado em aliases de busca comuns.
