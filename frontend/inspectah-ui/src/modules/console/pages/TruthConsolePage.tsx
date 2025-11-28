import { useEffect, useState } from 'react';

type TruthRecord = {
  id: string;
  slug: string;
  domain: string;
  current_state: string;
};

export function TruthConsolePage() {
  const [records, setRecords] = useState<TruthRecord[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/console/truth')
      .then((res) => res.json())
      .then(setRecords)
      .catch(() => setError('Não foi possível carregar TruthRecords agora.'));
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-4">Truth Console</h1>
      {error && <div className="text-red-600 mb-2">{error}</div>}
      <table className="w-full text-left border">
        <thead>
          <tr className="bg-gray-100">
            <th className="p-2">Slug</th>
            <th className="p-2">Domínio</th>
            <th className="p-2">Estado</th>
          </tr>
        </thead>
        <tbody>
          {records.map((r) => (
            <tr key={r.id} className="border-t">
              <td className="p-2">{r.slug}</td>
              <td className="p-2">{r.domain}</td>
              <td className="p-2">{r.current_state}</td>
            </tr>
          ))}
          {records.length === 0 && !error && (
            <tr>
              <td className="p-2" colSpan={3}>
                Nenhum registro ainda. Execute pipelines ou importe golden sets.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

export default TruthConsolePage;
