import { endpoints } from '../../../core/api/endpoints';
import { httpClient } from '../../../core/api/http-client';
import type { CopilotoAction, CopilotoSessionResponse } from '../../../core/api/api-types';
export type { CopilotoAction };

export interface CopilotoMessagePayload {
  user_message: string;
  form_state: Record<string, unknown>;
  metadata?: Record<string, unknown>;
  files?: Array<{ file_id: string; filename?: string }>;
  agent_mode?: boolean;
  source_id?: string;
}

export interface CopilotoResponse {
  session_id?: string;
  agent_mode?: boolean;
  source_id?: string | null;
  assistant_message?: string;
  message?: string;
  actions: CopilotoAction[];
}

export interface CopilotoFileInfo {
  file_id: string;
  filename: string;
  content_type?: string;
  path?: string;
  session_id?: string;
}

export interface CopilotoSessionCreate {
  agent_mode?: boolean;
  source_id?: string;
}

export async function createSession(params?: CopilotoSessionCreate, authToken?: string): Promise<CopilotoSessionResponse> {
  const response = await httpClient<CopilotoSessionResponse>(endpoints.admin.copiloto.sessions, {
    method: 'POST',
    authToken,
    body: JSON.stringify(params || {}),
  });
  return response;
}

export async function sendMessage(sessionId: string, payload: CopilotoMessagePayload, authToken?: string): Promise<CopilotoResponse> {
  const response = await httpClient<CopilotoResponse>(endpoints.admin.copiloto.messages(sessionId), {
    method: 'POST',
    authToken,
    body: JSON.stringify(payload),
  });
  return response;
}

export async function uploadFile(sessionId: string, file: globalThis.File, authToken?: string): Promise<CopilotoFileInfo> {
  const formData = new globalThis.FormData();
  formData.append('file', file);
  const response = await httpClient<CopilotoFileInfo>(endpoints.admin.copiloto.files(sessionId), {
    method: 'POST',
    authToken,
    body: formData,
    isForm: true,
  });
  return response;
}
