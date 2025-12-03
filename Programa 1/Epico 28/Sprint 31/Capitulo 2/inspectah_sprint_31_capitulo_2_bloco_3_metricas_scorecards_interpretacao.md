# Inspectah — Sprint 31 (E28-S3)
## Capítulo 2 — Bloco 3: Métricas, Scorecards & Interpretação

### 2.17 Papel deste bloco

Este bloco define **como medir** o que a Sprint 31 está fazendo e **como ler** esses números de forma consistente com o roadmap. Ele responde a três perguntas:

1. Quais métricas mínimas precisamos para dizer que ingestão provider-first está saudável nos perfis-piloto?
2. Como essas métricas aparecem nos scorecards S31-G2, S31-G3, S31-G5 e S31-ORR?
3. Como interpretar esses scorecards para decidir GO / GO-com-ressalva / NO-GO?

A ideia é simples: sem métrica e scorecard, qualquer conversa sobre custo, qualidade ou risco vira opinião. Com eles, dá pra discutir em cima de fatos.

---

### 2.18 Métricas mínimas por perfil de ingestão

Para cada **Perfil de Ingestão** (news ou social) relevante na Sprint 31, precisamos acompanhar um conjunto pequeno, mas expressivo, de métricas. O foco não é throughput absoluto, e sim **sanidade, custo e governabilidade**.

Métricas base por perfil (news_provider e social_provider)

1. `provider_calls_total`
   - O que é: número de chamadas feitas à API do provider em um intervalo (dia, semana, sprint).
   - Por que importa: é a unidade básica de custo; quotas e faturas são função disso.

2. `items_ingested_total`
   - O que é: número de itens brutos retornados pelo provider para um determinado perfil, antes de dedupe.
   - Por que importa: mostra a “largura” do funil e ajuda a entender se filtros estão muito abertos ou muito fechados.

3. `contentitems_created_total`
   - O que é: número de ContentItems únicos realmente criados a partir daquele perfil, após dedupe.
   - Por que importa: mostra o volume efetivo que chega no Data Hub; é o que alimenta Claims, ClaimGraph e Truth-DB.

4. `provider_errors_total`
   - O que é: número de chamadas com erro, segmentadas por tipo (rate limit, auth, timeout, payload inválido etc.).
   - Por que importa: dá visibilidade de instabilidade do provider ou de má configuração do perfil; erros crônicos distorcem análises e sinais.

5. `dedupe_ratio`
   - Definição: `dedupe_ratio = contentitems_created_total / items_ingested_total`.
   - Por que importa: indica o quanto do que o provider manda é realmente novo. Valores muito baixos podem indicar filtros genéricos demais ou overlap forte entre perfis/providers; valores estranhamente altos podem indicar dedupe ruim (deixando passar duplicates).

6. `budget_limit_calls`
   - O que é: limite de chamadas configurado para o perfil em um intervalo (por exemplo, chamadas/dia).
   - Por que importa: é o trilho de segurança para custo; sem limite, o sistema não tem freio.

7. `budget_usage_ratio`
   - Definição: `budget_usage_ratio = provider_calls_total / budget_limit_calls`.
   - Por que importa: mostra o quão perto do teto estamos. É a métrica que aciona decisões como “desligar entretenimento para preservar política/saúde”.

8. `latency_p95`
   - O que é: tempo de resposta p95 das chamadas ao provider para aquele perfil.
   - Por que importa: extremo de performance; latências muito altas podem comprometer SLAs de ingestão ou mascarar erros intermitentes.

9. `items_to_claims_ratio` (para perfis ligados a Programa 2)
   - Definição: número de Claims gerados a partir de ContentItems de um perfil dividido pelo número de ContentItems desse perfil usados no ClaimGraph.
   - Por que importa: ajuda a entender se o perfil está alimentando conteúdo que realmente vira conhecimento e sinal, ou se está despejando ruído.

Essas métricas não precisam estar perfeitas na S31, mas precisam existir para os perfis-piloto e ser fáceis de consultar nos painéis internos.

---

### 2.19 Estrutura dos scorecards

Cada gate relevante produz pelo menos um scorecard JSON em `out/scorecards/`. A Sprint 31 adota um formato padrão para facilitar leitura humana e automatização.

Formato base de scorecard

- `gate_id`: string (ex.: `"S31-G2"`).
- `status`: um de `"PASS"`, `"FAIL"`, `"WARN"`.
- `summary`: texto curto (2–4 frases) explicando o que foi verificado e o resultado.
- `metrics`: objeto com métricas relevantes para aquele gate.
- `evidence_paths`: lista de caminhos para arquivos em `out/evidence/...`.
- `notes` (opcional): observações adicionais, riscos percebidos, TODOs.

Exemplo conceitual (não é JSON real do repo, é formato mental)

```
{
  "gate_id": "S31-G2",
  "status": "PASS",
  "summary": "Ingestão via providers rodou fim a fim para perfis BR_PT_HARD_NEWS e LATAM_ES_POLITICS com dedupe_ratio saudável e sem erros críticos.",
  "metrics": {
    "profiles": [
      {
        "id": "BR_PT_HARD_NEWS",
        "provider_calls_total": 1200,
        "items_ingested_total": 8500,
        "contentitems_created_total": 3200,
        "dedupe_ratio": 0.38,
        "provider_errors_total": 7
      },
      {
        "id": "LATAM_ES_POLITICS",
        "provider_calls_total": 600,
        "items_ingested_total": 4200,
        "contentitems_created_total": 1500,
        "dedupe_ratio": 0.36,
        "provider_errors_total": 3
      }
    ]
  },
  "evidence_paths": [
    "out/evidence/S31_G2_provider_ingestion/jobs.log",
    "out/evidence/S31_G2_provider_ingestion/dedupe_sample.json"
  ],
  "notes": "Perfil social ainda em ajuste, ficará para próxima execução do gate."
}
```

Scorecards principais da S31

1. `S31_G2_provider_ingestion.json`
   - Foco: métricas de ingestão via providers, por perfil.
   - Leitura: se perfis-piloto estão trazendo conteúdo real, com dedupe aceitável e erros sob controle.

2. `S31_G3_observabilidade.json`
   - Foco: métricas de observabilidade/budget por perfil (calls, errors, budget_usage_ratio, latency_p95).
   - Leitura: se temos visão suficiente para operar sem ficar cegos em relação a custo e saúde.

3. `S31_G4_legacy_and_compat.json`
   - Foco: estado dos fluxos legados, status da migração/coexistência.
   - Leitura: se provider-first entrou sem destruir o que já era crítico.

4. `S31_G5_p2_p3_integration.json`
   - Foco: ligação perfis → ContentItems → Claims → FactBlocks no domínio piloto.
   - Leitura: se provider-first está alimentando Programas 2–3 como previsto.

5. `S31_ORR_overview.json`
   - Foco: visão consolidada da sprint.
   - Leitura: veredito GO / GO_WITH_WARNINGS / NO_GO, com resumo de riscos.

---

### 2.20 Como interpretar os scorecards na prática

A leitura de scorecards da S31 deve seguir algumas regras simples para evitar autoengano.

Regra 1 — `PASS` não é só testes verdes; é teste + métrica em zona saudável

Um gate só é `PASS` de verdade se:
- os scripts/testes rodaram sem erro; e
- as métricas associadas estão dentro de faixas razoáveis para piloto.

Exemplo: se S31-G2 rodou sem erro, mas `dedupe_ratio` ficou em 0.02 (2% de aproveitamento) porque os perfis estão absurdamente abertos, faz mais sentido marcar `status = "WARN"` com explicação no resumo, do que um `PASS` triunfalista.

Regra 2 — `WARN` é sinal amarelo, não decoração

Um `WARN` em scorecard significa: “a sprint passou tecnicamente, mas há risco ou dívida explícita aqui”. Tipicamente:
- custo alto demais por conteúdo útil;
- erro recorrente no provider, ainda sem mitigação robusta;
- legado ainda muito dependente de scrapers em áreas críticas;
- domínio piloto com ingestão ok, mas ligação fraca com Programas 2–3.

A presença de `WARN` não impede GO por definição, mas obriga o ORR a propor limites para a expansão (por exemplo, “não ligar perfis internacionais em produção antes de S32”).

Regra 3 — `FAIL` em gate estrutural é NO-GO, mesmo que o resto esteja verde

Alguns gates (G1, G2, G3, G5) são estruturais: se falharem, a sprint não pode ser considerada entregue como sprint provider-first.

Exemplos de `FAIL` que puxam NO-GO:
- G1: migrations quebram dados legados ou tornam o modelo inconsistente.
- G2: jobs de ingestão via provider são flakey, criam conteúdo inconsistente ou não respeitam proveniência.
- G3: Console não permite operar perfis-piloto ou não expõe métricas mínimas.
- G5: não é possível reconstruir a trilha Provider → Perfil → ContentItem → Claim → FactBlock no domínio piloto.

Regra 4 — S31-ORR é o desempate

Mesmo se todos os gates técnicos estiverem `PASS`, o `S31_ORR_overview.json` pode recomendar:
- `GO` simples, se tudo estiver saudável;
- `GO_WITH_WARNINGS`, se houver riscos claros, mas mitigáveis, para expansão;
- `NO_GO`, se a combinação de custos, fragilidade de providers ou legado sugere que ainda não é hora de depender de provider-first em produção.

O ORR olha scorecards, métricas e notas, e transforma em decisão de produto.

---

### 2.21 Faixas de sanidade sugeridas (para leitura inicial)

Para a Sprint 31, que trabalha com **pilotos** e não escala global, algumas faixas de sanidade aproximadas ajudam na leitura dos scorecards (não são limites rígidos, mas guias):

- `dedupe_ratio` por perfil:
  - 0.15–0.60: faixa saudável para perfis de hard news, dependendo do quão amplo é o recorte;
  - < 0.05: provável excesso de overlap ou filtros muito genéricos — candidato a WARN;
  - > 0.80: suspeita de dedupe frouxa ou filtros estreitos demais.

- `budget_usage_ratio` por perfil (na média da sprint):
  - 0.30–0.80: saudável para piloto (há espaço, mas não estamos ociosos demais);
  - > 0.90: risco de estourar quota / custo — requer justificativa ou ajuste;
  - < 0.10: possivelmente perfil mal configurado ou subutilizado.

- `provider_errors_total` / `provider_calls_total`:
  - até ~1–3%: aceitável, desde que haja monitoramento e retries;
  - 3–10%: amarelo, requer análise (problema de rede? throttling? auth?);
  - > 10%: vermelho, provider ou configuração não confiável para produção.

Essas faixas são ponto de partida. O objetivo da S31 é coletar dados suficientes para, no futuro, calibrar esses ranges com base em experiência real.

---

### 2.22 Conclusão do bloco

Métricas e scorecards da Sprint 31 existem para garantir que "provider-first" não vire slogan. Ao amarrar perfis de ingestão a números concretos e a gates binários, o projeto ganha uma forma objetiva de responder:

- se a ingestão via providers está trazendo conteúdo útil na proporção certa;
- se o custo está sob controle para os pilotos;
- se o legado continua respirando até ser substituído;
- se Programas 2 e 3 estão recebendo uma dieta de dados coerente.

Nos blocos seguintes, os invariantes amarram isso tudo com um laço bem apertado: certas coisas simplesmente não podem quebrar, não importa o quão bonitas estejam as métricas em volta.

