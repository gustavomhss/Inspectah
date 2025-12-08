import PageContainer from '../../../shared/layout/PageContainer';
import PageHeader from '../../../shared/layout/PageHeader';

function HowToPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="HowTo — Admin completo"
        subtitle="Manual simples, sem jargão. Siga na ordem para não se perder."
      />

      <PageContainer>
        <h3 className="text-lg font-semibold text-white">0) Ligar tudo (serviços, backend, frontend, Prom/Alerts)</h3>
        <p className="mt-2 text-sm text-slate-200">Cole estes comandos no terminal (já dentro do repo):</p>
        <pre className="mt-3 rounded-lg bg-slate-800 p-3 text-xs text-slate-100">
{`source .venv/bin/activate
bin/dev_down.sh || true
bin/dev_up.sh
# subir Prometheus/Alertmanager (uma vez; se já estiver rodando, ignore erros de porta)
nohup prometheus --config.file=configs/prometheus.dev.yml --web.listen-address=:9090 >/tmp/prometheus_sf3.log 2>&1 &
nohup /tmp/alertmanager-0.27.0.darwin-amd64/alertmanager --config.file=/tmp/alertmanager_sf2.yml --web.listen-address=:9093 --cluster.listen-address=127.0.0.1:0 >/tmp/alertmanager_sf3.log 2>&1 &
# checar prontidão
curl -s http://localhost:9090/-/ready
curl -s http://localhost:9093/-/ready
# gerar token JWT (troque ROLE/ACTOR se precisar)
ROLE=admin ACTOR=admin-user AUD=inspectah-api ISS=inspectah-idp .venv/bin/python bin/sf3_jwt_gen.py
# frontend
cd frontend/inspectah-ui
npm install
npm run dev`}
        </pre>
        <ul className="mt-3 list-disc space-y-2 pl-5 text-sm text-slate-200">
          <li>Token: copie a saída do gerador e ponha no ModHeader como <strong>Authorization: Bearer &lt;token&gt;</strong>.</li>
          <li>Token bom: issuer <code>inspectah-idp</code>, audience <code>inspectah-api</code>, expira em 15 min.</li>
          <li>Se der 401/403, gere novo token e confira se o header está com o prefixo <strong>Bearer</strong>.</li>
        </ul>
      </PageContainer>

      <PageContainer>
        <h3 className="text-lg font-semibold text-white">1) Visão Geral (Admin)</h3>
        <p className="mt-2 text-sm text-slate-200">
          Dashboard inicial com cartões de saúde. Use para checar se fontes e casos estão ok.
        </p>
        <ol className="mt-2 list-decimal space-y-2 pl-5 text-sm text-slate-200">
          <li>Abra <strong>Visão Geral</strong> no topo.</li>
          <li>Veja cartões verdes/amarelos/vermelhos. Se algo estiver vermelho, clique na seção correspondente (Fontes ou Casos).</li>
          <li>Se o carregamento falhar, confira o token ou se o backend está de pé.</li>
        </ol>
      </PageContainer>

      <PageContainer>
        <h3 className="text-lg font-semibold text-white">2) Fontes</h3>
        <p className="mt-2 text-sm text-slate-200">
          Lista, cria e edita fontes de ingestão.
        </p>
        <ol className="mt-2 list-decimal space-y-2 pl-5 text-sm text-slate-200">
          <li><strong>Fontes</strong>: tabela com estado, tipo e saúde. Use filtros para achar rapidamente.</li>
          <li>Clique em uma fonte para abrir o <strong>detalhe</strong>: histórico de healthcheck, último erro, botão para rodar ingestão.</li>
          <li><strong>Novo</strong>: botão “Nova fonte” leva ao formulário para cadastrar nome, tipo e URL.</li>
          <li><strong>Perfis de Fonte</strong>: coleções de fontes pré-configuradas. Abra, selecione um perfil e rode “run now”.</li>
        </ol>
      </PageContainer>

      <PageContainer>
        <h3 className="text-lg font-semibold text-white">3) Ingestão</h3>
        <p className="mt-2 text-sm text-slate-200">
          Visualiza execuções, estados (ok, erro, vazio) e permite reprocessar.
        </p>
        <ol className="mt-2 list-decimal space-y-2 pl-5 text-sm text-slate-200">
          <li><strong>Ingestão</strong>: veja runs recentes com status e duração.</li>
          <li>Para um run com erro, clique para ver o motivo e tente reprocessar.</li>
          <li>Use filtros (tipo/status) para isolar problemas (ex.: fontes paradas).</li>
        </ol>
      </PageContainer>

      <PageContainer>
        <h3 className="text-lg font-semibold text-white">4) Agentes</h3>
        <p className="mt-2 text-sm text-slate-200">
          Cadastre agentes, comitês e políticas de modelo.
        </p>
        <ol className="mt-2 list-decimal space-y-2 pl-5 text-sm text-slate-200">
          <li><strong>Agentes</strong>: lista, pesquisa e cria. Clique para editar papel, camada e modelos.</li>
          <li><strong>Comitês</strong>: dentro do agente, crie grupos de agentes para votação/consenso.</li>
          <li><strong>Política de modelos</strong>: defina quais modelos cada papel pode usar. Salve e verifique se não há erro 401/403.</li>
        </ol>
      </PageContainer>

      <PageContainer>
        <h3 className="text-lg font-semibold text-white">5) Fluxos e Fluxos de Agentes</h3>
        <p className="mt-2 text-sm text-slate-200">
          Controle dois níveis: o fluxo operacional (dados/casos) e o fluxo interno de agentes.
        </p>
        <ol className="mt-2 list-decimal space-y-2 pl-5 text-sm text-slate-200">
          <li><strong>Fluxos</strong>: lista de fluxos (ex.: news_v2). Abra para ver status, catálogo e histórico.</li>
          <li><strong>Fluxos de agentes</strong>: construa o pipeline de agentes (camadas, ordem, validação). Arraste/adicione agentes e salve.</li>
          <li>Erros comuns: 401/403 (token faltando ou role errada). Se vir, renove o token.</li>
        </ol>
      </PageContainer>

      <PageContainer>
        <h3 className="text-lg font-semibold text-white">6) Casos, Timeline e Raio-X</h3>
        <p className="mt-2 text-sm text-slate-200">
          Use para acompanhar casos/temas e ver eventos detalhados.
        </p>
        <ol className="mt-2 list-decimal space-y-2 pl-5 text-sm text-slate-200">
          <li><strong>Casos/Temas</strong>: lista com status. Clique no caso.</li>
          <li><strong>Timeline</strong>: eventos ordenados. Filtros no topo. Se vazio, significa que não há eventos novos.</li>
          <li><strong>Raio-X</strong>: visão 360° (evidências, debunk, âncoras). Navegue pelas abas internas.</li>
        </ol>
      </PageContainer>

      <PageContainer>
        <h3 className="text-lg font-semibold text-white">7) Consoles (Truth, Incidentes, Estúdio)</h3>
        <ol className="mt-2 list-decimal space-y-2 pl-5 text-sm text-slate-200">
          <li><strong>Console Truth</strong>: aprovar/reprovar promoções. Exige token com role truth_admin/truth_reviewer.</li>
          <li><strong>Console de Incidentes</strong>: monitora incidentes operacionais (status, causa, ação). Use para registrar resolução.</li>
          <li><strong>Estúdio de Agentes</strong>: playground para testar prompts/configuração de agentes antes de publicar.</li>
        </ol>
      </PageContainer>

      <PageContainer>
        <h3 className="text-lg font-semibold text-white">8) Ops Cockpit e Observabilidade</h3>
        <ol className="mt-2 list-decimal space-y-2 pl-5 text-sm text-slate-200">
          <li><strong>Ops Cockpit</strong>: painel de SLO/alertas. Se algo quebrar na UI (cards vazios), verifique /metrics e Prometheus.</li>
          <li><strong>SF3 Obs Overview</strong>: painel exportado; veja gráficos de auth, ingest, truth e UI. Se gráfico vazio, falta métrica.</li>
        </ol>
      </PageContainer>

      <PageContainer>
        <h3 className="text-lg font-semibold text-white">9) Dicas rápidas de socorro</h3>
        <ul className="mt-3 list-disc space-y-2 pl-5 text-sm text-slate-200">
          <li>Erro 401: token ausente/expirado. Pegue um novo e reinsira no header Authorization.</li>
          <li>Erro 403: token sem a role certa (ex.: admin vs truth_admin). Gere token com a role correta.</li>
          <li>Lista vazia: pode ser filtro ativo ou fonte/caso inexistente. Limpe filtros.</li>
          <li>UI travada: recarregue a página depois de subir backend com <code>bin/dev_up.sh</code>.</li>
          <li>Dúvida: volte para esta aba e siga o passo a passo do módulo desejado.</li>
        </ul>
      </PageContainer>
    </div>
  );
}

export default HowToPage;
