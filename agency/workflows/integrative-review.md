<!-- .agent/workflows/integrative-review.md | Atualizado em: 21-05-2026 11:31:00(GMT-04:00) -->
---
description: >
  Ponto de entrada principal para iniciar, estruturar e orquestrar uma Revisão Sistemática ou Integrativa da Literatura.
---

# Workflow: Integrative Review (`/integrative-review`)

**Description**: Ponto de entrada principal para iniciar, estruturar e orquestrar uma Revisão Sistemática ou Integrativa da Literatura. Conduz o pesquisador pelo Painel Interativo de Setup, calibra os critérios com base na amostra, e aciona o Esquadrão Science (`chief-reviewer`, `data-librarian`, `methodology-auditor`).

---

## 1. Fase Exploratória — Painel Interativo de Setup

Quando o usuário acionar `/integrative-review`, o agente deve primeiro inspecionar o diretório de trabalho.
Se encontrar dados existentes (`criteria_config.yaml`, `exportacao/`, `amostra/`, `lotes/`, `saida/`, `fichamentos/` ou outros artefatos relacionados), ele deve pré-preencher o painel lateral com um resumo desses itens e orientar o usuário sobre como exportar ou arquivar os dados antes de prosseguir.

Quando o usuário acionar `/integrative-review`, **PARE E COLETE** as informações abaixo. Apresente este formulário criando um **Artifact** em formato Markdown ou HTML (ex: `setup_revisao.md` ou `setup_revisao.html`), que abrirá em um painel, permitindo ao usuário visualizar e aprovar os dados de entrada de forma estruturada:

### 1.1 Identidade do Estudo
1. **Título provisório** do estudo
2. **Autores e filiação institucional** (para o artigo final)
3. **Periódico alvo** (ex: *JMIR mHealth and uHealth*)
4. **Pergunta Norteadora (PICO/PCC)**: qual é a exata pergunta científica que a revisão pretende responder?
5. **Recorte temporal** (ex: 2020–2026)
6. **Tipos de estudo aceitos** (ex: RCTs, Meta-análises, estudos observacionais)
7. **Bases de dados alvo** — aconselhe Scopus + Web of Science via RNP/Institucional. O workflow deve adaptar suas configurações de busca com base nas escolhas do usuário. Nota: Como arquivos `.csv` brutos que vêm da nuvem frequentemente têm limites estipulados pelas plataformas de busca, a configuração deve prever múltiplos arquivos para processar.

> **Dica Smart Setup:** Ofereça ativamente a opção para o pesquisador apontar/fornecer o texto ou PDF de um **"artigo de exemplo (Gold Standard)"**. Se o usuário aceitar, leia o documento fornecido e **extraia automaticamente** as sugestões de respostas para os itens acima e categorias temáticas, poupando o trabalho manual do usuário.

### 1.2 Configuração das Pastas de Trabalho

> [!IMPORTANT]
> Todos os nomes de pasta são definidos aqui. Nenhum valor é fixo no código. Os nomes escolhidos serão gravados em `criteria_config.yaml` e usados por todos os agentes e scripts.

| Finalidade | Nome da pasta (sugestão padrão) |
|---|---|
| CSV bruto da base de dados | `exportacao` |
| Amostra — PDFs (Scopus) | `amostra/scopus` |
| Amostra — CSV (WoS) | `amostra/webofscience` |
| Pool de lotes para triagem em massa | `lotes` |
| Saída PRISMA (logs e resultados) | `saida` |
| Fichamentos (leitura integral) | `fichamentos` |

O pesquisador pode aceitar os nomes padrão ou redefinir cada um.

### 1.3 Infraestrutura de Processamento
- **URL da API Ollama local** (ex: `http://ip-do-servidor:11434`)
- **Modelo de linguagem** (ex: `llama3.2:3b`)
- **Modelo de embeddings** (ex: `nomic-embed-text`)
- **Tamanho do lote** para triagem em massa (ex: `1000`)
- **Domínios de alto valor**: temas de interesse especial → receberão tag `TRENDING_TOPIC`

### 1.4 Critérios e Perguntas CoT
Proponha ativamente ao pesquisador (com base no tema da revisão):
- As perguntas binárias do Chain-of-Thought (ex: "q1: A intervenção envolve tecnologia digital?")
- A `decision_rule` em formato condicional legível (ex: "If q1 is Yes AND q2 is Yes, then INCLUIR, else EXCLUIR")
- Os `extraction_fields` recomendados para a extração do tema.

Permita a validação e edição de cada campo pelo pesquisador antes de persistir no `criteria_config.yaml`.

### 1.5 Geração e Validação Interativa de Exemplos Few-Shot
Gere dinamicamente 2 artigos sintéticos baseados no tema (1 positivo e 1 negativo) para calibrar a resposta do LLM. Exiba em tela um painel interativo de validação com as seguintes opções antes de gravar:
- **[A] Aprovar**: Confirma o exemplo e prossegue.
- **[E] Editar título/resumo**: Abre entrada para editar o texto sintético.
- **[J] Editar JSON esperado**: Permite ajustar o formato de saída do cot_analysis ou final_decision.
- **[R] Regenerar**: Solicita um novo exemplo para o agente.

O setup não prossegue sem que ambos os exemplos sejam validados e confirmados.

### 1.6 Seleção, Pesquisa e Atualização de Fontes de Dados (Regra Anti-Alucinação)
Apresente uma tabela visual das fontes mapeadas no `sources_config.yaml` canônico do kit com suas respectivas datas de última validação e links oficiais de documentação.

> [!IMPORTANT]
> **REGRA DE OURO (Anti-Alucinação):** É estritamente proibido ao agente validar colunas e delimitadores acadêmicos usando seu conhecimento interno. Para qualquer base selecionada, se houver solicitação de atualização, o agente DEVE executar `search_web` e `read_url_content` sobre as documentações e links oficiais.

Para cada fonte selecionada pelo usuário:
1. Apresente as opções: `[V] Usar sem reverificar`, `[P] Pesquisar agora na documentação oficial` ou `[M] Modificar manualmente os aliases`.
2. Se selecionado `[P]`:
   - Efetue busca e leitura dos links da base.
   - Apresente um diff claro comparando a especificação do kit com a encontrada na pesquisa viva.
   - Permita a aplicação automática das correções ou edições manuais.
3. Se adicionado nova fonte `[N]`: colete o nome da base e URL de documentação e monte o perfil via pesquisa viva estruturada.
4. Salve o arquivo `sources_config.yaml` resultante na raiz do diretório `scripts/review_pipeline/` do projeto com auditoria (`last_verified`, `verified_by`).

---

## 2. Inicialização do Ambiente ("Clean Room")

Após aprovação do painel pelo pesquisador:

1. Crie o `00_SUMARIO_EXECUTIVO.md` preenchido com a Pergunta Norteadora e todos os dados coletados acima
2. Crie as pastas de trabalho com os nomes definidos no painel:
   ```bash
   mkdir -p [pasta-exportacao] [pasta-amostra]/scopus [pasta-amostra]/webofscience [pasta-lotes] [pasta-saida] [pasta-fichamentos]
   ```
3. Copie o template modular do pipeline de revisão do kit para o projeto local:
   ```bash
   cp -r [kit_path]/scripts/review_pipeline ./scripts/review_pipeline
   ```
4. Salve o `sources_config.yaml` personalizado e validado em `./scripts/review_pipeline/sources_config.yaml`.
5. Gere o `criteria_config.yaml` na raiz do projeto com todos os parâmetros definidos (incluindo `active_sources`, `prompt_configuration`, CoT e few-shots).
6. **Substituição de Variáveis:** O Agente de IA deve editar os arquivos dentro da pasta `inicio/` substituindo as tags correspondentes.

---

## 3. Pré-condição de Dados (Aguardar Depósito)

Após criar as pastas, **PARE e instrua o pesquisador**:

```
📥 Ambiente inicializado. Antes de prosseguir, deposite os dados de calibração:

  → [pasta-amostra]/scopus/       — PDFs dos artigos mais relevantes (baixados do Scopus)
  → [pasta-amostra]/webofscience/ — CSV de metadados exportado da Web of Science
  → [pasta-exportacao]/           — CSV bruto completo da busca nas bases

Quando os arquivos estiverem depositados, confirme para iniciar a análise da amostra.

### 3.1 Opções de Reconfiguração e Backup

Se o usuário desejar reiniciar ou recalibrar o processo, ofereça duas opções explícitas antes de qualquer limpeza automática:

- **(A) Reconfiguração Total — "Refazer tudo"**: apaga artefatos de run (pastas `lotes/`, `saida/`, `amostra/` processada e `PRISMA_LOG.csv`) e reinicia o painel de setup desde o começo. Esta opção DEVE solicitar um backup automático antes de qualquer exclusão.
- **(B) Recalibração Final — "Refazer fase final"**: mantém a estrutura e dados brutos, mas regenera apenas os exemplos few-shot e limpa os shards da Fase 1 para reprocessamento. Não apaga `criteria_config.yaml` a menos que o usuário confirme.

Quando qualquer opção que remova dados for selecionada, o agente **deve** oferecer criar um backup automaticamente chamando o script de utilidade:

```
python scripts/review_pipeline/backup_workdir.py
```

O backup será salvo em `saida/backups/` e um registro de sessão será persistido em `.agent/session/last_backup.json`.
```

---

## 4. Análise da Amostra e Calibração dos Critérios

Após confirmação do depósito:

1. Leia a pasta de amostra (PDFs e CSVs)
2. Mapeie os temas recorrentes
3. **Sugira ativamente** os critérios de Inclusão e Exclusão com base na amostra
4. Permita ao pesquisador refinar critérios.
5. Grave os critérios aprovados em `criteria_config.yaml`.

---

## 5. Disparo da Orquestração

Assim que `criteria_config.yaml` estiver aprovado e os lotes depositados:

1. **Acione o `@data-librarian`** usando a skill `data-ingestion`: Executa `run_ingestion.py` para ler múltiplos CSVs na pasta de exportação, detectar formatos a partir de `./scripts/review_pipeline/sources_config.yaml`, normalizar os DOIs, deduplicar os registros e construir o arquivo `PRISMA_LOG.csv`.
2. **Acione o `@chief-reviewer`** usando a skill `llm-screener`: Executa `run_fase1.py` para processar a triagem de Fase 1 via Ollama com tratamento automático de retries, salvando shards JSON e atualizando em tempo real o PRISMA_LOG.csv.

---

## 6. Verificação de Arquivos Ignorados (.gitignore)

No final do processo de inicialização, verifique com o usuário a necessidade de editar o arquivo `.gitignore`.
1. Apresente as pastas criadas.
2. Peça que o usuário confirme quais caminhos não devem ir para o repositório.
3. Edite o `.gitignore` para corrigir/adicionar os caminhos das pastas de dados conforme a escolha do usuário.

---

## Anti-Patterns 🚫

- **NUNCA** inicie triagem pegando abstracts do Google — siga a exportação metodológica do portal
- **NUNCA** pule o Log Total PRISMA — todo artigo excluído deve ter motivo registrado
- **NUNCA** altere `criteria_config.yaml` ou `sources_config.yaml` manualmente durante o processamento — use o workflow para ajustes
- **NUNCA** hardcode nomes de pasta ou mapeamentos de cabeçalho nos scripts — leia sempre dos configs estruturados

