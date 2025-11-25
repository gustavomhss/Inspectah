import { useCallback, useEffect, useState } from 'react';
import { useAuth } from '../../../app/providers/AuthProvider';
import type { CopilotoAction, CopilotoFileInfo, CopilotoMessagePayload } from '../api/copilotoClient';
import { createSession, sendMessage, uploadFile } from '../api/copilotoClient';

export type CopilotoMessage = {
  role: 'user' | 'assistant';
  content: string;
};

export function useCopilotoAgent() {
  const { token } = useAuth();
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<CopilotoMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [attachedFiles, setAttachedFiles] = useState<CopilotoFileInfo[]>([]);

  const ensureSession = useCallback(async () => {
    if (sessionId) return sessionId;
    const newSession = await createSession(token || undefined);
    setSessionId(newSession);
    return newSession;
  }, [sessionId, token]);

  const startNewChat = useCallback(async () => {
    const newSession = await createSession(token || undefined);
    setSessionId(newSession);
    setMessages([]);
    setAttachedFiles([]);
  }, [token]);

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
        };
        setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
        const response = await sendMessage(currentSession, payload, token || undefined);
        setMessages((prev) => [...prev, { role: 'assistant', content: response.assistant_message }]);
        setAttachedFiles([]);
        if (response.session_id && response.session_id !== currentSession) {
          setSessionId(response.session_id);
        }
        return response.actions || [];
      } catch (err) {
        const message = (err as Error).message || 'Falha ao enviar mensagem para o Copiloto.';
        setError(message);
        return [];
      } finally {
        setLoading(false);
      }
    },
    [ensureSession, token, attachedFiles]
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
    sendUserMessage,
    startNewChat,
    attachFile,
  };
}
