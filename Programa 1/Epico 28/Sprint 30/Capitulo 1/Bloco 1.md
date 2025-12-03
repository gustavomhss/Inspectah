# Inspectah — Sprint 30 — Capítulo 1 — Bloco 1
## Identidade, Contexto Estratégico e Problema Central da Sprint

### 1. Identidade da Sprint

**Código**: S30  
**Programa**: Programa 1 — Data Hub & Consoles 24/7  
**Épico dominante**: E28 — Fluxo de Agentes Configurável v1  
**Posição no épico**: 2ª de 7 sprints (E28 ocupa S29–S35)  
**Squad responsável**: Squad Fluxos & Orquestração  

**Frase‑guia da S30**:  
> “Levar o fluxo de notícias do estado ‘console que mostra coisas’ para ‘fluxo realmente operável, controlado pelo console, com estados que mandam de verdade no sistema’.”

Esta sprint não é sobre “incrementar UI” nem “polir modelos”; é sobre cravar, de forma irreversível, que **fluxos de agentes são uma entidade operacional de primeira classe** no Inspectah, começando pelo caso mais óbvio e crítico: **notícias**.

---

### 2. Contexto Estratégico: Onde S30 se Encaixa

O Programa 1 tem como missão tirar o Inspectah do protótipo e colocá‑lo na rota de **operação 24/7 com consoles fortes**: fontes, ingestão, evidências, casos e fluxos precisam ser coisas que um operador consegue ver, entender e controlar em tempo quase real.

Dentro desse programa, o **Épico E28** é a espinha dorsal da orquestração: define como eventos brutos (ex.: notícias) atravessam uma **cadeia configurável de agentes** — intérprete, classificador, analistas, debunkers, decision maker — até virar algo estruturado, auditável e utilizável por outros módulos (Truth‑DB, Debunker, UI de casos, etc.).

A Sprint 29 já executou o primeiro corte desse épico:

- materializou o **modelo de Fluxo de Agentes v1** (entidades Fluxo, Etapa, Nó/Agente, Execução de Fluxo, Execução de Etapa);  
- entregou um **Console de Fluxos v1**, capaz de listar fluxos, mostrar sua estrutura básica e exibir um recorte de execuções;  
- conectou ingestão e fluxos de forma mínima, permitindo que ao menos um tipo de evento (notícia) seja roteado para um fluxo configurável.

Resultado: fluxos deixaram de ser só uma ideia bonita em documento e passaram a existir no código, com uma face administrativa mínima.

A Sprint 30 assume este estado como pré‑requisito e sobe a barra:

- não basta **ver** fluxos; o operador precisa **mandar** neles;  
- não basta ter estados (`draft`, `em_teste`, `ativo`, `pausado`); esses estados têm que **mandar no tráfego**;  
- não basta ter “um fluxo de notícias que funciona”; é necessário um **fluxo de notícias‑pivô**, nascido de **template oficial**, rastreável de ponta a ponta e com observabilidade mínima de gente grande.

S30 é, portanto, a sprint em que o E28 ganha seu primeiro **caso de prova operacional**.

---

### 3. Problema Central da Sprint (Formulado Cirurgicamente)

Hoje, mesmo após S29, a realidade operacional ainda é incômoda:

- o Console de Fluxos é mais um **visor de RX** do que uma **sala de controle**;  
- estados de fluxo existem como rótulos, mas **não há contrato rígido** ligando esses estados ao roteamento real de eventos;  
- o fluxo de notícias é configurável, mas **não é fácil provar**, na prática, que o operador consegue:  
  - criar um novo fluxo a partir de um template;  
  - colocá‑lo em teste, com tráfego real controlado;  
  - promovê‑lo a ativo de forma segura;  
  - pausar e retomar quando algo dá errado;  
  - trocar agentes problemáticos sem mexer em código;  
  - reprocessar itens críticos sem causar tempestade de duplicidade ou loops.

O **problema central** que S30 precisa matar é:

> “Para o caso de notícias, o Console de Fluxos ainda não é o cockpit operacional definitivo: o comportamento real do sistema não está rigidamente subordinado ao que o console e o modelo de fluxos dizem.”

Enquanto isso for verdade, o E28 existe “um nível abaixo do necessário”: o modelo é elegante, o console é útil para inspeção, mas a **autoridade real** continua no código, nos scripts e na cabeça de quem implementou. Isso é incompatível com a visão de um Inspectah **operável por squads diferentes**, com separação clara entre quem desenha fluxos, quem opera e quem mexe na infraestrutura.

S30, então, tem um mandato muito específico:

- **elevar o fluxo de notícias a primeiro cidadão plenamente operável via Console**;  
- fazer com que **estados de fluxo virem lei**, e não sugestão;  
- provar que um operador treinado consegue controlar esse fluxo — criar, testar, ativar, pausar, trocar agente, reprocessar — **sem pedir socorro para um desenvolvedor**.

Se, no fim da sprint, ainda for possível argumentar que “na prática é melhor mexer direto no código para resolver rápido”, a S30 falhou, independentemente da quantidade de código escrita ou telas polidas.

Este Bloco 1 fixa, portanto, o **eixo conceitual** da sprint: tudo o que vier nos blocos seguintes (objetivos específicos, métricas, filemap, tasks) existe para transformar esse problema central em algo do passado.

