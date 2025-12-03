# Sprint 29 — Capítulo 6
## Bloco 4 — Plano de mitigação e follow-up (curto e médio prazo)

Este Bloco 4 transforma o que foi levantado nos Blocos 2 e 3 (riscos e débitos técnicos) em um **plano de mitigação e follow-up** concreto. A pergunta aqui é prática:

> "Dado tudo o que sabemos que pode dar errado e tudo o que conscientemente deixamos de fora, o que vamos fazer a respeito, quando e sob responsabilidade de quem?"

O plano é dividido em dois horizontes principais:

- **Curto prazo (pós-S29 imediato)** — ações que devem acontecer logo após o merge da sprint e durante o piloto de fluxos configuráveis.
- **Médio prazo (E28.2, E28.3, E28.4 e correlatas)** — ações que precisam entrar como candidatos explícitos de escopo de próximas sprints.

---

### 4.1. Mitigações de curto prazo (pós-S29 imediato)

Estas ações têm como objetivo impedir que a v1 de fluxos configuráveis crie riscos desnecessários enquanto ainda está fresca.

#### Ação C1 — Definir governança mínima de quem pode editar fluxos

- Objetivo:  
  - reduzir o risco de alterações imprudentes de fluxo em domínios piloto;
  - garantir que apenas pessoas com contexto adequado possam alterar configurações sensíveis.
- Conteúdo mínimo:  
  - listar quais perfis/roles de usuário podem editar fluxos em geral;  
  - mapear, para cada domínio piloto, quem é responsável pelas alterações de fluxo;  
  - definir se alguma alteração exige dupla checagem informal (por exemplo, sempre discutir em canal interno antes de salvar mudanças relevantes).
- Donos sugeridos:  
  - Produto do Programa 1 (definição de política);  
  - Squad de Operações/Plataforma (aplicação em permissões/roles).
- Prazo ideal:  
  - até o final da janela de encerramento da S29, antes do início de uso ativo pelos pilotos.

#### Ação C2 — Ativar monitoramento básico de fallback de fluxo

- Objetivo:  
  - evitar que o sistema caia em fallback sem que ninguém perceba;  
  - criar um termômetro mínimo de saúde da feature.
- Passos mínimos:  
  - garantir que logs de runtime incluam um campo explícito indicando quando o fallback foi usado, com motivo;  
  - criar, mesmo que via script simples, uma agregação periódica "% de itens com fallback" por domínio;  
  - se possível, expor essa métrica em um painel interno simples.
- Donos sugeridos:  
  - Squad de Observabilidade/Plataforma;  
  - apoio do squad de Backend para ajustes em logs.
- Prazo ideal:  
  - durante o primeiro ciclo de piloto, não mais que algumas iterações após S29.

#### Ação C3 — Comunicar limitações da v1 de fluxo para stakeholders

- Objetivo:  
  - alinhar expectativas internas;  
  - reduzir o risco de alguém planejar em cima de capabilities que ainda não existem (versionamento, approvals, branching completo).
- Formato sugerido:  
  - apresentação curta do ORR da S29, destacando:  
    - o que a feature faz;  
    - o que ainda não faz;  
    - quais trilhas de E28.x estão planejadas;  
  - envio de resumo (linkando Capítulos 5 e 6) para times impactados.
- Donos sugeridos:  
  - PO/PM do Programa 1;  
  - apoio do squad de Engenharia para detalhes técnicos.
- Prazo ideal:  
  - imediatamente após o ORR formal de S29.

#### Ação C4 — Criar uma nota operacional rápida para operadores admin

- Objetivo:  
  - reduzir sobrecarga cognitiva e evitar erros básicos na edição de fluxos.
- Conteúdo mínimo:  
  - explicação em uma página:  
    - o que é um fluxo;  
    - o que cada papel principal faz;  
    - recomendações de boas práticas em v1 (por exemplo, não remover DEBUNKER de domínios sensíveis);  
    - quando acionar o time de engenharia.
- Donos sugeridos:  
  - Produto + alguém do squad Verdade & Interpretação;  
  - revisão breve pelo squad técnico de E28.
- Prazo ideal:  
  - logo no início da fase piloto, enquanto a superfície de operadores ainda é pequena.

---

### 4.2. Mitigações de médio prazo — trilhas de E28.x

Aqui entram ações que não fazem sentido como hotfixes, mas sim como escopo de novas sprints. Elas se conectam diretamente às trilhas desenhadas no Capítulo 5.

#### Ação M1 — Versionamento e approvals de fluxo (candidato forte a E28.2)

- Objetivo:  
  - transformar fluxos em entidades versionadas com ciclo de vida (draft/active/deprecated) e workflow de aprovação para domínios sensíveis.
- Relação com riscos e débitos:  
  - mitiga P1/P2 (governança fraca de alterações), P4 (expectativas irreais sobre v1);  
  - endereça débitos D1/D2 parcialmente, ao forçar uma reflexão mais estruturada sobre o modelo de fluxo e catálogo de papéis.
- Elementos mínimos de escopo:  
  - modelo de dados para versões de fluxo;  
  - API e UI para criar versões em draft e promovê-las a active;  
  - mecanismo de rollback simples entre versões;  
  - workflow de approvals (no mínimo, registro de "quem aprovou o quê" e, idealmente, dois pares de olhos em domínios críticos).

#### Ação M2 — Branching e fluxos condicionais (candidato a E28.3)

- Objetivo:  
  - permitir fluxos que respondem a condições de contexto (tipo de item, tema, criticidade), sem degenerar em caos.
- Relação com riscos e débitos:  
  - toca diretamente T1 (complexidade do modelo de fluxo), T3 (performance), D5 (UX baseada em lista linear);  
  - precisa ser alinhado com S23–S25 para não colidir com políticas de verdade/debunking.
- Elementos mínimos de escopo:  
  - design de modelo para representar condições no fluxo (antes de código);  
  - atualização do runtime para avaliar condições de forma eficiente;  
  - evolução da UI para expressar pelo menos cenários de branching mais comuns.

#### Ação M3 — Métricas, tuning e painel de fluxos (candidato a E28.4)

- Objetivo:  
  - transformar logs de execução de fluxo em métricas acionáveis e visualizações úteis.
- Relação com riscos e débitos:  
  - mitiga T3/T5 (performance e instrumentação mínima);  
  - ajuda a controlar R3 (proliferação de fluxos exóticos) com dados;  
  - reduz incerteza sobre o real impacto de mudanças de fluxo.
- Elementos mínimos de escopo:  
  - definição de métricas essenciais (tempo médio por agente, taxa de erro por fluxo, uso de fallback, etc.);  
  - agregações e armazenamento dessas métricas;  
  - painel básico para operadores e produto acompanharem fluxos e health.

#### Ação M4 — Catálogo de fluxos canônicos por domínio

- Objetivo:  
  - criar um conjunto de fluxos "de referência" para principais tipos de domínio (política, economia, saúde, dados estatísticos, etc.), com justificativas.
- Relação com riscos e débitos:  
  - mitiga P3 (sobrecarga cognitiva) e D9 (falta de exemplos públicos);  
  - conecta decisões de fluxo com políticas de verdade, contestação e comitês.
- Elementos mínimos de escopo:  
  - trabalho conjunto entre squad Verdade & Interpretação e squad técnico de E28;  
  - documentação dos fluxos recomendados e sua motivação;  
  - opcional: provisionar esses fluxos como presets na UI.

---

### 4.3. Tabela-resumo de ações, donos e horizonte

Para facilitar planejamento e acompanhamento, o plano de mitigação pode ser resumido em uma tabela (no próprio Capítulo 6 ou em doc auxiliar), com colunas:

- `Código da ação` — C1, C2, M1, etc.;  
- `Descrição curta`;  
- `Horizonte` — curto/médio;  
- `Squad(s) responsável(is)`;  
- `Estado` — PLANEJADA, EM ANDAMENTO, CONCLUÍDA.

Isso permite que, a cada ciclo de planejamento, o time revise o quadro e atualize o status das mitigações, sem que o Capítulo 6 vire um texto morto.

---

### 4.4. Amarração do Bloco 4

Com este Bloco 4, o Capítulo 6 sai do diagnóstico e entra na **ação estruturada**:

- riscos críticos e débitos relevantes da S29 deixam de ser apenas uma lista e ganham um plano de resposta;  
- ações de curto prazo protegem o piloto de fluxos configuráveis contra erros básicos de governança e observabilidade;  
- ações de médio prazo entram como trilhas claras dentro de E28.x (versionamento/approvals, branching, métricas, catálogo canônico).

Os blocos seguintes do Capítulo 6 fecham o arco definindo:

- como monitorar o comportamento do sistema pós-S29 (indicadores, critérios de rollback e expansão);  
- e qual é o "long tail" da S29 — isto é, quais artefatos e decisões desta sprint precisam ser obrigatoriamente carregados para o futuro do Programa 1.

