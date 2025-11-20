import React, { FormEvent, useEffect, useState } from "react";
import { CasePage } from "./CasePage";

export interface CaseSummary {
  id_caso: string;
  dominio: string;
  titulo: string;
  descricao: string;
  status: string;
  updated_at?: string;
}

interface CasesResponse {
  query: string;
  results: CaseSummary[];
  total: number;
}

async function fetchJSON<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, init);
  if (!response.ok) {
    throw new Error(`Falha ao chamar ${url}: ${response.status}`);
  }
  return (await response.json()) as T;
}

export function SearchPage(): JSX.Element {
  const [query, setQuery] = useState("obra");
  const [cases, setCases] = useState<CaseSummary[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedCase, setSelectedCase] = useState<string | null>(null);

  async function runSearch(customQuery?: string) {
    try {
      setLoading(true);
      setError(null);
      const payload = await fetchJSON<CasesResponse>(`/explorer/cases?query=${encodeURIComponent(customQuery ?? query)}`);
      setCases(payload.results);
      setTotal(payload.total);
      if (!payload.results.find((entry) => entry.id_caso === selectedCase)) {
        setSelectedCase(null);
      }
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    runSearch(query).catch(() => null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    runSearch(query).catch(() => null);
  }

  return (
    <div className="s12-explorer">
      <section className="search-panel">
        <h1>Inspectah Explorer v0</h1>
        <form onSubmit={handleSubmit}>
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Busque por caso, domínio ou palavras-chave"
          />
          <button type="submit" disabled={loading}>
            Buscar
          </button>
        </form>
        {loading && <p>Buscando casos...</p>}
        {error && <p className="error">{error}</p>}
        <p>Total encontrado: {total}</p>
        <ul className="case-list">
          {cases.map((item) => (
            <li key={item.id_caso} className={item.id_caso === selectedCase ? "selected" : ""}>
              <button type="button" onClick={() => setSelectedCase(item.id_caso)}>
                <strong>{item.titulo}</strong>
                <span>{item.dominio}</span>
                <span>Status: {item.status}</span>
              </button>
            </li>
          ))}
        </ul>
      </section>
      <section className="case-panel">
        {selectedCase ? <CasePage caseId={selectedCase} onClose={() => setSelectedCase(null)} /> : <p>Selecione um caso.</p>}
      </section>
    </div>
  );
}
