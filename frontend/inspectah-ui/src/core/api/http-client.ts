import { env } from '../config/env';

type UnauthorizedHandler = () => void | Promise<void>;
let unauthorizedHandler: UnauthorizedHandler | null = null;

export function setUnauthorizedHandler(handler: UnauthorizedHandler | null) {
  unauthorizedHandler = handler;
}

export class HttpError extends Error {
  status?: number;

  constructor(message: string, status?: number) {
    super(message);
    this.name = 'HttpError';
    this.status = status;
  }
}

const DEFAULT_TIMEOUT_MS = 15000;

export interface HttpClientOptions extends RequestInit {
  authToken?: string;
  handleUnauthorized?: boolean;
  isForm?: boolean;
}

function normalizeErrorDetail(body: unknown): string | undefined {
  if (!body) return undefined;
  if (typeof body === 'string') return body;
  if (Array.isArray(body)) {
    const parts = body
      .map((item) => {
        if (!item) return null;
        if (typeof item === 'string') return item;
        if (typeof item === 'object') {
          const obj = item as Record<string, unknown>;
          const msg = obj.message || obj.msg || obj.detail || obj.error;
          if (typeof msg === 'string') return msg;
          if (Array.isArray(msg)) {
            return msg.map((m) => (typeof m === 'string' ? m : JSON.stringify(m))).join(', ');
          }
          const loc = obj.loc;
          if (Array.isArray(loc)) return `${loc.join('.')}: ${JSON.stringify(obj)}`;
        }
        return JSON.stringify(item);
      })
      .filter(Boolean) as string[];
    return parts.join('; ');
  }
  if (typeof body === 'object') {
    const obj = body as Record<string, unknown>;
    const direct = obj.error || obj.message || obj.detail;
    if (typeof direct === 'string') return direct;
    if (Array.isArray(direct)) {
      return direct.map((d) => (typeof d === 'string' ? d : JSON.stringify(d))).join('; ');
    }
    return JSON.stringify(obj);
  }
  return undefined;
}

export async function httpClient<T>(path: string, options: HttpClientOptions = {}): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), DEFAULT_TIMEOUT_MS);
  const { authToken, handleUnauthorized = true, isForm = false, ...fetchOptions } = options;
  const headers: HeadersInit = {
    ...(isForm ? {} : { 'Content-Type': 'application/json' }),
    ...(fetchOptions.headers || {}),
    ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
  };

  const url = path.startsWith('http')
    ? path
    : path.startsWith('/')
      ? `${env.apiBaseUrl}${path}`
      : `${env.apiBaseUrl}/${path}`;

  try {
    const response = await fetch(url, {
      ...fetchOptions,
      headers,
      signal: fetchOptions.signal ?? controller.signal,
    });
    clearTimeout(timeoutId);

    if (!response.ok) {
      let detail: string | undefined;
      try {
        const body = await response.json();
        detail = normalizeErrorDetail(body);
      } catch {
        detail = undefined;
      }
      if (handleUnauthorized && authToken && (response.status === 401 || response.status === 403)) {
        void unauthorizedHandler?.();
      }
      throw new HttpError(detail || `Falha na requisição (${response.status})`, response.status);
    }

    // Respostas vazias (204) ou sem body: retornam undefined
    if (response.status === 204 || response.headers.get('Content-Length') === '0') {
      return undefined as T;
    }
    try {
      return (await response.json()) as T;
    } catch (error) {
      throw new HttpError('Resposta inválida do servidor do Inspectah', response.status);
    }
  } catch (error) {
    clearTimeout(timeoutId);
    if (error instanceof HttpError) {
      throw error;
    }
    if ((error as Error).name === 'AbortError') {
      throw new HttpError('Tempo de resposta excedido', 408);
    }
    throw new HttpError('Falha de rede ao consultar o Inspectah');
  }
}
