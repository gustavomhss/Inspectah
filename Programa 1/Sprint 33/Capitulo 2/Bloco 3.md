# Sprint 33 — Capítulo 2

## Bloco 3 — Gates G2 e G3: OracleOps Cockpit v1 e SLOs em produção

Este bloco desce ao nível operacional dos gates **G2** e **G3** da Sprint 33:

- **G2 — OracleOps Cockpit v1 navegável e conectado**;
- **G3 — SLOs e observabilidade aplicada para o recorte da sprint**.

Se o Bloco 2 consolidou a fundação semântica (escopo, componentes, Incident como entidade), o Bloco 3 trata da **superfície operável**: o que o operador enxerga no cockpit e como isso se ancora em SLOs e métricas reais. A ideia é que, a partir deste texto, o time consiga implementar os scripts de gate (`bin/s33_g2_*.sh`, `bin/s33_g3_*.sh`), os scorecards (`S33_G2_*.json`, `S33_G3_*.json`) e os roteiros de validação de forma direta, sem precisar adivinhar intenção.

---

### 2.3.1 G2 — OracleOps Cockpit v1 navegável e conectado (detalhado)

**Pergunta que G2 responde:**
> "Um operador consegue, usando apenas o OracleOps Cockpit v1, responder às perguntas básicas sobre o recorte da S33 sem recorrer a scripts obscuros ou conhecimento tribal?"

G2 não quer provar que o cockpit é "bonito"; quer provar que ele é **operável**. Isso significa que a UI precisa ser:
- **coerente com o recorte de G0** (mesmos componentes, mesmos nomes);
- **alimentada por dados reais** (mesmo que via mocks mínimos em ambiente de dev);
- **capaz de suportar a rotina de um operador** olhando para saúde, incidentes e caminhos de drill‑down.

#### Artefatos formais de G2

G2 se ancora nos seguintes elementos:

1. **Implementação da UI do OracleOps Cockpit v1**, com pelo menos:
   - rota de overview (por exemplo, `/ops/cockpit/overview`);
   - rota de detalhe por fonte (ex.: `/ops/cockpit/source/:source_id`);
   - rota de detalhe por pipeline (ex.: `/ops/cockpit/pipeline/:pipeline_id`);
   - rota de incidentes (lista + detalhe, ex.: `/ops/cockpit/incidents`).

2. **Contrato da API de cockpit** (ex.: `app/api/ops_cockpit_routes.py` + doc):
   - endpoints para overview, listas de componentes, estados resumidos e incidentes;
   - payloads alinhados com o `components_map` de G0 e o modelo de `Incident` de G1.

3. **Fixture de dados mínimos para ambiente de validação**:
   - conjunto de componentes do recorte com estados distintos (OK, degradado, falhando);
   - ao menos um incidente ativo e um resolvido;
   - alguns SLOs com estados diferentes (cumprindo / violado) refletidos no cockpit.

4. **Scorecard de G2** (ex.: `out/scorecards/S33_G2_cockpit_ui.json`), com checklist de verificação.

#### Invariantes de G2

Para que G2 seja considerado "PASS", as seguintes invariantes precisam ser verdade:

- **Inv‑G2‑1 — Correspondência com o recorte da S33.**  
  Todos os componentes (fontes, pipelines, APIs) do recorte definido em G0 estão visíveis em alguma parte do cockpit (overview ou páginas de detalhe). Não existem componentes do recorte totalmente invisíveis.

- **Inv‑G2‑2 — Consistência de naming e identificadores.**  
  Os nomes/IDs exibidos no cockpit para fontes e pipelines coincidem com:
  - `component_id` e labels no `components_map` de G0;
  - identificadores usados em métricas e logs;
  - identificadores usados pelo modelo de Incident (quando relacionado).

- **Inv‑G2‑3 — Representação honesta de estado.**  
  Indicadores de estado (por exemplo, "OK", "Lento", "Falhando") estão baseados em dados (métricas, healthchecks, consultas a jobs) — ainda que com thresholds simples — e não em valores hard‑coded divorciados da realidade. Em ambiente de validação, é possível manipular dados para ver mudança de estado na UI.

- **Inv‑G2‑4 — Navegação de drill‑down funcional.**  
  A partir da visão de overview, o operador consegue acessar:
  - detalhes de uma fonte;
  - detalhes de um pipeline;
  - lista de incidentes associados.
  Nenhuma dessas rotas resulta em erro grave (500, 404) ou páginas vazias sem mensagem clara.

- **Inv‑G2‑5 — Integração mínima com observabilidade externa.**  
  Para componentes que possuem dashboards externos, o cockpit oferece links consistentes e utilizáveis (por exemplo, icones/links que abrem o painel correto). Não é necessário cobertura total, mas pelo menos um caso de ponta a ponta precisa funcionar.

#### Execução de G2 (script + sessão guiada)

G2 é validado em duas camadas complementares:

1. **Verificação automatizada básica** (script `bin/s33_g2_cockpit_sanity.sh`):
   - Checa se os principais endpoints de cockpit respondem com 2xx em ambiente de validação;
   - Verifica se o payload contém todos os componentes do recorte (comparando IDs com `components_map`);
   - Gera um resumo com contagem de componentes por estado (OK/degradado/falhando) para inspeção humana.

2. **Sessão guiada de operador** (mini‑teste de usabilidade operacional):
   - Uma pessoa que não implementou diretamente o cockpit assume o papel de operador;
   - Usando apenas a UI, deve conseguir:
     - responder "quais componentes do recorte estão com problemas agora?";
     - navegar até o detalhe de um componente em estado anômalo;
     - localizar incidentes ativos relacionados (se houver);
     - encontrar links para observabilidade quando disponíveis.
   - Observações relevantes (pontos de confusão, buracos de informação) são registradas como backlog.

**Critério de aceite para G2:**

- G2 é "PASS" se o script de sanity não encontrar falhas estruturais (endpoints quebrados, payloads inconsistentes) e se a sessão guiada demonstrar que um operador consegue cumprir o roteiro sem precisar abandonar o cockpit para achar informações básicas.

---

### 2.3.2 G3 — SLOs e observabilidade aplicada para o recorte da sprint (detalhado)

**Pergunta que G3 responde:**
> "Os SLOs da S33 existem na prática: são medidos, podem ser consultados e, em casos críticos, disparam sinais que chegam até o operador?"

G3 é o gate que testa se a ponte **SLO → métrica → observabilidade → cockpit/alerta** foi construída de forma mínima, mas real. Ele não exige que todo o universo de SLOs do Inspectah esteja implementado; exige que o subconjunto escolhido para a S33 seja levado até o fim.

#### Artefatos formais de G3

G3 se apoia em:

1. **Lista consolidada de SLOs da S33** (documento, ex.: `docs/s33/s33_slos.md`), contendo para cada SLO:
   - `slo_id` estável;
   - descrição em uma frase;
   - métrica base (nome da métrica + labels relevantes);
   - expressão/consulta usada para avaliar o SLO (ex.: PromQL, SQL, outra DSL);
   - target (ex.: `>= 99.5%`, `<= 3600s`);
   - janela de observação (ex.: 1h, 24h);
   - componentes e incidentes relacionados.

2. **Consultas implementadas na stack de observabilidade**:
   - Arquivos de configuração de dashboards ou queries salvos em repositório (quando aplicável);
   - Scripts ou documentação de como executar as consultas que avaliam os SLOs.

3. **Configuração mínima de alertas para SLOs críticos**:
   - Definições de alertas para pelo menos um subconjunto dos SLOs (os mais importantes do recorte);
   - Configuração de canal de notificação (mesmo que em ambiente de teste: log, email, webhook etc.).

4. **Integração SLO → cockpit**:
   - Campos ou seções na UI do cockpit que apresentem o estado atual de pelo menos alguns SLOs (cumprindo / violado / sem dados);
   - Chamadas de API que tragam esse estado.

5. **Scorecard de G3** (ex.: `out/scorecards/S33_G3_slos_and_observability.json`).

#### Invariantes de G3

G3 só é considerado "PASS" se as seguintes invariantes forem satisfeitas:

- **Inv‑G3‑1 — Nenhum SLO "de papel".**  
  Todo SLO da lista da S33 tem:
  - métrica base definida;
  - consulta associada que pode ser executada;
  - target e janela definidos.

- **Inv‑G3‑2 — Consultas executáveis.**  
  As consultas associadas a cada SLO rodam sem erro na stack de observabilidade ou ambiente equivalente. Não há consultas inválidas ou que dependam de métricas inexistentes.

- **Inv‑G3‑3 — Ligação com o recorte de G0.**  
  Cada SLO está ligado a pelo menos um componente do recorte (fonte, pipeline, API). Não existem SLOs sem relação clara com o mundo que G0 definiu.

- **Inv‑G3‑4 — SLOs críticos com alerta mínimo.**  
  Para os SLOs marcados como críticos:
  - existe regra de alerta associada;
  - é possível simular ou reproduzir uma violação e observar o alerta ser disparado (mesmo que apenas em log ou canal de teste).

- **Inv‑G3‑5 — SLOs visíveis no cockpit.**  
  O OracleOps Cockpit v1 exibe o estado de pelo menos um subconjunto representativo dos SLOs da S33. A UI pode ser simples (por exemplo, "dentro" / "fora" / "sem dados"), mas precisa ser baseada nos dados reais das consultas.

#### Execução de G3 (script + validação em ORR)

G3 é verificado em duas frentes:

1. **Script de validação de SLOs** (ex.: `bin/s33_g3_slos_sanity.sh`):
   - Lê `s33_slos.md` ou equivalente;
   - Para cada SLO, tenta executar a consulta associada (em modo dry‑run ou real);
   - Verifica se há dados suficientes na janela definida;
   - Gera um relatório com o estado atual de cada SLO (cumprindo / violado / sem dados) e registra em `out/evidence/S33_G3_slos_sanity/`.

2. **Checagem integrada em ORR** (ligação com G5):
   - Durante a ORR operacional, o facilitador escolhe 2–3 SLOs da lista;
   - Pede para o operador mostrar, via cockpit, o estado desses SLOs;
   - E, quando aplicável, demonstra ou descreve como um alerta seria (ou foi) disparado em caso de violação.

**Critério de aceite para G3:**

- G3 é "PASS" se o script de sanity indicar que todas as consultas rodam, nenhum SLO está "desconectado" de métricas e pelo menos um SLO crítico tem alerta testado com sucesso;
- SLOs sem métrica ou consulta, alertas configurados apenas "no papel" ou SLOs invisíveis ao cockpit derrubam o gate.

---

### 2.3.3 Encadeamento de G2 e G3 com os demais gates

G2 e G3 formam o "rosto" da Sprint 33 do ponto de vista operacional:

- G2 garante que o operador tem um lugar central para enxergar o recorte da S33 e navegar por componentes e incidentes;
- G3 garante que esse cockpit não é uma maquete estática, mas uma visão conectada a SLOs e métricas reais.

Na sequência dos gates:

- G0/G1 definem o **vocabulário** (recorte + Incident);
- G2/G3 constroem a **superfície visível** (cockpit + SLOs observáveis);
- G4 (próximo bloco) garante que existe **musculatura de resposta** (runbooks + evidência);
- G5 testa a **integração** em um cenário realista.

Este bloco deve ser usado diretamente pelo time responsável pela implementação do cockpit e pela instrumentação de SLOs, e também pelo time que escreverá os scripts de gate e os scorecards correspondentes. Divergência entre o que está descrito aqui e o que aparecer em código/scorecards deve ser tratada como bug de especificação e corrigida antes da S33 ser promovida como "GO" em ORR.