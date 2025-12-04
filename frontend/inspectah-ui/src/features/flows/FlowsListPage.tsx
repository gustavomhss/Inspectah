import { useNavigate } from 'react-router-dom';
import { AdminContent, AdminHeader, Banner, Button, Input, Select, Table } from '@/ui/admin';
import { FlowStateBadge } from './FlowStateBadge';
import { useFlowsList } from './hooks';
import type { Flow } from './types';

export function FlowsListPage() {
  const navigate = useNavigate();
  const { items, loading, error, reload } = useFlowsList();
  const flows = items as Flow[];

  return (
    <div className="flex flex-col gap-4">
      <AdminHeader
        title="Fluxos"
        subtitle="Console de Fluxos — listar e operar fluxos."
        actions={
          <div className="flex gap-2">
            <Button variant="secondary" onClick={() => reload()} disabled={loading}>
              {loading ? 'Atualizando...' : 'Atualizar'}
            </Button>
            <Button onClick={() => navigate('/flows/new')}>Criar fluxo</Button>
          </div>
        }
      />

      {error && <Banner tone="danger" title="Erro ao carregar fluxos" description={error} />}

      <AdminContent>
        <div className="mb-3 flex gap-2">
          <Input placeholder="Buscar por nome ou tipo" onChange={() => undefined} />
          <Select aria-label="Estado">
            <option value="">Estado</option>
            <option value="draft">Rascunho</option>
            <option value="em_teste">Em teste</option>
            <option value="ativo">Ativo</option>
            <option value="pausado">Pausado</option>
            <option value="deprecado">Deprecado</option>
          </Select>
        </div>
        <Table
          headers={['Nome', 'Tipo', 'Estado', 'Template']}
          isEmpty={flows.length === 0}
          emptyState={<span className="text-sm text-slate-500 py-4">Nenhum fluxo cadastrado.</span>}
        >
          {flows.map((flow) => (
            <tr key={flow.id} className="cursor-pointer hover:bg-slate-50" onClick={() => navigate(`/flows/${flow.id}`)}>
              <td className="px-4 py-3">{flow.nome}</td>
              <td className="text-sm text-slate-600 px-4 py-3">{flow.tipo_entrada}</td>
              <td className="px-4 py-3">
                <FlowStateBadge state={flow.estado} />
              </td>
              <td className="text-sm text-slate-600 px-4 py-3">{flow.template_origem_id || '-'}</td>
            </tr>
          ))}
        </Table>
      </AdminContent>
    </div>
  );
}

export default FlowsListPage;
