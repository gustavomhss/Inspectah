function EmptyState() {
  return (
    <div className="rounded-2xl border border-dashed border-white/10 bg-white/5 p-6 text-slate-50 shadow-card" role="status">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-300">Pronto para consultar</p>
      <h2 className="mt-2 text-xl font-bold text-white">Faça uma pergunta para ver resposta, risco e evidências.</h2>
      <p className="mt-2 text-sm text-slate-200">
        Use linguagem natural. Se não houver dados suficientes, avisaremos de forma clara. Nenhuma ação altera o backend nesta tela.
      </p>
    </div>
  );
}

export default EmptyState;
