# Inspectah — Sprint 27 (S27)
## Capítulo 3 — Bloco 1
### Visão macro da arquitetura da S27 e papel de Admin v1

> Arquivo-alvo no repo: `docs/s27_cap_3_1_visao_macro_arquitetura.md`
>
> Função: descrever a **arquitetura macro** da Sprint 27, com foco em como o Design System Admin v1 orquestra os consoles de Fontes, Ingestão 2.0 e Debunker, e como isso se conecta às camadas de backend, qualidade e operação. Este bloco é o quadro geral antes de descer para filemaps detalhados.

---

## 1. Posição da S27 dentro da arquitetura do Inspectah

A S27 atua em cima de uma arquitetura já existente do Inspectah, mas com um recorte muito específico:

- Ela **não cria um novo sistema**; consolida e alinha a interface admin de três domínios críticos sobre o Design System Inspectah Admin v1.  
- Ela conecta frontend admin, APIs e docs de operação de forma coerente, de modo que **Admin v1 deixe de ser um piloto de Fontes** e passe a ser o **idioma oficial** de consoles internos do Programa 1.

Do ponto de vista arquitetural, a S27 é uma sprint de **convergência**:

- convergência de UI (layout, componentes, padrões visuais),  
- convergência de experiência de operação (runbooks e fluxos),  
- convergência de contratos (o que front espera vs o que back entrega),  
- convergência de verificação (gates G0–G6 olhando para as mesmas peças).

---

## 2. Blocos arquiteturais principais impactados pela S27

A S27 toca diretamente quatro blocos macro da arquitetura Inspectah:

1. **Camada de UI Admin (Design System Admin v1)**  
   - Papel: fornecer um "esqueleto" comum para todos os consoles admin internos — layout, navegação, tokens visuais e componentes fundamentais.  
   - Local típico: `frontend/inspectah-ui/ui/admin/`.  
   - Responsabilidade: padrão de experiência, não lógica de negócio.

2. **Consoles Admin de Domínio (Fontes, Ingestão, Debunker)**  
   - Papel: traduzir necessidades de operação de cada domínio em telas concretas sobre Admin v1.  
   - Locais típicos:  
     - `frontend/inspectah-ui/features/sources/*`  
     - `frontend/inspectah-ui/features/ingestion/*`  
     - `frontend/inspectah-ui/features/debunker/*`  
   - Responsabilidade: orquestrar dados, ações e fluxos usando o design system.

3. **Camada de Serviços & Contratos de Backend**  
   - Papel: expor **APIs coerentes** para que os consoles admin leiam estado e executem comandos.  
   - Locais típicos:  
     - `app/api/*_routes.py` (rotas HTTP),  
     - `app/models/*` e `app/schemas/*` (modelos e schemas).  
   - Responsabilidade: ser a "verdade" de dados e regras que o admin enxerga.

4. **Camada de Qualidade, Verificação & Operação**  
   - Papel: garantir que a consolidação feita pela S27 **não é frágil** — via gates, testes, scorecards, evidências e docs.  
   - Locais típicos:  
     - `bin/s27_g*_*.sh` (scripts de gates),  
     - `tests/*` (tests de front e API),  
     - `out/scorecards/` e `out/evidence/`,  
     - `docs/` (Cap.1–Cap.6, guias, runbooks).

A S27 está no cruzamento desses quatro blocos, com Admin v1 como eixo central.

---

## 3. Papel de Admin v1 como "sistema operacional" dos consoles

Dentro da S27, o **Design System Inspectah Admin v1** deve ser tratado arquiteturalmente como uma espécie de "sistema operacional" para consoles internos:

- Ele define **layout padrão**: header, sidebar, área de conteúdo, padrões de responsividade.  
- Ele define **vocabulário visual**: cores, tipografia, spacing, ícones e estados (erro, alerta, sucesso, neutro).  
- Ele define **padrões de interação**: como tabelas se comportam, como filtros aparecem, como ações críticas são confirmadas.

Em termos de arquitetura de front:

- Consoles **não devem** inventar seus próprios shells, sidebars, headers ou paletas para telas admin.  
- Consoles devem compor páginas a partir de blocos de Admin v1 (por exemplo: `<AdminShell>`, `<AdminPageHeader>`, `<AdminTable>`, `<AdminAlert>`), plugando neles dados e ações de domínio.

A S27, portanto, **não é apenas uma sprint de UI**; é a sprint que cristaliza a ideia de que:  
> “Para o Programa 1, todo console admin nasce e vive em cima de Admin v1, a não ser que exista uma exceção muito bem justificada e documentada.”

---

## 4. Relação arquitetural entre Fontes, Ingestão e Debunker

Do ponto de vista de fluxo de informação e arquitetura, os três consoles admin atingidos pela S27 têm uma relação clara:

- **Fontes**: definem **de onde** os dados vêm e **como** eles entram no sistema (tipos de fonte, configurações, ativação/desativação).  
- **Ingestão 2.0**: mostra **como** esses dados estão entrando ao longo do tempo (jobs, filas, atrasos, falhas, retries).  
- **Debunker**: lida com **consequências** e disputas em cima de dados (casos, evidências, decisões).

Arquiteturalmente:

- Fontes e Ingestão compartilham entidades como "fonte" e "job de ingestão", mas expostas sob perspectivas diferentes (configuração vs operação em tempo).  
- Ingestão e Debunker se encontram via eventos e casos: problemas de ingestão podem gerar casos, e decisões em Debunker podem exigir ações em ingestão ou revisões de fontes.  
- Todas essas relações precisam ser **navegáveis** na UI admin pós-S27 (fluxos E2E protegidos por G2), de modo que um operador consiga saltar de uma visão para outra sem sentir que trocou de produto.

A S27 garante que essa relação já existente no backend apareça, de forma coerente, nos consoles admin sob Admin v1.

---

## 5. Como a S27 conversa com arquitetura futura (além de E26)

A arquitetura consolidada pela S27 serve de base para evoluções futuras em múltiplos eixos:

1. **Novos consoles admin** (ex.: Evidence Vault, Truth-DB, Agentes)  
   - A existência de Admin v1 consolidado em Fontes/Ingestão/Debunker cria um **caminho padrão** para novos consoles.  
   - Arquitetos e squads futuros podem tomar o filemap e os patterns da S27 como blueprint.

2. **Observabilidade e Cockpits mais avançados**  
   - Uma UI admin coerente facilita plugar dashboards, gráficos e indicadores mais ricos no futuro, sem precisar reinventar layout ou linguagem visual.

3. **Automação de operações**  
   - Com padrões claros de componentes e estados, fica mais viável acoplar agentes (human-in-the-loop + LLMs) que consigam "entender" a interface admin para sugerir ações ou automatizar partes de fluxos.

4. **Governança e controles mais rígidos**  
   - A consolidação de Admin v1 e a existência de gates G0–G6 permitem que, no futuro, epics de governança definam políticas do tipo:  
     - "Nenhum novo console admin pode ser mergeado sem passar pelos gates de Admin v1".

A S27, do ponto de vista arquitetural, é o ponto de inflexão em que Admin v1 deixa de ser experimento e passa a ser **infraestrutura obrigatória**.

---

## 6. Conexão deste bloco com os demais blocos do Capítulo 3

- O **Bloco 1** (este doc) fixa a visão macro: quais blocos da arquitetura a S27 toca, qual o papel de Admin v1, como Fontes/Ingestão/Debunker se relacionam e que impacto isso tem no futuro.  
- O **Bloco 2** descerá para o **filemap detalhado de frontend** (Admin v1 + features dos consoles), com caminhos e responsabilidades mais específicos.  
- O **Bloco 3** tratará do **backend e dos contratos de API**, conectando modelos, rotas e testes aos consoles admin.  
- O **Bloco 4** fará a costura final entre arquitetura/filemap, gates (Cap.2) e plano de execução (Cap.4), garantindo que não existam buracos entre o que foi desenhado e o que será implementado.

Depois de ler este Bloco 1, qualquer pessoa deve conseguir responder, em linguagem simples:  
> "Qual é o papel da S27 na arquitetura do Inspectah e como Admin v1 organiza os consoles de Fontes, Ingestão e Debunker?"