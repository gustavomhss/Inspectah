import { AdminContent, AdminHeader, Banner } from '@/ui/admin';

export function SourcesDebunkerPage() {
  return (
    <div className="flex flex-col gap-6">
      <AdminHeader
        title="Debunker & Confiabilidade"
        subtitle="Acompanhe sinais de confiança das fontes, contestação e flags de suspeita."
      />
      <AdminContent>
        <Banner
          tone="warning"
          title="Estado atual"
          description="Esta área está em modo esqueleto: use-a para visualizar flags de confiança e contestação assim que forem disponibilizadas pelo backend."
        />
        <div className="mt-4 space-y-3 text-sm text-slate-200">
          <p>• Flags típicas: trust_severity, conflict_flags, has_open_contestation, evidências relacionadas.</p>
          <p>• Quando houver dados, cada fonte exibirá seu status de risco e histórico de contestação.</p>
          <p>• Se nenhuma contestação estiver registrada, mostre uma mensagem clara em vez de JSON ou erro cru.</p>
        </div>
      </AdminContent>
    </div>
  );
}

export default SourcesDebunkerPage;
