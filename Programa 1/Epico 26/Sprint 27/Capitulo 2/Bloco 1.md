# Inspectah — Sprint 27 (S27)
## Capítulo 2 — Bloco 1
### Visão geral dos gates, filosofia de verificação e mapa de scorecards

> Arquivo-alvo no repo: `docs/s27_cap_2_1_visao_geral_gates_e_scorecards.md`
>
> Função: explicar **como a Sprint 27 será verificada**, quais são os gates, o que cada um protege e como os scorecards se encaixam. Este bloco é a leitura obrigatória antes de alguém editar scripts em `bin/s27_g*_*.sh` ou mexer nos scorecards em `out/scorecards/`.

---

## 1. Papel dos gates na S27

A S27 não é uma sprint de "features soltas"; ela é uma sprint de **consolidação de padrão** (Admin v1) em três consoles críticos: Fontes, Ingestão 2.0 e Debunker.

Por isso, o Capítulo 2 assume uma postura mais dura:

- Nada é considerado entregue se não passar por pelo menos um gate relevante.  
- Todo gate gera **scorecards** e **evidências** em pastas bem definidas.  
- O ORR (G6) só pode declarar GO/NO-GO apoiado nesses artefatos.

Gates na S27 são o mecanismo para garantir que os estados-alvo do Cap.1 (Bloco 3) não fiquem apenas no papel.

---

## 2. Lista dos gates da S27 e seus domínios

A S27 usa sete gates numerados de **G0 a G6**, com os seguintes domínios de proteção:

- **G0 — Escopo, Grounding & Sanidade de Ambiente**  
  - Protege: integridade mínima do repositório e ambiente, presença de docs de Cap.1 e Cap.2, alinhamento de escopo.  
  - Pergunta-chave: estamos de fato rodando a S27 sobre o terreno certo, ou já começamos tortos?

- **G1 — Design System Admin v1 (Tokens & Componentes)**  
  - Protege: integridade de `ui/admin` e adesão dos consoles alvo ao design system.  
  - Pergunta-chave: Fontes, Ingestão e Debunker estão usando Admin v1 de verdade ou só fingindo?

- **G2 — Fluxos de Consoles Admin (Fontes / Ingestão / Debunker)**  
  - Protege: funcionamento E2E dos fluxos principais de operação nesses consoles, sob Admin v1.  
  - Pergunta-chave: um operador consegue, na prática, executar suas tarefas críticas sem cair em buracos?

- **G3 — Qualidade Global de Frontend Admin**  
  - Protege: saúde básica do frontend (lint, testes, build) com foco no admin.  
  - Pergunta-chave: a casa está minimamente organizada ou estamos construindo em cima de um front quebrado?

- **G4 — Contratos & APIs relevantes para consoles admin**  
  - Protege: coerência de contratos entre frontend admin e APIs de Fontes, Ingestão e Debunker.  
  - Pergunta-chave: as telas que o operador vê correspondem a contratos estáveis no backend?

- **G5 — Documentação & Runbooks de Operação**  
  - Protege: existência e qualidade mínima de guias e runbooks para operar os consoles pós-S27.  
  - Pergunta-chave: dá para operar isso na vida real sem depender da memória tribal da equipe?

- **G6 — ORR & Bundle de Evidências da S27**  
  - Protege: decisão de GO/NO-GO bem fundamentada, fechamento do Épico E26 e integridade do bundle de evidências.  
  - Pergunta-chave: olhando para tudo, E26 (Admin v1 em Fontes/Ingestão/Debunker) está realmente pronto?

Cada gate é implementado como, no mínimo, um script em `bin/` + um scorecard JSON em `out/scorecards/` + uma pasta de logs em `out/evidence/`.

---

## 3. Filosofia de verificação na S27

A filosofia de verificação da S27 combina três princípios:

1. **Traçabilidade ao Cap.1**  
   - Todo gate deve ser rastreável a pelo menos um estado-alvo do Bloco 3 do Cap.1.  
   - Se um gate não consegue apontar que parte do problema central ele ajuda a resolver, algo está errado.

2. **Evidência ou não aconteceu**  
   - Nenhum "está funcionando aqui na minha máquina" vale sem log, scorecard ou captura de E2E.  
   - Se o ORR não consegue ver o efeito da S27 em `out/evidence/` e `out/scorecards/`, a sprint está incompleta.

3. **Foco em operação, não só em compilação**  
   - G3 cuida de build/lint/tests, mas G2 e G5/G6 puxam a verificação para o nível de **operador**: fluxos e runbooks.  
   - A S27 é bem-sucedida apenas se a operação de Fontes + Ingestão + Debunker melhorar, não só se o front compilar.

---

## 4. Mapa de scorecards e evidências

Para evitar caos de arquivos, a S27 segue uma convenção clara para scorecards e evidências:

- **Scorecards por gate**  
  - G0: `out/scorecards/S27_G0_scope_and_env.json`  
  - G1: `out/scorecards/S27_G1_admin_design_system.json`  
  - G2: `out/scorecards/S27_G2_admin_flows.json`  
  - G3: `out/scorecards/S27_G3_front_quality_admin.json`  
  - G4: `out/scorecards/S27_G4_admin_contracts.json`  
  - G5: `out/scorecards/S27_G5_docs_runbooks.json`  
  - G6: `out/scorecards/S27_G6_orr_summary.json`

- **Evidências por gate**  
  - `out/evidence/S27_G0_env_repo/`  
  - `out/evidence/S27_G1_admin_design_system/`  
  - `out/evidence/S27_G2_admin_flows/`  
  - `out/evidence/S27_G3_front_quality_admin/`  
  - `out/evidence/S27_G4_admin_contracts/`  
  - `out/evidence/S27_G5_docs_runbooks/`  
  - `out/evidence/S27_G6_orr/`

- **Bundle final da S27**  
  - `out/bundles/inspectah_s27_evidence_bundle.zip` — agregando scorecards + evidências principais, como na S26.

Esse mapa deve ser seguido à risca pelo Codex e pelos scripts, para manter continuidade com sprints anteriores.

---

## 5. Relação entre os gates e o problema da S27

Cada gate da S27 existe para bater em uma parte específica do problema central (Cap.1 Bloco 2):

- G0 garante que não estamos puxando uma S27 "fantasma" em cima de ambiente quebrado ou docs ausentes.  
- G1 ataca diretamente a fragmentação de UI/Admin (faz Admin v1 ser real em código).  
- G2 garante que os fluxos críticos de operadores em Fontes/Ingestão/Debunker realmente funcionam sob o novo padrão.  
- G3 impede que problemas básicos de front contaminem a leitura dos demais gates.  
- G4 evita que a UI "minta" sobre o estado do backend; contratos quebrados são expostos.  
- G5 garante que a mudança é operável por humanos, não só por testes automatizados.  
- G6 junta tudo e responde, com base em evidência, se o Épico E26 pode ser fechado.

---

## 6. Como este bloco conversa com os demais do Capítulo 2

- O **Bloco 1** (este doc) é o atlas: nome, domínio e relação de cada gate com o problema da S27, além do mapa de scorecards/evidências.  
- O **Bloco 2** detalhará G0–G2 (escopo, scripts, campos de scorecard, critérios de GO/NO-GO).  
- O **Bloco 3** fará o mesmo para G3–G4.  
- O **Bloco 4** cobrirá G5–G6 e o desenho do ORR da S27.

Depois de ler este Bloco 1, qualquer pessoa deve conseguir responder, sem hesitar:  
> "Quais são os gates da S27, o que cada um protege, e onde vejo se passaram ou não?"