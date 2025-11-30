import { AdminContent, Banner } from '@/ui/admin';

export function SourcesNotFoundPage() {
  return (
    <AdminContent>
      <Banner tone="danger" title="Página de fontes não encontrada" description="A rota acessada não existe. Use o menu lateral para navegar." />
    </AdminContent>
  );
}

export default SourcesNotFoundPage;
