# Inspectah — Sprint 31 (E28-S3)
## Capítulo 3 — Bloco 3: Frontend & Console de Fontes v2 (Providers & Perfis)

### 3.10 Objetivo deste bloco

Este bloco detalha **como o provider-first aparece para humanos** no Inspectah:

- quais telas novas (ou evoluídas) entram no Console de Fontes v2;
- quais APIs o frontend consome para operar Providers e Perfis;
- quais fluxos mínimos de UX precisam existir para S31 ser considerada “operável” e não só “rodável via script”.

A regra aqui é simples: se um operador precisar abrir terminal para entender ou operar provider-first no dia a dia, a S31 falhou parcialmente.

---

### 3.11 Princípios de UX do Console provider-first

Antes de falar de componentes, alguns princípios explícitos:

1. **Provider é infraestrutura, Perfil é ferramenta**  
   - Providers são relativamente poucos, alterados raramente, configurados por gente mais técnica.
   - Perfis são muitos, mudam com frequência e são a unidade que o operador de conteúdo realmente manipula.

2. **Perfis falam a língua do domínio, não da API**  
   - Nomes de perfis tipo `BR_PT_HARD_NEWS`, `LATAM_ES_POLITICS` e “Social — Política BR — Timeline” são aceitáveis; `newsdata_query_123` não.
   - Campos do formulário precisam refletir país/idioma/tema/budget, não parâmetros crús da API do provider.

3. **Estado e risco sempre visíveis**  
   - Operador precisa enxergar: se o perfil está ativo/pausado, quando rodou, se falhou, quanto está gastando.
   - Perfis que exageram em erro ou budget devem gritar visualmente.

4. **Operações perigosas com confirmação clara**  
   - Ativar/pausar perfil, mudar filtros agressivamente ou aumentar muito budget requerem confirmação explícita.

---

### 3.12 Mapa de telas do Console

Diretórios sugeridos no frontend (React/Next, adaptar ao padrão real):

- `frontend/inspectah-ui/src/pages/console/providers/`
- `frontend/inspectah-ui/src/pages/console/ingestion-profiles/`
- `frontend/inspectah-ui/src/components/console/`

#### 3.12.1 Tela de lista de Providers

**Rota**: `/console/providers`

**Objetivo**: dar visão geral dos providers configurados no sistema e seu estado.

**Elementos principais**:

- Tabela com colunas:
  - Nome (ex.: "News Provider Global");
  - Slug (`news_provider_global`);
  - Tipo (`NEWS` / `SOCIAL`);
  - Status (`ACTIVE`, `INACTIVE`, `EXPERIMENTAL`);
  - Regiões/idiomas principais (ex.: `global`, `BR/PT`);
  - Nº de Perfis associados.
- Filtros e busca:
  - por tipo (NEWS/SOCIAL);
  - por status;
  - por texto livre (nome/slug).
- Ações:
  - abrir detalhes do provider;
  - (opcional, com guardrails) alternar status `ACTIVE`/`INACTIVE` para providers que suportem isso.

#### 3.12.2 Tela de detalhes de Provider

**Rota**: `/console/providers/:providerId`

**Objetivo**: concentrar informações técnicas e operacionais relevantes sobre um provider.

**Elementos principais**:

- Card de informações gerais:
  - nome, slug, tipo;
  - regiões e idiomas suportados;
  - status atual;
  - notas internas (ex.: "ótimo para hard news BR", "latência alta à noite").

- Lista de Perfis associados (subseção):
  - tabelinha com nome do perfil, domínio (ex.: `BR_PT_HARD_NEWS`), status, últimas execuções;
  - botão para ir ao detalhe de cada perfil.

- Métricas agregadas por provider:
  - total de chamadas na sprint;
  - taxa de erro média;
  - perfis com maior uso de budget.

Esta tela é mais usada por quem faz tuning de arquitetura/operação do que pelo operador diário, mas precisa existir.

#### 3.12.3 Tela de lista de Perfis de Ingestão

**Rota**: `/console/ingestion-profiles`

**Objetivo**: ser a **home do operador de ingestão**. É aqui que a S31 vive no dia a dia.

**Elementos principais**:

- Tabela com colunas mínimas:
  - Nome do Perfil;
  - Provider (nome curto);
  - Tipo (NEWS/SOCIAL);
  - Domínio/escopo (ex.: "BR — PT — Política & Economia");
  - Status (`ACTIVE`, `PAUSED`, `EXPERIMENTAL`);
  - Última execução (timestamp + resultado: sucesso/erro);
  - Volume último run (ContentItems criados);
  - Uso de budget (ex.: "45% / dia").

- Filtros e busca:
  - por provider;
  - por status;
  - por tipo;
  - por texto (nome do perfil, domínio).

- Ações:
  - criar novo perfil;
  - abrir tela de edição/detalhe;
  - acionar "Rodar agora" (para perfis-piloto em ambiente controlado).

Perfis com erro recorrente ou perto do limite de budget devem aparecer com badges/cores de alerta.

#### 3.12.4 Tela de criação/edição de Perfil

**Rota**: `/console/ingestion-profiles/new` e `/console/ingestion-profiles/:profileId/edit`

**Objetivo**: permitir que operadores com permissão criem ou modifiquem perfis sem tocar em YAML.

**Sessões sugeridas no formulário**:

1. **Identidade do Perfil**
   - Nome interno (com ajuda/tooltip para padrão de nomenclatura);
   - Descrição opcional (explicando em linguagem de negócio o objetivo do perfil).

2. **Provider & tipo**
   - Select de Provider (listando apenas os ativos para aquele tipo de dado);
   - Campo de tipo inferido (NEWS/SOCIAL).

3. **Escopo de conteúdo**
   - País(es) (multi-select com códigos padrão);
   - Idioma(s);
   - Categorias/temas (politics, business, health, etc.);
   - Keywords principais (com sugestão de boas práticas).

4. **Agendamento & janela**
   - Frequência (cron abstrato ou presets: a cada 15m, 1h, 6h, 24h);
   - Janela padrão de busca (últimas X horas/dias por run).

5. **Budget & risco**
   - `budget_limit_calls` por período;
   - prioridade (BAIXA/MÉDIA/ALTA);
   - flag "perfil experimental" (sem uso em produção ainda).

6. **Controles**
   - Status (ACTIVE/PAUSED/EXPERIMENTAL);
   - Botão "Salvar";
   - Botão "Salvar e Rodar agora" (com confirmação extra, apenas em ambientes de teste/staging ou com permissões adequadas).

Validações:

- impedir salvar perfil `ACTIVE` sem `budget_limit_calls` definido;
- alertar se filtros estiverem extremamente genéricos (ex.: mundo inteiro, sem categorias, sem keywords);
- avisar quando alteração pode aumentar muito o custo estimado.

#### 3.12.5 Tela de execuções recentes de Perfil

**Rota**: `/console/ingestion-profiles/:profileId` (detalhe)

**Objetivo**: ser o lugar para investigar se um perfil está se comportando bem.

**Elementos principais**:

- Card com resumo do perfil (provider, escopo, schedule, budget, status).
- Seção "Últimas execuções":
  - tabela/lista com colunas: horário, duração, status, nº de chamadas, itens brutos, ContentItems criados, erros.
  - link para log crú (somente para quem precisa).
- Mini-painéis com métricas:
  - gráfico simples de chamadas vs ContentItems por dia;
  - uso de budget ao longo da sprint;
  - taxa de erro por run.

Ações:

- botão "Rodar agora" (igual ao da lista);
- botão "Editar perfil".

---

### 3.13 APIs de backend para o Console

O frontend do Console se apoia em um conjunto de APIs relativamente enxuto. Abaixo, um contrato conceitual (adaptar para o framework real: FastAPI/DRF/etc.).

#### 3.13.1 Providers

- `GET /api/console/providers`
  - Retorna lista de providers com filtros opcionais (tipo, status).

- `GET /api/console/providers/{provider_id}`
  - Retorna detalhes de um provider específico, incluindo resumo de perfis.

- (Opcional) `PATCH /api/console/providers/{provider_id}`
  - Permite alterar status ou notas internas (uso restrito a roles específicas).

#### 3.13.2 Perfis de Ingestão

- `GET /api/console/ingestion-profiles`
  - Retorna lista paginada de perfis com filtros (provider, tipo, status, texto).

- `GET /api/console/ingestion-profiles/{profile_id}`
  - Retorna detalhes do perfil + resumo das últimas execuções + métricas básicas.

- `POST /api/console/ingestion-profiles`
  - Cria novo perfil com base em payload validado.

- `PATCH /api/console/ingestion-profiles/{profile_id}`
  - Atualiza perfil existente (filtros, schedule, budget, status).

- `POST /api/console/ingestion-profiles/{profile_id}/run-now`
  - Enfileira job imediato para o perfil especificado;
  - retorna identificação do job ou confirmação de enfileiramento.

#### 3.13.3 Métricas & execuções

- `GET /api/console/ingestion-profiles/{profile_id}/runs`
  - Lista execuções recentes desse perfil, com campos suficientes para a tela de detalhe.

- `GET /api/console/ingestion-profiles/{profile_id}/metrics`
  - Retorna métricas agregadas (calls, itens, errors, dedupe_ratio, budget_usage) por período.

Essas APIs não precisam ser perfeitas na S31, mas precisam suportar as telas descritas acima e os gates G2/G3.

---

### 3.14 Fluxos mínimos de UX para S31 ser GO

Para dizer que S31 entregou um Console de Fontes v2 digno do nome, alguns fluxos precisam funcionar ponta a ponta.

#### Fluxo A — Operador descobre e inspeciona perfis-piloto

1. Operador abre `/console/ingestion-profiles`.
2. Filtra por `BR`/`PT` e tipo `NEWS`.
3. Vê perfis como `BR_PT_HARD_NEWS` e o status de cada um (ativo/pausado, última execução etc.).
4. Clica em um perfil e abre `/console/ingestion-profiles/:profileId`.
5. Vê resumo do perfil, últimas execuções e mini-métricas.

Se esse fluxo exige terminal, a S31 não está pronta.

#### Fluxo B — Operador aciona um run de teste

1. Operador abre detalhe de um perfil-piloto.
2. Clica em "Rodar agora".
3. Sistema enfileira job, mostra estado "run em execução".
4. Após alguns minutos, operador atualiza tela e vê nova execução na lista, com contagens atualizadas.

Esse fluxo é importante para validações rápidas e debugging.

#### Fluxo C — Operador ajusta budget de um perfil

1. Operador abre perfil que está perto de estourar budget.
2. Ajusta `budget_limit_calls` no formulário.
3. Salva e vê nova configuração refletida.
4. No dia seguinte, painel de métricas mostra uso mais saudável.

Isso conecta UI, API, modelo de perfil e métricas.

#### Fluxo D — Operador pausa um perfil problemático

1. Operador identifica perfil com alta taxa de erro.
2. Abre detalhe e troca status para `PAUSED`.
3. Scheduler deixa de gerar jobs para esse perfil.
4. Painel de métricas confirma queda de activity.

---

### 3.15 Qualidade mínima esperada de UI

Mesmo sendo um console interno, a UI da S31 precisa respeitar alguns critérios de qualidade:

- **Legibilidade**: colunas com nome claro, tooltips para termos técnicos, layout que respira.
- **Feedback de ações**: ao salvar perfil ou rodar job, o usuário vê feedback imediato de sucesso/erro.
- **Erros explicáveis**: mensagens que ajudem a corrigir problema (ex.: "provider retornou rate limit, reduza frequência ou aumente budget").
- **Consistência**: estilos, componentes e padrões alinhados com o restante do Inspectah UI.

---

### 3.16 Fecho do Bloco 3

Com este frontend e este conjunto de APIs, a Sprint 31 garante que provider-first não é só um festival de scripts escondidos no backend, mas uma **capacidade operável**:

- operadores conseguem ver e entender Providers e Perfis;
- conseguem ajustar escopo e budget sem editar YAML;
- conseguem rodar testes, investigar falhas e acompanhar métricas;
- e tudo isso converge para o mesmo modelo mental que Programas 2–4 vão usar para explicar de onde vem cada pedaço de informação.

No próximo bloco do Capítulo 3, a arquitetura fecha com observabilidade detalhada, convivência fina com legado e filemap completo para o Codex seguir sem sair do trilho.

