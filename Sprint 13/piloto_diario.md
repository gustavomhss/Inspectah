# Sprint 13 – Piloto controlado v0 (diário)

## Casos escolhidos

- Caso 1:
  - Tipo: Obra pública municipal (reforma de escola)
  - Fontes principais: Diário Oficial do município (publicação do contrato/ato), portal de transparência (empenhos/pagamentos), notícia em portal local
  - Região / contexto: Cidade de médio porte na Região Metropolitana do Rio (ex.: Niterói / São Gonçalo – cenário piloto)
  - Por que escolhi esse caso:
    - Tem ato formal em Diário Oficial (contrato/dispensa/resultado de licitação).
    - Tem movimentação financeira rastreável em portal de transparência.
    - Tem cobertura mínima na imprensa local.
    - É um tipo de caso que o Inspectah deve saber acompanhar muito bem (obra, valor, situação “andamento vs. abandono”).

- Caso 2 (opcional):
  - Tipo: Evento climático severo (chuva forte, alagamento, deslizamento)
  - Fontes principais: serviço nacional de meteorologia (alertas oficiais), defesa civil estadual/municipal (comunicados), notícias em portais grandes
  - Região / contexto: Região Metropolitana do Rio ou outra capital com histórico de chuva forte
  - Por que escolhi esse caso:
    - Gera linha do tempo clara (alertas → evento → consequências).
    - Mostra bem o papel do Inspectah em “juntar” alertas oficiais + notícias + relatórios.
    - Exercita o domínio de evento climático que a Sprint 12 já modelou.

## Como estou rodando o Inspectah no piloto

- Estado do código:
  - Branch: main
  - Versão de referência: tag v0.3-s12 (Sprint 12 – ingestão contínua + Explorer v0)

- Comando(s) para validar o backbone S12 antes/depois de testar:
  - cd /Users/gustavoschneiter/Documents/Inspectah
  - git checkout main
  - git pull --ff-only origin main
  - bash bin/s12_gates_all.sh
  - bash bin/s12_g8_decision.sh

- Comando(s) que uso pra subir backend/UI durante o piloto:
  - (preencher com os comandos reais que já uso hoje, quando quiser)

## Observações de uso (Explorer, Debunker, casos/timeline, feedback)

### Dia 1 – Foco em obra pública (Caso 1)

- O que funcionou bem:
  - Consegui localizar rapidamente o caso de obra pública usando a busca do Explorer a partir de parte do título/tema.
  - A timeline respeita a ordem cronológica dos eventos (licitação → contrato → movimentações → problemas).
  - Os links de evidência (DO, portal, notícia) estão clicáveis e me levam para fontes que fazem sentido para o caso.
  - O Debunker está sendo chamado de forma consistente para eventos sensíveis (contrato, aditivo, paralisação), sem “pular” eventos importantes.

- O que doeu / ficou confuso:
  - O título do caso na CasePage é pouco informativo: não deixa claro, de primeira, qual é a obra, qual o número do contrato e o valor envolvido.
  - Falta um resumo curto em linguagem humana no topo da CasePage (“esta obra está em situação X, por causa de Y/Z”); tenho que ler a timeline inteira para montar esse filme na cabeça.
  - A timeline tem cara de log técnico: os textos são corretos, mas pouco legíveis para um humano não técnico (campos muito crus, pouco contexto).
  - A decisão do Debunker aparece de forma pouco amigável: é possível entender que o evento foi aceito/suspeito/etc., mas a explicação é “seca” demais (parece debug, não justificativa).
  - Não fica evidente, em nenhum lugar, um “estado consolidado” do caso (OK, suspeito, crítico). Fico com a sensação de que o sistema não fecha um veredito mínimo.
  - O botão de feedback na CasePage é discreto: dá pra usar, mas não salta aos olhos; um usuário comum poderia não perceber essa possibilidade de “reportar problema”.

- Ideias de melhoria:
  - Enriquecer o cabeçalho da CasePage com um título mais informativo, por exemplo: “Reforma da Escola Municipal X – Contrato 123/2025 – R$ 4,2M”.
  - Adicionar um resumo curto no topo (“visão executiva” do caso): 2–3 frases explicando a situação atual da obra (andamento, riscos, pontos de atenção).
  - Tornar os textos da timeline mais legíveis, traduzindo campo técnico em frases humanas (“Em 10/03/2025, a prefeitura assinou o contrato 123/2025 com a empresa Y de R$ 4,2M para reforma da Escola X.”).
  - Exibir a decisão do Debunker em linguagem clara, com justificativa condensada (“Aceito porque DO + portal de transparência + notícia local convergem”; “Suspeito porque há rompimento de padrão nos valores/atrasos sem explicação.”).
  - Introduzir um indicador visual de estado consolidado do caso (OK / suspeito / crítico), calculado a partir da timeline + Debunker, para reduzir o esforço cognitivo de entender “como está” a obra.
  - Destacar melhor o botão de feedback, com texto explícito (“Reportar problema nesta obra”) e posição mais evidente na CasePage.

### Dia 2 – Foco em evento climático (Caso 2)

- O que funcionou bem:
  - A timeline de evento climático consegue representar bem a sequência de alertas e acontecimentos (alertas iniciais → intensificação → registro de danos).
  - As fontes oficiais (serviço meteorológico, defesa civil) aparecem na timeline em pontos coerentes, ajudando a confiar mais no que está sendo exibido.
  - Fica claro que o Debunker está sendo aplicado em eventos relevantes (alertas de nível laranja/vermelho, relatórios de danos mais graves).

- O que doeu / ficou confuso:
  - Falta um “painel geral” no caso climático indicando, em uma frase, qual foi o impacto principal daquele evento (ex.: “chuva intensa com alagamentos moderados em tais bairros”).
  - A timeline mistura um pouco eventos “muito técnicos” (alertas, boletins) com eventos mais narrativos (notícias, relatórios de danos) de um jeito que exige esforço pra entender a gravidade real.
  - Não fica claro o critério do Debunker para classificar certos eventos como incertos/suspeitos, principalmente quando fontes divergem.
  - Assim como na obra pública, falta um estado consolidado (“evento sob controle / evento crítico / informações conflitantes”), dificultando uma leitura rápida da situação.
  - O fluxo de feedback ainda é “interno demais”: é funcional para quem está operando o sistema, mas não está otimizado para alguém leigo relatar rapidamente um problema (“informação errada”, “evento faltando”, etc.).

- Ideias de melhoria:
  - Adicionar um pequeno resumo de impacto no topo da CasePage de evento climático, com uma frase do tipo “Evento de chuva forte com alagamentos em X bairros, sem registro de mortes até o momento”.
  - Separar visualmente na timeline o que é “alerta técnico” do que é “relato de impacto” (por exemplo, com labels ou seções), para facilitar a leitura do que realmente aconteceu com as pessoas.
  - Deixar mais clara a racionalidade do Debunker para eventos climáticos, com explicações simples do tipo “classificado como incerto porque as fontes oficiais divergem no número de ocorrências”.
  - Expor um estado consolidado do evento (por exemplo, um badge “situação monitorada”, “risco elevado”, “relatos conflitantes”), resumindo a leitura da timeline + Debunker.
  - Ajustar o fluxo de feedback para permitir que o usuário reporte, em 2–3 cliques, que há “informação desatualizada”, “fonte quebrada” ou “evento importante faltando”.

## Backlog bruto para próxima sprint

- [ ] Enriquecer o cabeçalho da CasePage com título informativo (nome da obra/evento + identificador + valor/tipo).
- [ ] Criar um resumo curto (“visão executiva”) no topo dos casos, explicando a situação atual em 2–3 frases.
- [ ] Tornar a timeline mais legível, com textos em linguagem humana e, quando fizer sentido, separação entre eventos técnicos e de impacto.
- [ ] Expor a decisão do Debunker na UI em formato amigável, com justificativa curta e compreensível.
- [ ] Introduzir um indicador visual de estado consolidado do caso (OK / suspeito / crítico / conflituoso) a partir da timeline + Debunker.
- [ ] Melhorar a visibilidade e o texto do botão de feedback na CasePage, deixando claro que o usuário pode “reportar um problema neste caso”.
- [ ] Otimizar o fluxo de feedback para que seja possível reportar problemas comuns (info errada, fonte quebrada, evento faltando) em poucos cliques, com boa rastreabilidade no painel interno.

