# Inspectah — Sprint 32
## Capítulo 3 — Bloco 1
### Visão de Arquitetura de Alto Nível (Truth-DB, Blocos & Contestação v1)

> Este bloco responde à pergunta: **“onde, em termos de arquitetura, a Sprint 32 mexe?”** Ele amarra o Capítulo 1 (intenção) e o Capítulo 2 (gates/SA) em um desenho coerente de componentes.

---

#### 3.1.1 Domínios tocados pela S32

A Sprint 32 atua em quatro domínios principais do backend do Inspectah:

1. **Domínio de Verdade (Truth-DB & Sistema de Blocos)**  
   - Onde vivem `FactBlock`, `EvidenceBlock`, `DecisionBlock`, `TruthState` e registros de contestação.  
   - É o núcleo responsável por materializar “o que o Inspectah considera verdadeiro, contestado ou rejeitado”, com trilha auditável.

2. **Domínio de Claims & Entidades (Programa 2)**  
   - Onde vivem as claims estruturadas que chegam do pipeline de ingestão/interpretação.  
   - A S32 não redesenha esse domínio, mas depende fortemente dele para o tipo de claim prioritário.

3. **Domínio de Serviços de Fluxo (Promoção & Contestação)**  
   - Onde ficam os serviços que orquestram a passagem de uma claim por blocos e estados de verdade, e a contestação desses estados.  
   - Aqui ficam `PromotionService`, `ContestationService` e, se necessário, adaptadores auxiliares.

4. **Domínio de Observabilidade & Gates**  
   - Onde vivem métricas, logs e scripts `bin/s32_gX_*.sh`.  
   - Faz a ponte entre o comportamento do Truth-DB e o painel de saúde da plataforma.

A arquitetura da S32 não inventa um novo sistema à parte; ela acopla esses domínios dentro do monólito/backend existente, respeitando o que já foi decidido nos Programas 1–4.

---

#### 3.1.2 Componentes centrais (caixas e responsabilidades)

A visão de alto nível pode ser lida como quatro caixas principais:

1. **Caixa “Models & Storage (Truth-DB)”**  
   - Responsável por:
     - definir as tabelas e relações do Truth-DB (blocos, estados, contestações);  
     - aplicar migrações S32 no banco;  
     - garantir invariantes estruturais via schema/ORM.
   - Arquivos típicos:  
     - `app/truthdb/models.py`  
     - `migrations/versions/XXXX_s32_truthdb_blocks.py`

2. **Caixa “Services & Flows (Promotion & Contestation)”**  
   - Responsável por:
     - consumir claims do Programa 2;  
     - construir blocos (`FactBlock`, `EvidenceBlock`);  
     - manter/atualizar `TruthState`;  
     - registrar e processar contestações;  
     - emitir métricas e acionar logs relevantes.
   - Arquivos típicos:  
     - `app/truthdb/services.py` (ou similar)  
     - opcionalmente `app/claims/adapters_truthdb.py` para mapear claims → blocos.

3. **Caixa “Metrics & Observability (Truth-DB telemetry)”**  
   - Responsável por:
     - expor funções utilitárias para registrar as métricas mínimas da S32;  
     - integrar com o client/stack de métricas do Programa 1;  
     - evitar duplicação de lógica de métricas espalhada pelos serviços.
   - Arquivo típico:  
     - `app/truthdb/metrics.py`

4. **Caixa “Tests, Gates & Evidence”**  
   - Responsável por:
     - testes de modelos, invariantes, promoção e contestação;  
     - scripts de gates S32_G0–S32_G4 em `bin/`;  
     - diretórios `out/scorecards/`, `out/evidence/` e `out/bundles/` específicos da S32.
   - Arquivos/diretórios típicos:  
     - `tests/truthdb/test_models_and_invariants.py`  
     - `tests/truthdb/test_promotion_flows.py`  
     - `tests/truthdb/test_contestation_flows.py`  
     - `bin/s32_g*.sh`  
     - `out/scorecards/S32_*.json`, `out/evidence/S32_GX_*/`, `out/bundles/inspectah_s32_evidence_bundle.zip`

---

#### 3.1.3 Limites arquiteturais: o que a S32 NÃO faz

Para manter a S32 focada e executável, a visão de arquitetura inclui fronteiras explícitas:

- **Não cria um microserviço novo só para o Truth-DB.**  
  O Truth-DB é um módulo interno. Se um dia virar serviço, será em outra sprint, com outro contexto.

- **Não recria o domínio de claims.**  
  A S32 parte do que o Programa 2 já entrega; no máximo, adiciona adaptadores ou ajustes pequenos.

- **Não desenha UIs complexas de casos, narrativas e painéis avançados.**  
  Esses elementos ficam para S33+ / Programa 4. Aqui o foco é motor de verdade + contestação.

- **Não resolve sharding, multi-região ou otimizações extremas de performance.**  
  A S32 precisa ser razoavelmente eficiente, mas não transforma Truth-DB em engine distribuído global.

---

#### 3.1.4 Como esta visão se conecta aos Capítulos 1 e 2

- O **Capítulo 1** disse “o que” a S32 precisa fazer (fluxo claim → verdade → contestação, invariantes, bundle).  
- O **Capítulo 2** disse “como cobramos isso” (SA32_x, gates, métricas, GO/NO-GO).  
- Este Bloco 1 do Capítulo 3 diz **“onde isso mora na arquitetura”**:
  - quais módulos recebem claims;  
  - onde os blocos são criados;  
  - onde os estados de verdade são mantidos;  
  - onde contestações são registradas;  
  - por onde métricas saem;  
  - como os gates enxergam tudo isso.

Nos próximos blocos do Capítulo 3, essa visão de alto nível será refinada em:
- modelos e migrações concretas (3.2 – dados & schema);  
- serviços e fluxos detalhados (3.3);  
- filemap exato para o repositório (3.4+).

Este Bloco 1 funciona como mapa mental e contrato de fronteiras: qualquer novo componente proposto na S32 deve se encaixar claramente em uma dessas caixas ou justificar, no Capítulo 6, por que existe fora delas.

