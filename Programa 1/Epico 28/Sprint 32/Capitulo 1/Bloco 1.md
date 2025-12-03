# Inspectah — Sprint 32
## Capítulo 1 — Bloco 1
### Contexto macro da Sprint 32 dentro do Épico E28 e dos Programas 1–4

#### 1.1 Posição da S32 no Épico E28 (S29–S35)

O **Épico E28** (S29–S35) é o arco em que o Inspectah deixa de ser “um conjunto de pipelines e ideias fortes” e passa a operar como uma **plataforma 24/7 de casos, verdade e contestação**, com começo, meio e fim rastreáveis. Dentro desse arco:

- **S29** alinhou visão, recortes de escopo e a função do Épico E28 como guarda‑chuva da operação 24/7.
- **S30** consolidou o modelo de operação contínua (ingestão + manutenção + operação) e o encaixe com os Programas 1–4.
- **S31** reforçou o lado de ingestão, administração e operação do console, garantindo que a casa está em ordem para suportar fluxos mais sensíveis.

A **Sprint 32** entra como o momento em que o foco migra de “só” ingestão/operacional para o **coração epistemológico do Inspectah**:

> fazer o **Truth‑DB + Sistema de Blocos** saírem do papel e operarem, de forma enxuta, porém real, em modo 24/7.

Em termos práticos, a S32 precisa entregar:

1. Um **fluxo executável e testável** de claim → blocos → estado de verdade, ainda que focado em um tipo de claim prioritário.
2. Uma **v1 funcional de contestação**, em que seja possível contestar um estado de verdade, disparar uma reavaliação mínima e registrar o resultado em novos blocos, sem apagar histórico.
3. Um Truth‑DB com **invariantes explicitadas em código** (testes/contratos) e integrado à observabilidade 24/7, com métricas mínimas de promoção, contestação, erros e latência.

A S32 é, portanto, a sprint que transforma o núcleo “verdade & contestação” de:

- **Blueprint bonito + modelos parciais**  
  em
- **Sistema vivo, auditável e minimamente operacional**.

Esse “esqueleto vivo” é propositalmente enxuto: ele não tenta resolver todo o mundo, mas precisa ser sólido o bastante para aguentar expansão nas S33–S35 sem refazer conceitos básicos.

#### 1.2 Relação da S32 com os Programas 1–4

A S32 está no cruzamento entre **Programa 2 (claims)**, **Programa 3 (Truth‑DB & Blocos)** e **Programa 1 (operação/observabilidade)**, preparando o terreno para **Programa 4 (produtos & exposição)**.

- **Programa 1 — Data Hub & Operação 24/7**  
  - Já estabeleceu ingestão contínua, console de fontes e stack de observabilidade.  
  - Na S32, seu papel é garantir que os novos fluxos de Truth‑DB e contestação possam rodar de forma contínua, com **jobs, serviços e métricas encaixados** no ecossistema 24/7.

- **Programa 2 — Interpretação, Claims & Entidades**  
  - Produz claims estruturadas, entidades, sinais e logs mínimos que descrevem “o que foi entendido” de cada item ingerido.  
  - Na S32, fornece **um tipo de claim prioritário**, com schema acordado e estável, que será o insumo oficial para promoção a bloco/estado de verdade.

- **Programa 3 — Truth‑DB, Sistema de Blocos & Contestação**  
  - É o protagonista da S32.  
  - Pega as claims do Programa 2 e as transforma em **FactBlocks, EvidenceBlocks, DecisionBlocks e estados de verdade**, além de orquestrar contestações e reavaliações.  
  - Implementa invariantes, serviços e scripts de gates que permitem testar e auditar esse comportamento.

- **Programa 4 — Exposição, Produtos & Uso Responsável**  
  - Ainda não recebe grandes entregas de UI/feature na S32.  
  - O papel da sprint aqui é **preparar o motor de verdade** que o Programa 4 vai consumir no futuro: estados de verdade confiáveis, trilhas de contestação e APIs/consultas mínimas.

Resumindo o encaixe:

- Programa 2 entrega **“o que foi dito e como foi entendido”**.
- Programa 3, na S32, passa a entregar **“o que o Inspectah considera verdadeiro/agendado para contestação, com trilha de blocos”**.
- Programa 1 garante que isso tudo roda **sem cair**, com logs e métricas.
- Programa 4, depois, transforma isso em **produtos, painéis e superfícies de uso responsável**.

O Capítulo 1 — Bloco 1 fixa esse contexto como base: a partir daqui, todo o restante da especificação (estados‑alvo, gates, arquitetura, execução, ORR e tasks) deve ser coerente com essa posição da S32 dentro do Épico E28 e dos Programas 1–4.