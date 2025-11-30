import { Outlet } from 'react-router-dom';
import { AdminHeader, AdminShell, AdminSidebar, Banner } from '@/ui/admin';

const navItems = [
  { label: 'Fontes', to: '/admin/sources' },
  { label: 'Ingestão', to: '/admin/sources/ingestao' },
  { label: 'Debunker', to: '/admin/sources/debunker' },
];

export function SourcesLayout() {
  const header = (
    <AdminHeader
      title="Console de Fontes"
      subtitle="Gerencie cadastro, ingestão e confiabilidade das fontes usando o design system do Inspectah."
    />
  );

  return (
    <AdminShell sidebar={<AdminSidebar title="Fontes" navItems={navItems} />} header={header}>
      <div className="flex flex-col gap-6">
        <Banner
          tone="info"
          title="Navegação"
          description="Use as abas ao lado para alternar entre cadastro, saúde de ingestão e sinais de confiança das fontes."
        />
        <Outlet />
      </div>
    </AdminShell>
  );
}

export default SourcesLayout;
