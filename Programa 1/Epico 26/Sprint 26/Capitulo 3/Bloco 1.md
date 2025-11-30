# Inspectah — Sprint 26 (S26)
## Capítulo 3 — Bloco 3.1
### Visão de Arquitetura Lógica da S26

Este bloco responde, em termos de arquitetura, à pergunta: **“Onde exatamente a S26 encosta no sistema e o que ela reorganiza?”**

A resposta é: a S26 não cria um novo domínio de negócio; ela **reorganiza a camada de UI admin** e **reconstrói o Console de Fontes** em cima de um Design System Admin v1, conectando tudo de forma limpa ao backend de fontes e aos gates da sprint.

---

## 1. Papel da S26 na Arquitetura do Inspectah

Na visão macro do Inspectah, a S26 toca três zonas principais:

1. **Frontend Admin (UI Interna)**  
   - Introdução do **Design System Inspectah Admin v1** como camada transversal de UI para todos os consoles internos.
   - É a “biblioteca raiz” de componentes que, a partir de agora, deve ser usada para qualquer tela admin relevante.

2. **Console de Fontes (Frontend Feature Sources)**  
   - Reconstrução do console de gestão de fontes em cima do Design System Admin v1.
   - Foco em tornar os fluxos básicos de operação (CRUD + ON/OFF/arquivar) coesos, treináveis e auditáveis.

3. **APIs & Modelo de Dados de Fontes (Backend Domain Sources)**  
   - Uso (e, se necessário, ajuste fino) das rotas e modelos de fontes já existentes.
   - Criação de testes de API alinhados ao novo console, garantindo que a UI não “inventa” estados diferentes do backend.

A S26 é, portanto, uma sprint de **arquitetura aplicada**: ela mexe “onde o operador enxerga” (UI) e “onde a verdade das fontes vive” (API/modelo), amarrando os dois com contratos e gates rigorosos.

---

## 2. Componentes Lógicos Centrais da S26

### 2.1 Design System Inspectah Admin v1 (UI/Admin Core)

Camada de UI genérica para consoles internos. Suas responsabilidades:

- Definir **tokens de design** (cores, tipografia, espaçamentos, sombras, raios, estados de foco/erro/sucesso).  
- Fornecer **layout base** para telas admin (shell com sidebar, header, conteúdo).  
- Expor **componentes genéricos** reutilizáveis:
  - botões, inputs, selects, textareas, checkboxes, radios;  
  - tabelas e listas;  
  - badges/tags de status;  
  - modais de confirmação;  
  - toasts de feedback;  
  - banners de estado (erro global, vazio, aviso).

Propriedade fundamental: o design system **não conhece domínios** (não sabe o que é “fonte”, “caso”, “debunker”). Ele é uma camada **agnóstica de negócio**, especializada em UI admin.

### 2.2 Console de Fontes v2 (UI/Feature Sources)

Camada de UI específica para o domínio de fontes, construída **exclusivamente** com o Design System Admin v1.

Responsabilidades:

- Expor telas de:
  - **lista de fontes** (com filtros básicos e overview de estado);  
  - **criação/edição de fonte**, com formulários guiados e validações claras.
- Orquestrar as ações de:
  - criar nova fonte;  
  - alterar dados de uma fonte existente;  
  - ativar, desativar e arquivar fontes (quando aplicável).  
- Refletir de forma fiel o estado retornado pelas APIs (status, mensagens de erro, etc.), usando componentes de feedback do design system.

O Console de Fontes v2 é o **primeiro cliente real** do Design System Admin v1. Ele serve como prova de que o design system é utilizável em um fluxo admin concreto.

### 2.3 APIs e Modelo de Dados de Fontes (Backend/Domain)

Camada responsável pela verdade sobre fontes no sistema. Inclui:

- modelos de dados (por exemplo, `Source`, com campos como `id`, `nome`, `tipo`, `status`, `config`);  
- schemas de entrada/saída das rotas de API;  
- rotas REST (ou equivalentes) para listar, criar, editar e alterar o status de fontes.

Na S26, essa camada:

- é usada intensamente pelo Console de Fontes v2;  
- pode receber ajustes localizados (validações, endpoints específicos para ativar/desativar/arquivar);  
- é cercada por testes de API que garantem os contratos esperados pela UI.

---

## 3. Fluxo de Interação entre as Camadas

A arquitetura lógica da S26 pode ser vista como um fluxo em três passos:

1. **Operador ↔ Console de Fontes v2**  
   - O operador acessa o Console de Fontes v2, que está montado em cima do `AdminShell` e dos componentes do design system.  
   - As interações (cliques, preenchimento de formulários) acionam handlers do console.

2. **Console de Fontes v2 ↔ APIs de Fontes**  
   - O console chama funções de `sourcesApi` (ou equivalente), que fazem requests para as rotas de backend (listar, criar, atualizar, ativar/desativar/arquivar).  
   - As respostas (sucesso/erro) são traduzidas em estados de UI (tabelas atualizadas, toasts, banners, mensagens de campo) usando o design system.

3. **Gates de S26 ↔ Código & Evidências**  
   - G1 verifica a integridade estática do design system (tokens, componentes, testes).  
   - G2 verifica o funcionamento dos fluxos principais do Console de Fontes v2.  
   - G3 garante que o frontend como um todo segue saudável (lint, testes, build).  
   - G4 garante a coerência das APIs de fontes com o que o console espera.  
   - G5 e G6 amarram docs e evidências a esse arranjo.

Esse fluxo cria um **circuito fechado**: 

- operador → console → backend → console → operador,  
- com os gates atuando como “fusíveis” de arquitetura, evitando que implementações desviem do desenho.

---

## 4. Separação de Responsabilidades & Fronteiras Claras

Para evitar acoplamento indevido e garantir evolutividade, a S26 estabelece fronteiras claras:

- **Design System Admin v1**
  - conhece apenas conceitos de UI (layout, componentes, tokens);  
  - não conhece `Source`, `Case`, `Debunker`, `Truth`, etc.;  
  - pode ser usado por qualquer console admin futuro.

- **Console de Fontes v2**
  - conhece o domínio "fonte" e como o operador interage com ele;  
  - não implementa componentes genéricos do zero (sempre usa o design system);  
  - não implementa lógica de persistência; delega isso às APIs.

- **APIs/Modelo de Fontes**
  - conhecem a verdade sobre fontes (regras de negócio, estados válidos, invariantes);  
  - não conhecem detalhes de UI (layouts, componentes, nomes de componentes).

Essa separação é reforçada pelos scripts de gate, que falham se:

- componentes de console começam a reinventar UI fora do design system;  
- a UI começa a depender de estados de backend que não estão formalizados;  
- o backend passa a depender de conceitos de UI.

---

## 5. Conclusão do Bloco 3.1

O Bloco 3.1 coloca a S26 no mapa da arquitetura do Inspectah:

- **onde** ela encosta (frontend admin, console de fontes, APIs de fontes),
- **o que** ela introduz (Design System Admin v1 e Console de Fontes v2),
- **como** as camadas conversam (operador → console → backend, com feedback via UI),
- **quais fronteiras** precisam ser respeitadas.

A partir dessa visão lógica, os próximos blocos (3.2, 3.3 e 3.4) descem o nível para o **filemap concreto**, as dependências e os invariantes estruturais que os scripts de gates vão verificar.