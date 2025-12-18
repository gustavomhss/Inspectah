/**
 * S40-FE-008: Truth API Client
 *
 * API client for Truth Twin P4 endpoints.
 */

import type {
  TruthTwinResponse,
  DecisionInspectResponse,
  TimelineResponse,
  TruthApiError,
} from '../types';

// API base URL - defaults to relative path
const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

// Helper to build full URL
function buildUrl(path: string): string {
  return `${API_BASE}/api/truth${path}`;
}

// Generic fetch wrapper with error handling
async function fetchApi<T>(
  url: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    let errorDetail = 'Request failed';
    try {
      const errorData = await response.json();
      errorDetail = errorData.detail || errorData.message || errorDetail;
    } catch {
      errorDetail = response.statusText || errorDetail;
    }

    const error: TruthApiError = {
      detail: errorDetail,
      status_code: response.status,
    };
    throw error;
  }

  return response.json();
}

/**
 * Get Truth Twin for a claim (S40-BE-023)
 *
 * @param claimId - The claim ID or slug
 * @returns TruthTwinResponse with full provenance
 */
export async function getTruthTwin(claimId: string): Promise<TruthTwinResponse> {
  if (!claimId) {
    throw { detail: 'claim_id is required', status_code: 400 } as TruthApiError;
  }

  const url = buildUrl(`/${encodeURIComponent(claimId)}/twin`);
  return fetchApi<TruthTwinResponse>(url);
}

/**
 * Inspect a specific decision (S40-BE-024)
 *
 * @param decisionId - The decision ID
 * @returns DecisionInspectResponse with full provenance
 */
export async function inspectDecision(
  decisionId: string
): Promise<DecisionInspectResponse> {
  if (!decisionId) {
    throw { detail: 'decision_id is required', status_code: 400 } as TruthApiError;
  }

  const url = buildUrl(`/decision/${encodeURIComponent(decisionId)}/inspect`);
  return fetchApi<DecisionInspectResponse>(url);
}

/**
 * Get decision timeline for a claim
 *
 * @param claimId - The claim ID
 * @param limit - Maximum number of decisions (default 50)
 * @returns TimelineResponse
 */
export async function getDecisionTimeline(
  claimId: string,
  limit?: number
): Promise<TimelineResponse> {
  if (!claimId) {
    throw { detail: 'claim_id is required', status_code: 400 } as TruthApiError;
  }

  let url = buildUrl(`/${encodeURIComponent(claimId)}/timeline`);
  if (limit !== undefined && limit > 0) {
    url += `?limit=${limit}`;
  }

  return fetchApi<TimelineResponse>(url);
}

// Re-export types for convenience
export type { TruthTwinResponse, DecisionInspectResponse, TimelineResponse, TruthApiError };
