import { useState } from 'react';
import CopilotoChatPanel from './CopilotoChatPanel';
import type { CopilotoAction, CopilotoFileInfo } from '../api/copilotoClient';
import type { CopilotoMessage } from '../hooks/useCopilotoAgent';

interface Props {
  messages: CopilotoMessage[];
  attachedFiles: CopilotoFileInfo[];
  loading?: boolean;
  error?: string | null;
  onSend: (message: string) => Promise<CopilotoAction[]>;
  onNewChat: () => Promise<void>;
  onAttach: (file: globalThis.File) => Promise<void>;
}

function CopilotoWidget({ messages, attachedFiles, loading, error, onSend, onNewChat, onAttach }: Props) {
  const [open, setOpen] = useState(false);

  const handleSend = async (message: string) => {
    await onSend(message);
  };

  return (
    <>
      <button
        type="button"
        className="fixed bottom-4 right-4 z-40 rounded-full bg-sky-600 px-4 py-3 text-sm font-semibold text-white shadow-lg hover:bg-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-300"
        onClick={() => setOpen((prev) => !prev)}
      >
        Copiloto de Fontes
      </button>
      {open ? (
        <CopilotoChatPanel
          messages={messages}
          attachedFiles={attachedFiles}
          loading={loading}
          error={error}
          onSend={handleSend}
          onNewChat={onNewChat}
          onAttach={onAttach}
          onClose={() => setOpen(false)}
        />
      ) : null}
    </>
  );
}

export default CopilotoWidget;
