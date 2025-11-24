import type { CopilotoMessage } from '../hooks/useCopilotoAgent';

interface Props {
  messages: CopilotoMessage[];
}

function CopilotoMessageList({ messages }: Props) {
  return (
    <div className="flex flex-col gap-2 overflow-y-auto rounded-lg bg-white/5 p-3 text-sm text-white h-64">
      {messages.length === 0 ? <span className="text-slate-300">Comece uma conversa com o Copiloto.</span> : null}
      {messages.map((msg, idx) => (
        <div
          key={`${msg.role}-${idx}`}
          className={`w-fit max-w-[90%] rounded-md px-3 py-2 ${msg.role === 'user' ? 'ml-auto bg-sky-600/80' : 'mr-auto bg-white/10 border border-white/10'}`}
        >
          <span className="block text-[11px] uppercase tracking-wide text-slate-200">{msg.role === 'user' ? 'Você' : 'Copiloto'}</span>
          <span className="text-sm leading-relaxed">{msg.content}</span>
        </div>
      ))}
    </div>
  );
}

export default CopilotoMessageList;
