import { useState } from 'react';
import { clsx } from 'clsx';
import { SpCard } from '../../components/ui/Card';
import { SpButton } from '../../components/ui/Button';
import { SpBadge } from '../../components/ui/Badge';

interface ConsultResult {
  id: string;
  claim: string;
  verdict: 'true' | 'false' | 'misleading' | 'unverified';
  confidence: number;
  summary: string;
  sources: { name: string; url: string; type: string }[];
  checkedAt: string;
}

const mockResults: ConsultResult[] = [
  {
    id: '1',
    claim: 'Governo vai acabar com o 13o salario',
    verdict: 'false',
    confidence: 0.98,
    summary: 'Nao existe nenhuma proposta ou projeto de lei em tramitacao que vise acabar com o 13o salario. A informacao e falsa e circula periodicamente nas redes sociais.',
    sources: [
      { name: 'Planalto', url: '#', type: 'official' },
      { name: 'Agencia Brasil', url: '#', type: 'news' },
      { name: 'TST', url: '#', type: 'official' },
    ],
    checkedAt: '2024-01-15T10:30:00Z',
  },
];

export function SpConsultPage() {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<ConsultResult[]>([]);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = () => {
    if (!query.trim()) return;
    setIsLoading(true);
    setHasSearched(true);
    // Simulate API call
    setTimeout(() => {
      setResults(mockResults);
      setIsLoading(false);
    }, 1500);
  };

  const getVerdictConfig = (verdict: ConsultResult['verdict']) => {
    const config = {
      true: { color: 'text-emerald-400', bg: 'bg-emerald-400/10', label: 'VERDADEIRO', icon: '✓' },
      false: { color: 'text-red-400', bg: 'bg-red-400/10', label: 'FALSO', icon: '✗' },
      misleading: { color: 'text-yellow-400', bg: 'bg-yellow-400/10', label: 'ENGANOSO', icon: '!' },
      unverified: { color: 'text-slate-400', bg: 'bg-slate-400/10', label: 'NAO VERIFICADO', icon: '?' },
    };
    return config[verdict];
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-900 to-slate-950">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-violet-600/10 via-transparent to-cyan-600/10" />
        <div className="relative max-w-4xl mx-auto px-6 py-16 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-violet-600/20 mb-6">
            <svg className="w-8 h-8 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <h1 className="text-4xl sm:text-5xl font-bold text-white mb-4">
            Verifique antes de compartilhar
          </h1>
          <p className="text-lg text-slate-400 max-w-2xl mx-auto mb-8">
            Cole uma noticia, afirmacao ou link para verificar se a informacao e verdadeira, falsa ou enganosa.
          </p>

          {/* Search Box */}
          <div className="max-w-2xl mx-auto">
            <div className="relative">
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Cole aqui a noticia ou afirmacao que deseja verificar..."
                className="w-full px-4 py-4 bg-slate-800/50 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent resize-none"
                rows={3}
              />
            </div>
            <SpButton
              onClick={handleSearch}
              disabled={!query.trim() || isLoading}
              className="mt-4 w-full sm:w-auto px-8"
            >
              {isLoading ? (
                <>
                  <svg className="animate-spin w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Verificando...
                </>
              ) : (
                <>
                  <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  Verificar
                </>
              )}
            </SpButton>
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="max-w-4xl mx-auto px-6 pb-16">
        {isLoading && (
          <SpCard variant="bordered" className="text-center py-12">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-violet-600/20 mb-4 animate-pulse">
              <svg className="w-8 h-8 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Analisando informacao</h3>
            <p className="text-slate-400">Consultando fontes oficiais e base de dados...</p>
          </SpCard>
        )}

        {!isLoading && hasSearched && results.length === 0 && (
          <SpCard variant="bordered" className="text-center py-12">
            <svg className="w-16 h-16 text-slate-600 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 className="text-lg font-semibold text-white mb-2">Nenhum resultado encontrado</h3>
            <p className="text-slate-400">Nao encontramos verificacoes para esta informacao. Tente reformular sua busca.</p>
          </SpCard>
        )}

        {!isLoading && results.length > 0 && (
          <div className="space-y-6">
            {results.map((result) => {
              const verdictConfig = getVerdictConfig(result.verdict);
              return (
                <SpCard key={result.id} variant="bordered">
                  {/* Verdict Banner */}
                  <div className={clsx('flex items-center gap-4 p-4 rounded-lg mb-6', verdictConfig.bg)}>
                    <div className={clsx('w-12 h-12 rounded-full flex items-center justify-center text-2xl font-bold', verdictConfig.color, verdictConfig.bg)}>
                      {verdictConfig.icon}
                    </div>
                    <div>
                      <p className={clsx('text-xl font-bold', verdictConfig.color)}>{verdictConfig.label}</p>
                      <p className="text-sm text-slate-400">Confianca: {Math.round(result.confidence * 100)}%</p>
                    </div>
                  </div>

                  {/* Claim */}
                  <div className="mb-6">
                    <label className="text-xs text-slate-500 uppercase tracking-wide">Afirmacao verificada</label>
                    <p className="text-lg text-white mt-1">{result.claim}</p>
                  </div>

                  {/* Summary */}
                  <div className="mb-6">
                    <label className="text-xs text-slate-500 uppercase tracking-wide">Resumo da verificacao</label>
                    <p className="text-slate-300 mt-1">{result.summary}</p>
                  </div>

                  {/* Sources */}
                  <div>
                    <label className="text-xs text-slate-500 uppercase tracking-wide">Fontes consultadas</label>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {result.sources.map((source, idx) => (
                        <SpBadge
                          key={idx}
                          variant={source.type === 'official' ? 'success' : 'default'}
                          size="sm"
                        >
                          {source.name}
                        </SpBadge>
                      ))}
                    </div>
                  </div>

                  {/* Footer */}
                  <div className="mt-6 pt-4 border-t border-slate-700 flex items-center justify-between">
                    <span className="text-xs text-slate-500">
                      Verificado em {new Date(result.checkedAt).toLocaleString()}
                    </span>
                    <div className="flex gap-2">
                      <SpButton variant="outline" size="sm">
                        <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                        </svg>
                        Compartilhar
                      </SpButton>
                      <SpButton variant="outline" size="sm">
                        <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        Ver detalhes
                      </SpButton>
                    </div>
                  </div>
                </SpCard>
              );
            })}
          </div>
        )}

        {/* How it works */}
        {!hasSearched && (
          <SpCard variant="bordered" className="mt-8">
            <h3 className="text-lg font-bold text-white mb-6 text-center">Como funciona</h3>
            <div className="grid sm:grid-cols-3 gap-6">
              {[
                {
                  icon: (
                    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  ),
                  title: 'Cole a informacao',
                  description: 'Copie e cole a noticia, mensagem ou link que voce recebeu',
                },
                {
                  icon: (
                    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                  ),
                  title: 'Verificacao automatica',
                  description: 'Nossa IA consulta fontes oficiais e base de dados verificados',
                },
                {
                  icon: (
                    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  ),
                  title: 'Resultado claro',
                  description: 'Receba o veredito com explicacao e fontes de referencia',
                },
              ].map((item, idx) => (
                <div key={idx} className="text-center">
                  <div className="w-12 h-12 rounded-full bg-violet-600/20 flex items-center justify-center mx-auto mb-3 text-violet-400">
                    {item.icon}
                  </div>
                  <h4 className="font-semibold text-white mb-1">{item.title}</h4>
                  <p className="text-sm text-slate-400">{item.description}</p>
                </div>
              ))}
            </div>
          </SpCard>
        )}
      </div>
    </div>
  );
}
