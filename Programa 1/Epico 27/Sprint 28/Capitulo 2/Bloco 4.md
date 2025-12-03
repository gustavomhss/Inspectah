# Inspectah — Sprint 28
## Capítulo 2 — Bloco 4
### Gate S28_G6, Gate S28_G7, Métricas da Sprint e DoD Global

---

#### 2.4.1 Gate S28_G6 — Demo Interna & UX

**Objetivo do gate**  
Validar, com pessoas, que o que foi construído em S28 é **operável de verdade** por humanos, e não apenas tecnicamente correto no papel e nos testes automatizados.

S28_G6 responde à pergunta:  
> “Se eu entregar essa versão do Inspectah para o time de operação hoje, eles conseguem usar o console de fontes e confiar no comportamento de ON/OFF sem gambiarras?”

Enquanto os gates anteriores (G0–G5) olham para código, schema, testes e regressões, o G6 olha para:
- fluxo real de uso,  
- clareza da UI,  
- previsibilidade das ações,  
- fricções que só aparecem quando alguém tenta “viver” o produto.

**Script oficial**  
`bin/s28_g6_demo_internal.sh`

**Pré-requisitos para rodar o gate**
- Backend da aplicação rodando em ambiente local ou de staging, com:
  - migrations de S28 aplicadas,  
  - Ingestão 2.0 operando em modo de teste (scheduler controlável/trigger manual),  
  - API `/admin/sources` estável (G2 em PASS).
- Frontend (console de fontes v2) buildado e disponível (G3 em PASS).  
- Dados mínimos de teste:
  - ao menos 1 fonte existente (pode ser criada como parte do roteiro),  
  - ambiente pronto para simular ingestão (logs/`IngestionRun` visíveis).

**Roteiro mínimo da demo (obrigatório)**  
A demo deve ser guiada por um roteiro simples e repetível, cobrindo os casos canônicos:

1. **Caso A — Cadastro de nova fonte de notícias (RSS)**
   - Abrir o console de fontes v2.  
   - Criar uma nova fonte do tipo `news_rss` com config válida.  
   - Ver a fonte aparecer na lista em estado `ACTIVE` (ou `DISABLED`, se essa for a política inicial definida).  
   - Verificar (via logs ou tela auxiliar) que a nova fonte passa a ser ingerida após o ciclo de ingestão.

2. **Caso B — Desativação de fonte problemática**
   - Selecionar uma fonte que esteja sendo ingerida.  
   - Desativá-la pelo console (ação de ON/OFF).  
   - Confirmar visualmente mudança de estado (`ACTIVE` → `DISABLED`).  
   - Validar que novos `IngestionRun` deixam de aparecer, dentro de 1–2 ciclos de scheduler.

3. **Caso C — Reativação após manutenção**
   - Reativar a mesma fonte (`DISABLED` → `ACTIVE`) via console.  
   - Acompanhar retorno da ingestão (novos `IngestionRun` surgindo).  
   - Confirmar que não foi necessário fazer nenhum ajuste manual extra.

4. **Caso D — Ajuste de configuração em fonte existente**
   - Editar uma fonte existente para ajustar cadência/descrição/domínio.  
   - Salvar alterações.  
   - Verificar que a UI reflete os novos valores e que a ingestão passa a usar a nova configuração.

5. **Robustez mínima de UX**
   - Simular erro da API (ex.: desligar o backend) e observar mensagens de erro no console.  
   - Ver o comportamento da tela de lista de fontes quando não há nenhuma fonte cadastrada.

**Participantes recomendados na demo**
- 1 pessoa com perfil de **Operador de Ingestão**.  
- 1 pessoa com perfil de **SRE/On-call**, se disponível.  
- 1 dev da squad, para anotar feedback técnico e de UX.

**Coleta de feedback**
Durante a demo, registrar respostas para três perguntas simples:
1. O que ficou **muito bom**? (pontos fortes)  
2. O que ainda **incomoda**? (fricções, confusões, ruídos)  
3. O que seria **inaceitável** em operação real se não fosse melhorado em sprints futuras?

Esse feedback deve ser resumido e anexado ao scorecard.

**Scorecard S28_G6 — Campos mínimos**
Local: `out/scorecards/S28_G6_demo_internal.json`

- `gate_id`: "S28_G6_demo_internal"  
- `status`: "PASS" | "FAIL"  
- `scenarios_demoed`: lista de cenários (A–D, robustez) com `ok = true/false`  
- `participants`: lista (nomes ou papéis)  
- `ux_feedback_summary`: texto curto consolidando feedback  
- `followup_items`: lista de itens para backlog futuro (E27.2, E27.3, E29–E32)

**Critérios de PASS**
- Todos os cenários do roteiro mínimo (A–D) executados até o fim **usando apenas a UI**.  
- Não há bloqueios graves de UX (ex.: ações essenciais invisíveis ou confusas ao ponto de exigir suporte constante).  
- `status = "PASS"` com followups aceitáveis como melhorias incrementais.

**Critérios de FAIL**
- Incapacidade de concluir qualquer cenário canônico via UI.  
- Fricções de UX tão severas que impeçam uso real, segundo o julgamento conjunto squad + operação.  
- Ausência de registro adequado de feedback.

**Impacto do FAIL**
- Bloqueia o GO global: uma sprint que mexe em operação de fontes não pode ser aprovada sem uma demo aceitável.  
- Deve disparar correções rápidas e, se necessário, ajustes de escopo antes de tentar o gate novamente.

---

#### 2.4.2 Gate S28_G7 — GO/NO_GO Final

**Objetivo do gate**  
Consolidar a decisão final da Sprint 28 de forma **explícita, rastreável e baseada em evidências**, não em opinião.

S28_G7 responde às perguntas:
- “Podemos declarar a Sprint 28 GO, com responsabilidade?”  
- “Quais evidências sustentam essa decisão?”

**Script oficial**  
`bin/s28_g7_go_no_go.sh`

**Pré-requisitos**
- Gates S28_G0 a S28_G6 executados ao menos uma vez.  
- Scorecards individuais presentes:
  - `out/scorecards/S28_G0_*.json`  
  - ...  
  - `out/scorecards/S28_G6_*.json`

**Responsabilidades do script**
1. Ler os scorecards S28_G0…S28_G6.  
2. Validar que todos estão com `status = "PASS"`.  
3. Agregar informações relevantes:
   - lista de gates, status, observações-chave,  
   - principais riscos remanescentes e sua classificação (P0/P1/P2).  
4. Gerar o scorecard global da sprint:
   - `out/scorecards/S28_overall.json`

**Campos mínimos do scorecard S28_overall**
- `sprint_id`: "S28"  
- `epic`: "E27.1_CRUD_and_onoff_sources" (ou similar)  
- `status`: "GO" | "NO_GO"  
- `gates`: array de objetos `{ gate_id, status }`  
- `states_alvo`: resumo booleano dos estados-alvo SA-28-01…SA-28-05  
- `risks`: lista de riscos remanescentes, com:
  - `id` (ex.: "RISK-S28-01"),  
  - `severity`: "P0" | "P1" | "P2",  
  - `description`,  
  - `mitigation_plan` (se P2)  
- `decision_owners`: lista de papéis/pessoas que participaram da decisão GO/NO_GO  
- `notes`: campo livre com observações adicionais

**Critérios de GO**
- Todos os gates S28_G0…S28_G6 com `status = "PASS"`.  
- Riscos P0/P1 mitigados ou resolvidos dentro da sprint (não deixam pendência que comprometa operação de fontes).  
- Riscos remanescentes, se houver, classificados apenas como P2 (melhorias desejáveis, não bloqueantes).

**Critérios de NO_GO**
- Qualquer gate G0–G6 com `status = "FAIL"`.  
- Existência de risco P0/P1 sem plano de resolução imediato dentro da sprint.  
- Evidência de que ON/OFF ainda não é determinístico ou console está impróprio para uso diário.

**Impacto de um NO_GO**
- S28 não é considerada parte de um baseline “seguro” do produto.  
- As mudanças da sprint podem ser mantidas em branch/feature isolada até que condições de GO sejam atingidas.  
- A decisão e o motivo do NO_GO ficam registrados no `S28_overall.json` e na documentação (Cap. 4).

---

#### 2.4.3 Métricas da Sprint 28

Além do veredito binário dos gates, a Sprint 28 acompanha um conjunto de **métricas complementares** para dar textura à avaliação de qualidade.

**M1 — Cobertura de testes relacionada a fontes & ingestão**
- Cobertura no módulo de domínio de fontes (`app/sources/models.py`, `tests/domain/...`).  
- Cobertura de API de admin (`tests/api/test_admin_sources_crud_onoff.py`).  
- Cobertura de integração ON/OFF × Ingestão (`tests/integration/test_sources_ingestion_onoff.py`).  
- Cobertura de UI (fluxos A–D) nos testes de console.

Objetivo qualitativo:  
> “Todos os caminhos críticos da operação de fontes e ON/OFF possuem testes automatizados que quebram se alguém estragar o contrato.”

**M2 — Tempo de ação percebido em ON/OFF**
- Medida qualitativa capturada na demo (G6):  
  - tempo entre clique em “Desativar” e percepção clara de que a fonte saiu do fluxo (ex.: ausência de novos `IngestionRun`).  
  - tempo entre clique em “Ativar” e retorno da ingestão.

Não precisa ser uma métrica super precisa em ms; basta registrar:
- se a sensação é de “quase imediata dentro da janela de scheduler”,  
- se causa dúvidas (“será que desligou mesmo?”).

**M3 — Regressões de legado detectadas e corrigidas**
- Número de regressões funcionais encontradas em S21/S22 durante o G5.  
- Quantas foram corrigidas dentro da sprint.  
- Ideal: zero regressões no final.

**M4 — Qualidade de UX percebida**
- Consolidada a partir das respostas do G6:
  - clareza dos estados de fonte,  
  - facilidade de encontrar ações de ON/OFF,  
  - facilidade de seguir o fluxo A–D sem instruções externas.

Essas métricas alimentam retrospectivas e planejamento de sprints futuras (E27.2, E27.3, E29–E32), mesmo que não apareçam como gates binários.

---

#### 2.4.4 Definition of Done (DoD) global da Sprint 28

A **Definition of Done global** da S28 sintetiza tudo o que já foi dito em Cap. 1 e 2 em um conjunto de afirmações que devem ser verdade ao final da sprint.

A Sprint 28 só está **DONE** se, simultaneamente:

1. **Gates concluídos**  
   - Todos os gates S28_G0…S28_G7 estão em `PASS`.  
   - O scorecard agregado `out/scorecards/S28_overall.json` existe, está bem formado e indica `status = "GO"`.

2. **Modelo & schema consolidados**  
   - O modelo de `Source` (domínio) possui todos os campos e enums definidos para E27.1.  
   - Migrations de S28 foram aplicadas e testadas; não há campos órfãos ou estados ilegais na base.  
   - Invariantes críticas (ciclo de vida de estados, validações por tipo) estão cobertas por testes automatizados.

3. **API de admin `/admin/sources` pronta para uso real**  
   - CRUD & ON/OFF de fontes expostos via API de admin de forma clara e testada.  
   - Erros retornam códigos HTTP adequados (400/404/409) e mensagens consistentes.  
   - OpenAPI atualizado descrevendo essas rotas de forma fiel.

4. **Console de fontes v2 operável**  
   - Operadores conseguem, via UI: criar, editar, ativar, desativar e deprecar fontes em cenários típicos.  
   - Fluxos canônicos A–D cobertos por testes de UI e validados em demo.  
   - Console visualmente coerente com o Design System Admin v1.

5. **ON/OFF × Ingestão 2.0 determinístico**  
   - Não há cenários em que fonte `DISABLED` continue a ser ingerida.  
   - Reativar fonte recoloca-a no fluxo sem necessidade de hacks.  
   - Cenários essenciais documentados e testados.

6. **Legado S21/S22 em paz**  
   - Gates relevantes de S21/S22 relacionados a fontes e ingestão executam em `PASS` após S28.  
   - Eventuais mudanças inevitáveis no comportamento foram documentadas e comunicadas.

7. **Documentação e evidências organizadas**  
   - Capítulos 1–4 da Sprint 28 atualizados, coerentes com o estado final do código.  
   - Evidências dos gates armazenadas em `out/evidence/S28_G*/**`.  
   - Scorecards individuais e o scorecard global presentes em `out/scorecards/`.

8. **Backlog de descobertas futuras registrado**  
   - Pontos identificados como fora de escopo (E27.2, E27.3, E29–E32) foram registrados com contexto e sugestão de encaixe.  
   - Nenhum assunto crítico foi "jogado para debaixo do tapete" sem rastreabilidade.

---

Com este Bloco 4, o Capítulo 2 da Sprint 28 fica completo:  
- G6 garante que o produto é utilizável por humanos,  
- G7 consolida a decisão final com base em evidências,  
- as métricas dão textura à avaliação,  
- e o DoD global fecha o que significa, sem dúvida, que a S28 está realmente DONE e em GO.