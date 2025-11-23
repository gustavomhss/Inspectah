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
}

export async function httpClient<T>(path: string, options: HttpClientOptions = {}): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), DEFAULT_TIMEOUT_MS);
  const { authToken, handleUnauthorized = true, ...fetchOptions } = options;
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
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
        detail = (body && (body.error || body.message || body.detail)) as string | undefined;
      } catch {
        detail = undefined;
      }
      if (handleUnauthorized && authToken && (response.status === 401 || response.status === 403)) {
        void unauthorizedHandler?.();
      }
      throw new HttpError(detail || `Falha na requisição (${response.status})`, response.status);
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
