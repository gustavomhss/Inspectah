# Inspectah — Sprint 27 (S27)
## Capítulo 6 — Bloco 3
### Dívidas da S27 (Técnicas, Produto/UX, Operação & Processo)

> Arquivo-alvo sugerido no repo: `docs/s27_cap_6_3_dividas_da_s27.md`
>
> Função: registrar de forma estruturada **as dívidas que a S27 deixa para frente** — o que ficou abaixo do ideal, mas foi conscientemente aceito para permitir a entrega do Épico E26. Serve como ponte entre o veredito do ORR (G6), o backlog futuro e os próximos épicos.

---

## 1. Modelo de registro de dívidas

Cada dívida deve ser registrada num formato mínimo como:

- **ID**: `DEBT-XXX`  
- **Tipo**: `tecnica` | `produto` | `ux` | `operacao` | `processo`  
- **Título**: frase curta e específica.  
- **Descrição**: 2–5 linhas, explicando o problema.  
- **Impacto**: `baixo` | `medio` | `alto` (para Programa 1 e/ou para o roadmap).  
- **Urgência**: `baixa` | `media` | `alta`.  
- **Estado desejado**: como deveria ser quando a dívida for quitada.  
- **Sugestão de encaminhamento**: próximos passos razoáveis para tratá-la.  
- **Relacionamentos**: `RISK-XXX`, `ACT-XXX`, tasks `S27-T-XXX` e/ou épicos futuros.

O objetivo não é criar uma enciclopédia infinita, mas uma lista **curta e relevante** das dívidas que realmente importam.

---

## 2. Dívidas técnicas

> Aqui entram problemas de código, arquitetura, testes, automação e infraestrutura diretamente relacionados à S27.

### 2.1 Exemplos de categorias de dívida técnica

- **Cobertura de testes insuficiente em áreas críticas**  
  - E2E cobrindo apenas cenários "happy path".  
  - Poucos testes para fluxos avançados de Debunker ou combinações Fontes → Ingestão → Debunker.

- **Acoplamento forte entre UI admin e APIs**  
  - Telas que dependem demais de detalhes de implementação do backend, tornando difícil evoluir contratos de API.

- **Scripts de gates frágeis ou prolixos**  
  - Gates que rodam com flakiness (intermitência) ou que exigem setups manuais frequentes.  
  - Scripts que se tornaram difíceis de manter pela falta de modularização.

- **Componentes Admin v1 com pontos de melhoria interna**  
  - Componentes que estão funcionando, mas têm duplicação de lógica, propriedades pouco claras, ou pouca separação entre layout e dados.

### 2.2 Como priorizar dívidas técnicas

Critérios práticos para priorização:

1. **Risco de regressão**: se uma área é crítica e mal testada, tende a quebrar em silêncio.  
2. **Custo de mudança futuro**: quanto mais tarde o refactor, maior o impacto.  
3. **Efeito cascata**: dívidas que complicam múltiplos consoles e módulos merecem prioridade maior.

Sugestão: vincular cada dívida técnica importante a pelo menos um `RISK-XXX` em `S27_G6_orr_summary.json`.

---

## 3. Dívidas de produto & UX

> Foco aqui é a experiência de uso dos consoles admin de Programa 1 sob Admin v1: clareza, fluxo, descoberta, ergonomia.

### 3.1 Principais tipos de dívida de produto/UX

- **Fluxos pouco naturais ou com etapas redundantes**  
  - Sequências de passos que poderiam ser simplificadas (por exemplo, número excessivo de cliques para chegar de uma fonte com problema até o caso correspondente em Debunker).

- **Telas com sobrecarga de informação ou sem hierarquia clara**  
  - Overviews que tentam mostrar tudo ao mesmo tempo e acabam dificultando a priorização.  
  - Falta de divisão entre "estado global" e "detalhe da entidade".

- **Ausência de visões de síntese importantes**  
  - Falta de métricas/resumos na UI (ex.: nº de fontes críticas, ingestões em erro, casos de Debunker abertos) que permitiria decisões mais rápidas.

- **Estados avançados de Debunker pouco compreensíveis**  
  - Casos com múltiplas revisões e evidências que, visualmente, não diferem muito de casos simples.  
  - Ausência de uma linha do tempo clara da vida de um caso.

### 3.2 Como essas dívidas impactam Programa 1

- A curto prazo, operadores conseguem trabalhar, mas com **custo cognitivo maior** do que o ideal.  
- A médio prazo, essas dívidas podem:  
  - reduzir a confiança no sistema (quando o usuário não entende se algo está "certo" ou "errado");  
  - tornar mais difícil escalar o número de pessoas operando Programa 1 sem treinamento intenso.

Por isso, dívidas de UX não são cosméticas: são parte da saúde operacional do sistema.

---

## 4. Dívidas de operação

> São lacunas em runbooks, playbooks, monitoramento e práticas operacionais que ficaram evidentes na S27.

### 4.1 Tipos comuns de dívida de operação

- **Runbooks incompletos ou genéricos demais**  
  - Procedimentos que cobrem apenas o "happy path" ou incidentes extremos, sem tratar situações intermediárias.

- **Ausência de playbooks para classes específicas de incidentes**  
  - Ex.: como agir quando apenas uma subset de fontes apresenta falha de ingestão.  
  - Ex.: como lidar com backlog crescente de casos no Debunker.

- **Dependência de conhecimento tácito**  
  - Passos operacionais que só são conhecidos por quem desenvolveu a feature, e não estão escritos em lugar nenhum.

- **Falta de métricas e observabilidade na camada admin**  
  - Consoles que exigem "caçar" evidências em múltiplas telas ao invés de oferecer KPIs claros.

### 4.2 Riscos associados às dívidas de operação

- Maior probabilidade de erros humanos em incidentes reais.  
- Maior tempo de resposta em situações de crise.  
- Maior dificuldade de onbordar novos operadores para Programa 1.

Estas dívidas devem ser cruzadas com os learnings de Cap.6 Bloco 2 e com riscos operacionais em G6.

---

## 5. Dívidas de processo

> São aprendizados sobre como a equipe trabalhou na S27 — pontos onde o próprio modelo de trabalho pode ser refinado.

### 5.1 Exemplos típicos de dívidas de processo

- **Atualização tardia dos capítulos**  
  - Em alguns momentos, Cap.2–Cap.4 ficaram defasados em relação ao código/evidências, gerando desalinhamento na reta final.

- **Rodadas de gates concentradas demais no fim**  
  - Rodar G1–G4 apenas no final da sprint aumenta o risco de descobrir problemas grandes tarde demais.

- **Pouco uso incremental de G6 ao longo da sprint**  
  - Tratar G6 só como artefato do fim tira a chance de ir anotando riscos e ações conforme eles aparecem.

- **Falta de cadência explícita para revisitar learnings**  
  - Learnings surgem no dia a dia, mas nem sempre viram itens estruturados de Cap.6.

### 5.2 Possíveis encaminhamentos

- Definir rituais explícitos (por exemplo, checkpoints semanais) para atualizar capítulos e rodar subsets de gates.  
- Tratar G6 como documento vivo desde o meio da sprint (já registrar riscos provisórios, por exemplo).  
- Incluir a revisão de Cap.6 como parte fixa do encerramento, não como tarefa opcional.

---

## 6. Consolidando as principais dívidas em uma lista curta

> Este bloco não deve virar um dump infinito: o valor está em **destilar** as 5–15 dívidas que realmente movem o ponteiro.

Sugestão de estrutura final (a ser preenchida com conteúdo real após o ORR):

- `DEBT-001` — Tipo: `tecnica`  
  **Título**: Cobertura E2E insuficiente em cenários avançados de Debunker.  
  **Descrição**: Cenários complexos de contestação (várias revisões, múltiplas evidências, relações com múltiplas fontes) não estão cobertos pelos testes atuais, deixando riscos de regressão silenciosa.  
  **Impacto**: `alto` — Debunker é peça central de credibilidade do Inspectah.  
  **Urgência**: `alta`.  
  **Estado desejado**: Conjunto mínimo de cenários E2E cobrindo linhas de tempo complexas de casos, rodando em G2/G4.  
  **Sugestão de encaminhamento**: épico ou sprint focada em "Debunker E2E + observabilidade".  
  **Relacionamentos**: `RISK-001`, `ACT-001`.

- `DEBT-002` — Tipo: `ux`  
  **Título**: Falta de visão consolidada de saúde de Programa 1 na UI admin.  
  **Descrição**: Operadores precisam caçar informações em várias telas para entender o estado geral de Fontes, Ingestão e Debunker, o que aumenta o tempo de resposta.  
  **Impacto**: `medio`.  
  **Urgência**: `media`.  
  **Estado desejado**: dashboards síntese por console, com KPIs críticos e links de drill-down.  
  **Sugestão de encaminhamento**: sprint futura de "Admin v1.2 — painéis de saúde".  
  **Relacionamentos**: riscos operacionais em G6.

- `DEBT-003` — Tipo: `operacao`  
  **Título**: Runbooks de incidentes parciais em ingestão incompletos.  
  **Descrição**: Não há documentação clara para casos em que apenas subset de fontes está em falha, o que atrasa diagnóstico e correção.  
  **Impacto**: `medio`.  
  **Urgência**: `media`.  
  **Estado desejado**: seções específicas de runbook com fluxos de "falha parcial".  
  **Sugestão de encaminhamento**: complementar runbooks existentes com base em simulações.  
  **Relacionamentos**: riscos operacionais e learnings de Cap.6 Bloco 2.

(...)  

A lista final deve ser construída junto com o preenchimento de G6 e dos demais blocos de Cap.6, garantindo coerência entre riscos, ações e dívidas.

---

## 7. Como esta lista de dívidas deve ser usada

- **Planejamento de próximas sprints**: usar esta lista como insumo direto, não como curiosidade.  
- **Definição de novos épicos**: se uma dívida é grande demais para caber em uma sprint, ela pode ser a semente de um novo épico.  
- **Revisões futuras**: em próximos ORRs, voltar a este Bloco 3 para verificar quais dívidas foram reduzidas, quais cresceram e quais surgiram novas.

Assim, Cap.6 Bloco 3 garante que a S27 não deixe apenas "resquícios" informais, mas um inventário claro e acionável do que ainda precisa ser resolvido para que Admin v1 e Programa 1 atinjam maturidade plena.