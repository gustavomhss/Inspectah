# Inspectah — Sprint 31 (E28-S3)
## Capítulo 4 — Bloco 2: Fase 1 — Fundação de Dados & Migrations

### 4.4 Escopo exato da Fase 1

A Fase 1 tem uma missão simples de enunciar e fácil de estragar se feita na pressa:

> Colocar de pé o esqueleto provider-first no **modelo de dados** e nas **migrations**, sem quebrar nada que já existe.

Escopo incluído:

- novos modelos e campos:
  - criação de `Provider`;
  - criação de `IngestionProfile`;
  - ajustes em `ContentItem` para proveniência provider-first;
  - ajustes necessários em `Source` para mapear domínios/veículos;
- migrations correspondentes, aplicáveis tanto em banco limpo quanto em banco com dados reais;
- configuração inicial de providers e perfis-piloto em arquivos de config.

Escopo explicitamente fora desta fase:

- clients de providers (chamar a API de fato);
- serviços de normalização/dedupe;
- jobs e scheduler;
- telas de Console;
- integração com Programas 2–3.

A Fase 1 termina quando:

- o modelo está estável;
- as migrations sobem e descem sem drama;
- o banco de desenvolvimento tem providers/perfis-piloto minimamente configurados;
- o gate S31-G1 roda limpo, com scorecard e evidências salvos.

---

### 4.5 Ordem de trabalho recomendada na Fase 1

Para evitar retrabalho, a sequência sugerida é:

1. Modelo em rascunho (sem migrations ainda)
   - Esboçar `Provider` e `IngestionProfile` no código, alinhando nomes de campos e tipos com o Capítulo 3.
   - Esboçar os novos campos de `ContentItem` e ajustes mínimos de `Source`.
   - Revisar com o modelo mental de Programa 2–3: “o que um Claim/Fact precisa saber sobre a origem do conteúdo?”

2. Refinar nomes, tipos e índices
   - Garantir que campos obrigatórios em provider-first estejam presentes: `provider_id`, `ingestion_profile_id`, `external_id` (quando existir), `source_domain`, `ingested_at`.
   - Definir índices essenciais para consultas e dedupe (por exemplo, `(provider_id, external_id)` e `(ingestion_profile_id, ingested_at)`).
   - Documentar decisões em comentários leves ou em notas breves no Cap.3.

3. Gerar migrations
   - Criar migrations individuais para:
     - novos modelos (`Provider`, `IngestionProfile`);
     - alterações em `ContentItem`;
     - ajustes em `Source` (se houver).
   - Preferir migrations menores e legíveis a uma gigantesca; facilitam debugging.

4. Aplicar migrations em banco limpo
   - Dropar e recriar o banco de desenvolvimento (conforme padrão do projeto).
   - Rodar as migrations completas nesse banco vazio.
   - Verificar se o schema final bate com o esperado (via ferramentas do ORM ou inspeção manual).

5. Aplicar migrations em banco com dados reais
   - Restaurar ou apontar para um dump recente do banco de desenvolvimento com dados das sprints anteriores.
   - Rodar migrations sem apagar dados.
   - Checar se tabelas antigas permanecem consistentes e se as novas colunas em `ContentItem`/`Source` surgiram com valores nulos aceitáveis.

6. Popular providers/perfis-piloto mínimos
   - Preencher `config/providers.yml` com pelo menos:
     - um provider de news (ex.: `news_provider_global`);
     - um provider de social (ex.: `social_radar_br`).
   - Preencher `config/ingestion_profiles.yml` com perfis-piloto:
     - `BR_PT_HARD_NEWS`;
     - um perfil social focado em política BR.
   - Criar script leve ou comando de gestão para importar essas configs para o banco, se essa for a convenção do projeto.

7. Rodar sanity de modelo
   - Executar testes unitários/integração focados em:
     - criação e leitura de `Provider` e `IngestionProfile`;
     - criação de `ContentItem` com proveniência provider-first;
     - criação/leitura de `Source` associado a domínios.

8. Rodar gate S31-G1 em modo local
   - Executar `bin/s31_g1_models_and_migrations.sh` (ou equivalente) em ambiente de desenvolvimento.
   - Conferir se evidências e scorecard foram produzidos.

Quando essa sequência estiver verde, a Fase 1 está pronta para ser “selada” e empurrada para CI.

---

### 4.6 Comandos e rotinas locais esperados

Os comandos exatos dependem do setup do repo, mas o roteiro esperado para um dev é algo na linha de:

1. Preparar ambiente

- ativar virtualenv e demais requisitos do projeto;
- garantir que dependências de migrations (ex.: Alembic) estejam instaladas.

2. Gerar migrations

- usar a ferramenta oficial do projeto para autogerar e depois revisar/editá-las;
- conferir se não há renomeações implícitas ou drop de colunas perigosos.

3. Aplicar migrations em banco limpo

- rodar comando de “reset + migrate” do projeto;
- conferir logs e, se existir, arquivo de evidência de migrations.

4. Aplicar migrations em banco com dados reais

- apontar para base com dados reais de desenvolvimento;
- rodar migrations e observar se há warnings ou tempo anormal;
- fazer queries simples para checar que dados antigos seguem íntegros.

5. Rodar testes

- executar suíte de testes focados em modelos e migrations (pelo menos os marcados como relacionados à S31);
- se existir subset de testes “core models”, incluir nessa rodada.

6. Rodar gate G1

- executar `bin/s31_g1_models_and_migrations.sh`;
- verificar se ele:
  - prepara ambiente;
  - aplica migrations em banco de teste;
  - roda testes;
  - escreve logs em `out/evidence/S31_G1_models_and_migrations/`;
  - gera `out/scorecards/S31_G1_models_and_migrations.json`.

Esses passos devem ser baratos o suficiente para serem repetidos sempre que o modelo for ajustado.

---

### 4.7 Gate S31-G1 — Contrato, evidências e scorecard

O gate S31-G1 é o porteiro oficial da Fase 1. Ele só diz PASS quando três coisas forem verdade, ao mesmo tempo:

1. Migrations sobem em banco limpo sem erros.
2. Migrations sobem em banco com dados reais sem corromper nada.
3. Testes de modelo/migrations passam.

O script `bin/s31_g1_models_and_migrations.sh` deve:

- preparar ambiente de teste (variáveis, banco temporário, etc.);
- aplicar migrations em pelo menos um cenário limpo;
- aplicar migrations em um cenário com dump de dados reais ou base de desenvolvimento;
- rodar testes relevantes;
- salvar logs representativos em `out/evidence/S31_G1_models_and_migrations/`;
- gerar `out/scorecards/S31_G1_models_and_migrations.json` com campos mínimos:
  - `gate_id`: `"S31-G1"`;
  - `status`: `"PASS"`, `"WARN"` ou `"FAIL"`;
  - `summary`: 2–4 frases explicando o resultado;
  - `metrics`: número de migrations aplicadas, tempo, se houve fallback, etc.;
  - `evidence_paths`: lista de arquivos gerados em `out/evidence`.

Regra prática:

- `PASS` exige zero erro em migrations e testes;
- `WARN` pode ser usado se existirem particularidades documentadas (ex.: tempo alto em base muito grande, mas aceitável);
- `FAIL` é qualquer situação em que migrations não são idempotentes ou testes de modelo falham.

Sem G1 em PASS (ou, no máximo, WARN bem justificado), a sprint **não** avança para implementação de clients de provider (Fase 2).

---

### 4.8 Sanity explícito com legado na Fase 1

Mesmo que a convivência com legado seja tratada com mais profundidade na Fase 4, a Fase 1 já precisa garantir uma coisa muito simples:

> “Adicionar campos e tabelas novas não fez o banco esquecer o que sabia ontem.”

Sanity mínimo esperado:

- Após rodar migrations em banco com dados reais:
  - contar registros em tabelas críticas antes e depois;
  - verificar se colunas chave (IDs, chaves estrangeiras) permanecem válidas;
  - garantir que qualquer coluna nova em `ContentItem`/`Source` foi criada com default seguro (nulo aceitável ou valor neutro).

Se o projeto já tiver scripts de sanity anteriores de outras sprints (ex.: S10, S20), a Fase 1 deve reaproveitar ao máximo esses scripts, apenas adicionando checagens relacionadas a providers/perfis.

---

### 4.9 Erros típicos desta fase e como detectá-los cedo

Algumas armadilhas clássicas de Fase 1 e como o plano tenta neutralizá-las:

1. Campos obrigatórios demais cedo demais
   - Sintoma: migrations falham em bases com dados antigos porque exigem `provider_id`/`ingestion_profile_id` onde isso ainda não existe.
   - Mitigação: na Fase 1, esses campos são opcionais em registros antigos; tornam-se obrigatórios apenas para novos ContentItems de provider (regra em código, não na migration).

2. Migrations gigantes e opacas
   - Sintoma: um único arquivo de migration que faz “tudo” e ninguém entende.
   - Mitigação: dividir migrations em unidades lógicas menores; comentar partes críticas; rodar G1 em cima delas.

3. Índices mal pensados
   - Sintoma: migrations sobem, mas consultas ficam lentas ou estranhas.
   - Mitigação: pensar desde já em consultas típicas (por provider/profile/domínio) e criar índices apropriados; usar dumps pequenos para testar.

4. Divergência entre código e docs
   - Sintoma: Cap.3 descreve campos que não existem no modelo, ou vice-versa.
   - Mitigação: sempre que o modelo for ajustado, atualizar o trecho correspondente de Cap.3 nesta mesma sprint, antes de considerar a Fase 1 encerrada.

---

### 4.10 Resultado esperado ao fim da Fase 1

Quando a Fase 1 estiver concluída de verdade, o estado alvo é:

- o banco sabe o que é um `Provider` e um `IngestionProfile`;
- `ContentItem` e `Source` estão prontos para guardar proveniência provider-first sem quebrar o que existia;
- migrations sobem em bases limpas e com dados reais sem drama;
- configs mínimas de providers/perfis-piloto existem e podem ser carregadas;
- o gate S31-G1 está verde, com evidências e scorecard em seus lugares;
- Capítulos 1–3 e este bloco do Cap.4 descrevem fielmente o que está implementado.

A partir desse ponto, a Sprint 31 pode partir para a Fase 2 com a confiança de que está construindo em cima de um chão sólido, e não em cima de um banco remendado às pressas.