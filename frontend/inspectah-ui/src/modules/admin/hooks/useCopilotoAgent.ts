import { useCallback, useEffect, useState } from 'react';
import { useAuth } from '../../../app/providers/AuthProvider';
import type { CopilotoAction, CopilotoFileInfo, CopilotoMessagePayload } from '../api/copilotoClient';
import { createSession, sendMessage, uploadFile } from '../api/copilotoClient';

export type CopilotoMessage = {
  role: 'user' | 'assistant';
  content: string;
};

export function useCopilotoAgent(sourceId?: string) {
  const { token } = useAuth();
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<CopilotoMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [attachedFiles, setAttachedFiles] = useState<CopilotoFileInfo[]>([]);
  const [agentMode, setAgentMode] = useState(true);
  const [interacted, setInteracted] = useState(false);

  const ensureSession = useCallback(async () => {
    if (sessionId) return sessionId;
    const session = await createSession({ agent_mode: agentMode, source_id: sourceId }, token || undefined);
    setSessionId(session.session_id);
    return session.session_id;
  }, [sessionId, token, agentMode, sourceId]);

  const startNewChat = useCallback(async () => {
    const session = await createSession({ agent_mode: agentMode, source_id: sourceId }, token || undefined);
    setSessionId(session.session_id);
    setMessages([]);
    setAttachedFiles([]);
    setInteracted(false);
  }, [token, agentMode, sourceId]);

  const attachFile = useCallback(
    async (file: globalThis.File) => {
      const currentSession = await ensureSession();
      const info = await uploadFile(currentSession, file, token || undefined);
      setAttachedFiles((prev) => [...prev, info]);
      return info;
    },
    [ensureSession, token]
  );

  const sendUserMessage = useCallback(
    async (userMessage: string, formState: Record<string, unknown>): Promise<CopilotoAction[]> => {
      setLoading(true);
      setError(null);
      try {
        const currentSession = await ensureSession();
        const payload: CopilotoMessagePayload = {
          user_message: userMessage,
          form_state: formState,
          files: attachedFiles.map((f) => ({ file_id: f.file_id, filename: f.filename })),
          agent_mode: agentMode,
          source_id: sourceId,
        };
        setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
        const response = await sendMessage(currentSession, payload, token || undefined);
        const assistantText = response.message || response.assistant_message || 'Sem resposta do Copiloto.';
        setMessages((prev) => [...prev, { role: 'assistant', content: assistantText }]);
        setAttachedFiles([]);
        if (response.session_id && response.session_id !== currentSession) {
          setSessionId(response.session_id);
        }
        setInteracted(true);
        return response.actions || [];
      } catch (err) {
        const message = (err as Error).message || 'Falha ao enviar mensagem para o Copiloto.';
        setError(message);
        return [];
      } finally {
        setLoading(false);
      }
    },
    [ensureSession, token, attachedFiles, agentMode, sourceId]
  );

  useEffect(() => {
    setError(null);
  }, [sessionId]);

  return {
    sessionId,
    messages,
    loading,
    error,
    attachedFiles,
    agentMode,
    interacted,
    setAgentMode,
    sendUserMessage,
    startNewChat,
    attachFile,
  };
}
