# Inspectah — Sprint 32
## Capítulo 5 — Bloco 4
### Critérios de GO/NO-GO, Operação Pós-Sprint & Dever de Casa para as Próximas Sprints

> Este bloco fecha o Capítulo 5 transformando o ORR da S32 em **decisão operacional concreta**: critérios formais de GO/GO COM RESTRIÇÕES/NO-GO, plano de operação mínima do Truth-DB + Contestação v1, tratamento de incidentes e o “dever de casa” que a S32 deixa para sprints futuras.

---

#### 5.4.1 Critérios formais de decisão — GO, GO COM RESTRIÇÕES, NO-GO

O conselho de ORR da Sprint 32 deve sempre terminar a sessão com uma destas três sentenças registradas de forma explícita:

- **Decisão A — GO**  
- **Decisão B — GO COM RESTRIÇÕES**  
- **Decisão C — NO-GO**

Abaixo, o contrato mínimo para cada uma.

##### 5.4.1.1 GO (liberação plena no ambiente-alvo)

A S32 recebe **GO** quando todas as condições a seguir são verdadeiras:

1. **Integridade técnica comprovada**  
   - Gates G1, G2, G3 e G4 em `status = "PASS"`.  
   - Não há violações conhecidas de invariantes críticas:  
     - ausência de blocos órfãos;  
     - estados finais sempre com DecisionBlock;  
     - histórico monotônico (contestações apenas acrescentam blocos/estados, não destroem).  

2. **Fluxos principais funcionam de forma repetível**  
   - Fluxo de promoção (claim → blocos → estado) validado com testes e demos;  
   - Fluxo de contestação (estado → contestação → novos blocos/estado) validado com testes e demos;  
   - Níveis aceitáveis de erro nos cenários de teste;  
   - Nenhuma falha silenciosa — erros aparecem em logs e métricas.

3. **Observabilidade mínima em produção/staging**  
   - Métricas-chave (`truthdb_promotion_success_rate`, `truthdb_contestation_rate`, `truthdb_flow_error_rate`, `truthdb_flow_latency_p95`) estão configuradas e visíveis em painel ou endpoint de métricas;  
   - Existe, no mínimo, uma forma clara de responder à pergunta:  
     > “O Truth-DB parece saudável hoje?”

4. **Sanidade cruzada aceitável com ingestão/claims**  
   - Sanidade pós-S32 rodou sobre as sprints de ingestão/claims críticas (S21, S24, etc.);  
   - Não há regressões classificadas como **BLOQUEANTES**;  
   - Regressões não-bloqueantes foram registradas com plano de correção.

5. **Bundle da S32 íntegro e reexecutável**  
   - `inspectah_s32_evidence_bundle.zip` existe, abre sem erro e contém:  
     - scorecards S32_G0–G4;  
     - evidências de G1–G3;  
     - README de replay;  
   - Ao menos um teste de reexecução de G1–G3 foi feito a partir do bundle, com sucesso.

Se todas estas condições forem verdadeiras, o conselho pode registrar GO com a consciência de que o Truth-DB + Contestação v1 é tecnicamente confiável para o ambiente-alvo.

##### 5.4.1.2 GO COM RESTRIÇÕES (liberação controlada)

A S32 recebe **GO COM RESTRIÇÕES** quando:

1. Todos os critérios de **integridade técnica básica** são atendidos (G1–G3 PASS, invariantes centrais ok), mas…  
2. Existe um ou mais destes fatores:
   - **Cobertura funcional limitada:** apenas um tipo de claim suportado, ou lacunas claras em cenários importantes.  
   - **Observabilidade parcial:** métricas presentes, mas sem painéis consolidados ou com baixa granularidade.  
   - **Regressões não-bloqueantes, porém incômodas:** falhas em caminhos importantes, com workaround definido, mas ainda não corrigidas.  
   - **Lacunas na experiência de operação:** runbook diário incompleto, ausência de scripts de healthcheck lógico, etc.

Nesses casos, o conselho deve registrar:

- quais restrições se aplicam (ex.:  
  - “uso apenas interno por analistas”;  
  - “apenas claims de fonte X e tipo Y são elegíveis para Truth-DB”;  
  - “contestações só podem ser feitas de forma semi-manual neste estágio”);
- qual sprint ficará responsável por remover cada restrição (linkando com Capítulo 7 – Tasks, ou backlog de sprints futuras).

GO COM RESTRIÇÕES é um **sim, mas…** — válido desde que os “mas” estejam escritos em letras garrafais.

##### 5.4.1.3 NO-GO (bloqueio)

A S32 recebe **NO-GO** se qualquer um destes pontos for verdadeiro:

1. **Risco estrutural**  
   - Evidência (ou forte suspeita) de corrupção de dados, perda de histórico ou violação séria de invariantes;  
   - Scorecard de G1, G2 ou G3 em `status = "FAIL"`, sem workaround plausível.

2. **Invisibilidade operacional**  
   - Métricas do Truth-DB praticamente ausentes ou inutilizáveis;  
   - Ausência total de runbook de operação mínima;  
   - Impossibilidade de detectar incidentes de forma tempestiva.

3. **Impacto crítico em ingestão/claims ou em outros núcleos**  
   - Regressões classificadas como BLOQUEANTES na sanidade cruzada;  
   - Quebra de contratos críticos de APIs, schemas ou pipelines.

4. **Bundle inexistente ou completamente inconsistente**  
   - Falta do `inspectah_s32_evidence_bundle.zip`;  
   - bundle com conteúdo irrecuperável ou incompatível com o filemap/scorecards.

NO-GO não é um drama existencial: significa que o código da S32 pode continuar vivendo em branch, feature flag ou ambiente isolado — **mas ainda não ganhou o direito de conviver com o restante da plataforma**.

---

#### 5.4.2 Operação mínima pós-S32 — runbook e guardrails

Uma vez tomada a decisão de GO ou GO COM RESTRIÇÕES, o Truth-DB + Contestação v1 passa a existir como componente operacional. A S32 define, então, o **runbook mínimo** que a equipe precisa seguir.

##### 5.4.2.1 Rotina diária recomendada

1. **Checar métricas-chave**  
   - Olhar para o painel/endpoint de métricas e verificar:  
     - taxa de sucesso de promoção (`truthdb_promotion_success_rate`);  
     - taxa de contestações (`truthdb_contestation_rate`);  
     - taxa de erro (`truthdb_flow_error_rate`);  
     - latência p95 (`truthdb_flow_latency_p95`).

2. **Verificar logs de erro críticos**  
   - Filtrar logs do `PromotionService` e `ContestationService` em busca de:  
     - exceções recorrentes;  
     - falhas de banco;  
     - violações de invariantes.

3. **Executar healthcheck lógico simples**  
   - Rodar um script tipo `python -m scripts.truthdb_healthcheck` que:  
     - cria ou localiza uma claim de teste;  
     - promove a claim;  
     - registra e processa uma contestação;  
     - confirma, em queries simples, que blocos/estados foram criados conforme esperado.

4. **Registrar pequeno status diário (semi-automatizável)**  
   - Ex.: guardar em um log ou sistema de anotações:  
     - número de promoções e contestações do dia;  
     - incidentes observados;  
     - qualquer comportamento estranho.

##### 5.4.2.2 Tratamento de incidentes

Quando algo der errado (e eventualmente vai), a S32 define como reagir:

1. **Detectar e qualificar o incidente**  
   - É falha intermitente ou sistemática?  
   - Atinge um caso isolado ou muitos casos?  
   - Aparece em métricas/logs ou foi descoberto por acaso?

2. **Reduzir impacto imediato**  
   - Se necessário, reduzir volume de novas promoções/contestações;  
   - colocar certos tipos de claims em “modo de observação”;  
   - pausar integrações automáticas que dependam do Truth-DB.

3. **Congelar contexto para análise**  
   - Guardar dumps adicionais de blocos/estados para casos afetados;  
   - anotar IDs de claims e de contestações problemáticas;  
   - salvar uma cópia do bundle parcial do momento do incidente, se útil.

4. **Reproduzir em ambiente de teste**  
   - Usar scripts, testes e, se necessário, o bundle da S32 para reproduzir o bug em ambiente controlado;  
   - escrever ou ajustar testes (unitários/integração) que capturem o problema.

5. **Corrigir e registrar post-mortem curto**  
   - Documentar causa raiz, impacto e correção;  
   - atualizar, se for o caso, o runbook (incluindo checks adicionais);  
   - considerar se o bug indica uma lacuna de especificação a ser endereçada em sprint futura.

---

#### 5.4.3 Dever de casa da S32 para sprints futuras (S33+)

A Sprint 32 não esgota o tema “verdade e contestação”; ela inaugura o núcleo. Este bloco registra o “dever de casa” que a S32 explicitamente passa para as próximas sprints.

##### 5.4.3.1 Extensão de escopo

- Suportar novos tipos de claims além do prioritário v1;  
- Refatorar/estender `claims/adapters_truthdb.py` para cobrir mais domínios;  
- Garantir que cada novo tipo venha acompanhado de testes de promoção e, quando fizer sentido, de contestação.

##### 5.4.3.2 Sofisticação da lógica de decisão

- Evoluir de uma lógica v1 (simples) para uma lógica que incorpore:  
  - comitês de agentes;  
  - pesos de evidência;  
  - políticas de promoção mais ricas (verdade provisória, verdade consolidada, etc.).

- Qualquer nova lógica deve respeitar o histórico criado pela S32 — sem reescrever o passado de forma incompatível.

##### 5.4.3.3 Observabilidade e produtos

- Criar painéis mais ricos para Truth-DB (por caso, por tema, por fonte).  
- Conectar a camada de produtos (Programa 4) ao Truth-DB como fonte oficial:  
  - battlefield de narrativas;  
  - Fact Cards;  
  - painéis de estado de caso.

##### 5.4.3.4 Padrão para novos núcleos críticos

- Estabelecer a S32 como **referência**: qualquer sprint que introduzir outro núcleo crítico (ex.: motor de comitês, camada de causalidade, etc.) deve:  
  - replicar o nível de rigor de gates, bundle e ORR definido aqui;  
  - tratar integridade, auditabilidade e observabilidade como requisitos hard, não opcionais.

---

#### 5.4.4 Síntese final do Bloco 4 (e do Capítulo 5)

Com este Bloco 4, o Capítulo 5 passa a ter:

- critérios claros para **GO / GO COM RESTRIÇÕES / NO-GO**;  
- um **runbook mínimo** para operar o Truth-DB + Contestação v1 sem andar no escuro;  
- um protocolo de tratamento de incidentes que respeita o espírito do Inspectah (sempre com evidência e rastreabilidade);  
- um conjunto explícito de **obrigações deixadas para sprints futuras** — para que a S32 seja o começo sólido do núcleo de verdade, não um fim em si mesma.

O resultado final é que a Sprint 32 não só entrega código, mas entrega um **módulo vivo, julgável, auditável e operável**, com padrões que elevam a barra para tudo que vier depois no Inspectah.

