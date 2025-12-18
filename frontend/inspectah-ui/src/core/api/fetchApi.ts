/**
 * fetchApi - Wrapper for httpClient
 *
 * Provides a simple interface for making API requests.
 */

import { httpClient, HttpClientOptions } from './http-client';

export interface FetchApiOptions extends Omit<HttpClientOptions, 'method'> {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
}

/**
 * Fetch data from the API
 */
export async function fetchApi<T>(
  path: string,
  options: FetchApiOptions = {}
): Promise<T> {
  return httpClient<T>(path, {
    method: 'GET',
    ...options,
  });
}

/**
 * POST data to the API
 */
export async function postApi<T>(
  path: string,
  data?: unknown,
  options: FetchApiOptions = {}
): Promise<T> {
  return httpClient<T>(path, {
    method: 'POST',
    body: data ? JSON.stringify(data) : undefined,
    ...options,
  });
}

/**
 * PUT data to the API
 */
export async function putApi<T>(
  path: string,
  data?: unknown,
  options: FetchApiOptions = {}
): Promise<T> {
  return httpClient<T>(path, {
    method: 'PUT',
    body: data ? JSON.stringify(data) : undefined,
    ...options,
  });
}

/**
 * DELETE from the API
 */
export async function deleteApi<T>(
  path: string,
  options: FetchApiOptions = {}
): Promise<T> {
  return httpClient<T>(path, {
    method: 'DELETE',
    ...options,
  });
}
