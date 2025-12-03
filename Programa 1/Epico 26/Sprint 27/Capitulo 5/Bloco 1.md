# Inspectah — Sprint 27 (S27)
## Capítulo 5 — Bloco 1
### Contexto, Escopo e Perguntas-Chave do ORR da S27

> Arquivo-alvo sugerido no repo: `docs/s27_cap_5_1_orr_contexto_e_escopo.md`
>
> Função: explicar **por que** o ORR da Sprint 27 existe, **o que exatamente será julgado** e **quais perguntas o comitê precisa responder** ao final. Este bloco é a moldura mental do ORR: o resto do Cap.5 (blocos seguintes) detalha o como.

---

## 1. Por que existe um ORR específico para a S27

A S27 é a segunda sprint do Épico E26 (Admin v1 para Programa 1: Fontes, Ingestão e Debunker). Ela não é uma sprint qualquer: é a sprint onde o Admin v1 deixa de ser um "experimento simpático" e passa a ser o padrão real dos consoles mais críticos do Inspectah.

O ORR da S27 existe para responder, com base em evidências concretas:

1. Se o que foi prometido para a S27 realmente foi entregue.  
2. Se o pacote "Admin v1 + Consoles de Programa 1" está pronto para ser usado em produção (mesmo que inicialmente em regime limitado).  
3. Se os riscos que sobram são aceitáveis e conhecidos — e não bombas escondidas.

Sem esse ORR, o Épico E26 correria o risco clássico de ser considerado "pronto" só porque o código compila e alguém fez uma demo bonita.

---

## 2. Escopo lógico da avaliação da S27

O ORR da S27 não tenta avaliar o Inspectah como um todo; ele foca num subconjunto muito específico:

- **Design System Admin v1**  
  - tokens, componentes base, padrões de layout e interação;  
  - qualidade técnica mínima (build, tests, estrutura de imports).  

- **Consoles Admin de Programa 1**  
  - Console de Fontes: cadastro, visão de saúde, estados de fonte;  
  - Console de Ingestão 2.0: overview, status por fonte, runs de ingestão;  
  - Console Debunker: casos, evidências, decisões.  

- **Fluxos E2E críticos cruzando esses consoles**  
  - Pelo menos um caminho que vai de um problema ou alteração em Fontes → impacto/visibilidade em Ingestão → eventual caso em Debunker.  

- **Camada de contratos de API que sustenta esses consoles**  
  - rotas, schemas e testes de contrato dos domínios Fontes, Ingestão e Debunker.  

- **Camada de operação/documentação para Programa 1**  
  - guia Admin v1.1;  
  - runbooks de operação de Fontes, Ingestão e Debunker.

O que **não** está diretamente em escopo do ORR da S27 (embora possa aparecer indiretamente):

- Consoles de outros programas ou módulos que não sejam Programa 1.  
- Decisões profundas sobre Truth-DB, Debunker global ou System of Blocks (estes são verificados por outros épicos/sprints).  
- Detalhes de infraestrutura fora do necessário para suportar os consoles admin avaliados.

O ORR pode mencionar problemas fora desse escopo, mas eles não deveriam travar o veredito da S27/E26 a menos que tenham impacto direto nos consoles e fluxos avaliados.

---

## 3. Relação entre S26, S27 e o Épico E26

O Épico E26 é composto por duas sprints:

- **S26** — foco em preparar o terreno de Admin v1 (design system base, alinhamento de Programa 1, primeiros encaixes).  
- **S27** — foco em consolidar Admin v1 como padrão real nos consoles de Programa 1, com fluxos E2E, contratos consolidados e operação documentada.

O ORR da S27, portanto:

- avalia **a S27 em si** (se entregou seus estados-alvo);  
- e, ao mesmo tempo, funciona como **ORR do Épico E26**: a soma S26 + S27 precisa resultar em algo que faça sentido como degrau do roadmap do Inspectah.

Imagem mental: S26 prepara a pista, S27 decola o avião. O ORR da S27 decide se o avião está mesmo no ar em condições de voo aceitáveis, ou se foi só uma "corridinha de táxi até a metade da pista".

---

## 4. Estados-alvo que o ORR vai verificar

Os estados-alvo da S27 já foram definidos em Cap.1, mas aqui são recapitulados na forma que interessa ao ORR:

- **SA-01 — Admin v1 como padrão real**  
  - Consoles de Fontes, Ingestão e Debunker usam AdminShell, AdminHeader, AdminContent e componentes base de forma consistente;  
  - o design system não é opcional nem apenas "demo".

- **SA-02 — Fluxos admin críticos funcionando E2E**  
  - Há cenários E2E claros (G2) cobrindo pelo menos:  
    - fluxo principal em Fontes;  
    - fluxo principal em Ingestão;  
    - fluxo principal em Debunker;  
    - pelo menos um fluxo combinado Fontes → Ingestão → Debunker.  

- **SA-03 — Contratos de API estáveis e verificáveis**  
  - rotas e schemas dos domínios Fontes, Ingestão e Debunker estão cobertos por testes de contrato;  
  - scorecard G4 está estável, sem mismatches graves.

- **SA-04 — Operação documentada para Programa 1**  
  - existe um guia Admin v1.1;  
  - existem runbooks de operação dos consoles de Fontes, Ingestão e Debunker;  
  - esses runbooks foram usados ao menos em simulações internas.

- **SA-05 — Avaliação objetiva da S27 e do Épico E26**  
  - scorecards G0–G6 completos;  
  - bundle de evidências gerado;  
  - ORR realizado com veredito registrado.

O ORR precisa responder explicitamente se cada um desses estados está: **atingido**, **parcialmente atingido** ou **não atingido**.

---

## 5. Perguntas-chave que o comitê de ORR deve responder

Para evitar reuniões genéricas, o ORR da S27 deve, no mínimo, responder às seguintes perguntas:

1. **Sobre Admin v1 (SA-01)**  
   - Admin v1 está sendo usado de forma consistente nos consoles, ou ainda existem telas importantes em padrão antigo?  
   - Há algum problema estrutural de ergonomia, performance ou manutenibilidade no design system atual?

2. **Sobre fluxos E2E (SA-02)**  
   - Um operador consegue, na prática, executar os fluxos críticos em Fontes, Ingestão e Debunker usando os consoles admin, sem gambiarras?  
   - Os cenários E2E documentados em G2 refletem bem o uso real dos consoles?

3. **Sobre contratos e APIs (SA-03)**  
   - Existem contratos/API que ainda são "frágeis" ou inconsistentes com o que as telas esperam?  
   - Se sim, esses problemas são graves o suficiente para impedir o uso em Programa 1?

4. **Sobre operação e runbooks (SA-04)**  
   - Um time de operações, que não participou diretamente do desenvolvimento, conseguiria operar Programa 1 usando apenas os runbooks e o guia Admin v1.1?  
   - Quais partes da operação ainda dependem de conhecimento tácito da equipe?

5. **Sobre riscos e roadmap (SA-05)**  
   - Quais riscos ainda estão presentes, e com qual impacto/likelihood?  
   - É aceitável seguir com Admin v1 em Programa 1 do jeito que está, ou o risco é alto demais?  
   - Quais são os próximos passos recomendados (por exemplo: sprints adicionais para ampliar cobertura, refinar UX, reforçar contratos)?

6. **Sobre o Épico E26 como degrau de produto**  
   - Com S26 + S27, Admin v1 em Programa 1 aproxima ou afasta o Inspectah da visão de produto desejada?  
   - O que precisa acontecer antes de escalar Admin v1 para outros programas ou módulos?

As respostas a essas perguntas devem aparecer em forma sintética em `S27_G6_orr_summary.json` e em forma explicada neste Cap.5.

---

## 6. Critérios mínimos para o ORR acontecer

O Bloco 1 também define o que precisa estar pronto **antes** da reunião de ORR, para que ela não vire uma terapia em grupo sem dados:

- Todos os gates G0–G5 foram rodados pelo menos uma vez na configuração final da S27, com scorecards e evidências organizados.  
- O script de G6 (`bin/s27_g6_orr_bundle.sh`) foi implementado e, no mínimo, testado em modo "dry-run" ou semi-final.  
- Consoles admin estão funcionalmente acessíveis no ambiente em que será feita a demonstração.  
- Cap.1–Cap.4 estão atualizados o suficiente para não gerar confusão sobre o que foi combinado/doado.  
- Os principais owners confirmaram disponibilidade para a sessão de ORR.

Se algum desses itens falhar, o ORR deve ser adiado ou explicitamente marcado como **ORR preliminar**, sem veredito definitivo.

---

## 7. Resultado esperado deste bloco

Ao final da leitura deste Bloco 1, todo participante do ORR deve saber:

- qual "jogo" está sendo jogado na S27;  
- quais são as peças em campo (Admin v1, consoles, fluxos, APIs, docs);  
- quais são os estados que precisam ser julgados;  
- quais perguntas precisam ser respondidas na sessão;  
- e quais pré-requisitos precisam estar atendidos para o ORR não ser perda de tempo.

Os blocos seguintes de Cap.5 (formato detalhado do scorecard G6, roteiro detalhado da sessão, critérios GO/NO_GO/GO_WITH_RISKS, etc.) constroem em cima deste contexto.