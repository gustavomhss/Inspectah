# Inspectah — Sprint 27 (S27)
## Capítulo 4 — Execução, Evidências & Tasks

> Arquivo-alvo no repo: `docs/s27_cap_4_execucao_e_evidencias.md`
>
> Função: transformar o contexto (Cap.1), os gates (Cap.2) e a arquitetura/filemap (Cap.3) em um **plano de ataque executável**: waves, tasks, evidências e ritmo de gates. Aqui vive o contrato de execução da S27. As tasks detalhadas moram no Bloco 4.4.

---

## 1. Papel do Capítulo 4 na S27

Este capítulo responde, de forma prática:

- **Como** a S27 será executada (ordem de waves, foco de cada uma, cadência).  
- **Quem bate o quê** em cada momento (quais gates são alvo em cada wave).  
- **Que evidências** precisam existir ao final de cada etapa.  
- **Como as tasks S27-T-XXX** se organizam e se conectam a Cap.1–3.

Se Cap.1 é o "porquê", Cap.2 é o "como vamos verificar" e Cap.3 é o "onde vive o quê", Cap.4 é o **"o que fazemos amanhã de manhã"**.

---

## 2. Estrutura do Capítulo 4

O Capítulo 4 da S27 segue o Sprint Playbook v3 e é dividido em quatro blocos:

- **Bloco 4.1 — Plano de Waves**  
  - Define W0, W1, W2, W3 (quando aplicável), com objetivos, critérios de saída e gates associados a cada wave.

- **Bloco 4.2 — Plano de Evidências & Logs**  
  - Define que tipos de evidência cada wave deve produzir (scorecards, logs, capturas, docs atualizados) e em quais paths.

- **Bloco 4.3 — Estratégia de Gates & Execução Local/CI**  
  - Define como e quando rodar G0–G6 ao longo da sprint (loops locais, checkpoints de wave, rodadas completas, ORR).

- **Bloco 4.4 — Tasks S27-T-XXX (Tabela Oficial)**  
  - Tabela detalhada de tasks, com ID, wave, categoria, descrição, artefatos, gates, estados-alvo, critérios de DONE e evidências.

Este documento macro (Cap.4) descreve a filosofia e o formato. Cada bloco terá seu próprio arquivo detalhado.

---

## 3. Plano macro de waves da S27 (visão geral)

A S27 é a segunda sprint do Épico E26 (Admin v1 para Fontes/Ingestão/Debunker). Em termos de execução, ela é organizada em waves:

- **W0 — Groundwork & sanidade da S27**  
  - Verificar ambiente, repo e docs da S27 (Cap.1–3).  
  - Checar que G0 está implementado e rodando.  
  - Garantir que Admin v1, consoles e APIs mapeados em Cap.3 existem nos paths esperados.

- **W1 — Núcleo funcional Admin v1 nos consoles**  
  - Consolidar uso de Admin v1 em Fontes, Ingestão e Debunker (estrutura de páginas principais).  
  - Garantir que fluxos E2E básicos funcionam (escopo de G2 mínimo).  
  - Começar ajustes de contratos necessários (G4 parcial).

- **W2 — Refinos, UX e docs de operação**  
  - Refinar consoles (fluxos mais completos, navegação entre domínios).  
  - Consolidar contratos de API e testes de contrato (G4 mais amplo).  
  - Produzir e alinhar docs + runbooks admin (G5).  
  - Expandir cobertura de G2 e G3.

- **W3 — Hardening, ORR & bundle**  
  - Fechar bugs e arestas surgidos em W1/W2.  
  - Rodar suite completa de G0–G6.  
  - Preparar e validar `inspectah_s27_evidence_bundle.zip`.  
  - Conduzir ORR da S27 e emitir veredito sobre o Épico E26.

O Bloco 4.1 descerá esses pontos para objetivos, critérios de saída e gates por wave.

---

## 4. Filosofia de evidências na S27

A S27 segue a regra geral do Inspectah: **sem evidência, o trabalho não existe**.

No contexto do Cap.4, isso significa:

- Toda task S27-T-XXX deve apontar para pelo menos um artefato concreto (arquivo, pasta, scorecard, log, doc).  
- Toda wave tem um conjunto mínimo de evidências que precisa estar presente para ser considerada concluída.  
- G0–G6 só podem ser declarados GO se seus scorecards e pastas de evidência estiverem preenchidos.

O Bloco 4.2 formalizará, por wave e por gate:

- quais evidências são obrigatórias,  
- em que paths (`out/evidence/`, `out/scorecards/`, `docs/`, etc.),  
- e como elas serão usadas em Cap.5 (ORR) e Cap.6 (learnings/dívidas).

---

## 5. Estratégia macro de execução de gates

Em vez de rodar todos os gates apenas no final, a S27 distribui a execução de G0–G6 ao longo das waves:

- **W0**  
  - Foco em G0: ambiente, repo, presença de docs, sanity mínima de backend/frontend.

- **W1**  
  - G1 em modo estrito sobre Admin v1 e consoles;  
  - G3 voltado para garantir que o front continua buildando e testando com as mudanças;  
  - primeiros sinais para G2 (E2E mínimo).

- **W2**  
  - G2 em versão ampliada (mais cenários E2E);  
  - G3 rodando em cadência mais ampla (lint/test/build completos);  
  - G4 validando contratos atualizados;  
  - G5 assegurando que docs/runbooks foram escritos e usados.

- **W3**  
  - Rodada completa de G0–G6 como pré-ORR;  
  - Execução do ORR formal (Cap.5), gerando o scorecard G6;  
  - Geração e checagem do bundle de evidências.

O Bloco 4.3 traduzirá essa estratégia em instruções concretas (quais scripts rodar, em que momentos, em que ordem, local vs CI).

---

## 6. Estrutura e contrato das tasks S27-T-XXX

As tasks da S27 seguem o modelo do Sprint Playbook v3. Cada task S27-T-XXX deve registrar, no mínimo:

- ID: `S27-T-YYY` (YYY sequencial).  
- Wave: `W0`, `W1`, `W2` ou `W3`.  
- Categoria: `frontend`, `backend`, `gates`, `tests`, `docs`, `ops`, etc.  
- Descrição: frase clara iniciando com verbo, por exemplo: "Refatorar SourcesListPage para usar AdminShell".  
- Artefatos: paths específicos de arquivos/pastas (coerentes com Cap.3).  
- Gates: lista de gates impactados ou protegidos pela task (ex.: `[G1, G2]`).  
- Estados-alvo: IDs dos estados-alvo da S27 (SA-01, SA-02, etc.) que a task ajuda a satisfazer.  
- Done condition: critério objetivo de conclusão (ex.: "G1 e G3 rodando OK sobre SourcesListPage" + "fluxo X validado em cenário Y").  
- Evidências: paths esperados em `out/evidence/`, `out/scorecards/`, `docs/`, capturas de tela, etc.

O Bloco 4.4 conterá a tabela oficial dessas tasks, servindo de trilha primária para o Codex e para o time.

---

## 7. Como Cap.4 se conecta com os demais capítulos

- **Com Cap.1 (Contexto & Objetivos)**:  
  - Cap.4 garante que cada wave e cada task apontam para estados-alvo específicos (SA-XX) da S27.

- **Com Cap.2 (Gates, Métricas & ORR)**:  
  - Cap.4 distribui G0–G6 no tempo, definindo em quais waves cada gate é atacado e quais tasks suportam cada gate.

- **Com Cap.3 (Arquitetura & Filemap)**:  
  - Cap.4 exige que toda task cite paths do Cap.3, evitando trabalho "fantasma" em pastas improvisadas.

- **Com Cap.5 (ORR)**:  
  - Cap.4 prepara, ao longo das waves, o material que o ORR usará (cenários E2E, scorecards, bundle).

- **Com Cap.6 (Learnings, Dívidas & Roadmap)**:  
  - Cap.4 fornece a trilha de tasks e evidências que Cap.6 usará para explicar o que funcionou, o que quebrou e o que fica de dívida.

Com este Capítulo 4 macro definido, os próximos passos são construir, em conjunto com o squad, os quatro blocos detalhados (4.1–4.4), garantindo que **nenhuma execução da S27 aconteça fora desse trilho**.

