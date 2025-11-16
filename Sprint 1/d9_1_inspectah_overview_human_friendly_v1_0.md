# D9.1 — Inspectah Overview Human-Friendly (v1.0)
> Status: CONGELADO (LOCKED) — Inspectah D9 v1.1 — não editar fora de novas sprints ou PATCH_D9 explícito.

## O que é o Inspectah?
O Inspectah é o **cérebro de evidências** do ecossistema CE/MBP. Ele junta, organiza e explica dados vindos de feeds RSS, APIs públicas, boletins oficiais, relatórios HTML simples e outras fontes confiáveis. Em vez de caçar prints antigos ou repetir buscas manuais, o time abre o Inspectah e vê **de onde veio cada informação, quando foi coletada e como foi tratada**.

## Por que ele existe?
1. **Confiar nas decisões**: toda resolução do MBP, limite de risco ou alerta precisa estar ancorado em evidências verificáveis.
2. **Evitar trabalho repetitivo**: Operators deixam de fazer scraping manual e passam a configurar pipelines declarativas.
3. **Explicar o histórico**: quando alguém pergunta "o que mudou desde ontem?", o Inspectah mostra a linha do tempo completa.
4. **Plugar novos dados com segurança**: fontes novas entram com checklist LGPD/ToS e transforms padronizados.

## Como o Inspectah funciona (versão de bolso)
1. **Cadastro da Fonte** – alguém configura a origem dos dados (URL, periodicidade, autenticação opcional).
2. **Field Designer** – é a oficina onde dizemos como os dados brutos viram campos estruturados (números, datas, enums etc.).
3. **Pipelines** – o Inspectah coleta, normaliza, aplica regras e salva tudo com histórico e hash.
4. **Evidence Vault** – guarda os manifests (quem coletou, quando, hash) e snapshots opcionais para auditoria.
5. **Explore & Integrações** – o time consulta via API, exporta CSV/JSON, recebe webhooks ou vê diffs para tomar decisões.

## Em que situações usar?
- **Monitorar preços, índices, indicadores locais** sem depender de planilhas frágeis.
- **Documentar as evidências** por trás de uma resolução sensível ou investigação do MBP.
- **Comparar versões** de editais, termos ou regulamentos que mudam com frequência.
- **Compartilhar dados confiáveis** com squads parceiros, mantendo rastro do que pode ou não ser usado.

## O que entra no v0?
- Ingestão batch baseada em fontes estáveis (RSS, JSON/CSV via HTTP, APIs REST simples).
- Biblioteca inicial de transforms + computed fields determinísticos.
- Evidence Vault com manifest obrigatório e snapshot opcional.
- Explore API com filtros por fonte, tags, campos e intervalo de data, além de export CSV/JSON.
- Webhooks básicos (item criado/atualizado, erro de fonte) e checklist LGPD/ToS por fonte.

## O que **não** entra agora?
- Integrações profundas com protocolos UMA/Reality ou contratos on-chain.
- Scraping agressivo de sites que proíbem automação.
- Interface riquíssima de dashboards; focamos em APIs, exports e vistas textuais.
- Automação complexa de alertas (fica para v1, embora diffs simples já possam ser calculados).

## Valores que guiam o Inspectah
- **Transparência total**: toda informação tem origem, hash e histórico.
- **Modularidade**: Field Designer, Data Model e APIs são blocos reutilizáveis em outras sprints.
- **Compliance by design**: limites de LGPD/ToS são tratados como cidadãos de primeira classe.
- **Pronto para Codex**: o superprompt (D9.7) pega este overview + blueprint e gera código consistente.

## Como explicar em 30 segundos
> "O Inspectah é o painel de evidências do MBP. Ele coleta dados de várias fontes, transforma com regras declarativas, guarda tudo com histórico auditável e entrega APIs/exports para quem precisa tomar decisões ou auditar o que aconteceu."

Com este overview, qualquer pessoa nova entende por que o Inspectah existe, o que entra no v0 e como ele conversa com o restante do ecossistema CE/MBP.
