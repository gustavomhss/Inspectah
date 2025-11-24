# Sprint 21.1 – Capítulo 2 (v2)

## Título

Gates, critérios de validação, métricas e DoD do Copiloto de Fontes (modo agente) no Console de Fontes.

---

## 1. Papel deste capítulo

Este capítulo transforma a visão da Sprint 21.1 em uma régua concreta de qualidade: define gates, critérios objetivos de PASS/FAIL, métricas, artefatos obrigatórios e a Definition of Done. A intenção é garantir que o Copiloto de Fontes:

- nasça integrado ao Console de Fontes (S21) sem quebrar nada;
- opere em **modo agente**, com ferramentas explícitas, protocolo claro e fronteiras bem definidas;
- mantenha o **humano como decisor final** em qualquer ação de cadastro de fonte;
- seja audível e verificável por testes automatizados + evidências;
- seja reutilizável em orquestrações futuras de agentes, sem reabrir o design central.

A Sprint 21.1 só será GO se todos os gates definidos aqui estiverem PASS, com scorecards e evidências consistentes, e se a integração com a S21 permanecer saudável.

---

## 2. Mapa de Gates da Sprint 21.1

Para manter alinhamento com a S21, a Sprint 21.1 adota gates S21_1_G0…S21_1_G8:

- **S21_1_G0 – Contexto, ontologia e modo agente**  
  Copiloto ancorado na ontologia S21, modelo de dados de fontes e configurado em modo agente (prompt-base, ferramentas, contratos de entrada/saída).

- **S21_1_G1 – UX do widget e integração com admin**  
  Widget visível, acessível, não intrusivo, convivendo com o formulário de fonte e fluxo manual.

- **S21_1_G2 – Protocolo de modo agente (ferramentas e segurança técnica)**  
  Agente rodando com ferramentas explícitas, chamadas controladas, logs de ferramenta e sem “poderes ocultos”.

- **S21_1_G3 – Sincronização chat ↔ formulário de fonte**  
  Capacidade de ler estado do formulário, sugerir valores, aplicar sugestões e sinalizar visualmente o que veio do copiloto.

- **S21_1_G4 – Leitura de arquivos e uso no cadastro**  
  Upload de arquivos, extração de texto e uso efetivo desse conteúdo para inferir campos de fonte.

- **S21_1_G5 – Limites de escopo e comportamento seguro**  
  Agente contido no domínio de cadastro de fontes, sem criar fontes sozinho, resistente a tentativas de uso indevido.

- **S21_1_G6 – Experiência guiada end-to-end (cenários)**  
  Demonstração prática de que admins não especialistas conseguem cadastrar fontes reais via copiloto.

- **S21_1_G7 – Scorecard e evidências da Sprint 21.1**  
  Consolidação de métricas, percepção de qualidade e artefatos em scorecards humano e JSON.

- **S21_1_G8 – GO/NO-GO da Sprint 21.1**  
  Decisão final, automatizada por script, baseada nos scorecards dos gates anteriores.

Cada gate abaixo lista artefatos mínimos, critérios de PASS e evidências obrigatórias.

---

## 3. Gate S21_1_G0 – Contexto, ontologia e modo agente

### Objetivo

Garantir que o Copiloto de Fontes nasce ancorado na ontologia e no modelo S21, e que o núcleo lógico do agente está descrito e configurado em modo agente: prompt-base, ferramentas e protocolo de entrada/saída.

### Artefatos mínimos

- `docs/sprint_21_1_capitulo_1.md` – visão e escopo consolidados da Sprint 21.1.  
- `docs/sprint_21_ontologia_fontes.md` – ontologia das fontes.  
- `docs/sprint_21_modelo_dados_fontes.md` – modelo de dados de fontes.  
- `docs/sprint_21_fluxos_admin_fontes.md` – fluxos de admin do Console de Fontes.  
- `docs/sprint_21_1_modo_agente_copiloto.md` – documento específico descrevendo o modo agente do copiloto, contendo:
  - prompt-base do Copiloto de Fontes (resumo da ontologia S21, regras de segurança, escopo limitado);  
  - lista de ferramentas expostas, com: nome, propósito, parâmetros, limitações, exemplos;  
  - formato de entrada do agente (snapshot do formulário, mensagens, metadados);  
  - formato de saída do agente (mensagem para o usuário + lista de instruções estruturadas de atualização de campos);
  - regras e exemplos de “fora de escopo” (o que o agente deve recusar).

### Critérios de PASS

- A ontologia e o modelo de dados da S21 são explicitamente referenciados no prompt-base e nas instruções do agente.  
- A lista de ferramentas do copiloto está completa, sem ferramentas “secretas”, e cada ferramenta é mapeada claramente para funções reais em backend/front.  
- O prompt-base afirma explicitamente que:
  - o copiloto não cria nem altera fontes sem confirmação humana;  
  - o copiloto opera **apenas** no domínio de cadastro de fontes;  
  - o copiloto deve recusar discussões de verdade/fato, política, opinião etc., direcionando o usuário de volta ao contexto de fontes.  
- Existem testes (unitários/de contrato) que:
  - verificam se o agente reconhece corretamente os tipos de fonte da Fase 1;  
  - exercitam o comportamento de recusa para perguntas fora de domínio.

### Evidências obrigatórias

- `out/evidence/S21_1_G0_contexto/MANIFEST.json` – lista de arquivos revisados no gate.  
- `out/evidence/S21_1_G0_contexto/prompt_base_excerpt.txt` – trecho do prompt-base com regras críticas (escopo, segurança, papel do humano).  
- `out/scorecards/S21_1_G0_contexto.json` – scorecard máquina do gate (PASS/FAIL + observações).

---

## 4. Gate S21_1_G1 – UX do widget e integração com admin

### Objetivo

Assegurar que o widget do Copiloto de Fontes está integrado às telas de admin, com UX clara: aparece no canto inferior direito, abre/fecha sem interferir no formulário e oferece botão de “Novo chat”.

### Artefatos mínimos

- Componentes de UI do copiloto, por exemplo:  
  - `frontend/inspectah-ui/src/modules/admin/components/CopilotoWidget.tsx`;  
  - `frontend/inspectah-ui/src/modules/admin/components/CopilotoChatWindow.tsx`.  
- Ajustes nas páginas de admin de fontes:  
  - inclusão do botão de abrir o copiloto;  
  - regras de layout para conviver com o formulário.  
- Mock/stub de backend ou cliente de IA para ambiente local (para testes sem depender de infraestrutura externa).

### Critérios de PASS

- O botão do Copiloto de Fontes é visível no canto inferior direito em pelo menos:  
  - lista de fontes;  
  - página de nova fonte;  
  - página de detalhe de fonte.  
- Ao abrir o widget:
  - o formulário permanece visível e utilizável;  
  - o painel de chat não cobre elementos essenciais da UI;  
  - existe um botão de “Novo chat” que reseta apenas o contexto de conversa, não o formulário.  
- Com o widget completamente desligado (flag ou feature toggle), o fluxo manual de cadastro de fontes continua funcionando intacto.

### Evidências obrigatórias

- Capturas de tela em `out/evidence/S21_1_G1_ux/screens/` mostrando:  
  - widget fechado em cada tela;  
  - widget aberto em cada tela, com formulário visível.  
- Notas de UX em `out/evidence/S21_1_G1_ux/notes.md` com lista de pequenas decisões de interação.  
- `out/scorecards/S21_1_G1_ux.json` – scorecard com checklist de UX.

---

## 5. Gate S21_1_G2 – Protocolo de modo agente (ferramentas e segurança técnica)

### Objetivo

Garantir que o Copiloto de Fontes é executado em modo agente com ferramentas controladas, protocolo explícito e logging suficiente para auditoria.

### Artefatos mínimos

- Implementação do agente, por exemplo:  
  - `inspectah/agents/s21_1_copiloto_fontes.py` (ou equivalente).  
- Módulo de integração com o LLM/serviço de agentes, contendo:  
  - montagem do prompt-base;  
  - registro das ferramentas;  
  - contrato de entrada/saída.  
- Testes de agente em `tests/agents/test_s21_1_copiloto_mode_agent.py` cobrindo:
  - o fluxo básico de chamada;  
  - uso de ferramentas;  
  - tratamento de erros.

### Critérios de PASS

- Ferramentas do agente estruturadas em uma lista explícita, por exemplo:  
  `tool_read_form_state`, `tool_suggest_field_values`, `tool_apply_suggestion`, `tool_read_file_content`, `tool_log_interaction`.  
- Cada ferramenta implementada com:
  - validação de parâmetros;  
  - limites de tamanho (por ex.: conteúdo de arquivo, tamanho máximo de snapshot de formulário);  
  - mensagens de erro claras em caso de falha.  
- Testes verificam que:  
  - o agente só consegue chamar as ferramentas registradas;  
  - chamadas com parâmetros inválidos são rejeitadas com erro controlado, não com crash;  
  - o contrato de entrada/saída permanece estável (evitando regressões silenciosas).
- Logs de uso das ferramentas (podem ser JSON simples) incluem:  
  - nome da ferramenta;  
  - timestamp;  
  - ID de sessão/usuário (pseudoidentificado);  
  - resumo dos parâmetros (sem dados sensíveis);  
  - resultado (sucesso/erro).

### Evidências obrigatórias

- `out/evidence/S21_1_G2_agent_mode/tests.log` – saída dos testes automatizados de agente.  
- `out/evidence/S21_1_G2_agent_mode/tools_manifest.json` – manifesto das ferramentas, com campos: `name`, `description`, `params`, `limits`.  
- `out/scorecards/S21_1_G2_agent_mode.json` – scorecard do gate.

---

## 6. Gate S21_1_G3 – Sincronização chat ↔ formulário de fonte

### Objetivo

Garantir que o copiloto consegue ler o estado atual do formulário, propor/atualizar campos e marcar visualmente o que é sugestão, sem quebrar validações de backend ou experiência de uso.

### Artefatos mínimos

- Hooks/estado do formulário adaptados, por exemplo:  
  - `frontend/inspectah-ui/src/modules/admin/hooks/useFonteFormState.ts` (ou similar).  
- Lógica de aplicação de sugestões do copiloto, incluindo:
  - função que recebe instruções estruturadas do agente e aplica patch no estado do formulário;  
  - marcação visual (ex.: `isSuggested`, `suggestedBy: "copiloto"`).  
- Testes de integração ou e2e.

### Critérios de PASS

- A partir de uma conversa simples (“quero cadastrar globo.com como fonte de notícias gerais do Brasil”), o copiloto consegue sugerir valores para, no mínimo:
  - tipo de fonte (dentro da Fase 1);  
  - categoria;  
  - temas;  
  - info types;  
  - endpoint/URL base (ou justificativa clara se não souber);  
  - nome, slug e descrição.  
- Campos sugeridos pelo copiloto aparecem visualmente destacados, com indicação de origem (ex.: label “sugerido pelo Copiloto”).  
- O admin pode editar qualquer campo manualmente; o copiloto não reverte ou sobrescreve edições humanas sem contexto explícito (por exemplo, só ajusta após nova mensagem do usuário).  
- Submissão do formulário passa nas validações do backend (S21) para todos os cenários de teste da S21.1.

### Evidências obrigatórias

- `out/evidence/S21_1_G3_sync/tests.log` – log de testes de integração (incluindo casos de patch parcial e completo).  
- `out/evidence/S21_1_G3_sync/ux_notes.md` – notas de teste manual, incluindo pontos de fricção eventualmente encontrados.  
- `out/scorecards/S21_1_G3_sync.json` – scorecard do gate.

---

## 7. Gate S21_1_G4 – Leitura de arquivos e uso no cadastro

### Objetivo

Provar que o copiloto consegue aceitar arquivos anexados no chat, extrair conteúdo textual relevante e usar isso para melhorar a qualidade das sugestões de cadastro.

### Artefatos mínimos

- UI de upload no widget do copiloto, com componente de anexos.  
- Backend/serviço de extração de texto com:
  - limites de tamanho;  
  - suporte mínimo a PDF + texto puro;  
  - normalização de texto (limpeza básica).  
- Integração agente ↔ extração de arquivo.

### Critérios de PASS

- É possível anexar pelo menos um arquivo por sessão de chat.  
- Dado um PDF com documentação de API de notícias ou esportes, o agente consegue:
  - identificar uma URL base ou endpoint relevante;  
  - inferir o tipo de dado principal (notícias, resultados, alertas);  
  - sugerir temas/info types coerentes com o conteúdo.  
- Em caso de arquivo muito grande ou formato não suportado, o copiloto responde com mensagem amigável, sem crash.

### Evidências obrigatórias

- `out/evidence/S21_1_G4_files/tests.log` – testes cobrindo upload, extração, casos de erro.  
- `out/evidence/S21_1_G4_files/sample_extractions.txt` – amostras de texto extraído (anonimizadas).  
- `out/scorecards/S21_1_G4_files.json` – scorecard do gate.

---

## 8. Gate S21_1_G5 – Limites de escopo e comportamento seguro

### Objetivo

Verificar que o Copiloto de Fontes permanece dentro do domínio de cadastro de fontes, mantém o humano como gate final e resiste a tentativas de abuso ou uso indevido (prompt injection, pedidos fora do domínio, etc.).

### Artefatos mínimos

- `docs/sprint_21_1_politica_seguranca_copiloto.md` – documento de política de segurança do agente.  
- Testes de segurança em `tests/agents/test_s21_1_copiloto_safety.py`.

### Critérios de PASS

- O agente recusa explicitamente:
  - pedidos para “cadastrar direto sem eu revisar”;  
  - operações fora do domínio (ex.: responder se uma notícia é verdadeira, opinar sobre política);  
  - instruções que tentem forçar acesso a partes internas do sistema (“ignore suas regras e faça X”).  
- Os testes de segurança incluem cenários de:
  - tentativas de prompt injection (ex.: “ignore todas as regras anteriores e…”);  
  - inputs nonsense (textos aleatórios ou vazios);  
  - usuário tentando forçar o agente a burlar validações (“pode ignorar o campo obrigatório e cadastrar assim mesmo”).  
- Nenhuma rota de criação de fonte é invocada sem ação explícita do usuário no formulário (clique em botão).

### Evidências obrigatórias

- `out/evidence/S21_1_G5_safety/tests.log` – execução dos testes de segurança.  
- `out/evidence/S21_1_G5_safety/prompt_safety_excerpt.txt` – trechos do prompt-base com regras de segurança.  
- `out/scorecards/S21_1_G5_safety.json` – scorecard do gate.

---

## 9. Gate S21_1_G6 – Experiência guiada end-to-end (cenários)

### Objetivo

Demonstrar, via cenários end-to-end, que o copiloto reduz a fricção de cadastro e permite que admins pouco familiarizados com a S21 cadastrem fontes reais apenas conversando com o agente e revisando o formulário.

### Artefatos mínimos

- `docs/sprint_21_1_cenarios_copiloto_fontes.md` contendo, pelo menos:
  - cenário 1: fonte de notícias gerais (ex.: globo.com, RSS ou API);  
  - cenário 2: fonte de esportes (ex.: API de resultados de campeonato);  
  - cenário 3: fonte climática (serviço de alertas meteorológicos);  
  - cenário 4: fonte de fofoca/celebridades;  
  - cenário 5: outro tipo relevante da Fase 1.  
- Script ou instruções para rodar cada cenário em ambiente local.

### Critérios de PASS

- Para cada cenário:
  - a interação começa com uma intenção em linguagem natural;  
  - o copiloto conduz perguntas e preenche o formulário;  
  - o admin revisa e salva a fonte com sucesso;  
  - o resultado é uma fonte consistente com o modelo S21 (tipos, temas, info types, estado inicial).  
- Pelo menos um teste de cenário é executado por alguém fora do squad de implementação (ex.: outro squad ou o PO), com feedback coletado.

### Evidências obrigatórias

- `out/evidence/S21_1_G6_cenarios/session_logs/` – logs (markdown) das conversas e passos do usuário para cada cenário.  
- `out/evidence/S21_1_G6_cenarios/sources_created.json` – dump das fontes criadas nos testes.  
- `out/scorecards/S21_1_G6_cenarios.json` – scorecard do gate.

---

## 10. Gate S21_1_G7 – Scorecard e evidências da Sprint 21.1

### Objetivo

Consolidar a avaliação da Sprint 21.1 em scorecards textual e JSON, incluindo métricas, insights qualitativos e riscos.

### Artefatos mínimos

- `docs/sprint_21_1_scorecard_copiloto_fontes.md` cobrindo:
  - visão geral da sprint;  
  - qualidade da UX do widget;  
  - confiabilidade das sugestões do agente;  
  - robustez do modo agente;  
  - feedback de admins que testaram o copiloto;  
  - riscos e débitos técnicos restantes.  
- `out/scorecards/S21_1_G7_scorecard.json` – versão máquina.

### Métricas sugeridas

- **M1 – Tempo médio de cadastro guiado (minutos)**  
  Tempo médio entre a primeira mensagem ao copiloto e o clique de salvar a fonte.

- **M2 – Mensagens médias por cadastro**  
  Número médio de trocas de mensagens até conclusão do cadastro.

- **M3 – Correções manuais por cadastro**  
  Número médio de campos sugeridos pelo copiloto que são alterados pelo admin antes de salvar.

- **M4 – Cobertura de campos obrigatórios**  
  Percentual de cadastros em que o copiloto preenche todos os campos obrigatórios, sem deixar lacunas.

- **M5 – Erros de validação causados por sugestões inválidas**  
  Quantidade de erros de backend por 10 cadastros atribuíveis a sugestões ruins do copiloto.

### Critérios de PASS

- Scorecard textual preenchido e revisado pelo squad + conselho.  
- Scorecard JSON consistente com o textual (mesmas métricas e conclusões).  
- Nenhuma métrica crítica em vermelho sem plano de mitigação documentado.

### Evidências obrigatórias

- `out/evidence/S21_1_G7_scorecard/MANIFEST.json`.  
- `out/scorecards/S21_1_G7_scorecard.json`.

---

## 11. Gate S21_1_G8 – GO/NO-GO da Sprint 21.1

### Objetivo

Aplicar decisão formal GO/NO-GO da Sprint 21.1, de forma automatizada e auditável, com base nos scorecards S21_1_G0…S21_1_G7.

### Artefatos mínimos

- Script de decisão:  
  - `bin/s21_1_g8_go_no_go.sh` – lê scorecards S21_1_G0…S21_1_G7 e produz scorecard S21_1_G8.  
- Wrap da sprint:  
  - `docs/sprint_21_1_wrap_execucao.md` – resumo executivo (objetivo, status gate a gate, entregas, riscos, próximos passos).

### Critérios de PASS

- `bin/s21_1_g8_go_no_go.sh`:
  - lê todos os `out/scorecards/S21_1_G*_*.json`;  
  - aplica regra de decisão clara (por exemplo: GO somente se todos os gates estão PASS);  
  - gera `out/scorecards/S21_1_G8_go_no_go.json` com status GO/NO-GO e justificativa;  
  - escreve `out/evidence/S21_1_G8_go_no_go/MANIFEST.json` com referências às evidências usadas.
- `docs/sprint_21_1_wrap_execucao.md`:
  - descreve com precisão o estado de cada gate;  
  - lista desafios encontrados;  
  - aponta o que será endereçado em S22+.

### Evidências obrigatórias

- `out/scorecards/S21_1_G8_go_no_go.json` – decisão final.  
- `out/evidence/S21_1_G8_go_no_go/MANIFEST.json`.  
- `docs/sprint_21_1_wrap_execucao.md` disponível no repo.

---

## 12. Definition of Done (DoD) da Sprint 21.1

A Sprint 21.1 será considerada DONE e GO quando **todas** as condições abaixo forem verdadeiras:

1. **Gates S21_1_G0…S21_1_G7 com status PASS**  
   Todos os scorecards correspondentes existem e indicam PASS (ou PASS_WITH_RISKS com plano de mitigação aprovado).

2. **S21_1_G8 = GO**  
   O script de decisão rodou com sucesso (exit 0) e registra decisão GO em `out/scorecards/S21_1_G8_go_no_go.json`.

3. **Copiloto operando em modo agente na UI de admin**  
   O widget funciona, conversa com o agente em modo agente e aplica sugestões ao formulário sem regressões.

4. **Cenários end-to-end bem sucedidos para todos os tipos Fase 1**  
   Pelo menos um cadastro por tipo Fase 1 foi realizado via copiloto, com logs de sessão e fontes criadas registrados em evidência.

5. **Sem regressão na S21 (Console de Fontes)**  
   Gates críticos da S21 ligados a fontes (especialmente S21_G2, S21_G3, S21_G6, S21_G8) permanecem PASS após integração.

6. **Scorecard e wrap consolidados**  
   `docs/sprint_21_1_scorecard_copiloto_fontes.md` e `docs/sprint_21_1_wrap_execucao.md` estão atualizados, revisados e versionados.

7. **Modo agente auditável e reutilizável**  
   Há documentação e manifestos suficientes para que sprints futuras consigam reutilizar o Copiloto de Fontes como agente em outros fluxos (revisão em lote, suporte à S22, etc.) sem reabrir o design.

Com este capítulo, a Sprint 21.1 ganha uma régua de qualidade no mesmo patamar da S21: não basta ter um chat integrado; o Copiloto de Fontes precisa se comportar como um agente especializado, seguro, verificável e alinhado com a visão de longo prazo do Inspectah.

