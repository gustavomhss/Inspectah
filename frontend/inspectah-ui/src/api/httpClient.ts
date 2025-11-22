export class HttpError extends Error {
  status?: number;

  constructor(message: string, status?: number) {
    super(message);
    this.name = 'HttpError';
    this.status = status;
  }
}

const baseUrl = (import.meta.env.VITE_INSPECTAH_API_BASE_URL as string | undefined)?.replace(/\/$/, '') || 'http://localhost:8000';
const DEFAULT_TIMEOUT_MS = 15000;

export async function httpClient<T>(path: string, options: RequestInit = {}): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), DEFAULT_TIMEOUT_MS);
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  const url = path.startsWith('/') ? `${baseUrl}${path}` : `${baseUrl}/${path}`;

  try {
    const response = await fetch(url, {
      ...options,
      headers,
      signal: options.signal ?? controller.signal,
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
