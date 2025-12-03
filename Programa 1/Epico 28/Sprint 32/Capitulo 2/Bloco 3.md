# Inspectah — Sprint 32
## Capítulo 2 — Bloco 3
### Métricas & Observabilidade do Truth-DB (state of the art para S32)

> Este bloco desce o nível em **como o Truth-DB aparece no painel de saúde do Inspectah**: quais métricas são obrigatórias, onde são emitidas, como validar e como isso se conecta aos gates da S32.

---

#### 2.3.1 Princípios de observabilidade específicos da S32

A S32 não tem a pretensão de resolver toda a observabilidade do Inspectah, mas coloca um padrão mínimo e sério para o Truth-DB:

1. **Sem métrica, não existe “saúde”**  
   Se não dá para ver promoção, contestação, erros e latência em algum painel/log estruturado, então o Truth-DB não está “saudável”, está apenas “silencioso”.

2. **Métrica nasce junto com o fluxo**  
   Cada novo fluxo central (promoção, contestação) já deve vir com pontos de emissão de métricas definidos e implementados.

3. **Stack única de observabilidade**  
   O Truth-DB usa a mesma stack do Programa 1 (ex.: OpenTelemetry + Prometheus + Loki/Grafana ou equivalente). Nada de inventar um “mini-sistema paralelo” só para S32.

4. **Métricas atômicas, não novela**  
   As métricas obrigatórias da S32 são poucas, mas bem definidas. O resto pode ser explorado nas próximas sprints.

---

#### 2.3.2 Métrica 1 — `truthdb_promotion_success_rate`

**O que mede:**  
Proporção de promoções bem-sucedidas sobre o total de tentativas de promoção, segmentada por tipo de claim.

**Especificação mínima:**

- **Nome:** `truthdb_promotion_success_rate`  
- **Dimensões (labels):**  
  - `claim_type` (ex.: `news_fact_simple`);  
  - `env` (dev, staging, prod);  
  - opcionalmente `source` (classe da fonte, se fizer sentido).
- **Tipo:**  
  - Pode ser implementada como duas métricas contadoras (`promotions_total`, `promotions_success_total`) e um painel que mostra o rate; ou  
  - Como um gauge/histogram derivado de contadores.

**Pontos de emissão:**

- No `PromotionService`, em lugares bem definidos:  
  - logo antes de tentar promover uma claim (incrementando `promotions_total`);  
  - logo após uma promoção bem-sucedida (incrementando `promotions_success_total`);  
  - em caso de erro, opcionalmente registrar em `truthdb_flow_error_rate`.

**Validação em S32:**

- Gate G2 (`S32_G2_promotion_flows`) deve, ao menos, verificar que essas métricas foram emitidas durante o teste (por exemplo, via logs/endpoint de métricas em ambiente de teste).  
- Capítulo 5 deve mostrar como visualizar a métrica em um painel.

---

#### 2.3.3 Métrica 2 — `truthdb_contestation_rate`

**O que mede:**  
Volume de contestações registradas em uma janela de tempo, segmentado por tipo de claim/caso.

**Especificação mínima:**

- **Nome:** `truthdb_contestation_rate` (implementada sobre contadores).  
- **Dimensões:**  
  - `claim_type` ou `case_type`;  
  - `env`;  
  - opcionalmente `contest_outcome` (mantido, alterado, rejeitado, etc.).
- **Tipo:** contador (`contests_total`), com dashboards mostrando evolução ao longo do tempo.

**Pontos de emissão:**

- No serviço de contestação, no ato de registrar uma contestação válida.  
- Opcionalmente, em etapas internas do fluxo (ex.: contestação aceita para processamento → outro contador).

**Validação em S32:**

- Gate G3 (`S32_G3_contestation_flows`) deve produzir, pelo menos, um conjunto pequeno de contestações em ambiente de teste e verificar que a métrica foi atualizada.  
- O ORR deve ter pelo menos uma captura de tela ou descrição de como essa métrica aparece no painel.

---

#### 2.3.4 Métrica 3 — `truthdb_flow_error_rate`

**O que mede:**  
Quantidade de erros por etapa dos fluxos centrais do Truth-DB (promoção, contestação, gravação de blocos, migrações, etc.).

**Especificação mínima:**

- **Nome:** `truthdb_flow_error_rate` (novamente, implementada sobre contadores, ex.: `truthdb_flow_errors_total`).  
- **Dimensões:**  
  - `flow_stage` (ex.: `promotion`, `contestation`, `block_persist`, `migration`);  
  - `env`;  
  - opcionalmente `error_type` (categories de erro relevantes).

**Pontos de emissão:**

- No `PromotionService`, em qualquer exceção significativa que impeça promoção.  
- No fluxo de contestação, sempre que uma contestação falha por erro técnico.  
- Em migrações, se houver falhas capturadas em scripts ou ferramentas.

**Validação em S32:**

- G2 e G3 devem forçar, pelo menos em um cenário de teste, alguma condição de erro previsível para garantir que a métrica registra algo.  
- O painel não precisa ser bonito, mas deve permitir ver se há spikes de erro.

---

#### 2.3.5 Métrica 4 — `truthdb_flow_latency_p95`

**O que mede:**  
Latência p95 de um fluxo completo claim → estado de verdade, em cenários de teste controlados.

**Especificação mínima:**

- **Nome:** `truthdb_flow_latency_seconds` (histograma), a partir do qual o p95 é derivado no painel.  
- **Dimensões:**  
  - `flow_type` (ex.: `promotion`, `contestation`);  
  - `env`.

**Pontos de medição:**

- Ao entrar no fluxo de promoção, marcar timestamp inicial.  
- Ao finalizar (com sucesso ou falha), observar o histograma com a duração daquela execução.  
- Idem para contestação (ao menos em um fluxo principal).

**Validação em S32:**

- G2 e/ou G3 podem imprimir um sumário dos valores de latência observados durante os testes.  
- O Capítulo 5 deve referenciar pelo menos um painel/gráfico em que esse p95 apareça (mesmo que em ambiente de teste).

---

#### 2.3.6 Implementação de métricas — diretrizes práticas

1. **Usar o mesmo client/lib de métricas do resto da plataforma**  
   - Se o backend já exporta métricas via OpenTelemetry ou client específico de Prometheus, o Truth-DB deve apenas **adotar esse padrão**.

2. **Evitar lógica de negócio “escondida” em métricas**  
   - Métricas servem para observar; decisões de negócio continuam no código principal ou nos blocos, não em queries de painel.

3. **Campos e nomes estáveis**  
   - Nomes de métricas e labels definidos na S32 devem ser tratados como API interna estável. Mudanças futuras precisam de migração/documentação.

4. **Documentação mínima**  
   - Capítulo 5 deve incluir uma pequena seção “Como ver se o Truth-DB está saudável agora?” com referências diretas às métricas definidas neste bloco.

---

#### 2.3.7 Relação com states-alvo e gates

- **SA32_4** é diretamente cumprido por este bloco: as métricas aqui definidas são o núcleo da observabilidade mínima do Truth-DB.  
- **G2 e G3** devem, explicitamente, validar emissão e comportamento básico dessas métricas.  
- **G4** garante que qualquer instrução de ORR e o bundle incluam pelo menos um pointer claro para visualizar essas métricas.

Com este Bloco 3, o Capítulo 2 amarra o Truth-DB ao stack de observabilidade, garantindo que promoção e contestação não sejam caixas pretas silenciosas, mas motores com luz de painel acesa desde a S32.