# Sprint 24 – Debunker v0 & Humano‑no‑Loop
# Capítulo 2 – Gates & Métricas
## Sub‑capítulo 2.3 – Evidências, Scorecards e Critérios de GO/NO‑GO

Este sub‑capítulo define, de forma exaustiva e operacional, o que conta como evidência válida em cada gate da Sprint 24, como essas evidências são organizadas em scorecards, onde são armazenadas, como são auditadas e quais são os critérios objetivos de GO/NO‑GO. A ideia é simples: ninguém precisa “acreditar” em nada sobre o Debunker v0; basta abrir os artefatos desta sprint e seguir o rastro das evidências.

Ao final da Sprint 24, qualquer pessoa com acesso ao repositório deve ser capaz de:

1. Reconstruir a linha do tempo de execução de todos os gates S24_G0…S24_Gn apenas olhando para os scorecards e suas pastas de evidência.
2. Entender exatamente por que a sprint foi marcada como GO ou NO‑GO, sem depender de memória de time, chats paralelos ou decisões orais.
3. Validar se os requisitos de qualidade do Debunker v0 (latência, precisão, cobertura, segurança de fluxo humano‑no‑loop) foram de fato atingidos, e em que medida.
4. Reexecutar localmente qualquer gate e comparar o resultado obtido com o registrado nos scorecards, garantindo reprodutibilidade.

Para isso, este sub‑capítulo especifica: o modelo de scorecard, o layout de diretórios de evidência, o conjunto mínimo de artefatos obrigatórios por gate, os requisitos de integridade e as regras de GO/NO‑GO. Tudo aqui é sprint‑agnóstico o bastante para ser aproveitado nas próximas sprints críticas, mas detalhado o bastante para cobrir os casos específicos do Debunker v0.

---

### 2.3.1 – Modelo de scorecard para a Sprint 24

Cada gate da Sprint 24 terá um scorecard em formato JSON, armazenado em out/scorecards/, com o seguinte padrão de nome:

• S24_GX_<nome_gate>.json (por exemplo: S24_G0_sanity_and_alignment.json, S24_G3_debunker_quality.json).

Conteúdo mínimo do scorecard:

• metadata: bloco de metadados da execução do gate, incluindo:
  • sprint_id: "S24"
  • gate_id: "S24_GX" (por exemplo, "S24_G3")
  • gate_name: descrição curta do gate
  • run_id: identificador único da execução (timestamp + hash curto)
  • run_timestamp_utc: horário ISO 8601 da execução
  • runner: quem/qual sistema disparou o gate (ex.: "ci/github", "ci/local")
  • repo_sha: commit exato do repositório (git rev‑parse HEAD)
  • env: contexto mínimo do ambiente (ex.: "local-mac-m3", "github-ubuntu-latest")

• checks: lista de verificações realizadas pelo gate. Cada item deve conter:
  • id: identificador único do check dentro do gate (ex.: "debunker_accuracy_benchmark", "workflow_handoff_latency")
  • description: texto curto explicando o objetivo daquele check
  • type: categoria do check (ex.: "unit", "integration", "e2e", "benchmark", "policy", "manual_review")
  • status: "PASS" | "FAIL" | "SKIPPED"
  • metrics: objeto com métricas relevantes (quando aplicável)
  • evidence_paths: lista de caminhos para arquivos em out/evidence/S24_GX_*/ associados ao check
  • notes: observações relevantes, restrições, hipóteses ou anomalias conhecidas

• summary: visão consolidada do gate, contendo:
  • overall_status: "GO" | "NO_GO" | "WARN" (WARN significa que o gate passou com ressalvas explícitas)
  • failures_count: número de checks com status FAIL
  • warnings_count: número de checks com ressalvas (WARN ou notas críticas)
  • coverage: percentual aproximado de cobertura daquele gate em relação ao escopo previsto (por exemplo, proporção de casos de teste de Debunker v0 efetivamente cobertos)
  • decision_rationale: texto curto explicando, em linguagem natural, a razão da decisão (especialmente em caso de WARN ou NO_GO)

• signoff: bloco de aprovação, contendo:
  • reviewer: pessoa/entidade responsável pelo gate (pode ser um alias do squad)
  • review_timestamp_utc: horário da revisão humana
  • decision: "APPROVED" | "REJECTED" | "NEEDS_CLARIFICATION"
  • comments: campo textual para comentários adicionais.

Este modelo de scorecard é obrigatório e deve ser seguido por todos os gates S24_G0…S24_Gn. Pequenas variações são permitidas (campos adicionais), mas nunca a remoção de campos básicos.

---

### 2.3.2 – Layout de evidências e rastreabilidade por gate

Toda evidência gerada por um gate deve ser armazenada sob out/evidence/, em pastas específicas por gate. A convenção para a Sprint 24 é:

• out/evidence/S24_GX_<nome_gate>/

Dentro de cada pasta S24_GX_*, a organização mínima é:

• logs/: logs brutos e filtrados, incluindo saída de scripts, stack traces, logs de serviços de apoio usados na validação do Debunker v0.
• reports/: relatórios em formatos legíveis (Markdown, HTML, JSON de alto nível) com resultados de benchmarks, experimentos de qualidade, sanity checks sobre o fluxo humano‑no‑loop, etc.
• samples/: exemplos concretos de casos avaliados pelo Debunker v0 (inputs, saídas dos agentes, decisões humanas, estados finais).
• metrics/: dumps de métricas estruturadas, quando não estiverem diretamente embutidas no scorecard (por exemplo, tabelas CSV ou JSON com resultados de N cenários).
• misc/: qualquer artefato adicional relevante que não se encaixe nas categorias anteriores, com README explicando seu propósito.

Cada arquivo relevante em logs/reports/samples/metrics deve ser citado pelo menos uma vez em algum evidence_paths de um check de scorecard. Arquivo sem referência direta é considerado “lixo” sob a perspectiva de auditoria e deve ser evitado. Quando for inevitável manter artefatos auxiliares, um README.md dentro da pasta do gate deve explicar o motivo.

Para manter rastreabilidade:

1. Todo script de gate (por exemplo, bin/s24_g3_debunker_quality.sh) deve imprimir no início o path exato da pasta de evidências que está sendo usada para aquela execução.
2. O script deve também escrever um pequeno manifesto de execução (run_metadata.json) dentro da pasta de evidência, com SHA do commit, timestamp, runner e resumo dos comandos executados.
3. O scorecard S24_GX_*.json deve apontar para esse manifesto em evidence_paths (ex.: "out/evidence/S24_G3_debunker_quality/run_metadata.json").

Assim, qualquer pessoa consegue sair do scorecard, cair na pasta de evidência e, a partir dali, reconstruir o que aconteceu na execução do gate.

---

### 2.3.3 – Tabela de evidências mínimas por gate crítico da S24

Para a Sprint 24, alguns gates são mais sensíveis e exigem um conjunto mínimo de evidências específicas. A tabela abaixo descreve o pacote mínimo exigido para considerar cada gate elegível a GO.

1) S24_G0 – Sanidade, alinhamento e escopo de Debunker v0

Evidências mínimas:

• Manifesto de escopo da sprint (docs/inspectah_sprint_24_macro_v2.md ou equivalente) referenciado no scorecard.
• Log da execução do script de sanidade (ex.: bin/s24_g0_sanity.sh) em out/evidence/S24_G0_*/logs/.
• Lista consolidada de requisitos de Debunker v0, com rastreabilidade para claims e fluxos do Inspectah (documento em reports/).
• Amostra de pelo menos N cenários de “casos‑tipo” (samples/), cobrindo fake news, imprecisões estatísticas, interpretações tendenciosas e boatos triviais, mapeados para como o Debunker v0 deve tratá‑los.

Critério de GO:

• Todos os checks de sanidade com status PASS.
• Nenhuma divergência estrutural entre escopo definido no Capítulo 1 e o que foi implementado nos scripts/configs da sprint.

2) S24_G2 – Qualidade do pipeline humano‑no‑loop

Evidências mínimas:

• Logs de simulações de fluxo end‑to‑end com humanos simulados/“scriptados” (logs/).
• Relatório de cenários de escalonamento e fallback (reports/), incluindo casos em que o humano recusa a tarefa, demora a responder ou comete erro.
• Amostra de transcrições de casos (samples/) mostrando como a decisão final é construída a partir do comitê de agentes e da intervenção humana.
• Métricas de latência por etapa e tempo total até decisão (metrics/), associadas a SLIs da Sprint 24.

Critério de GO:

• Percentual mínimo de casos finalizados com sucesso acima do threshold definido em 2.2.
• Nenhum desvio grave de fluxo (ex.: casos que “somem” do pipeline ou ficam sem decisão final).

3) S24_G3 – Qualidade de decisão do Debunker v0

Evidências mínimas:

• Relatório de benchmark em massa (reports/) comparando decisões do Debunker v0 em relação a um conjunto de gabaritos construídos com apoio do Squad Verdade & Interpretação.
• Amostra estratificada de casos difíceis (samples/), incluindo edge cases de ambiguidade, múltiplas fontes em conflito e ausência parcial de evidência.
• Logs contendo explicações de agentes GPT e decisões humanas lado a lado, permitindo entender por que uma conclusão final foi tomada.
• Métricas de acurácia, recall, precisão e taxa de “não sei” calibrada, conforme definido em 2.2.

Critério de GO:

• Atingir todos os mínimos de qualidade definidos em 2.2 (por exemplo, acurácia >= X%, recall >= Y%, taxa de “não sei” dentro de uma faixa aceitável).
• Nenhuma família de casos (cluster temático) com desempenho catastrófico não tratado em plano de mitigação.

4) S24_G5 – Robustez e auditabilidade do Debunker v0

Evidências mínimas:

• Relatório de auditoria interna (reports/) descrevendo como alguém externo pode seguir o rastro de uma decisão: claim → evidências → agentes → humano → estado final.
• Amostras de timelines de decisão para vários casos representativos (samples/), preferencialmente em formato legível (tabelas ou JSON bem estruturado).
• Logs mostrando simulações de replay de decisões (rodar novamente o pipeline em ambiente controlado e comparar saída).
• Artefatos de integração com a Sprint 25 (quando aplicável), mostrando como as decisões de Debunker v0 alimentam o Truth‑DB.

Critério de GO:

• Pelo menos uma trilha de decisão completa e auditada para cada tipo de caso principal (notícia, dados estatísticos, declarações de autoridade, boato de rede social).
• Nenhuma decisão “caixa‑preta”: todas as decisões auditadas devem ter caminhos explicáveis.

Outros gates de S24 seguirão o mesmo padrão: uma seção dedicada, com evidências mínimas e critérios objetivos de GO. Se alguma evidência mínima não puder ser gerada por motivo justificado, isso deve constar explicitamente em decision_rationale e notes do scorecard, com impacto claro para a sprint.

---

### 2.3.4 – Regras formais de GO/NO‑GO da Sprint 24

A decisão final de GO/NO‑GO da Sprint 24 não é um ato político, e sim uma consequência lógica da combinação dos scorecards de todos os gates. As regras formais são:

1. Condição necessária: nenhum gate crítico (S24_G0, S24_G2, S24_G3, S24_G5, e quaisquer outros designados como críticos no Capítulo 2.1) pode terminar com overall_status = "NO_GO". Se qualquer um deles estiver em NO_GO, a sprint inteira é automaticamente NO_GO.

2. Condição de consistência: não pode haver divergência entre status e evidência. Se um scorecard marcar GO mas evidências mínimas do gate não estiverem presentes (por exemplo, faltam relatórios obrigatórios, amostras ou métricas definidas neste sub‑capítulo), o gate deve ser rebaixado para NO_GO até que o pacote de evidências seja completado.

3. Condição de cobertura: a soma dos scorecards precisa mostrar cobertura aceitável do espaço de casos planejados. Se a cobertura reportada em summary.coverage de um gate ficar abaixo do mínimo definido em 2.2, o gate é NO_GO, ainda que os casos cobertos tenham desempenho excelente.

4. Condição de sanidade cruzada: se evidências de um gate contradisserem outra (por exemplo, S24_G3 mostra acurácia alta, mas S24_G5 revela famílias inteiras de casos com decisões absurdas não mapeadas), o Squad Verdade & Interpretação deve abrir uma análise de conflito e, até que seja resolvida, o status global da sprint não pode ser marcado como GO pleno. Pode‑se usar o estado WARN com plano de ação explícito, mas nunca GO “limpo” ignorando os conflitos.

5. Condição de reprodutibilidade: pelo menos um subset representativo de gates deve ser reexecutado localmente (fora da CI) e gerar scorecards equivalentes (mesmos números com pequenas variações toleráveis). Se a reexecução diverge de forma significativa, o gate é marcado como NO_GO até a causa ser identificada.

A decisão final da sprint é documentada em um artefato específico (por exemplo, docs/sprint_24_cap_2_gates_decisao_final.md), com links para todos os scorecards relevantes e uma explicação textual curta baseada nas regras acima. O objetivo é que qualquer pessoa consiga ler esse arquivo e entender por que a S24 foi GO, NO_GO ou GO com ressalvas.

---

### 2.3.5 – Auditoria pós‑sprint e herança para S25

Como a Sprint 24 é a base do Debunker v0 e da camada humano‑no‑loop, a qualidade das evidências aqui impacta diretamente a Sprint 25 (Governança de Verdade & Truth‑DB). Por isso, este sub‑capítulo também define um pequeno ritual de auditoria pós‑sprint:

1. Após o fechamento da S24, o Squad Verdade & Interpretação seleciona um conjunto de decisões reais do Debunker v0 que foram promovidas para o Truth‑DB (ou para algum estado equivalente transitório).
2. Para cada decisão selecionada, o time tenta reconstruir a trilha completa usando apenas as evidências desta sprint: scorecards, logs, reports, samples e integrações.
3. Qualquer lacuna encontrada (por exemplo, falta de explicação em logs, ausência de ligação clara entre um caso e um check específico) é registrada em um documento de lessons learned que alimentará diretamente os requisitos de evidência da Sprint 25.

Esse ciclo garante que o modelo de evidências e scorecards da Sprint 24 não seja descartável, mas sim o primeiro degrau de um padrão permanente de auditabilidade nos blocos de verdade do Inspectah.

Com isso, o sub‑capítulo 2.3 estabelece a espinha dorsal de como a Sprint 24 prova, com artefatos concretos, que o Debunker v0 funciona como prometido – e que essa prova pode ser auditada, reexecutada e herdada pelas próximas sprints focadas em verdade, governança e persistência em Truth‑DB.

