# Sprint 13 — Capítulo 1 — Piloto Controlado & Explorer v1 (Visão de Produto, v2)

## 0) Ponto de partida

Após a Sprint 12, o Inspectah está em **v0.3-s12**:

- Ingestão contínua enxuta com registry de fontes e scheduler.
- Normalizadores de domínio (obra pública, evento climático) e Debunker v0 obrigatórios no fluxo.
- Serviços de casos/timeline/adapter para Truth-DB em memória.
- Explorer v0 + painel de feedback v0 funcionais.
- Gates S12_G0…G8 verdes, com scorecards e evidências reproduzíveis.

Do ponto de vista de engenharia, o backbone está saudável. Do ponto de vista de produto, porém, ainda se parece demais com uma **ferramenta de desenvolvedor com dados corretos**, e pouco com um **narrador de histórias compreensível para humanos**.

A Sprint 13 é o primeiro movimento explícito para mudar isso.

---

## 1) Papel da Sprint 13 no roadmap

### 1.1 Relação com S10–S16 e Fase 2

- S10 definiu Truth-DB + Guardião de Blocos como núcleo de verdade e ponte futura para o **Sistema de Blocos** e blockchain.
- S11–S16, conforme o plano de Sistema de Blocos, foram promovidas a **blueprint de Fase 2**: visão estratégica, não escopo imediato.
- A Nota de Escopo Temporário é clara: **sem reputação avançada, sem blockchain automática, sem Sistema de Blocos completo, sem comunidade avançada** neste momento.

A Sprint 13, portanto, não é sobre inventar mais infraestrutura. É sobre provar que o que já temos na S12 consegue, com ajustes de produto, **contar histórias complexas de forma clara e confiável**.

### 1.2 De pipeline bonito para produto multi-domínio

O usuário real do Inspectah não pensa em "pipelines". Ele pensa em histórias:

- "Essa obra vai sair ou é só promessa?"
- "Essa enchente foi evento pontual ou mini-desastre?"
- "Esse projeto de lei está vivo, morto ou andando aos trancos?"
- "Essa carreira política é limpa, nebulosa ou tóxica?"
- "Esse influencer é crescimento estável ou case de cancelamento?"
- "Esse atleta teve trajetória sólida, conturbada ou trágica?"

A Sprint 13 assume que o modelo **caso + timeline + fontes + Debunker + feedback + estado consolidado** precisa funcionar não só para obra e clima, mas também para:

1. Obra pública municipal.
2. Evento climático severo.
3. Projeto de lei.
4. Carreira política.
5. Perfil de influencer.
6. Carreira de atleta.

O objetivo da S13 é **provar a generalidade desse modelo** em um piloto bem definido, sem explodir o escopo técnico.

---

## 2) Problema central a resolver

### 2.1 Sintoma transversal

Mesmo com S12 concluída, olhando apenas para o Explorer v0 e a CasePage atual, temos um padrão de dor comum em todos os domínios:

- A CasePage não responde de cara **“que caso é esse e por que importa”**.
- A timeline parece mais **log técnico** do que narrativa humana.
- O Debunker aparece como **status seco** (aceito/suspeito/incerto), não como explicação.
- Não existe um **estado consolidado do caso** (OK/suspeito/crítico/conflituoso) em lugar óbvio.
- O fluxo de feedback funciona, mas é tímido, pouco visível e pouco guiado.

Resultado: o Inspectah exige esforço cognitivo alto para responder perguntas simples. Em vez de aliviar trabalho mental, ele ainda exige "tradução" mental por parte de quem usa.

### 2.2 Como esse problema se manifesta por domínio

- **Obra pública**  
  Difícil entender rapidamente qual é a obra, qual contrato, qual valor, em que estágio está e quais são os riscos. A timeline lista atos, mas não conta claramente se a obra está em andamento normal, atrasada, suspeita ou abandonada.

- **Evento climático**  
  Falta um resumo claro do impacto (onde, quando, quão grave). Alertas técnicos se misturam com relatos de dano. O usuário não entende, sem esforço, se aquilo foi um evento moderado, severo ou crítico.

- **Projeto de lei**  
  A tramitação é cheia de etapas (apresentação, comissões, pareceres, emendas, votações, arquivamento). Sem narrativa clara, o usuário se perde em detalhes e não sabe se o PL está vivo, travado ou morto.

- **Carreira política**  
  Muitos mandatos, cargos, votações importantes, escândalos, investigações e desfechos. O usuário precisa enxergar rapidamente se a trajetória é majoritariamente limpa, nebulosa ou problemática.

- **Perfil de influencer**  
  Mistura de crescimento, colaborações, campanhas, polêmicas e mini-cancelamentos. O usuário quer um filme coerente: como essa pessoa chegou até aqui e qual é o estado atual da reputação.

- **Carreira de atleta**  
  Clubes, títulos, lesões, quedas de performance, polêmicas e aposentadoria. A linha do tempo é longa e emocionalmente carregada. O usuário quer um arco claro: ascensão, auge, declínio, rupturas.

Em todos os casos, falta ao Inspectah atuar como **narrador confiável**. Os dados estão lá, mas não organizados em uma história que responda rapidamente às perguntas básicas.

---

## 3) Visão da Sprint 13

### 3.1 O que a S13 quer que o Explorer v1 seja

Ao final da Sprint 13, o Explorer v1 deve se comportar como uma **superfície de produto mínima viável**, capaz de:

- Explicar rapidamente **que caso é**, **por que importa** e **em que estado está**.
- Contar uma **timeline em linguagem humana**, não em jargão técnico.
- Mostrar o Debunker como **voz explicativa**, não só como rótulo.
- Exibir um **estado consolidado do caso** visível e coerente com a história.
- Permitir **feedback rápido e rastreável**, tanto para o usuário quanto para o operador interno.

Tudo isso com o backbone de S12 por baixo, sem reescrever o mundo.

### 3.2 Domínios piloto e arquétipos de caso

A S13 trabalha com seis arquétipos de caso, que representam bem tipos diferentes de narrativa:

1. **Obra pública municipal**  
   Uma reforma de escola municipal com: ato em Diário Oficial, registros em portal de transparência e cobertura mínima na imprensa local.  
   Foco: valores, contratos, aditivos, denúncias, paralisações.

2. **Evento climático severo**  
   Um episódio de chuva forte/alagamento com: alertas de órgão meteorológico, comunicados de defesa civil e notícias sobre danos.  
   Foco: linha do tempo de alertas → evento → impacto.

3. **Projeto de lei**  
   Um PL de impacto médio/alto cujo ciclo completo seja observável (apresentação, comissões, emendas, votações, aprovação ou arquivamento).  
   Foco: status atual, histórico de avanços/travas, episódios-chave.

4. **Carreira política**  
   Trajetória de um político com múltiplos mandatos/cargos e pelo menos uma controvérsia relevante.  
   Foco: cargos, promessas, escândalos, investigações, desfechos.

5. **Perfil de influencer**  
   Influencer digital com história de crescimento, colaborações, campanhas, polêmicas e um ou mais "mini-cancelamentos".  
   Foco: ascensão, picos, quedas, impacto de controvérsias na reputação.

6. **Carreira de atleta**  
   Atleta de destaque com passagens por diferentes clubes/seleções, títulos, lesões marcantes e possíveis polêmicas.  
   Foco: fases da carreira (ascensão, auge, declínio) e eventos críticos.

Esses seis casos servem como "laboratório" para o Explorer v1. Se ele conseguir contar bem essas histórias, estará no caminho certo para generalizar.

---

## 4) Escopo da Sprint 13 (IN / OUT)

### 4.1 Escopo IN — o que a S13 vai fazer

A S13 atua em camadas claras, reaproveitando o que a S12 já construiu.

**1. Cabeçalho enriquecido da CasePage (por domínio)**

Cada caso passa a ter um cabeçalho que responda "o que é isso" sem esforço:

- Obra pública: nome da obra + contrato + valor + município/UF.
- Evento climático: tipo de evento + local + período + severidade básica.
- Projeto de lei: identificador + tema + casa legislativa + situação atual (aprovado/em tramitação/arquivado).
- Carreira política: nome + principais cargos + período de atuação.
- Influencer: nome/nick + plataforma principal + ordem de grandeza de seguidores.
- Atleta: nome + esporte + clube/seleção mais associada + período.

**2. Resumo executivo curto no topo**

Para cada caso, a CasePage passa a exibir 2–3 frases de resumo em linguagem humana, cobrindo:

- o que é o caso;
- o que aconteceu até aqui;
- qual é a situação atual e o ponto de atenção principal (se houver).

Esse resumo deve ser lido em segundos e servir como “mini relatório executivo”.

**3. Timeline em linguagem humana e estruturada**

A timeline passa a ser tratada como narrativa, não como dump de eventos:

- textos de eventos reescritos para português claro, usando campos técnicos apenas como insumo;
- organização visual ou por labels que destaque:
  - eventos técnicos (atos oficiais, decisões formais, alertas, registros de contrato);
  - eventos de impacto (denúncias, polêmicas, resultados esportivos, danos, repercussão pública).

**4. Debunker v0,5 na UI (explicação, não só status)**

O Debunker continua tomando decisões com o mesmo motor da S12, porém a superfície muda:

- para eventos críticos, a UI mostra:
  - status (aceito/suspeito/incerto/crítico);
  - justificativa curta em linguagem natural.

Exemplos:

- "Aceito porque Diário Oficial, portal de transparência e notícia local convergem nos mesmos valores e datas."  
- "Suspeito porque há divergência entre fontes oficiais e padrão de valor foge do esperado."  
- "Incerto porque ainda faltam evidências suficientes de fontes independentes."

**5. Estado consolidado do caso**

Cada caso passa a ter um **estado consolidado visível** (OK/suspeito/crítico/conflituoso), calculado com regras simples por domínio, usando como insumos:

- decisões do Debunker em eventos relevantes;
- presença e gravidade de eventos de impacto na timeline.

A regra detalhada por domínio será formalizada no Capítulo 2 (gates), mas a visão de produto é: um indicador simples, compreensível e explicável, sempre coerente com a história mostrada.

**6. Feedback v1 (CasePage + painel interno)**

O fluxo de feedback deixa de ser "botão tímido" e passa a ser parte explícita do produto:

- botão chamativo na CasePage (ex.: "Reportar problema neste caso");
- formulário simples com categorias pré-definidas:
  - informação errada/desatualizada;
  - fonte quebrada;
  - evento importante faltando;
  - dúvida sobre a decisão do Debunker;
  - outro (campo livre);
- painel interno ajustado para:
  - listar feedbacks por caso e por estado;
  - permitir atualização de status de forma simples;
  - manter rastreabilidade mínima (quem reportou, quando, sobre qual evento/campo).

**7. Backlog de produto para S14+**

A S13 termina com um backlog explícito de melhorias futuras, separado em:

- evolução de UX/Explorer/Timeline/Feedback;
- necessidades estruturais que pertencem claramente ao **Sistema de Blocos / Fase 2** (ex.: versionamento formal, disputa de fatos, reputação).

### 4.2 Escopo OUT — o que a S13 não vai fazer

Para proteger a sanidade e respeitar a Nota de Escopo Temporário, a S13 **não** fará:

- Implementação do **Sistema de Blocos completo** (blocos, sub-blocos, disputas formais, estados on-chain etc.).
- Reputação avançada (pontos, rankings, pesos por reputação de usuário/agente).
- Integrações reais de blockchain ou âncoras automáticas on-chain.
- Ingestão 24/7 completa para todos os domínios novos (PL, carreira política, influencer, atleta):
  - nesta sprint, esses domínios podem operar com fixtures e pipelines simplificados; o foco é a narrativa e o Explorer v1, não o backbone de ingestão.
- Novas camadas complexas de backend que não tenham impacto direto em Explorer/Timeline/Debunker/Feedback nesta sprint.

---

## 5) Objetivos de produto e critérios de sucesso

### 5.1 Objetivo macro

Transformar Explorer v1 + CasePage + Timeline + Debunker + Feedback em uma superfície de produto capaz de:

- contar a história de pelo menos um caso representativo em cada um dos seis domínios;
- comunicar claramente, em cada caso:
  - o que é;
  - o que aconteceu;
  - qual a situação atual;
  - quais são os pontos de atenção;
- gerar um backlog coerente e priorizado para S14+.

### 5.2 Critérios de sucesso (nível conceitual)

Para considerar a S13 bem-sucedida, queremos ser capazes de fazer uma **demo de 10–15 minutos** que:

- use apenas Explorer v1 + CasePage + Timeline + Debunker + Feedback (sem abrir código, scorecards ou logs);
- percorra, com segurança, pelo menos um caso de cada domínio piloto;
- permita que um observador inteligente, mas não técnico, responda para cada caso:
  - que caso é esse?;
  - por que ele importa?;
  - o que aconteceu ao longo do tempo?;
  - qual é o estado atual (OK/suspeito/crítico/conflituoso)?;
  - por que o sistema chegou a esse estado?;
- deixe claro, ao final, quais são os próximos passos lógicos (S14+) para refinar o produto e, depois, ligar essa camada de narrativa ao Sistema de Blocos / Fase 2.

---

## 6) Riscos, decisões e não-negociáveis

- **Risco: escopo excessivo em domínios novos.**  
  Decisão: PL, carreira política, influencer e atleta operam, nesta sprint, com ingestão controlada (fixtures/pipelines simplificados). O foco é comprovar o modelo de narrativa e Explorer v1.

- **Risco: drift para Sistema de Blocos / Fase 2.**  
  Decisão: qualquer necessidade relacionada a blocos form

