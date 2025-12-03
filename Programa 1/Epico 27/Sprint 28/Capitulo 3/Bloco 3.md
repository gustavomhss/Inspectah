# Inspectah — Sprint 28
## Capítulo 3 — Bloco 3
### Ingestão 2.0 & Scheduler em detalhe — comportamento ON/OFF, IngestionRun e observabilidade mínima

---

#### 3.3.1 Papel da Ingestão 2.0 na Sprint 28

Na Sprint 28, a Ingestão 2.0 não está sendo reinventada: ela já existe desde sprints anteriores (S22). O que muda é a **forma como o estado da fonte passa a governar o comportamento da ingestão**.

E27.1 exige que:

1. O domínio de fontes (`Source`) seja a **fonte de verdade** para decidir se uma fonte deve ou não ser ingerida.  
2. O estado `Source.state` (`ACTIVE`/`DISABLED`/`DEPRECATED`) e o `Source.mode` (`AUTO`/`MANUAL`) passem a ser **primeiros cidadãos** da lógica de seleção de fontes.  
3. O comportamento ON/OFF seja **determinístico** e verificável via testes (Gate S28_G4) e via demo (Gate S28_G6).

Ou seja, a Sprint 28 é a sprint em que o scheduler passa a respeitar, sem ambiguidade, a operação feita no console/API.

---

#### 3.3.2 Contrato de "fontes elegíveis" para ingestão automática

A lógica de seleção de fontes para ingestão automática pode ser resumida em um contrato claro:

> Uma fonte é elegível para ingestão automática se, e somente se:
> - `mode = AUTO`,
> - `state = ACTIVE`,
> - e todos os demais critérios de elegibilidade herdados de S22 forem satisfeitos.

Critérios herdados de S22 (exemplos, ajustáveis ao que já existe no código real):
- A fonte não está marcada com algum flag de suspensão global (se o sistema tiver esse conceito).  
- A fonte está dentro de uma janela de tempo válida, caso exista configuração de janelas (ex.: não ingerir de madrugada).  
- A configuração `config` da fonte está minimamente válida (URL não vazia, etc.).

Fontes **não elegíveis**:
- `state = DISABLED` → **nunca** deve ser considerada pelo scheduler, independentemente de `mode`.  
- `state = DEPRECATED` → tratada como fora de circulação para ingestão regular (pode ser usada apenas para consultas históricas ou migrações; fora de escopo da S28).  
- `mode = MANUAL` → mesmo que `ACTIVE`, a ingestão automática não deve ser acionada (apenas modos manuais futuros).

Esse contrato precisa ser refletido em:
- consultas de banco (queries do scheduler),  
- testes de integração (`test_sources_ingestion_onoff.py`),  
- documentação (Cap. 2 e Cap. 3).

---

#### 3.3.3 Módulo de scheduler e fluxo interno

**Localização esperada**  
`app/ingestion/scheduler.py`

Responsabilidades do módulo de scheduler:

1. Obter a lista de fontes elegíveis para ingestão automática.  
2. Para cada fonte elegível, produzir um ou mais `IngestionRun` que serão executados pelo pipeline de ingestão.  
3. Garantir que fontes não elegíveis (DISABLED/DEPRECATED, MANUAL) sejam **ignoradas**.

Um fluxo conceitual (pseudo-código) pode ser descrito assim:

```python
# app/ingestion/scheduler.py (pseudo-código conceitual)

def get_auto_eligible_sources(db_session) -> list[Source]:
    return (
        db_session.query(Source)
        .filter(Source.mode == SourceMode.AUTO)
        .filter(Source.state == SourceState.ACTIVE)
        # + quaisquer filtros adicionais de S22 (janela, flags, etc.)
        .all()
    )


def run_scheduler_cycle(db_session):
    sources = get_auto_eligible_sources(db_session)

    for source in sources:
        create_ingestion_run_for_source(db_session, source)
        # lógica de enfileirar/dispatch para worker da ingestão
```

Pontos importantes:
- As regras de `mode` e `state` são **linhas de corte**, não "sugestões".  
- A função `get_auto_eligible_sources` deve ser facilmente testável e isolável.  
- Se o sistema tiver camadas de serviço (ex.: `IngestionService`), essa lógica pode estar encapsulada lá, desde que os mesmos critérios sejam usados.

---

#### 3.3.4 Modelo `IngestionRun` e rastreabilidade

A relação entre fontes e ingestões é rastreada via entidade `IngestionRun`.

**Localização típica**  
`app/ingestion/models.py`

Campos esperados (conceituais):
- `id`: identificador único da execução.  
- `source_id`: referência à fonte (`Source.id`).  
- `started_at`, `finished_at`: timestamps de início/fim.  
- `status`: `PENDING`, `RUNNING`, `SUCCESS`, `ERROR` (ou variação equivalente).  
- `error_reason`: mensagem ou código indicando o motivo da falha, se houver.  
- Metadados extras (ex.: número de itens ingeridos).

Relação com a Sprint 28:
- O comportamento ON/OFF será verificado **observando criação (ou não) de `IngestionRun`** quando estados de fonte mudam.  
- `test_sources_ingestion_onoff.py` deve usar essa entidade como parte da evidência de que a ingestão parou/voltou.

---

#### 3.3.5 Tratamento de ON/OFF na prática (com testes)

Os cenários essenciais da Sprint 28 (Gate S28_G4) podem ser recontados aqui sob a ótica da arquitetura:

1. **Criar fonte ativa AUTO e verificar ingestão**  
   - Fonte criada via Admin API com `mode = AUTO`, `state = ACTIVE`.  
   - Scheduler roda → `get_auto_eligible_sources` retorna essa fonte.  
   - Pelo menos um `IngestionRun` é criado (estado inicial `PENDING`/`RUNNING` → `SUCCESS`/`ERROR`).

2. **Desativar fonte e verificar parada**  
   - Fonte desativada via Admin API (`/disable`).  
   - Admin API aplica regras de domínio, atualiza `Source.state` para `DISABLED`.  
   - Scheduler roda → `get_auto_eligible_sources` não inclui mais essa fonte.  
   - Não há novos `IngestionRun` para esse `source_id` a partir dessa desativação.

3. **Reativar fonte e verificar retomada**  
   - Fonte reativada via Admin API (`/activate`).  
   - `state` volta para `ACTIVE` com `state_changed_at` atualizado.  
   - Scheduler roda → fonte volta a aparecer na lista elegível.  
   - Novos `IngestionRun` voltam a ser criados.

4. **Modo MANUAL (proteção mínima)**  
   - Fonte criada com `mode = MANUAL`, `state = ACTIVE`.  
   - Scheduler roda → fonte **não** aparece em `get_auto_eligible_sources`.  
   - Isso protege o sistema de uma ingestão automática acidental em fontes que deveriam ser usadas apenas sob demanda.

Esses cenários devem estar expressos em testes de integração sob `tests/integration/test_sources_ingestion_onoff.py`, usando as mesmas rotas e modelos do mundo real.

---

#### 3.3.6 Testes de integração — estrutura, fixtures e independência

Arquivo principal de testes de integração da S28 para ingestão:

- `tests/integration/test_sources_ingestion_onoff.py`

Características importantes desses testes:

1. **Uso da Admin API para criar e mutar fontes**  
   - Não criar fontes diretamente no banco.  
   - Não trocar estados via `db_session` sem passar pelo domínio/API.  
   - Isso garante que o teste valida o sistema real, não um atalho.

2. **Controle do scheduler em ambiente de teste**  
   - O scheduler deve ser invocado de forma controlada (por função ou comando).  
   - Evitar dependência de jobs assíncronos de longa duração.  
   - Em ambiente de teste, é aceitável usar um modo "single shot" do scheduler (ex.: `run_scheduler_cycle(db_session)`).

3. **Isolamento entre cenários**  
   - Cada cenário (1–4) deve ter seu próprio setup de banco/fixtures.  
   - O estado de uma fonte em um teste não deve vazar para o próximo.

4. **Evidência clara em asserts**  
   - Usar assertions claras em cima de `IngestionRun` (ex.: contagem antes/depois de mudar o estado).  
   - Em cenários de parada: `assert no_new_runs_for_source(source_id, since=disabled_at)`.

Dessa forma, o Gate S28_G4 pode confiar que os testes de integração representam fielmente a arquitetura.

---

#### 3.3.7 Observabilidade mínima ligada à ingestão (sem reinventar S22)

A Sprint 28 não redefine toda a observabilidade de ingestão — isso é trabalho de E27.2/E27.3. Mas alguns cuidados mínimos são necessários:

1. **Logs de ingestão por fonte**  
   - Cada `IngestionRun` deve gerar logs identificáveis (contendo `source_id` ou um identificador de fonte) para permitir troubleshooting básico.  
   - Quando uma fonte é desativada, é interessante ter logs que indiquem mudanças de comportamento (“source X disabled – no further runs scheduled”).

2. **Compatibilidade com métricas existentes (S22)**  
   - Se S22 já expõe métricas de ingestão (ex.: contagem de runs por status, latência média), a S28 não deve quebrá-las.  
   - O Gate S28_G5 (Legacy Sanity) ajuda a garantir isso rodando scripts e conferindo regressões.

3. **Pontos de acoplamento com futuros painéis**  
   - A presença de `criticality`, `domain`, `state` e `mode` em `Source` permite construir no futuro painéis como:  
     - “Fontes críticas desativadas”,  
     - “Tempo médio até reativação”,  
     - “Taxa de erro de ingestão por domínio”.

A S28 apenas garante que não existe retrocesso e que o modelo de dados está pronto para ser explorado em sprints futuras.

---

#### 3.3.8 Riscos arquiteturais e mitigação (foco em ingestão)

Alguns riscos específicos da camada de ingestão nesta sprint:

1. **Risco R1 — Fonte DISABLED ainda sendo ingerida**  
   - Causa: query de seleção de fontes não atualizada, cache, ou atalho em código legado.  
   - Mitigação:  
     - Revisar queries e serviços que selecionam fontes para ingestão.  
     - Cobrir cenário explicitamente em `test_sources_ingestion_onoff.py`.  
     - Validar comportamento em demo (G6) com logs.

2. **Risco R2 — Complexidade acidental no scheduler**  
   - Causa: tentar enfiar lógica de health/score/regras avançadas dentro de S28.  
   - Mitigação:  
     - Limitar escopo de S28 ao básico: `mode`, `state` e critérios já existentes de S22.  
     - Empurrar features mais avançadas explicitamente para E27.2/E27.3.

3. **Risco R3 — Dependência de cron/infra em ambiente de teste**  
   - Causa: testes de integração dependerem do cron real ou de ambiente de worker complexo.  
   - Mitigação:  
     - Oferecer função síncrona para disparar ciclo de ingestão em teste.  
     - Encapsular chamadas em helpers específicos para ambiente de teste.

4. **Risco R4 — Inconsistência entre API e Ingestão**  
   - Causa: atualização de estado via Admin API não sendo imediatamente refletida na leitura usada pelo scheduler (cache sem invalidação, por exemplo).  
   - Mitigação:  
     - Evitar caches complexos nesta sprint;  
     - Se houver caching, garantir invalidação explícita no momento da mudança de estado;  
     - Incluir asserts temporais nos testes, se fizer sentido.

---

Com isso, o Bloco 3 do Capítulo 3 detalha a camada de **Ingestão 2.0 & Scheduler** na Sprint 28: critérios de elegibilidade, fluxo interno, papel de `IngestionRun`, estrutura de testes de integração, observabilidade mínima e riscos arquiteturais. O próximo bloco pode agora fechar o Capítulo 3 com o frontend (console de fontes v2), scripts de gates, CI e o filemap consolidado da sprint.