import { useEffect, useState } from 'react';

type Incident = {
  id: string;
  title: string;
  summary: string;
  severity: string;
  domain: string;
  status: string;
};

export function IncidentConsolePage() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/console/incidents')
      .then((res) => res.json())
      .then(setIncidents)
      .catch(() => setError('Não foi possível carregar incidentes.'));
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-4">Incident Console</h1>
      {error && <div className="text-red-600 mb-2">{error}</div>}
      <ul className="space-y-3">
        {incidents.map((inc) => (
          <li key={inc.id} className="border rounded p-3">
            <div className="font-semibold">{inc.title}</div>
            <div className="text-gray-700">{inc.summary}</div>
            <div className="text-sm text-gray-500">
              Domínio: {inc.domain} · Severidade: {inc.severity} · Status: {inc.status}
            </div>
          </li>
        ))}
        {incidents.length === 0 && !error && <li>Nenhum incidente registrado.</li>}
      </ul>
    </div>
  );
}

export default IncidentConsolePage;
