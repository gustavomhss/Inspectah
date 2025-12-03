# Inspectah — Sprint 27 (S27)
## Capítulo 3 — Bloco 4
### Costura final: arquitetura, filemap, gates e plano de execução da S27

> Arquivo-alvo no repo: `docs/s27_cap_3_4_costura_arquitetura_gates_execucao.md`
>
> Função: costurar o que foi definido nos Blocos 1, 2 e 3 do Capítulo 3 com os gates do Cap.2 e com o futuro plano de execução do Cap.4, eliminando gaps entre "desenho" e "trabalho real". Este bloco é o elo final entre arquitetura/filemap e o dia a dia da sprint.

---

## 1. O problema clássico que este bloco quer evitar

Sem uma costura explícita, é comum acontecer:

- Cap.1 e Cap.2 definirem metas e gates ambiciosos.  
- Cap.3 desenhar uma arquitetura bonita e um filemap elegante.  
- Cap.4 criar tasks que "parecem certas" mas não têm ancoragem direta nos arquivos certos nem nos gates.

O resultado é conhecido: features aparecem nos lugares errados, scripts de gate não enxergam o que deveriam e o ORR precisa fazer ginástica para provar algo que deveria ser óbvio pelo repositório.

O Bloco 4 existe para impedir isso na S27.

---

## 2. Tabela de traçabilidade: estados-alvo ↔ arquitetura ↔ gates

A S27 tem alguns estados-alvo principais (Cap.1 Bloco 3) que, simplificando, podemos representar assim:

1) Admin v1 é o padrão real para consoles de Fontes, Ingestão e Debunker.  
2) Consoles admin críticos funcionam de ponta a ponta para fluxos chave.  
3) Contratos de API usados pelos consoles são consistentes e verificáveis.  
4) Operadores têm docs e runbooks que refletem a realidade da UI e das APIs.  
5) A sprint e o Épico E26 podem ser julgados de forma objetiva via ORR.

A tabela abaixo mostra como cada estado conversa com arquitetura/filemap (Cap.3) e com gates (Cap.2):

Estado 1: Admin v1 como padrão real  
Arquitetura/filemap:
- `frontend/inspectah-ui/ui/admin/*` (Bloco 2) como camada base.  
- `features/sources`, `features/ingestion`, `features/debunker` importando Admin v1 claramente.
Gates:
- G1 verifica uso de Admin v1 nas features.  
- G3 garante que o front continua saudável.

Estado 2: fluxos admin críticos funcionando E2E  
Arquitetura/filemap:
- pages e components em `features/sources/pages/*`, `features/ingestion/pages/*`, `features/debunker/pages/*` (Bloco 2).  
- Rotas e modelos correspondentes em `app/api/*_routes.py`, `app/models/*`, `app/schemas/*` (Bloco 3).
Gates:
- G2 testa fluxos E2E passando por essas telas e APIs.  
- G3 garante que build/lint/tests não sabotam a experiência.

Estado 3: contratos de API consistentes  
Arquitetura/filemap:
- rotas de Fontes/Ingestão/Debunker organizadas em `app/api`.  
- schemas em `app/schemas`.  
- testes de contrato em `tests/api/test_admin_*` (Bloco 3).
Gates:
- G4 verifica contratos, schemas e endpoints-chave.

Estado 4: operação com docs e runbooks fiéis  
Arquitetura/filemap:
- docs e runbooks em `docs/guia_consoles_admin_v1_1.md` e `docs/runbook_operacao_*` (Cap.3 visão macro).  
- referência cruzada em Cap.5 (ORR) e Cap.6.
Gates:
- G5 verifica presença, estrutura mínima e uso em ORR.

Estado 5: julgamento objetivo da S27 e do E26  
Arquitetura/filemap:
- scorecards em `out/scorecards/S27_G*.json`.  
- evidências em `out/evidence/S27_G*/`.  
- bundle zip em `out/bundles/inspectah_s27_evidence_bundle.zip`.  
- Cap.5 (ORR) em `docs/s27_cap_5_orr_local_summary.md`.
Gates:
- G6 consolida tudo isso num veredito GO/NO-GO/GO_WITH_RISKS.

Essa tabela de traçabilidade deve ser mantida viva: se a arquitetura ou os estados-alvo mudarem, este bloco precisa ser atualizado.

---

## 3. Regras de ouro para o Codex e para tasks do Cap.4

Para que Cap.4 não vire uma lista de tarefas soltas, a S27 define algumas regras explícitas que este Bloco 4 registra:

1) Toda task de frontend da S27 deve apontar para pelo menos um caminho explícito do Bloco 2.  
   Exemplo: "Refinar lista de fontes" → `frontend/inspectah-ui/features/sources/pages/SourcesListPage.tsx` + `features/sources/components/SourcesTable.tsx`.

2) Toda task de backend da S27 deve apontar para ao menos um caminho do Bloco 3.  
   Exemplo: "Expor overview de ingestão" → `app/api/ingestion_routes.py` + `app/schemas/ingestion.py` + `tests/api/test_admin_ingestion_contracts.py`.

3) Toda task que pretenda alterar comportamento validado por gate deve citar o gate relevante.  
   Exemplo: "Criar teste E2E de fluxo combinado Fontes→Ingestão→Debunker" → G2.

4) Nenhuma task considerada DONE pode existir sem pelo menos uma destas evidências:
   - diff em arquivo mapeado aqui,  
   - atualização em scorecard/evidência de gate,  
   - atualização em docs/runbooks ligados ao comportamento alterado.

5) Se for realmente necessário criar novos diretórios ou arquivos fora do filemap descrito, isso deve ser registrado em Cap.3 (atualização deste bloco ou dos blocos anteriores) antes de ser normalizado.

Essas regras são, na prática, o "contrato operacional" entre Cap.3 e Cap.4.

---

## 4. Macro-mapeamento para S27-T-XXX (Cap.4)

O Cap.4 da S27 vai decompor trabalho em tasks S27-T-XXX. Este bloco define um macro-mapeamento esperado entre tipos de task e regiões do repo:

Tipo de tarefa: "Refino de UI em Fontes sob Admin v1"  
Caminhos típicos:
- `frontend/inspectah-ui/ui/admin/*` (se surgir necessidade de novo componente genérico).  
- `frontend/inspectah-ui/features/sources/pages/*`  
- `frontend/inspectah-ui/features/sources/components/*`
Gates relacionados: G1, G2, G3.

Tipo de tarefa: "Criação/ajuste de visão de ingestão 2.0"  
Caminhos típicos:
- `frontend/inspectah-ui/features/ingestion/*`  
- `app/api/ingestion_routes.py`  
- `app/schemas/ingestion.py`  
- `tests/api/test_admin_ingestion_contracts.py`
Gates relacionados: G2, G3, G4.

Tipo de tarefa: "Aprimoramento de telas do Debunker"  
Caminhos típicos:
- `frontend/inspectah-ui/features/debunker/*`  
- `app/api/debunker_routes.py`  
- `app/schemas/debunker.py`  
- `tests/api/test_admin_debunker_contracts.py`
Gates relacionados: G2, G3, G4.

Tipo de tarefa: "Melhorar docs/runbooks admin"  
Caminhos típicos:
- `docs/guia_consoles_admin_v1_1.md`  
- `docs/runbook_operacao_fontes_vX.md`  
- `docs/runbook_operacao_ingestao_vX.md`  
- `docs/runbook_operacao_debunker_vX.md`
Gates relacionados: G5, G6.

Tipo de tarefa: "Ajustes em scripts de verificação e bundle"  
Caminhos típicos:
- `bin/s27_g*_*.sh`  
- `out/scorecards/S27_G*.json`  
- `out/evidence/S27_G*/`
Gates relacionados: G0–G6.

Cap.4 deve usar este macro-mapeamento como grid de referência ao criar as tasks.

---

## 5. Verificações de consistência entre Cap.2, Cap.3 e Cap.4

Durante a sprint, a S27 recomenda checkpoints rápidos para garantir que os capítulos não divergiram:

1) Checklist de sincronização Cap.2 ↔ Cap.3  
   - Para cada gate G0–G6, verificar se:  
     - os scripts citados em Cap.2 existem em `bin/`;  
     - os caminhos de frontend/backend/docs referidos por cada gate batem com o filemap deste Cap.3.

2) Checklist de sincronização Cap.3 ↔ Cap.4  
   - Amostragem de tasks S27-T-XXX:  
     - cada task deve referenciar explicitamente ao menos um caminho deste Cap.3;  
     - se uma task cita um caminho não descrito aqui, ou este bloco deve ser atualizado, ou a task está fora de escopo da S27.

3) Checklist ORR (Cap.5)  
   - O documento de ORR deve conter, idealmente em anexo, uma visão de quais partes do filemap foram tocadas e quais gates validaram cada parte.

Esses três checklists podem ser simplificados em um pequeno script/manual de revisão de sprint.

---

## 6. Impacto deste bloco na leitura do repositório pós-S27

Depois que a S27 for concluída, este Bloco 4 se torna uma peça importante para:

- Onboarding de novos devs nos consoles admin:  
  - "Quero mexer em Ingestão 2.0" → olhar Bloco 2 e Bloco 3, com apoio deste Bloco 4 para entender gates e tasks.  
- Planejamento de epics futuros que toquem Admin v1 ou Consoles:  
  - reusar padrões de filemap, gates e traçabilidade.  
- Auditorias e investigações de regressões:  
  - se algo quebra em Fontes/Ingestão/Debunker, é possível olhar:  
    - tasks S27-T-XXX correspondentes em Cap.4,  
    - caminhos deste Cap.3,  
    - gates que deveriam ter protegido aquele comportamento.

Em resumo, este Bloco 4 garante que a arquitetura e o filemap da S27 **não são apenas documentação estática**, mas parte ativa do ciclo de controle de qualidade e evolução do Inspectah.

---

## 7. Encerramento do Capítulo 3 e ponte para o Capítulo 4

Com os quatro blocos do Capítulo 3 concluídos, temos:

- Visão macro da arquitetura da S27 e papel central de Admin v1 (Bloco 1).  
- Filemap detalhado de frontend admin (Bloco 2).  
- Filemap detalhado de backend e contratos de API (Bloco 3).  
- Costura entre arquitetura/filemap, estados-alvo, gates e plano de execução (Bloco 4).

O Capítulo 4 (Execução & Evidências) passa agora a ter um trilho claro:

- decompor a S27 em tasks S27-T-XXX,  
- ancorar cada task em caminhos concretos deste Cap.3,  
- associar cada task a gates específicos do Cap.2,  
- indicar quais evidências (em `out/evidence/` e `out/scorecards/`) serão produzidas ou atualizadas.

Se Cap.3 é o mapa da cidade, este Bloco 4 é a planta das rotas de ônibus: mostra quais ruas (arquivos/pastas) cada linha (task/gate) percorre. Sem ele, a S27 teria mais improviso; com ele, a sprint passa a ter um traçado deliberado e auditável.