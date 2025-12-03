# Inspectah — Sprint 31 (E28-S3)
## Capítulo 5 — Bloco 3: Runbooks & Operação Pós-Sprint

### 5.15 Por que runbooks são obrigatórios na S31

A Sprint 31 introduz uma nova peça sensível na operação do Inspectah:

> ingestão provider-first + Console de Fontes v2 para o domínio piloto de notícias BR (e um perfil social).

Isso não pode depender de memória tribal, README solto ou “pergunta para quem implementou”. O risco não é só técnico (quebrar ingestão), é também financeiro (custo de provider) e reputacional (lacunas de cobertura, bugs de dedupe, verdades enviesadas).

Os **runbooks da S31** existem para:

- permitir que qualquer operador designado consiga **monitorar e intervir** na ingestão provider-first sem adivinhação;
- definir o que é um **incidente** aceitável e como reagir (incluindo quando acionar Truth Ops / liderança técnica);
- dar um caminho claro para **frear custo** e **desligar partes da S31** sem afetar o restante do Inspectah.

Este bloco define quais runbooks são obrigatórios, onde vivem, qual estrutura mínima devem seguir e como testá-los na prática antes de considerar a sprint concluída.

---

### 5.16 Conjunto mínimo de runbooks exigidos pela S31

A S31 exige, no mínimo, quatro runbooks formais relacionados a provider-first + Console v2. Todos devem ficar em `docs/runbooks/`, sob controle de versão.

#### 5.16.1 RB1 — Operação de ingestão provider-first (piloto BR)

Arquivo: `docs/runbooks/rb_provider_ingestion_piloto_br.md`

Escopo:

- perfis-piloto BR de news (ex.: `BR_PT_HARD_NEWS`) e social (ex.: `SOCIAL_BR_POLITICA_TIMELINE` ou equivalente);
- ingestão via providers e seus efeitos em `ContentItem` e métricas;
- limites operacionais de uso (budget, frequência, janelas de tempo).

Conteúdo mínimo:

1. **Contexto**
   - descrição curta de quais perfis e providers são considerados “piloto S31”;
   - objetivo da ingestão piloto (cobrir notícias políticas/econômicas BR + sinais sociais relevantes).

2. **Checklist diário (ou por janela de acompanhamento)**
   - quais painéis/metrics olhar (por exemplo: `provider_calls_total`, `items_ingested_total`, `contentitems_created_total`, `errors_total`, `budget_usage_ratio`);
   - quais períodos observar (últimas 24h, última hora, etc.);
   - thresholds que acendem alerta (ex.: taxa de erro > X%, dedupe_ratio em extremos).

3. **Ações em caso de comportamento anômalo**
   - steps para pausar um perfil específico (via Console ou flag de config);
   - steps para reduzir janela ou frequência de ingestão;
   - quando escalar para time técnico (erros persistentes de provider, payloads quebrados, etc.).

4. **Critérios de saúde**
   - o que significa “ingestão saudável” para pilotos (ex.: chamadas regulares, volume coerente com histórico, taxa de erro < Y%, custo dentro do previsto).

#### 5.16.2 RB2 — Operação básica do Console de Fontes v2

Arquivo: `docs/runbooks/rb_console_fontes_operacao_basica.md`

Escopo:

- uso do Console v2 por operadores (não devs);
- fluxos centrais: listar providers, listar perfis, inspecionar perfil, usar “Rodar agora”, pausar/reativar perfil.

Conteúdo mínimo:

1. **Mapa mental da UI**
   - breve descrição das principais telas: lista de providers, lista de perfis, detalhe de perfil;
   - o que cada coluna/indicador significa (especialmente métricas de volume e budget).

2. **Fluxos suportados**
   - “Como localizar um perfil específico e ver seus últimos runs”;  
   - “Como acionar um run manual de teste (Rodar agora) com segurança”;  
   - “Como pausar um perfil sem alterar sua configuração inteira”;  
   - “Como criar/editar um perfil com base em um template existente” (se permitido para operadores).

3. **Boas práticas de operação**
   - não criar perfis com escopo global sem aprovação;  
   - sempre definir `budget_limit_calls` antes de colocar perfis em ACTIVE;  
   - checar impacto estimado (calls/janela) antes de salvar mudanças grandes.

4. **Erros comuns e mensagens típicas**
   - exemplos de mensagens de erro na UI (e o que fazer em cada caso);
   - o que significa quando métricas aparecem vazias ou estão em atraso.

#### 5.16.3 RB3 — Incidentes relacionados a providers (API externa)

Arquivo: `docs/runbooks/rb_incidente_provider_api.md`

Escopo:

- problemas relativos à estabilidade, contrato e limites de uso do provider (news/social);
- respostas de erro (401, 403, 429, 5xx), mudanças em payload, degradação de latência.

Conteúdo mínimo:

1. **Sinais de incidente**
   - aumento súbito em `errors_total` por provider/perfil;
   - logs com erros de autenticação, autorização, rate limit ou schema incompatível;
   - ingestões com volume zero repetidas, sem justificativa aparente.

2. **Passos de diagnóstico**
   - verificar status de provider (status page, comunicação oficial);
   - isolar se o problema é de rede interna, credenciais ou contrato de API;
   - rodar chamadas de teste/simples fora do pipeline (ex.: script manual) para confirmar o problema.

3. **Ações imediatas**
   - reduzir frequência ou escopo de perfis mais pesados;
   - pausar perfis que mais sofrem com o erro, mantendo apenas os mais críticos;
   - registrar incidente em canal adequado (logs internos, ferramenta de incidentes).

4. **Escalonamento**
   - quando abrir chamado formal com o provider;  
   - quando envolver equipe de engenharia/arquitetura;  
   - como registrar impacto em custo, cobertura e confiabilidade.

#### 5.16.4 RB4 — Custo de ingestão explodindo / comportamento anômalo de budget

Arquivo: `docs/runbooks/rb_custo_explodindo_ingestao.md`

Escopo:

- situações em que o consumo de calls/volume de dados por provider foge do esperado;
- profilagem de perfis perigosos e ações para conter custo.

Conteúdo mínimo:

1. **Como detectar**
   - quais métricas olhar (calls totais por provider/perfil, budget_usage_ratio);  
   - sinais de explosão: crescimento abrupto vs histórico, gasto estimado acima de thresholds definidos.

2. **Passos para conter o problema**
   - reduzir janelas de tempo (ex.: de 24h para 1h);
   - reduzir frequência de runs (ex.: de 5min para 30min);
   - pausar perfis experimentais ou menos críticos;
   - limitar ingestão a perfis-piloto enquanto investiga.

3. **Ajustes de longo prazo**
   - refinar filtros de perfis (palavras-chave, idiomas, regiões);
   - separar perfis gigantes em subperfis mais controláveis;
   - revisar contrato com provider (planos, limites, alertas de uso).

4. **Critérios de estabilização**
   - valores de referência de calls/volume por dia para o domínio piloto;  
   - quando considerar custo “sob controle” novamente.

---

### 5.17 Estrutura mínima dos runbooks

Para evitar que cada runbook vire um texto freestyle, todos os runbooks da S31 devem seguir uma estrutura básica comum:

1. **Contexto**
   - o que este runbook cobre;  
   - quais sistemas/perfis/providers estão em escopo;  
   - link para Cap.1/Cap.3/Cap.5 da S31 se relevante.

2. **Sinais / Quando usar**
   - situações típicas que levam alguém a abrir este runbook;  
   - quais dashboards ou logs olhar primeiro.

3. **Procedimento passo a passo**
   - ações ordenadas, em linguagem operacional (comandos, telas, decisões);  
   - se houver branches (“se sim, faça X; se não, faça Y”), eles devem ser claros e poucos.

4. **Critérios de sucesso / encerramento**
   - como saber que o problema foi resolvido ou a tarefa foi concluída;  
   - o que registrar depois (ex.: nota de incidente, atualização de docs).

5. **Escalonamento**
   - quando envolver outras equipes (Truth Ops, arquitetura, produto);  
   - contatos/canais padrões (mesmo que genéricos, ex.: `#inspectah-ops`).

Essa estrutura é simples de manter e facilita reuso em sprints futuras.

---

### 5.18 Teste dos runbooks (simulações controladas)

Runbook que nunca foi “rodado” é ficção. A S31 define, como parte do DoD, ao menos duas simulações controladas:

1. **Simulação A — Incidente de provider**
   - Introduzir, em ambiente de staging, uma falha controlada (ex.: alterar temporariamente credenciais de um perfil ou simular resposta de erro via mock);
   - fazer um operador seguir `rb_incidente_provider_api.md` do início ao fim;
   - observar onde o runbook é vago, redundante ou incompleto;
   - ajustar o documento com base nessa experiência.

2. **Simulação B — Custo de ingestão anômalo**
   - Configurar, em ambiente de teste, um perfil exagerado (escopo amplo) e rodar poucas execuções em ambiente controlado;
   - usar `rb_custo_explodindo_ingestao.md` para diagnosticar e conter o “mini-incidente”;
   - ajustar thresholds e recomendações com base no que deu trabalho.

Resultados dessas simulações podem ser registrados em:

- `out/evidence/S31_ORR/runbook_simulation_A.log` e `runbook_simulation_B.log`;  
- referência no `sprint_31_orr_summary.md` indicando que os runbooks foram de fato testados.

---

### 5.19 Handover da Sprint 31 para operação

Ao final da S31, não basta ter código, docs e runbooks em tese. É necessário um **handover explícito** para quem vai operar (mesmo que hoje seja o próprio time de desenvolvimento).

Elementos mínimos do handover:

1. **Sessão de walkthrough**
   - apresentação curta (pode ser assíncrona) cobrindo:  
     - visão geral de provider-first + Console v2;  
     - cenários E2E da S31;  
     - runbooks disponíveis e onde encontrá-los;  
     - feature flags e plano de rollout.

2. **Checklist de handover**
   - confirmar que todos os runbooks obrigatórios existem e estão linkados no Cap.5;  
   - confirmar que `sprint_31_orr_summary.md` está completo;  
   - registrar quem é o “owner de operação” dos perfis-piloto (pessoa/role).

3. **Ponto de revisão futura**
   - definir data/condição para revisão dos runbooks S31 (ex.: após 30 dias de operação);  
   - registrar possíveis temas para sprints futuras (melhorias pedidas pelos operadores).

---

### 5.20 Resultado esperado deste bloco

Com o Bloco 3 do Capítulo 5, a Sprint 31 deixa claro que:

- provider-first + Console v2 **não são experimentos de laboratório**, mas capacidades com manual de operação;
- existem runbooks mínimos para monitorar ingestão, operar Console, lidar com incidentes de provider e conter custo;
- esses runbooks foram **testados** ao menos em simulações controladas;
- há um handover explícito para operação, mesmo que a operação ainda seja feita pelo próprio time técnico.

Os blocos seguintes vão fechar o Capítulo 5 detalhando riscos remanescentes, feature flags, rollback e a matriz GO / GO_WITH_WARNINGS / NO_GO amarrada ao ORR da S31.