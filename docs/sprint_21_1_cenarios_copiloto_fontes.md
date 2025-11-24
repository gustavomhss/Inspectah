# Sprint 21.1 — Cenários do Copiloto de Fontes

## Estrutura de cenário
- Frase inicial do admin.
- Passos esperados do Copiloto (mensagens + ações).
- Estado final esperado do formulário (campos sugeridos/preenchidos).

## Cenários

1) Notícias gerais (globo.com)
- Frase: "quero cadastrar globo.com como fonte de notícias gerais do Brasil"
- Copiloto: sugere `type=news_rss`, `category=official`, `themes=["política","economia"]`, `info_types=["news"]`, `endpoint=https://g1.globo.com/rss`, gera slug/nome e marca campos como sugeridos.
- Form final: campos acima preenchidos/sugeridos, admin revisa antes de salvar.

2) Esportes
- Frase: "cadastrar api da liga nacional de esportes"
- Copiloto: sugere `type=sports_api`, `themes=["esportes"]`, `info_types=["sports","placares"]`, pede endpoint/token, sugere nome/slug.
- Form final: type e temas marcados como sugeridos; endpoint em branco ou sugerido se houver no diálogo.

3) Clima
- Frase: "cadastrar fonte de alertas de clima do inmet"
- Copiloto: sugere `type=weather_api`, `themes=["clima","alertas"]`, `info_types=["weather","alertas_clima"]`, pede URL e frequência.
- Form final: type/themes/info_types sugeridos; endpoint aguardando confirmação ou sugerido se informado.

4) Fofoca/celebridades
- Frase: "quero monitorar um blog de fofocas famoso"
- Copiloto: sugere `type=news_rss`, `category=community`, `themes=["celebridades"]`, `info_types=["news"]`, solicita feed URL.
- Form final: type/themes marcados; endpoint aguardando input do admin.

5) Fonte científica/política especializada
- Frase: "cadastrar dataset científico de dados abertos sobre eleições"
- Copiloto: sugere `type=sports_api` ou `news_rss` conforme contexto; temas possíveis `["ciencia","politica"]`; info_types conforme tipo; solicita URL/base de dados e formato.
- Form final: type/themes/info_types sugeridos; endpoint/descrição aguardando revisão.
