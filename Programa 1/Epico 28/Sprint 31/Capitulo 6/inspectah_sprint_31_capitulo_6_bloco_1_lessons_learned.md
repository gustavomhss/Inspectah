# Inspectah — Sprint 31 (E28-S3)
## Capítulo 6 — Bloco 1: Lessons Learned

### 6.0 Papel deste bloco

O Capítulo 6 existe para garantir que a Sprint 31 não seja apenas “algo que passou pelo CI”, mas um **ponto de inflexão consciente** no projeto. Este Bloco 1 foca em capturar, de forma enxuta e utilizável, o que aprendemos em três frentes:

- **Técnica**: arquitetura, modelos, ingestão, Console, integração com Programas 2–3.
- **Processual**: forma de trabalhar, uso do Sprint Playbook, gates, ORR, runbooks.
- **Produto/estratégia**: custo, cobertura, verdade, escolha do domínio piloto.

Esses aprendizados são insumo direto para:

- o refinamento dos Programas 1–4;
- o recorte e foco das próximas sprints do Épico E28;
- e, principalmente, para evitar repetir erros caros em novos domínios e providers.

---

### 6.1 Lessons Learned — Técnicas

1. **Provider-first funciona como pilar de ingestão, mas só se tratado como sistema, não como script**  
   A combinação `client → normalizer → dedupe → ContentItem → métricas` se provou um esqueleto sólido. Quando implementado com contratos claros e testes minimamente decentes, o fluxo aguenta domínio real (notícias BR) sem se desmontar ao primeiro incidente. A principal lição é: provider-first precisa nascer com cara de subsistema de produção, não de ETL ad-hoc.

2. **`IngestionProfile` como unidade de controle foi o acerto central**  
   Concentrar provider, escopo, filtros, janelas, budget e status em um único objeto (`IngestionProfile`) deixou tudo mais legível: código, Console e operação. Fica óbvio que “ligar” ou “desligar” ingestão não é mexer em 10 flags soltas, é operar perfis. Próximos domínios devem reaproveitar essa unidade como padrão mental.

3. **Sem métricas por perfil, não existe conversa séria sobre custo e sanidade**  
   A S31 mostrou que métricas por perfil não são luxo. Contar chamadas, itens brutos, ContentItems, erros e budget_usage por perfil é o mínimo para qualquer discussão honesta sobre custo, cobertura e saúde. O modelo adotado (contadores agregados por run + agregados globais) funciona como baseline e deve ser aprofundado com painéis e alertas nas próximas sprints.

4. **Dedupe e normalização são intrinsecamente dependentes de domínio**  
   As heurísticas que funcionam bem para notícias BR não são automaticamente válidas para outros domínios (dados econômicos, social global, etc.). A S31 acertou ao isolar dedupe em serviço próprio e registrar quais chaves/estratégias usa, mas o aprendizado é claro: políticas de dedupe precisam ser declarativas e ajustáveis por domínio, não codificadas de forma rígida.

5. **Console v2 acoplado por API é o caminho certo**  
   A UI do Console de Fontes v2 falando apenas com APIs de Console (providers/perfis/runs) se mostrou uma escolha saudável. Isso evitou que lógica de ingestão “vazasse” para o frontend. A S31 valida esse padrão: o Console deve ser cliente de APIs estáveis, não guardião de regras de negócio escondidas em React.

6. **A trilha Provider → Perfil → ContentItem → Claim → FactBlock é viável na prática**  
   Um ganho concreto da S31 foi provar, com um caso piloto real, que o caminho completo até Programas 2–3 é possível sem gambiarras: os ContentItems com `provider_id` podem alimentar Claims e FactBlocks mantendo proveniência rastreável. Isso reduz o risco de termos uma ingestão “paralela” que não conversa com a camada de verdade.

---

### 6.2 Lessons Learned — Processuais

7. **Ancorar a sprint explicitamente nos Programas 1–3 evitou “subprojeto paralelo”**  
   Sempre que a discussão de S31 começava a derivar para um universo próprio (apenas ingestão, apenas Console), trazer de volta o mapa dos Programas 1–3 ajudou a cortar escopo decorativo. A lição é que grandes sprints de infraestrutura precisam ter um fio explícito até os programas de produto, ou viram playground técnico.

8. **O desenho de gates G0..G5 deu um mapa compartilhado de risco**  
   Ter gates separados para models/migrations (G1), provider ingestion (G2), Console & observabilidade (G3), legado & compatibilidade (G4) e P2–P3 (G5) simplificou a comunicação. Todo mundo sabia onde estavam os “pontos de estrangulamento” da sprint e que G2/G3/G5 eram os mais sensíveis.

9. **Capítulos 3 e 4 como espelho do código são essenciais para um ORR honesto**  
   A S31 confirmou que não dá para fazer ORR sério com documentação descolada do repositório. Sempre que o código andou e Cap.3/Cap.4 não foram atualizados, a confusão aumentou. O aprendizado é que atualizar esses capítulos durante a execução não é burocracia, é parte da própria engenharia.

10. **Runbooks dentro da sprint, não depois, elevam a qualidade do design**  
   Escrever e testar runbooks enquanto o código ainda está quente forçou o time a pensar em operação, custo, incidentes e rollback desde o início. As simulações de incidente (provider caindo, custo fugindo do controle) revelaram problemas de design que testes unitários não mostrariam.

11. **Delimitar fortemente o domínio piloto (notícias BR + 1 social) foi vital**  
   A S31 mostrou o valor de um piloto “opinado”. Em vez de tentar resolver ingestão global, o foco em um recorte politicamente carregado, ruidoso e sensível obrigou a tratar desde cedo temas como viés de cobertura, custo em contexto real e integração com camada de verdade. Isso gerou aprendizados muito mais ricos do que um piloto neutro geraria.

---

### 6.3 Lessons Learned — Produto, custo e estratégia

12. **Provider-first é um trade-off explícito entre complexidade de engenharia e complexidade de contratos**  
   A sprint deixou claro que trocamos o inferno de scrapers frágeis por um jogo mais claro: negociar e respeitar contratos, limites e TOS de providers. A engenharia fica mais limpa, mas a estratégia passa a exigir maturidade em custos, governança de fontes e compliance. Isso não é bug; é o verdadeiro jogo da S31 em diante.

13. **Console de Fontes v2 é ferramenta de produto, não só painel de operação**  
   O modo como perfis, métricas e status aparecem no Console sugerem uma futura funcionalidade de “curadoria de perfis” como produto. A sprint ensinou que operadores (e, no futuro, usuários avançados) podem enxergar o Console como cockpit de mix de fontes, não só como painel interno de SRE.

14. **Escolher notícias BR como primeira arena foi difícil… e correto**  
   O domínio BR de política/economia, com ruído, polarização e volume irregular, exigiu rigor e evitou que a arquitetura nascesse inocente. Essa dor inicial é um investimento: a mesma estrutura agora tem mais chance de aguentar domínios menos caóticos sem retrabalho pesado.

15. **Fechar o ciclo até Programas 2–3 demanda tempo realista**  
   A S31 confirmou que “puxar dados” é só metade do trabalho. Levar providers até casos e verdades exige trilha de proveniência, contratos claros de ContentItem e cuidado ao desenhar pipelines P2–P3. A lição aqui é de planejamento: sprints futuras que prometam “integrar ingestão com verdade” precisam reservar tempo real para essa parte, não tratá-la como pós-crédito.

---

### 6.4 Como usar estas lessons nos próximos passos

Este Bloco 1 não é um memorial; é uma lista de instruções para o futuro:

- Ao desenhar novos domínios ou providers, reutilizar o padrão `IngestionProfile + métricas por perfil + dedupe configurável` como fundação.
- Ao planejar sprints futuras de E28, sempre amarrar escopo a Programas 1–3 e prever tempo explícito para fechar o ciclo até a camada de verdade.
- Ao discutir custo, lembrar que provider-first exige conversar sobre **custo + cobertura + verdade** em conjunto, nunca isoladamente.

Os blocos seguintes do Capítulo 6 vão transformar essas lições em: dívidas técnicas nomeadas, ajustes de roadmap e um pacote de anti-gaps que impede o projeto de tropeçar nas mesmas pedras duas vezes.

