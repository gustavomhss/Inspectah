const agents = [
  { id: 'interpreter_a', name: 'Interpreter A', layer: 'Interpretation', domain: 'general', status: 'ATIVO' },
  { id: 'debunker_v0', name: 'Debunker v0', layer: 'Debunk', domain: 'politics', status: 'ATIVO' },
];

export function AgentStudioPage() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-4">Agent Studio</h1>
      <p className="mb-4 text-gray-700">Versões e instruções principais dos agentes de camada.</p>
      <table className="w-full text-left border">
        <thead>
          <tr className="bg-gray-100">
            <th className="p-2">Agente</th>
            <th className="p-2">Camada</th>
            <th className="p-2">Domínio</th>
            <th className="p-2">Status</th>
          </tr>
        </thead>
        <tbody>
          {agents.map((agent) => (
            <tr key={agent.id} className="border-t">
              <td className="p-2">{agent.name}</td>
              <td className="p-2">{agent.layer}</td>
              <td className="p-2">{agent.domain}</td>
              <td className="p-2">{agent.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="mt-6">
        <h2 className="text-xl font-semibold mb-2">KB e Guardrails</h2>
        <p className="text-gray-700">Anexe e revise KBs compartilhadas no backend. Guardrails globais aplicados.</p>
      </div>
    </div>
  );
}

export default AgentStudioPage;
