import { useState } from 'react';
import Button from '../../../shared/components/Button';
import ErrorMessage from '../../../shared/components/ErrorMessage';
import CopilotoFileAttachment from './CopilotoFileAttachment';
import CopilotoInputBar from './CopilotoInputBar';
import CopilotoMessageList from './CopilotoMessageList';
import type { CopilotoFileInfo } from '../api/copilotoClient';
import type { CopilotoMessage } from '../hooks/useCopilotoAgent';

interface Props {
  messages: CopilotoMessage[];
  attachedFiles: CopilotoFileInfo[];
  loading?: boolean;
  error?: string | null;
  onSend: (message: string) => Promise<void>;
  onNewChat: () => Promise<void>;
  onAttach: (file: globalThis.File) => Promise<void>;
  agentMode: boolean;
  onToggleAgentMode: (value: boolean) => void;
  onClose: () => void;
}

function CopilotoChatPanel({ messages, attachedFiles, loading, error, onSend, onNewChat, onAttach, agentMode, onToggleAgentMode, onClose }: Props) {
  const [input, setInput] = useState('');

  const handleSend = async () => {
    if (!input.trim()) return;
    await onSend(input.trim());
    setInput('');
  };

  const handleNewChat = async () => {
    await onNewChat();
    setInput('');
  };

  return (
    <div className="fixed bottom-4 right-4 z-50 w-96 max-w-[calc(100%-32px)] rounded-xl border border-white/10 bg-slate-900/90 p-4 shadow-2xl backdrop-blur">
      <div className="mb-2 flex items-center justify-between gap-2">
        <div>
          <p className="text-sm font-semibold text-white">Copiloto de Fontes</p>
          <p className="text-xs text-slate-300">Sugestões para preencher o formulário.</p>
        </div>
        <div className="flex gap-2">
          <label className="flex items-center gap-1 text-xs text-slate-200">
            <input type="checkbox" checked={agentMode} onChange={(e) => onToggleAgentMode(e.target.checked)} />
            modo agente
          </label>
          <Button type="button" variant="secondary" onClick={handleNewChat} disabled={!!loading}>
            Novo chat
          </Button>
          <Button type="button" variant="ghost" onClick={onClose}>
            Fechar
          </Button>
        </div>
      </div>
      {error ? <ErrorMessage message={error} /> : null}
      <CopilotoMessageList messages={messages} />
      <div className="mt-3 flex flex-col gap-3">
        <CopilotoFileAttachment onAttach={onAttach} attachedFiles={attachedFiles} disabled={!!loading} />
        <CopilotoInputBar value={input} onChange={setInput} onSend={handleSend} disabled={!!loading} />
      </div>
    </div>
  );
}

export default CopilotoChatPanel;
