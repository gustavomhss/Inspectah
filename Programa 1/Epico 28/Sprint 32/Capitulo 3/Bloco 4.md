# Inspectah — Sprint 32
## Capítulo 3 — Bloco 4
### Filemap Final, Dependências, Não-funcionais & Decisões Arquiteturais da S32

> Este bloco fecha o Capítulo 3 transformando a visão arquitetural em um **filemap final**, deixa claras as dependências com outros Programas e registra decisões não-funcionais e trade-offs conscientes da Sprint 32.

---

#### 3.4.1 Filemap final da Sprint 32 (foco em Truth-DB & Contestação)

Abaixo, o filemap consolidado da S32, destacando apenas arquivos novos ou diretamente impactados.

```text
Inspectah/
  app/
    truthdb/
      __init__.py
      models.py                 # Modelos Truth-DB: FactBlock, EvidenceBlock, TruthState, DecisionBlock, ContestRecord
      services.py               # PromotionService e ContestationService (fluxos centrais da S32)
      metrics.py                # Funções auxiliares para emissão de métricas do Truth-DB
      repositories.py           # (Opcional) Repositórios para acesso a dados de blocos/estados/contestações

    claims/
      models.py                 # Modelos de claim já existentes (Programa 2)
      adapters_truthdb.py       # (Novo/ajustado) Helpers para mapear claims → FactBlock/EvidenceBlock

  migrations/
    versions/
      XXXX_s32_truthdb_blocks.py  # Migração criando/alterando tabelas para Truth-DB & Sistema de Blocos

  tests/
    truthdb/
      __init__.py
      test_models_and_invariants.py    # Invariantes estruturais dos modelos Truth-DB
      test_promotion_flows.py          # Fluxo claim → blocos → estado de verdade (PromotionService)
      test_contestation_flows.py       # Fluxo de contestação end-to-end (ContestationService)

  bin/
    s32_g0_scope_and_baseline.sh      # Gate de estrutura/documentação
    s32_g1_models_and_invariants.sh   # Gate de schema + invariantes
    s32_g2_promotion_flows.sh         # Gate de fluxo de promoção
    s32_g3_contestation_flows.sh      # Gate de fluxo de contestação
    s32_g4_orr_and_bundle.sh          # Gate de ORR + bundle de evidências

  docs/
    sprint_32_capitulo_1_contexto.md
    sprint_32_capitulo_2_gates_e_metricas.md
    sprint_32_capitulo_3_arquitetura_e_filemap.md
    sprint_32_capitulo_4_execucao_e_evidencias.md
    sprint_32_capitulo_5_orr_operacao_pos_sprint.md
    sprint_32_capitulo_6_learnings_e_anti_gaps.md
    sprint_32_capitulo_7_tasks.md

  out/
    scorecards/
      S32_G0_scope_and_baseline.json
      S32_G1_models_and_invariants.json
      S32_G2_promotion_flows.json
      S32_G3_contestation_flows.json
      S32_G4_orr_and_bundle.json

    evidence/
      S32_G1_models_and_invariants/
      S32_G2_promotion_flows/
      S32_G3_contestation_flows/

    bundles/
      inspectah_s32_evidence_bundle.zip
```

Regras implícitas:
- Arquivos `docs/sprint_32_*.md` são a versão "materializada" dos capítulos da S32.  
- `models.py`, `services.py`, `metrics.py` e `repositories.py` devem seguir o padrão de estilo/naming do backend atual.  
- Scripts em `bin/` seguem a convenção das sprints anteriores (S20–S31) para gates e ORR.

---

#### 3.4.2 Dependências explícitas com outros Programas

Programa 1 — Data Hub & Operação 24/7
- Reuso de stack de métricas (Prometheus/OpenTelemetry, ou equivalente) para o módulo `truthdb/metrics.py`.  
- Reuso de padrões de logging estruturado já definidos para outros subsistemas.  
- Potencial integração com healthchecks: a S32 pode registrar um healthcheck mínimo do Truth-DB (ex.: consulta simples em `fact_blocks`/`truth_states`).

Programa 2 — Claims, Entidades & Sinais
- S32 depende de:
  - modelo de claim para o tipo prioritário (já definido em `app/claims/models.py`);  
  - capacidade de obter claims para promoção (repositórios ou serviços existentes).  
- O arquivo `claims/adapters_truthdb.py` é a principal ponte de mapeamento claim → FactBlock/EvidenceBlock.

Programa 3 — Sistema de Blocos & Truth-DB (blueprints anteriores)
- S32 materializa a **v1 operacional** do blueprint: blocos/fatos/estados/contestações deixam de ser apenas design conceitual.  
- Decisões simplificadas de S32 (por exemplo, tipos de status, campos mínimos) devem ser documentadas no Capítulo 6 para futuras extensões do Programa 3.

Programa 4 — Exposição, Produtos & UIs
- A S32 não entrega telas complexas, mas:
  - estabelece o contrato de consulta interna (via modelos/repos) que Programas futuros usarão para construir:  
    - battlefield de narrativas;  
    - Fact Cards;  
    - painéis "Quem ganha com isso?";  
    - etc.

---

#### 3.4.3 Aspectos não-funcionais relevantes para a S32

Performance
- Fluxos de promoção e contestação devem ser **razoavelmente rápidos**, mas a S32 não otimiza para milhões de eventos/dia.  
- A métrica `truthdb_flow_latency_p95` deve mostrar tempos aceitáveis em cenários de teste (ordem de centenas de milissegundos ou poucos segundos, conforme o caso).  
- Índices em FKs (`claim_id`, `truth_state_id`, `fact_block_id`) são obrigatórios para evitar consultas patéticas.

Escalabilidade
- Modelos e schema são pensados para crescer:  
  - uso de IDs simples/UUIDs;  
  - campos `metadata` para extensões de baixo risco;  
  - separação clara entre blocos, estados e contestações.

Confiabilidade & integridade
- Invariantes estruturais (sem blocos órfãos, estados finais com DecisionBlock, histórico monotônico) são priorizadas acima de micro-otimizações.  
- Em caso de dúvida entre performance e integridade, a S32 escolhe **integridade**.

Observabilidade
- Métricas mínimas definidas no Capítulo 2/Bloco 3 são tratadas como parte da arquitetura, não como “extra”.  
- Falhas de fluxo devem ser visíveis via `truthdb_flow_error_rate` e logs estruturados.

Testabilidade
- Serviços são projetados para serem testáveis isoladamente:  
  - dependências (db_session, metrics_client) injetáveis;  
  - funções puras onde possível (ex.: mapeamento claim → bloco).

---

#### 3.4.4 Decisões arquiteturais explícitas (registro da S32)

Decisão A — Truth-DB como módulo interno (não microserviço)
- Motivo: reduzir complexidade operacional na fase inicial, reaproveitando infra de DB, CI, métricas e deploy existente.  
- Implicação: latência de consulta interna é baixa; acoplamento com restante do backend é maior, mas aceitável nesta fase.

Decisão B — Serviços finos, não monolíticos
- `PromotionService` e `ContestationService` focam em orquestrar blocos/estados, delegando I/O e detalhes de DB a ORM/repos.  
- Facilita testes unitários e substituição de estratégias de decisão no futuro.

Decisão C — Uso moderado de `metadata`/JSON
- Campos `metadata` são permitidos em blocos, estados e contestações, mas o núcleo do domínio (IDs, FKs, status) permanece em colunas fortes.  
- Evita explosão de migrações para mudanças menores, sem transformar o banco em dumping ground de JSON.

Decisão D — Testes como parte da arquitetura
- Arquivos `tests/truthdb/*.py` são tratados como componente crítico: sem eles, as invariantes da S32 não são verificáveis.  
- Gates G1–G3 dependem diretamente desses testes.

Decisão E — Bundle como artefato de primeira classe
- O bundle `inspectah_s32_evidence_bundle.zip` é parte da arquitetura operacional do Truth-DB: ele encapsula scorecards, logs e snapshots necessários para reexecutar decisões e investigações futuras.

---

#### 3.4.5 Como usar este Bloco 4 na prática

Para o time de engenharia
- Como blueprint final de “onde criar/editar arquivos” ao implementar a S32.  
- Como referência de não-funcionais mínimos (performance, integridade, observabilidade).

Para o Codex/automatizações
- Como mapa para geração de código, testes e scripts sem inventar caminhos alternativos ou estruturas de pasta divergentes.

Para o conselho/ORR
- Como documentação das decisões arquiteturais e trade-offs, ajudando a interpretar se uma eventual alteração posterior está respeitando o espírito da S32.

Com este Bloco 4, o Capítulo 3 fica fechado: a Sprint 32 passa a ter um desenho arquitetural completo, com filemap, integrações, não-funcionais e decisões explícitas que sustentam o núcleo de verdade e contestação do Inspectah.