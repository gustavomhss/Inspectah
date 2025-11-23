const apiBaseUrl =
  (import.meta.env.VITE_INSPECTAH_API_BASE_URL as string | undefined)?.replace(/\/$/, '') || 'http://localhost:8000';

export const env = {
  apiBaseUrl,
  consultationPath: (import.meta.env.VITE_INSPECTAH_CONSULT_PATH as string | undefined) || '/api/consultation',
  authStorageKey: 'inspectah_auth_session',
};
