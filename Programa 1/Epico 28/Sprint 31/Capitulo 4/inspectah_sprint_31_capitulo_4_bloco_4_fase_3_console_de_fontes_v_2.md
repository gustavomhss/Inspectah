# Inspectah — Sprint 31 (E28-S3)
## Capítulo 4 — Bloco 4: Fase 3 — Console de Fontes v2 (Backend + Frontend)

### 4.17 Escopo exato da Fase 3

A Fase 3 sobe um andar na abstração:

> Transformar a ingestão provider-first em **capacidade operável via UI**, sem depender de scripts manuais.

Escopo incluído:

- implementação das **APIs de Console** para Providers e Perfis;
- implementação das **telas** de Console de Fontes v2 (lista/detalhe de Provider, lista/detalhe/criação/edição de Perfil);
- fio condutor "Rodar agora" para perfis-piloto, ligando UI → API → job → métricas;
- exibição mínima de **métricas** por perfil na UI (últimas execuções, status, uso de budget);
- gate **S31-G3** rodando, validando Console e observabilidade mínima.

Escopo explicitamente fora desta fase:

- dashboards avançados (isso é mais foco da Fase 4 / futuras sprints);
- telas de Programas 2–3 (casos, FactBlocks etc.);
- grandes refactors de UX global do Inspectah UI.

---

### 4.18 Ordem de trabalho recomendada na Fase 3

A ordem importa para não ter tela bonita em cima de API inexistente.

#### Passo 1 — Contratos de API (antes do código)

1. Revisar o desenho de API no Cap.3 (Bloco 3) e congelar contratos mínimos:
   - `GET /api/console/providers`;
   - `GET /api/console/providers/{id}`;
   - `GET /api/console/ingestion-profiles`;
   - `GET /api/console/ingestion-profiles/{id}`;
   - `POST /api/console/ingestion-profiles`;
   - `PATCH /api/console/ingestion-profiles/{id}`;
   - `POST /api/console/ingestion-profiles/{id}/run-now`;
   - `GET /api/console/ingestion-profiles/{id}/runs`;
   - `GET /api/console/ingestion-profiles/{id}/metrics`.
2. Documentar brevemente, em doc ou comentário, o payload esperado de cada endpoint (campos essenciais e tipos).

Esses contratos são o “pacto” entre backend e frontend na S31.

#### Passo 2 — Implementação das APIs de Providers

1. Criar `app/api/console_providers.py` com pelo menos:
   - `GET /providers`:
     - lista providers com filtros opcionais (tipo, status);
     - paginação simples, se necessário.
   - `GET /providers/{id}`:
     - retorna detalhes do provider;
     - inclui resumo de perfis associados (id, nome, status, últimas execuções, se disponível).
2. Garantir que:
   - as respostas usem DTOs/serializers consistentes com o restante da API;
   - erros sejam claros (ex.: 404 para provider inexistente).
3. Criar testes básicos de API cobrindo os dois endpoints.

#### Passo 3 — Implementação das APIs de Perfis

1. Em `app/api/console_ingestion_profiles.py`, implementar:
   - `GET /ingestion-profiles`:
     - suporta filtros por provider, tipo, status, texto;
     - retorna lista com colunas mínimas para a lista da UI (nome, provider, tipo, status, última execução, budget_usage aproximado).
   - `GET /ingestion-profiles/{id}`:
     - retorna detalhes completos do perfil;
     - inclui resumo de últimas execuções (cruzando com logs/metrics);
     - inclui visão rápida de métricas agregadas.
   - `POST /ingestion-profiles`:
     - cria novo perfil a partir de payload validado;
     - aplica validações de negócio (ex.: `budget_limit_calls` obrigatório para status ACTIVE).
   - `PATCH /ingestion-profiles/{id}`:
     - atualiza perfil existente (filtros, schedule, budget, status);
     - loga alterações relevantes (ex.: mudança de budget).
   - `POST /ingestion-profiles/{id}/run-now`:
     - enfileira job de ingestão para o perfil indicado;
     - retorna confirmação com ID do job ou status enfileirado.
2. Implementar o mínimo de validações para evitar perfis perigosos:
   - bloquear ativação de perfil sem `budget_limit_calls`;
   - emitir warnings (ou recusar) perfis com escopo absurdamente amplo sem motivo.
3. Criar testes de API focados em:
   - criação e atualização de perfis;
   - run-now enfileirando corretamente;
   - filtros básicos na listagem.

#### Passo 4 — Telas de Providers no Console

1. Criar página `/console/providers` (ex.: `frontend/inspectah-ui/src/pages/console/providers/index.tsx`):
   - tabela com colunas: nome, slug, tipo, status, regiões/idiomas principais, nº de perfis;
   - filtro por tipo e status;
   - busca textual.
2. Criar página `/console/providers/[id].tsx`:
   - card com informações gerais do provider;
   - lista dos perfis associados (nome, status, últimas execuções);
   - link para detalhe de cada perfil.
3. Garantir que a UI degrade bem se métricas ainda não estiverem completas (placeholders amigáveis em vez de erro).

#### Passo 5 — Telas de Perfis no Console

1. Criar página `/console/ingestion-profiles/index.tsx`:
   - tabela de perfis com colunas: Nome, Provider, Tipo, Domínio/escopo, Status, Última execução, Volume último run, Uso de budget;
   - filtros por provider/tipo/status;
   - busca textual.
2. Criar página `/console/ingestion-profiles/[id].tsx`:
   - card com dados do perfil (provider, filtros principais, schedule, budget, status);
   - lista de últimas execuções (hora, duração, status, calls, itens brutos, ContentItems, erros);
   - gráficos simples (ou KPIs) de:
     - calls vs ContentItems;
     - budget_usage ao longo do tempo;
     - taxa de erro.
   - botão "Rodar agora" chamado o endpoint `run-now`.
3. Criar página `/console/ingestion-profiles/edit.tsx` (ou similar) para criação/edição, com formulário descrito em Cap.3:
   - se o projeto usa rotas baseadas em ID, pode ser `[id]/edit.tsx`.
   - validações em tempo real/coerentes com as do backend.

#### Passo 6 — Experiência "Rodar agora" fim a fim

1. Na tela de detalhe de perfil:
   - botão “Rodar agora” que:
     - chama `POST /ingestion-profiles/{id}/run-now`;
     - mostra feedback imediato (sucesso ou erro);
     - opcionalmente, exibe “run em progresso”.
2. Garantir que, após alguns segundos/minutos (num ambiente de teste), o operador possa atualizar a tela e ver:
   - nova execução na lista de runs;
   - métricas atualizadas para aquele run.

Esse é o caminho dourado da Fase 3: provar que UI, API, jobs e metrics estão conversando.

---

### 4.19 Comportamento esperado de `bin/s31_g3_console_and_observability.sh`

O gate G3 valida que o Console de Fontes v2 **existe e funciona** no mínimo que a S31 promete.

O script deve, no mínimo:

1. **Preparar ambiente**
   - garantir que G1 e G2 já foram executados (ou executar as partes necessárias);
   - subir backend/API em modo teste (ex.: via `uvicorn`/`gunicorn`/comando do framework);
   - subir frontend em modo CI (build ou testes E2E, conforme padrão do projeto).

2. **Testar APIs de Console**
   - rodar testes automatizados que:
     - criam um perfil via API;
     - listam perfis e verificam que o novo aparece;
     - chamam `run-now` e verificam que job é enfileirado;
     - consultam detalhes do perfil depois de um run de teste.

3. **Testar UI básica**
   - rodar testes de UI (unitários ou E2E) que validem:
     - render da lista de providers;
     - render da lista de perfis;
     - render do detalhe de um perfil com execuções fictícias;
     - fluxo de criação/edição de perfil.

4. **Verificar observabilidade na UI (mínimo)**
   - garantir que, para ao menos um perfil-piloto, a tela de detalhe:
     - exibe últimas execuções com dados reais (vindos dos runs de G2 / runs extras de G3);
     - exibe um número coerente de calls/items/budget_usage.

5. **Gerar evidências**
   - salvar:
     - `out/evidence/S31_G3_console/front_tests.log` (resultados de testes front);
     - `out/evidence/S31_G3_console/api_tests.log` (resultados de testes API/Console);
     - opcionalmente, screenshots ou dumps de HTML em um subdiretório.

6. **Gerar scorecard G3**
   - escrever `out/scorecards/S31_G3_observabilidade.json` com campos mínimos:
     - `gate_id`: `"S31-G3"`;
     - `status`: `"PASS"`, `"WARN"` ou `"FAIL"`;
     - `summary`: visão rápida de como está o Console v2;
     - `checks`: lista de checks executados (APIs, E2E, métricas);
     - `issues_detected`;
     - `evidence_paths`.

Critério:

- `PASS`: APIs de Console funcionam, telas básicas renderizam, fluxo "Rodar agora" é comprovadamente funcional para pelo menos um perfil-piloto;
- `WARN`: pequenas falhas de UX/documentação, sem quebrar o fluxo principal;
- `FAIL`: UI indisponível, endpoints instáveis, ou incapacidade de operar perfis por Console.

---

### 4.20 Evidências mínimas da Fase 3

Esperamos encontrar, ao fim da Fase 3:

- `out/evidence/S31_G3_console/front_tests.log`
  - resultados dos testes de frontend (unit/E2E) relacionados ao Console de Fontes v2.

- `out/evidence/S31_G3_console/api_tests.log`
  - resultados dos testes de API para endpoints de Providers/Perfis.

- (Opcional, mas desejável)
  - `out/evidence/S31_G3_console/ui_screenshots/…`
    - screenshots ou dumps de UI usados em debugging.

- `out/scorecards/S31_G3_observabilidade.json`
  - veredito estruturado do gate G3.

Além disso, o time deve ser capaz de demonstrar, manualmente se necessário:

- listagem de providers;
- listagem de perfis-piloto;
- detalhe de perfil com últimas execuções;
- acionamento de "Rodar agora" via UI e observação do efeito.

---

### 4.21 Riscos específicos desta fase e mitigação

1. **Divergência entre API e UI**  
   Sintoma: UI espera campos que a API não entrega (ou vice-versa).
   
   Mitigação: congelar contratos antes; usar types/DTOs compartilhados quando possível; testes E2E que não passem se a UI falhar silenciosamente.

2. **UI enganosa em relação a métricas**  
   Sintoma: UI mostra números que não batem com logs/DB, confundindo operadores.
   
   Mitigação: construir a primeira versão da UI diretamente em cima das métricas/logs usados em G2; revisar com o time de backend se os valores exibidos são coerentes.

3. **Flow “Rodar agora” frágil**  
   Sintoma: botão parece funcionar, mas job não é enfileirado, ou erro não é comunicado.
   
   Mitigação: testes E2E específicos para esse fluxo; logs adicionais no endpoint e no job; feedback claro na UI em caso de falha.

4. **Testes de UI frágeis ou inexistentes**  
   Sintoma: qualquer mudança mínima quebra tudo, ou ninguém percebe regressão.
   
   Mitigação: focar em poucos fluxos críticos (lista, detalhe, criação, run-now) e cobri-los bem; não tentar automatizar cada microdetalhe de UI na S31.

---

### 4.22 Resultado esperado ao fim da Fase 3

Quando a Fase 3 estiver concluída de verdade, o estado alvo é:

- qualquer operador autorizado consegue:
  - ver a lista de Providers;
  - ver a lista de Perfis;
  - inspecionar detalhes de um perfil-piloto;
  - acionar um run de teste para esse perfil via UI;
  - enxergar, pela UI, que o run aconteceu (última execução, contagens básicas).
- as APIs de Console existem, são estáveis e têm cobertura mínima de testes;
- o gate S31-G3 está verde (ou WARN bem justificado), com evidências e scorecard em seu lugar;
- Cap.3 (Bloco 3 — frontend & Console v2) e este Bloco 4 descrevem exatamente o que foi implementado.

Com isso, a Sprint 31 entra na reta final: a Fase 4 pode amarrar legado, Programas 2–3 e ORR, fechando o ciclo provider-first para o domínio piloto.

