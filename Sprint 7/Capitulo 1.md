# Sprint 7 — Capítulo 1

## Objetivo, Escopo, Métricas e Filme da Experiência

> Arquivo de referência: `docs/sprint_7/sprint_7_capitulo_1.md`
> Este capítulo ancora os demais artefatos da Sprint 7 (Cap. 2–4, resultados e gates S7-G*).

---

## 1. Ponto de partida — estado pós Sprint 6

Ao final da Sprint 6, o Inspectah está em estado **Alpha headless**, robusto e validado:

- Domínio piloto definido (preços de itens básicos em uma cidade/região).
- Três fontes ativas e consistentes (`fonte_a`, `fonte_b`, `fonte_c`), com fixtures, parsers e configs em:
  - `config/sources/fonte_a.yaml`
  - `config/sources/fonte_b.yaml`
  - `config/sources/fonte_c.yaml`
- Modelo canônico do domínio piloto formalizado em `config/fields/dominio_piloto.yaml`.
- Runtime Python em `inspectah/sprint6/` capaz de:
  - carregar configs e campos;
  - coletar dados e gerar pacotes de evidência em `out/evidence/dominio_piloto/...`;
  - responder consultas e gerar exports em `out/queries/`;
  - capturar métricas básicas;
  - empacotar tudo em um bundle reprodutível em `out/s6_bundle/`.
- Entry-points CLI em `bin/inspectah_*.sh` encapsulando validação de fontes, preview de campos, coleta, consulta, evidência, métricas, bundle e guard.
- Suite de gates S6-G0…S6-G8 implementada em `bin/s6_g*_*.sh`, com scorecards em `out/scorecards/S6_G*.json` e evidência em `out/evidence/S6_G*/`, encerrando a Sprint 6 em **GO**.

Em outras palavras: o **motor do Inspectah** está pronto, testado e reprodutível — mas ainda exige terminal e edição de arquivos para ser operado.

---

## 2. Visão da Sprint 7

A Sprint 7 transforma esse motor em um **protótipo utilizável** com interface mínima, mantendo a mesma disciplina de evidência.

Visão em uma frase:

> "Depois da Sprint 7, um admin e um usuário interno conseguem **usar o Inspectah apenas pelo navegador**, dentro do domínio piloto, para cadastrar fontes, consultar dados, ver as respostas de cada fonte e enxergar uma **decisão consolidada explicável**, sem tocar em YAML ou CLI."

A Sprint 7 **não** busca um produto final, nem uma UI polida. Ela entrega um **Inspectah Alpha com interface**, focado em validar três coisas:

1. O fluxo de **administração de fontes** por tela (sem edição de arquivos).
2. O fluxo de **consulta e comparação entre fontes** por tela.
3. A capacidade do Inspectah de **propor uma "verdade consolidada"** a partir das fontes, com rastreabilidade para a evidência bruta.

---

## 3. Pilares da Sprint 7 (P1–P5)

### P1 — UI mínima de administração de fontes

Entregar uma interface web onde o admin consegue, para o domínio piloto:

- Listar as fontes existentes (fonte_a, fonte_b, fonte_c e futuras).
- Criar, editar e desativar fontes, definindo:
  - identificador da fonte;
  - tipo (`rss`, `api_json`, `html_plain` ou equivalentes suportados);
  - endpoint/caminho de leitura;
  - parâmetros de parsing essenciais (chaves, seletores, etc.), alinhados aos parsers da S6.
- Persistir essas alterações em formato compatível com o runtime da S6 (por ex., gerando/atualizando `config/sources/*.yaml` ou equivalente), sem necessidade de edição manual.

### P2 — UI mínima para o modelo canônico (campos)

Oferecer ao admin uma visão amigável do modelo canônico do domínio piloto:

- Exibir, em tela, os campos definidos em `config/fields/dominio_piloto.yaml`, com rótulos, tipo e indicação de obrigatoriedade.
- Permitir ajustes controlados (ex.: rótulos amigáveis, agrupamento visual, marcação de campos-chave para decisão) sem quebrar o contrato técnico estabelecido na S6.
- Exibir um **preview canônico real**, usando registros coletados, simulando o que hoje é fornecido via `inspectah_fields_preview.sh`.

### P3 — UI de consulta para usuários finais

Entregar uma tela de consulta simples para o domínio piloto, permitindo que um usuário:

- Escolha parâmetros básicos de consulta (produto, região, período/"data de referência").
- Veja o resultado em formato compreensível:
  - uma linha por fonte com preço, região, horário de coleta e observações;
  - indicação clara de qual fonte respondeu o quê.
- Tenha acesso rápido à evidência:
  - acesso a um identificador de evidência (ou link interno) para cada linha, apontando para os pacotes em `out/evidence/dominio_piloto/...`.

### P4 — Motor de decisão consolidada (verdade proposta)

Acoplar à UI de consulta um mecanismo simples, explícito e auditável de "verdade consolidada":

- Definir uma estratégia de agregação específica para o domínio piloto (ex.: mediana dos preços válidos; ou média truncada; ou regra de maioria com critérios de desempate).
- Calcular, para cada consulta, um valor consolidado a partir das respostas canônicas das fontes.
- Exibir na UI:
  - o valor consolidado;
  - um texto curto explicando a regra aplicada (por ex.: "mediana dos preços das fontes válidas no intervalo selecionado");
  - um indicador de divergência (faixa [mín, máx], desvio simples ou percentual entre fontes).
- Manter rastreabilidade: o valor consolidado deve sempre apontar de volta para os registros e pacotes de evidência que o originaram.

### P5 — Integração limpa com o runtime da S6 e experiência de demo

Garantir que a UI construída na S7 é uma **casca confiável** sobre o runtime existente, não um sistema paralelo:

- Reutilizar o runtime de configuração, coleta, normalização, consulta, métricas e evidência da S6 (`inspectah/sprint6/*`).
- Permitir que a UI dispare, quando apropriado, operações de coleta/refresh, respeitando o modelo de evidência.
- Manter os scripts e gates da S6 operando normalmente; ajustes da S7 **não podem quebrar** a suíte S6-G0…S6-G8.
- Entregar um fluxo de demo claro, executável em poucos minutos apenas pelo navegador (descrito no Capítulo 4 e em `docs/sprint_7/sprint_7_resultados.md`).

---

## 4. Escopo da Sprint 7

### 4.1 Itens explicitamente dentro do escopo

- Implementação de uma aplicação web local simples (stack a definir nos Capítulos 3 e 4), com três áreas principais:
  - Administração de fontes;
  - Visualização/ajuste amigável do modelo canônico;
  - Consulta, comparação entre fontes e exibição de decisão consolidada.
- Camada de integração UI ↔ runtime S6, com foco em:
  - leitura e escrita de configs de fontes de modo compatível com `config/sources`;
  - leitura do modelo canônico a partir de `config/fields`;
  - consumo de dados normalizados e evidências produzidas pela coleta da S6.
- Implementação da primeira versão do motor de decisão consolidada, alinhado ao domínio piloto.
- Atualização e criação dos artefatos de docs da S7:
  - `docs/sprint_7/sprint_7_capitulo_1.md` (este doc);
  - `docs/sprint_7/sprint_7_capitulo_2.md` (gates e validação S7-G*);
  - `docs/sprint_7/sprint_7_capitulo_3.md` (filemap e estrutura de código/artefatos da S7);
  - `docs/sprint_7/sprint_7_capitulo_4.md` (plano de execução);
  - `docs/sprint_7/sprint_7_resultados.md` (wrap final da sprint).

### 4.2 Fora de escopo (explícito)

A Sprint 7 **não** pretende:

- Implementar autenticação avançada, autorização granular, multi-tenant ou integrações de login.
- Generalizar a UI para múltiplos domínios ou dezenas de tipos de fonte além do domínio piloto.
- Investir em design visual sofisticado, branding ou responsividade avançada; o objetivo é uma UI funcional e clara.
- Orquestrar deploy em produção, pipelines remotos ou integrações externas; o foco é ambiente local de desenvolvimento/demonstração.

Qualquer item que envolva esses temas deve ser explicitamente empurrado para sprints futuras.

---

## 5. Critérios de sucesso e métricas da Sprint 7

A Sprint 7 será considerada bem-sucedida não apenas quando "funcionar", mas quando atender a critérios claros e mensuráveis.

### 5.1 Métricas de fluxo e usabilidade mínima

- **M1 — Demo UI-only**: um operador interno consegue executar um roteiro de demo completo (admin ajusta fonte → coleta é rodada/confirmada → usuário consulta → vê valor consolidado e evidência) **em até 5 minutos**, usando apenas o navegador, sem editar arquivos nem digitar comandos.
- **M2 — Zero terminal para admin/usuário**: perfis admin e usuário conseguem realizar suas tarefas principais (cadastrar/ajustar fontes, consultar dados e ver decisão consolidada) **sem abrir o terminal**. Terminal pode ser usado apenas pelo operador para subir/derrubar o servidor local.

### 5.2 Métricas de cobertura funcional

- **M3 — Fontes gerenciáveis via UI**: pelo menos as três fontes do domínio piloto (`fonte_a`, `fonte_b`, `fonte_c`) são totalmente gerenciáveis pela UI (criar/editar/desativar) sem precisar tocar em `config/sources` manualmente.
- **M4 — Consultas suportadas**: para um conjunto de consultas representativas definido no Capítulo 2 (cenários de validação S7-G*), 100% das consultas devem produzir:
  - respostas por fonte;
  - valor consolidado;
  - link/identificador de evidência.

### 5.3 Métricas de explicabilidade e evidência

- **M5 — Explicação da decisão**: para toda consulta em que há valor consolidado, a UI exibe uma explicação textual da regra usada, e essa explicação está consistente com a documentação da S7.
- **M6 — Rastreabilidade para evidência**: a partir da tela de resultado, é possível chegar ao identificador/caminho de evidência de qualquer linha em **até 2 cliques**.

Essas métricas serão ligadas diretamente aos gates S7-G* (definidos no Capítulo 2), de forma que o "GO" da Sprint 7 reflita esses critérios.

---

## 6. Personas e histórias de uso

### Persona A — Admin de Fontes

- Objetivo: configurar e manter as fontes do domínio piloto sem editar arquivos.
- História-chave S7-A1:
  - Abrir o Inspectah no navegador;
  - ver a lista de fontes;
  - editar uma fonte (por exemplo, ajustar endpoint);
  - salvar;
  - validar visualmente, via preview canônico, que a fonte continua produzindo dados coerentes.

### Persona B — Usuário de Consulta

- Objetivo: obter uma resposta rápida e explicável sobre preços do domínio piloto.
- História-chave S7-B1:
  - Abrir a tela de consulta;
  - escolher produto e região;
  - executar a consulta;
  - ver os valores por fonte, o valor consolidado e uma explicação simples da regra aplicada;
  - ter a opção de inspecionar a evidência de uma das linhas para conferir a origem do dado.

### Persona C — Operador Interno

- Objetivo: manter o sistema saudável e coerente entre runtime e UI.
- História-chave S7-C1:
  - Rodar os gates da S6 (e da S7, após definidos);
  - subir a UI;
  - confirmar que os dados exibidos na interface refletem os mesmos dados/evidências validados pelos gates.

---

## 7. Filme da Sprint 7 (narrativa)

1. **Início**
   - O repositório está no estado pós-Sprint 6, com S6-G0…S6-G8 em GO.
   - Este Capítulo 1 é criado em `docs/sprint_7/sprint_7_capitulo_1.md` e aprovado.
   - A equipe alinha entendimento sobre objetivos, escopo e métricas M1–M6.

2. **Meio — construção da UI e integração**
   - É implementado o backend leve da UI, capaz de ler configs e dados produzidos pela S6.
   - São construídas as telas de admin de fontes e campos, com round-trip completo entre UI e arquivos de configuração.
   - Em seguida, é implementada a tela de consulta e o motor de decisão consolidada.
   - A cada incremento, são executados testes manuais focados nas histórias S7-A1, S7-B1 e S7-C1.

3. **Fim — validação e GO**
   - São definidos e implementados os gates S7-G* (Capítulo 2), amarrando-os às métricas M1–M6.
   - O roteiro de demo UI-only é executado por pelo menos uma pessoa que não participou diretamente da implementação.
   - Os gates da S6 são reexecutados para garantir não regressão.
   - O documento `docs/sprint_7/sprint_7_resultados.md` é preenchido com a descrição do que foi entregue, como usar e quais são as limitações.

Quando esses passos se completam, a Sprint 7 fecha seu arco: o Inspectah deixa de ser apenas um motor robusto e passa a ser um **Alpha utilizável com interface**, onde um admin consegue configurar fontes e um usuário consegue fazer perguntas reais, ver as respostas das fontes, enxergar uma decisão consolidada e rastrear tudo até a evidência bruta.

---

## 8. Definition of Ready (DoR) da Sprint 7

A Sprint 7 está pronta para começar quando:

- O estado pós-Sprint 6 está presente no repositório local (runtime da S6 e gates S6-G0…S6-G8 em GO).
- Este Capítulo 1 está versionado em `docs/sprint_7/sprint_7_capitulo_1.md`.
- Há consenso sobre:
  - o domínio piloto utilizado;
  - as três fontes iniciais da S7;
  - o recorte de funcionalidades para a UI.
- A equipe entende que a S7 **consome** o runtime da S6 e não refatora sua lógica central.

---

## 9. Definition of Done (DoD) da Sprint 7

A Sprint 7 é considerada **concluída** quando, ao final, são verdadeiras todas as condições abaixo:

1. Existe uma aplicação web local acessível com:
   - tela de administração de fontes;
   - tela de visualização/ajuste amigável do modelo canônico;
   - tela de consulta com exibição por fonte, valor consolidado e acesso à evidência.

2. É possível executar, apenas pelo navegador, o roteiro de demo definido (atendendo às métricas M1, M2, M3 e M4).

3. O motor de decisão consolidada está implementado, documentado e visível na interface (atendendo à métrica M5).

4. A rastreabilidade para evidência cumpre a métrica M6.

5. Os gates da S6 permanecem em GO e os gates da S7-G* (definidos no Capítulo 2) também retornam GO.

6. O documento `docs/sprint_7/sprint_7_resultados.md` existe e descreve:
   - o que foi entregue;
   - como usar a interface;
   - como reproduzir a demo;
   - limitações conhecidas e próximos passos naturais.

Com isso, a Sprint 7 sela a transição do Inspectah de um **motor headless validado** para um **protótipo utilizável com interface mínima**, pronto para ser exercitado por humanos e servir como base para as próximas sprints de expansão e endurecimento do produto.

