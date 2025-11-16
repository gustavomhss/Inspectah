# Inspectah — Sprint 4 — Modelo de Dados e Invariantes (Gate T1)

Gate T1 transforma a visão da Sprint 4 em um contrato formal de objetos, relacionamentos e invariantes. Este documento é a referência viva para qualquer pessoa que precise entender como Fonte, Run, Item, Evidência e Consulta se encadeiam.

## Camadas oficiais

1. **Ingestão (Input)**  
   - Responsável por conectar cada Fonte P0 (ex.: `api_market_prices`, `html_market_watch`, `rss_news_minimal`) aos conectores de coleta.  
   - Define cadência alvo, autenticação, políticas de deduplicação e saneamento básico antes de criar um Run.  
   - Invariantes tocados: #2 (rastreamento Fonte→Run) e #7 (nada configurado apenas em código).

2. **Evidence Vault (Truth)**  
   - Persistência versionada de Runs, Itens e pacotes de Evidência completos (bruto + extraído + metadados + hash).  
   - Aplica idempotência e trilhas de auditoria; todo Item aponta para sua Evidência e vice-versa.  
   - Invariantes tocados: #1 (Nenhum Item P0 sem Evidência completa), #2 e #5 (fixtures/goldens reais).

3. **Exploração (View)**  
   - APIs e Explore M0 consumindo o Vault para consultas humanas.  
   - Implementa filtros seguros e garante que cada resultado possui link direto para a Evidência correspondente.  
   - Invariantes tocados: #3 (Fontes visíveis em observabilidade), #4 (Explore nunca mostra Item sem evidência), #6 (quebras detectadas em tempo finito).

## Objetos centrais e relacionamentos

| Objeto | Descrição | Campos obrigatórios | Relacionamentos chaves | Invariantes/SLOs afetados |
| --- | --- | --- | --- | --- |
| **Fonte** | Definição estável da origem P0 | `source_id`, `nome`, `tipo`, `cadencia_min`, `owner`, `risk_notes`, `field_profile` | 1→N Runs; 1→N Consultas padrão; cadastra Field Designer | Inv. #2, #3, #5, #7; SLO `onboarding_p50_min` |
| **Run** | Execução concreta de coleta | `run_id`, `source_id`, `started_at`, `finished_at`, `status`, `input_manifest`, `operator` | N→N Itens; 1 Run pertence a 1 Fonte | Inv. #1, #2, #6; SLO `run_success_rate`, `detection_latency_p95_min` |
| **Item** | Unidade normalizada de informação extraída de um Run | `item_id`, `run_id`, `source_id`, `canonical_key`, `observed_at`, `payload_normalized` | 1 Item tem 1 pacote de Evidência; aparece em Consultas | Inv. #1, #2, #4, #5; SLO `evidence_completeness_rate` |
| **Evidência** | Pacote completo: bruto, extraído, metadados, hash, manifesto | `evidence_id`, `item_id`, `hash_sha256`, `payload_raw`, `payload_extracted`, `metadata`, `checksum_manifest`, `storage_path` | 1→1 com Item; referenciado por Consultas e auditorias | Inv. #1, #2, #5; SLO `evidence_completeness_rate` |
| **Consulta** | Combinação de filtros e ordenações usadas por Explore/analistas | `query_id`, `source_scope`, `filters`, `sort`, `executed_by`, `latency_ms`, `result_count`, `evidence_links` | Mapeia para subconjuntos de Itens/Evidências; referência para logs/observabilidade | Inv. #3, #4, #6; SLO `explore_query_p95_ms`, `detection_latency_p95_min` |

### Regras de relacionamento

- **Fonte → Run:** cada Run precisa apontar para exatamente uma Fonte; sem `source_id` válido, o Run é inválido (T2 e T3 bloqueiam).  
- **Run → Item:** Runs podem gerar zero ou muitos Itens; cada Item retém `run_id` e `source_id` para rastreabilidade e para o cálculo de `run_success_rate`.  
- **Item → Evidência:** relação 1:1. Se um Item não possui Evidência completa, quebra direta do Invariante #1 e do SLO `evidence_completeness_rate`.  
- **Consulta → Item/Evidência:** consultas apenas retornam Itens cujo pacote de Evidência está íntegro. Links quebrados disparam alertas em T6/T7 e afetam o SLO `explore_query_p95_ms`.

## Ligações formais entre invariantes, objetos e SLOs

1. **Inv. #1 — Nenhum Item P0 sem Evidência completa**  
   - Objetos: Item + Evidência.  
   - SLO: `evidence_completeness_rate = 100%`.  
   - Gates responsáveis: preparação em T1 (este documento), validação prática em T3/T4/T5/T6.

2. **Inv. #2 — Toda Evidência rastreável à Fonte e ao Run**  
   - Objetos: Fonte, Run, Item, Evidência.  
   - SLOs: `run_success_rate`, `detection_latency_p95_min`.  
   - Regras: `evidence.metadata` precisa conter `source_id` e `run_id`; manifestos do Vault mantêm encadeamento.

3. **Inv. #3 — Nenhuma Fonte P0 ativa invisível em métricas/logs**  
   - Objetos: Fonte, Run, Consulta.  
   - SLOs: `run_success_rate`, `detection_latency_p95_min`.  
   - Preparação aqui define quais métricas cada Fonte deve emitir (ex.: `runs_total{source=...}`).

4. **Inv. #4 — Explore M0 nunca mostra Item sem Evidência**  
   - Objetos: Item, Evidência, Consulta.  
   - SLO: `explore_query_p95_ms` (tempo e conteúdo).  
   - Requisito: Query engine consulta sempre `evidence_links` antes de montar resposta.

5. **Inv. #5 — Fixtures do ORR vêm de dados reais e são versionadas**  
   - Objetos: Fonte, Run, Item, Evidência.  
   - Preparação: Field Designer + manifestos de coleta definem os campos críticos antes de gerar fixtures na Trilha B.

6. **Inv. #6 — Quebras relevantes detectadas em tempo finito**  
   - Objetos: Run, Consulta, Fonte.  
   - SLOs: `run_success_rate`, `detection_latency_p95_min`.  
   - Este documento fixa quais sinais são obrigatórios (latência, staleness, erros) por Fonte para T6 medir.

7. **Inv. #7 — Nenhum ajuste estrutural em Fonte P0 apenas em código**  
   - Objetos: Fonte e Field Designer (vista como extensão da Fonte).  
   - Requisito: toda mudança passa pelo registry oficial em `config/sources/sprint_4/fontes_p0/*.yaml` e respectivos perfis de campo.

## Rastreamento ponta-a-ponta

```
Fonte(api_market_prices) 
  └─ Run(run-2025-11-15T10:00Z)
       └─ Item(item-uuid, canonical_key=sku123)
            └─ Evidência(evidence-uuid, hash=sha256:...)
                 └─ Consulta(query-id-42) -> anexos de evidência observáveis em Explore
```

Esse encadeamento é obrigatório em todos os ambientes; qualquer etapa faltante significa gate T1 falhando e impede avanço para T2.
