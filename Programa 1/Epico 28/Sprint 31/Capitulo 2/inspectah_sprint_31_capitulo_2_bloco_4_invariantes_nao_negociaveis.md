# Inspectah — Sprint 31 (E28-S3)
## Capítulo 2 — Bloco 4: Invariantes & Não-Negociáveis

### 2.23 Papel deste bloco

Estados-alvo (Bloco 1) dizem o que queremos alcançar. Gates e métricas (Blocos 2 e 3) dizem como vamos medir. **Este bloco diz o que não pode quebrar de jeito nenhum.**

Invariantes são regras estruturais que, se violadas, anulam a tese da Sprint 31, mesmo que todos os testes superficiais pareçam verdes. Elas viram checagens explícitas em gates e ORR.

---

### 2.24 Invariante 1 — Nenhum ContentItem de provider sem proveniência completa

**Descrição**  
Todo ContentItem produzido via providers deve ter proveniência explicitamente registrada, permitindo reconstruir o caminho de entrada sem suposição.

**Conduta exigida**
- Para cada ContentItem criado a partir de um provider:
  - `provider_id` é obrigatório;
  - `profile_id` (perfil de ingestão) é obrigatório;
  - `source/domain` deve estar preenchido, quando aplicável (veículo concreto);
  - identificador externo e timestamps consistentes (created_at, published_at, fetched_at) precisam estar presentes.

**Por que é não-negociável**
- Sem isso, não existe trilha confiável Provider → Perfil → ContentItem → Claim → FactBlock.
- Programas 2–4 perdem transparência de origem e o produto perde credibilidade.

**Quem faz cumprir**
- G1 (modelos & migrations) garante que os campos existem e são obrigatórios na criação de ContentItem de provider.
- G2 (ingestão via providers) verifica que ContentItems reais do piloto nunca chegam sem esses campos.

Se, em qualquer amostra, ContentItems de provider surgirem sem proveniência completa, a sprint não é GO.

---

### 2.25 Invariante 2 — Provider-first não pode quebrar ingestão legada crítica

**Descrição**  
A entrada de providers não pode destruir ou degradar fluxos de ingestão legados marcados como críticos (dados oficiais, fontes que ainda não têm equivalente em provider, etc.).

**Conduta exigida**
- Migrations precisam ser **backwards-compatíveis** com dados pré-existentes.
- Jobs de ingestão legados críticos devem continuar rodando com sucesso após as mudanças da S31.
- Qualquer fonte legada que vá ser desativada precisa ser explicitamente marcada como tal em documentação e migração, nunca “sumir por acidente”.

**Por que é não-negociável**
- O Inspectah ainda não vive 100% em providers; matar fluxos essenciais por acidente cria buracos de cobertura invisíveis.
- Programas 2–4 dependem de continuidade histórica, não de resets arbitrários.

**Quem faz cumprir**
- G1 (models & migrations) valida que migrations rodam em bases com dados reais sem corromper.
- G4 (legado & compatibilidade) roda fluxos antigos e verifica que continuam íntegros.

Qualquer FAIL em fluxos legados críticos derruba a sprint para NO-GO até correção.

---

### 2.26 Invariante 3 — Nenhum perfil-piloto roda cegamente em relação a budget

**Descrição**  
Perfis-piloto não podem operar sem limite e visibilidade mínima de custo. Rodar ingestão agressiva sem budget configurado é proibido.

**Conduta exigida**
- Todo perfil-piloto deve ter:
  - `budget_limit_calls` definido (mesmo que alto, mas não infinito);
  - registro de `provider_calls_total` e `budget_usage_ratio`.
- Não é permitido executar perfis-piloto em ambiente de longa duração sem que essas métricas sejam visíveis em painéis/scorecards.

**Por que é não-negociável**
- Sem trilho de budget, qualquer experimento com providers vira potencial bomba de custo.
- O modelo de negócio do Inspectah depende de enxergar custo por domínio/região/tema desde os pilotos.

**Quem faz cumprir**
- G3 (Console & observabilidade) valida a existência de métricas por perfil e que `budget_limit_calls` está configurado.
- ORR revisa `S31_G3_observabilidade.json` e barra GO se houver perfis ativos sem budget e sem métrica.

Se algum perfil-piloto que roda de forma recorrente estiver sem budget e sem visibilidade, a sprint não passa.

---

### 2.27 Invariante 4 — Domínio piloto precisa ter trilha de origem auditável fim a fim

**Descrição**  
O domínio piloto (ex.: política/economia BR) precisa permitir reconstruir, para pelo menos um caso de exemplo, a cadeia completa de origem de um fato.

**Conduta exigida**
- Para um caso piloto escolhido:
  - é possível listar quais perfis de ingestão o alimentaram;
  - é possível recuperar os ContentItems usados como evidência;
  - é possível ver Claims derivados desses ContentItems;
  - é possível inspecionar FactBlocks/EvidenceBlocks em Truth-DB ligados a esses Claims.

**Forma canônica**  
Conseguir materializar algo equivalente a:

> Provider → Perfil → ContentItem → Claim → FactBlock → (eventual Contestação)

em evidência estruturada (arquivo JSON, por exemplo).

**Por que é não-negociável**
- Sem uma prova concreta de trilha de origem, provider-first é apenas uma promessa.
- O valor central do Inspectah está em explicar **de onde vem** cada fato, não apenas em agregá-los.

**Quem faz cumprir**
- G5 (integração P2–P3) precisa produzir evidência estruturada com essa trilha para o caso piloto.
- ORR verifica se essa trilha é clara, reproduzível e está à altura do que Programas 3–4 vão expor ao usuário final.

Se não for possível construir essa trilha de forma direta, a S31 não pode ser marcada como provider-first funcional.

---

### 2.28 Invariante 5 — Nada alimenta ClaimGraph “por fora” dos Perfis de Ingestão

**Descrição**  
No domínio piloto, qualquer fluxo que alimente o ClaimGraph precisa ser representado, explicitamente, por pelo menos um Perfil de Ingestão visível no Console. Não pode haver caminhos ocultos.

**Conduta exigida**
- Para o domínio piloto, todos os feeds que chegam ao ClaimGraph devem:
  - estar ligados a um perfil registrado (perfil news ou social);
  - aparecer na UI do Console (lista de perfis);
  - constar na documentação da sprint como parte da dieta de ingestão do domínio.

**Por que é não-negociável**
- Caminhos ocultos de ingestão tornam impossível explicar ao usuário final por que certos conteúdos estão no ClaimGraph.
- Sem essa disciplina, experimentos e ajustes de ingestão deixam de ser rastreáveis e reprodutíveis.

**Quem faz cumprir**
- G2 (ingestão via providers) e G3 (Console) garantem que perfis são a porta de entrada oficial.
- G5 mapeia perfis usados pelo ClaimGraph no domínio piloto.
- ORR confere se não há “atalhos escondidos” alimentando Programas 2–3.

Se houver conteúdo chegando ao ClaimGraph no domínio piloto sem passar por perfis conhecidos, é bug conceitual, não detalhe.

---

### 2.29 Invariante 6 — Ingestão provider-first precisa ser reproduzível

**Descrição**  
Dado um perfil-piloto e uma janela de tempo, a ingestão precisa ser reexecutável com resultados consistentes (descontando variações naturais de provider).

**Conduta exigida**
- Jobs de ingestão devem aceitar parâmetros de janela temporal (from/to) para facilitar replays controlados.
- Logs e evidências de run devem registrar parâmetros usados (perfil, janela, filtros, paginação).
- Deve ser possível repetir um run de teste num intervalo curto e explicar divergências (novos itens, itens expirados, etc.).

**Por que é não-negociável**
- Sem reprodutibilidade, investigações de bugs, auditoria e experimentação ficam inviáveis.
- Programas 2–3 dependem de poder revisitar ingestões passadas para entender como um caso foi formado.

**Quem faz cumprir**
- G2 (ingestão) registra parâmetros e permite runs controlados.
- ORR verifica pelo menos um replay de ingestão em ambiente de teste, com explicação clara das diferenças.

Se ingestão provider-first virar “caixa-preta não reexecutável”, a sprint falha como fundação de produto.

---

### 2.30 Invariante 7 — Documentação e realidade não podem divergir grossamente

**Descrição**  
Os documentos da Sprint 31 (Cap.1, Cap.2, Cap.3 e doc de execução) precisam descrever **o que realmente está em produção/staging**, não uma versão de fantasia.

**Conduta exigida**
- Sempre que um perfil, provider ou fluxo mudar de forma relevante, os docs dessa sprint precisam ser atualizados antes de marcar a sprint como encerrada.
- O plano de coexistência legado↔provider e o mapeamento do domínio piloto devem refletir a implementação final.

**Por que é não-negociável**
- Inspectah depende de documentação viva e fiel para escalar e para ser auditável.
- Divergência grande entre docs e realidade destrói confiança em gates, scorecards e ORR.

**Quem faz cumprir**
- G0 (scope & baseline) garante que docs existem;
- ORR (S31-ORR) faz uma amostragem direta: pega docs e checa contra o que o sistema faz de verdade.

Se o Conselho/Spec Office encontrar inconsistências graves entre docs e comportamento real, o status da sprint deve ser, no mínimo, rebaixado para GO_WITH_WARNINGS, e, em casos extremos, NO-GO.

---

### 2.31 Fechamento do Bloco 4

Os invariantes deste bloco são a armadura da Sprint 31. Eles garantem que:

- provider-first não é só “ligar um provider e rezar”, mas sim construir uma ingestão rastreável, compatível e economicamente controlável;
- o domínio piloto não é teatro, e sim um recorte real onde conseguimos explicar cada passo da cadeia de verdade;
- nada importante entra escondido ou sem trilha, e nada crítico é destruído em nome da novidade.

Com essas regras não-negociáveis, Capítulo 2 fecha o contrato da S31: se os estados-alvo forem alcançados, os gates passarem, os scorecards forem saudáveis **e** nenhum invariante for violado, o Inspectah pode dizer, sem vergonha, que se tornou provider-first de verdade para o seu primeiro domínio de interesse.