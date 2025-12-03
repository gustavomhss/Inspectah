# Inspectah — Sprint 27 (S27)
## Capítulo 1 — Bloco 3
### Estados-alvo, critérios de sucesso e não-negociáveis da S27

> Arquivo-alvo no repo: `docs/s27_cap_1_3_estados_alvo_e_sucesso.md`
>
> Função: transformar o problema descrito no Bloco 2 em **estados-alvo concretos** e **critérios de sucesso verificáveis** para a Sprint 27. Este bloco responde: “como sabemos, sem autoengano, que a S27 cumpriu sua missão dentro do Épico E26?”.

---

## 1. Estados-alvo da UI/Admin pós-S27

### 1.1 Estado-alvo 1 — Consoles críticos sob Admin v1

Após a S27, os três consoles admin críticos do Programa 1 — Fontes, Ingestão 2.0 e Debunker — devem estar em um estado em que possamos dizer:

> "Todos rodam sobre o Design System Inspectah Admin v1, sem ilhas de layout paralelo dentro do escopo do Épico E26."

Sinais concretos de que este estado foi atingido:

- Todos utilizam `AdminShell`, `AdminHeader`, `AdminSidebar`, `AdminContent` como base de layout.  
- Componentes de UI (botões, tabelas, badges, alerts, inputs) vêm de `ui/admin` ou são explicitamente marcados como exceções/dívidas técnicas `S27-DT-XXX`.  
- Rotas e breadcrumbs seguem um padrão comum para navegação entre Fontes, Ingestão e Debunker.

### 1.2 Estado-alvo 2 — Estados de UI padronizados entre consoles

Depois da S27, estados de UI como "vazio", "carregando", "erro", "alerta" e "sucesso" devem seguir um **vocabulário visual e textual comum** entre Fontes, Ingestão e Debunker.

Sinais concretos:

- Uso consistente de cores, ícones e tipografia para distinguir:  
  - erro crítico vs alerta vs informação neutra;  
  - ações destrutivas vs reversíveis;  
  - ausência de dados vs falha de carregamento.  
- Mensagens de sistema com estrutura similar (título curto, explicação objetiva, próxima ação sugerida).  
- Operadores reconhecem imediatamente que estão vendo "o mesmo tipo de coisa" quando um erro aparece em qualquer console admin.

### 1.3 Estado-alvo 3 — Guia de Consoles Admin v1.1 com exemplos reais

O **Guia de Consoles Admin v1** deve chegar à versão v1.1, contendo:

- princípios de layout e navegação para consoles admin;  
- exemplos concretos de telas de Fontes, Ingestão e Debunker;  
- padrões recomendados ("faça assim") e anti-padrões ("não faça assim"), com screenshots e comentários;
- diretrizes para representar estados críticos (erros, disputas sensíveis, ingestão atrasada) sem inventar estilos ad-hoc.

Esse guia passa a ser a referência obrigatória para qualquer novo console admin ou refino significativo.

### 1.4 Estado-alvo 4 — Runbooks de Ingestão e Debunker no mesmo idioma de Fontes

Após a S27, os runbooks de operação de Ingestão e Debunker devem:

- usar a mesma nomenclatura de componentes e ações do runbook de Fontes;  
- referenciar telas e elementos de UI que existem e se comportam conforme o design system;  
- permitir que um operador treinado em Fontes se adapte rapidamente a Ingestão e Debunker.

### 1.5 Estado-alvo 5 — Gates e ORR cobrindo o conjunto Admin v1

O sistema de gates e ORR precisa refletir a realidade de que os três consoles formam um **conjunto**:

- G1 protege o design system admin (tokens e componentes) em estado coerente para todos;  
- G2/G3 cobrem fluxos E2E que passam por Fontes, Ingestão e Debunker, não apenas por um console isolado;  
- Cap.5 define cenários E2E, ORR, runbooks e riscos considerando o conjunto, com bundle de evidências correspondente.

---

## 2. Critérios de sucesso da Sprint 27 (mensuráveis)

### 2.1 Critérios de sucesso de percepção (operadores)

1. Um operador experiente consegue alternar entre Fontes, Ingestão e Debunker, em ambiente de staging, e descreve a experiência como "é tudo o mesmo sistema" quando perguntado.  
2. Em simulações de incidentes que envolvem mais de um console, o on-call consegue seguir o runbook sem precisar de explicações adicionais sobre "como essa tela funciona".

### 2.2 Critérios de sucesso técnicos de UI/Admin

1. Revisão de código mostra que todos os consoles admin críticos da S27:
   - utilizam `AdminShell` e componentes padrão de `ui/admin`;  
   - não possuem CSS/layout "solto" para estruturar páginas (apenas para casos muito específicos, marcados como exceção).

2. Scripts de lint/check específicos (definidos em Cap.2/Cap.3) não apontam mais uso de layout/componentes legados nos consoles alvo.

### 2.3 Critérios de sucesso de docs & método

1. `guia_consoles_admin_v1_1.md` (ou nome equivalente) está criado, revisado e referenciado em Cap.3/Cap.5 da S27.  
2. Runbooks de Ingestão e Debunker estão atualizados e foram usados em pelo menos uma rodada de simulação/documentada no ORR da S27.  
3. Cap.6 da S27 não registra nenhum "gap óbvio" relacionado a falta de alinhamento entre consoles admin.

### 2.4 Critérios de sucesso de épico/roadmap

1. No fechamento da S27, o Conselho consegue declarar o Épico E26 como **"entregue"** por unanimidade, com Admin v1 estabelecido como padrão obrigatório para consoles do Programa 1.  
2. O `Roadmap.md`, atualizado no Cap.6, passa a tratar Admin v1 como infraestrutura dada, não como item a ser concluído.

---

## 3. Não-negociáveis da Sprint 27

Para evitar que a S27 seja diluída em dezenas de pequenas melhorias dispersas, definimos alguns **não-negociáveis**:

1. Nenhum novo console ou grande refino de UI admin pode ser feito fora do Admin v1 dentro do escopo da S27.  
2. Qualquer exceção necessária (ex.: componente muito específico) deve ser registrada como dívida técnica `S27-DT-XXX` com justificativa clara.  
3. Gates e ORR da S27 precisam, obrigatoriamente, incluir pelo menos um cenário E2E que passe por **Fontes → Ingestão → Debunker**.  
4. O Guia de Consoles Admin v1.1 e os runbooks atualizados não são opcionais: são entregáveis de primeira classe da sprint, com owners definidos.

---

## 4. Conexão com os próximos capítulos

- O **Capítulo 2** traduzirá esses estados-alvo e critérios em **gates, métricas e scorecards** (G0–G6) específicos da S27.  
- O **Capítulo 3** mapeará a arquitetura e o filemap de `ui/admin`, `features/sources`, `features/ingestion`, `features/debunker` alinhados com esses estados.  
- O **Capítulo 4** quebrará os estados-alvo em waves e tasks (S27-T-XXX), com plano de evidências associado.  
- Os **Capítulos 5 e 6** usarão os critérios deste bloco para avaliar se a sprint realmente cumpriu sua missão e para registrar qualquer gap remanescente.

Este Bloco 3 é a régua de sucesso da S27: se ao final da sprint não conseguimos checar esses estados-alvo e critérios, é sinal de que algo saiu do trilho em escopo, execução ou foco.