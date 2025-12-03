# Inspectah — Sprint 31 (E28-S3)
## Capítulo 4 — Bloco 1: Papel do Capítulo & Estratégia de Execução

### 4.0 Por que este capítulo existe

Os Capítulos 1, 2 e 3 da Sprint 31 respondem, respectivamente:

- **Cap.1**: *“O que a S31 quer mudar no mundo do Inspectah?”* (objetivos, estados-alvo, domínio piloto).
- **Cap.2**: *“Como vamos saber se deu certo?”* (gates, métricas, invariantes, scorecards, ORR).
- **Cap.3**: *“Onde cada peça mora na arquitetura e no repo?”* (backend, frontend, observabilidade, filemap).

O **Capítulo 4** responde à pergunta que falta:

> **“Em que ordem concreta colocamos tudo isso de pé, com quais comandos, e quais evidências precisamos guardar para provar que não nos enganamos?”**

Este Bloco 1 fixa o propósito do capítulo e define a **estratégia de execução** da Sprint 31, antes de descer para checklists detalhados nos blocos seguintes.

Se alguém da equipe ler só este bloco, deve sair com um mapa mental claro de:

- quais são as fases da S31;
- o que cada fase entrega;
- quais gates se acendem em cada momento;
- onde entram docs, código, evidências e CI.

---

### 4.1 Princípios de execução da Sprint 31

A execução da S31 segue alguns princípios explícitos, para evitar o clássico “tudo ao mesmo tempo, nada inteiro”:

1. **Primeiro dados e modelo, depois UI bonita**  
   Provider-first só existe de verdade se o modelo, as migrations e a proveniência estiverem corretos. Console, dashboards e integrações vêm em cima disso, não ao contrário.

2. **Pilotar antes de escalar**  
   A sprint trabalha com **perfis-piloto** (ex.: política/economia BR) para validar o desenho. Nada de tentar ligar o planeta inteiro de primeira.

3. **Cada fase fecha com gate e evidência**  
   Não se “avança” de fase porque o time está com vontade: avança porque o gate correspondente foi rodado, gerou evidência e scorecard aceitável.

4. **Legado não pode quebrar nunca “por engano”**  
   Tudo que mexe em modelo de dados passa por uma rodada explícita de sanity com fluxos legados críticos (via G4). Se algo quebrar, a S31 recua, corrige e só então prossegue.

5. **Docs e código caminham juntos**  
   Sempre que uma decisão relevante de modelo ou fluxo é implementada, o doc correspondente da sprint precisa ser atualizado. Cap.3 e Cap.4 não são teoria: são o espelho do branch.

---

### 4.2 Macroestratégia: quatro fases bem definidas

Para tornar a execução operável, a Sprint 31 é dividida em **quatro fases sequenciais**, com possibilidade de pequenas iterações internas em cada uma:

1. **Fase 1 — Fundação de dados & migrations**  
   Objetivo: colocar de pé o esqueleto provider-first no banco e nos modelos, sem quebrar o que existe.

   Entregas principais:
   - modelos `Provider` e `IngestionProfile` implementados;
   - `ContentItem` e `Source` ajustados para proveniência;
   - migrations criadas e aplicadas em ambiente de desenvolvimento;
   - configs mínimas em `config/providers.yml` e `config/ingestion_profiles.yml` com perfis-piloto;
   - G1 (`s31_g1_models_and_migrations`) rodando com evidências e scorecard inicial.

2. **Fase 2 — Backend de ingestão provider-first**  
   Objetivo: conseguir rodar ingestão via providers fim a fim, em modo piloto, a partir dos perfis configurados.

   Entregas principais:
   - clients de provider (news/social) implementados;
   - serviços de normalização, dedupe e `profile_runner` em funcionamento;
   - jobs/scheduler transformando perfis em runs reais;
   - métricas e logs básicos por perfil registrados;
   - G2 (`s31_g2_provider_ingestion`) rodando, com evidências de ingestão e dedupe.

3. **Fase 3 — Console de Fontes v2 (backend + frontend)**  
   Objetivo: permitir operar provider-first via UI, sem depender de scripts manuais.

   Entregas principais:
   - APIs de Console para Providers e Perfis expostas e testadas;
   - telas de lista/detalhe de Providers e Perfis implementadas;
   - formulário de criação/edição de perfil;
   - botão “Rodar agora” funcionando para perfis-piloto;
   - G3 (`s31_g3_console_and_observability`) rodando com testes de UI e primeiras métricas.

4. **Fase 4 — Legado, Programas 2–3, gates completos & ORR**  
   Objetivo: provar que provider-first convive com legado e alimenta Programas 2–3 como desenhado.

   Entregas principais:
   - adaptador de legado implementado, plano de migração documentado;
   - pipelines de Programa 2 consumindo ContentItems de perfis-piloto;
   - pelo menos um caso piloto completo em Programa 3, com trilha Provider → Perfil → ContentItem → Claim → FactBlock;
   - todos os gates S31-G0..G5 rodando;
   - `s31_orr.sh` gerando `S31_ORR_overview.json` com veredito GO/GO_WITH_WARNINGS/NO_GO.

Cada fase pode ser vista como um mini-projeto com sua própria Definition of Done parcial, mas a sprint só é considerada entregue quando **todas** passarem pelos gates e o ORR fechar com status aceitável.

---

### 4.3 Mapa fases ↔ gates ↔ capítulos

Para não virar mistério de quem valida o quê, a relação entre fases, gates e capítulos é explicitamente esta:

- **Fase 1**
  - Capítulos envolvidos: Cap.1 (estados-alvo), Cap.2 (G1, invariantes de modelo), Cap.3 (modelos & migrations).
  - Gates: G0 (scope/baseline) + G1.

- **Fase 2**
  - Capítulos envolvidos: Cap.2 (G2, métricas mínimas de ingestão), Cap.3 (serviços, jobs).
  - Gates: G2.

- **Fase 3**
  - Capítulos envolvidos: Cap.2 (G3, métricas de observabilidade), Cap.3 (frontend Console v2, APIs).
  - Gates: G3.

- **Fase 4**
  - Capítulos envolvidos: Cap.1 (domínio piloto), Cap.2 (G4, G5, ORR, invariantes de trilha de origem e legado), Cap.3 (legado, integração P2–P3).
  - Gates: G4, G5 + ORR.

Os blocos seguintes deste capítulo vão pegar cada fase e detalhar:

- ordem recomendada de tarefas;
- comandos típicos (local e CI);
- arquivos de evidência que precisam existir em `out/evidence`;
- scorecards que precisam ser preenchidos em `out/scorecards`.

Quando esse plano estiver sendo seguido e os artefatos estiverem no lugar certo, a Sprint 31 deixa de ser texto e passa a ser um pedaço concreto do Inspectah, com provider-first rodando em pista real (domínio piloto), dentro dos limites de custo e sanidade que a gente definiu.