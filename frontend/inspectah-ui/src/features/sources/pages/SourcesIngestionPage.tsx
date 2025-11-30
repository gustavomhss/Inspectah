import { AdminContent, AdminHeader, Banner, Button } from '@/ui/admin';

export function SourcesIngestionPage() {
  return (
    <div className="flex flex-col gap-6">
      <AdminHeader
        title="Ingestão de Fontes"
        subtitle="Painel de saúde das execuções de ingestão. Veja últimas execuções, status e acione ingestão manual quando disponível."
      />
      <AdminContent>
        <Banner
          tone="info"
          title="Status agregado"
          description="Visualize aqui o status recente das ingestões por fonte. Integração com métricas detalhadas pode ser adicionada nas próximas sprints."
        />
        <div className="mt-4 space-y-3 text-sm text-slate-200">
          <p>
            • Consulte rapidamente quais fontes estão saudáveis, degradadas ou falhando na última janela de tempo.
          </p>
          <p>
            • Quando suportado pelo backend, use o botão abaixo para disparar uma ingestão manual de uma fonte específica e ver o resultado.
          </p>
          <Button variant="secondary" disabled>
            Acionar ingestão manual (em breve)
          </Button>
        </div>
      </AdminContent>
    </div>
  );
}

export default SourcesIngestionPage;
