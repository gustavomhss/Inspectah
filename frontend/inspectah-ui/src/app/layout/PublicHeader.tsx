import { Link } from 'react-router-dom';
import { useAuth } from '../providers/AuthProvider';

function PublicHeader() {
  const { isAuthenticated } = useAuth();

  return (
    <header className="border-b border-white/5 bg-white/5 backdrop-blur">
      <div className="mx-auto flex max-w-5xl flex-col gap-3 px-4 py-6 md:flex-row md:items-center md:justify-between md:px-8">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-sky-300">Inspectah</p>
          <h1 className="mt-1 text-2xl font-bold text-white md:text-3xl" id="consulta-heading">
            Pergunte, veja o risco e as evidências principais
          </h1>
          <p className="mt-2 max-w-2xl text-sm text-slate-200 md:text-base">
            O Inspectah cruza múltiplas fontes, consolida uma resposta e expõe o nível de confiança. Faça uma pergunta em
            linguagem natural e veja risco e evidências sem abrir o terminal.
          </p>
        </div>
        <div className="flex flex-col items-start gap-2 text-xs text-slate-200 md:items-end">
          <div className="hidden rounded-full border border-white/10 bg-white/5 px-4 py-2 shadow-sm md:block">
            Sprint 20 · Consulta e acesso protegido ao Admin
          </div>
          <Link
            to="/admin"
            className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/10 px-4 py-2 text-sm font-semibold text-white transition hover:bg-white/20 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-300"
          >
            {isAuthenticated ? 'Ir para o Admin' : 'Entrar no Admin'}
            <span aria-hidden="true">→</span>
          </Link>
        </div>
      </div>
    </header>
  );
}

export default PublicHeader;
