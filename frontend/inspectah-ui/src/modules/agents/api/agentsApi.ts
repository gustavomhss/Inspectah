import { endpoints } from '../../../core/api/endpoints';
import { httpClient } from '../../../core/api/http-client';
import type {
  AgentCommittee,
  AgentInstructionVersion,
  AgentLayer,
  AgentProfile,
  AgentRun,
  AgentStatus,
  CommitteePolicy,
  ModelUpgradePolicy,
  AgentFlowLayer,
} from '../../../core/api/api-types';

export interface AgentCreatePayload {
  name: string;
  description?: string;
  instructions?: string;
  role: string;
  layer: AgentLayer;
  model_name?: string | null;
  recommended_model_name?: string | null;
  temperature?: number;
  max_tokens?: number;
  top_p?: number;
  status?: AgentStatus;
  kb_refs?: Array<{ id: string; kind: string; label: string; path_or_uri: string }>;
  created_by?: string | null;
}

export interface AgentUpdatePayload extends Partial<AgentCreatePayload> {
  last_modified_by?: string | null;
}

export async function listAgents(authToken?: string, filters?: { layer?: AgentLayer; role?: string; status?: AgentStatus }) {
  const search = new URLSearchParams();
  if (filters?.layer) search.set('layer', filters.layer);
  if (filters?.role) search.set('role', filters.role);
  if (filters?.status) search.set('status', filters.status);
  const path = `${endpoints.admin.agents.list}${search.toString() ? `?${search.toString()}` : ''}`;
  return httpClient<AgentProfile[]>(path, { authToken });
}

export async function getAgent(agentId: string, authToken?: string) {
  return httpClient<AgentProfile>(endpoints.admin.agents.detail(agentId), { authToken });
}

export async function createAgent(payload: AgentCreatePayload, authToken?: string) {
  return httpClient<AgentProfile>(endpoints.admin.agents.list, {
    method: 'POST',
    body: JSON.stringify(payload),
    authToken,
  });
}

export async function updateAgent(agentId: string, payload: AgentUpdatePayload, authToken?: string) {
  return httpClient<AgentProfile>(endpoints.admin.agents.detail(agentId), {
    method: 'PUT',
    body: JSON.stringify(payload),
    authToken,
  });
}

export async function listInstructionVersions(agentId: string, authToken?: string) {
  return httpClient<AgentInstructionVersion[]>(endpoints.admin.agents.instructions(agentId), { authToken });
}

export async function addInstructionVersion(
  agentId: string,
  payload: { changelog: string; instructions?: string; created_by?: string | null },
  authToken?: string,
) {
  return httpClient<AgentInstructionVersion>(endpoints.admin.agents.instructions(agentId), {
    method: 'POST',
    body: JSON.stringify(payload),
    authToken,
  });
}

export async function listCommittees(authToken?: string, layer?: AgentLayer) {
  const search = new URLSearchParams();
  if (layer) search.set('layer', layer);
  const path = `${endpoints.admin.agents.committees}${search.toString() ? `?${search.toString()}` : ''}`;
  return httpClient<AgentCommittee[]>(path, { authToken });
}

export interface CommitteePayload {
  name: string;
  description?: string;
  layer: AgentLayer;
  primary_agents: string[];
  mediator_agent: string;
  policy?: CommitteePolicy;
  status?: AgentStatus;
}

export async function createCommittee(payload: CommitteePayload, authToken?: string) {
  return httpClient<AgentCommittee>(endpoints.admin.agents.committees, {
    method: 'POST',
    body: JSON.stringify(payload),
    authToken,
  });
}

export async function updateCommittee(committeeId: string, payload: CommitteePayload, authToken?: string) {
  return httpClient<AgentCommittee>(endpoints.admin.agents.committeeDetail(committeeId), {
    method: 'PUT',
    body: JSON.stringify(payload),
    authToken,
  });
}

export async function listCommitteeRuns(committeeId: string, authToken?: string) {
  return httpClient<AgentRun[]>(endpoints.admin.agents.committeeRuns(committeeId), { authToken });
}

export async function triggerDryRun(committeeId: string, inputRef: string | null, payload: Record<string, unknown>, authToken?: string) {
  return httpClient<AgentRun>(endpoints.admin.agents.committeeDryRun(committeeId), {
    method: 'POST',
    body: JSON.stringify({ input_ref: inputRef, payload }),
    authToken,
  });
}

export async function getModelPolicy(authToken?: string) {
  return httpClient<ModelUpgradePolicy>(endpoints.admin.agents.modelPolicy, { authToken });
}

export async function updateModelPolicy(payload: Partial<ModelUpgradePolicy>, authToken?: string) {
  return httpClient<ModelUpgradePolicy>(endpoints.admin.agents.modelPolicy, {
    method: 'PUT',
    body: JSON.stringify(payload),
    authToken,
  });
}

// Flow
export async function getAgentsFlow(authToken?: string) {
  return httpClient<AgentFlowLayer[]>(endpoints.admin.agents.flow, { authToken });
}

export async function saveAgentsFlow(layers: Partial<AgentFlowLayer>[], authToken?: string) {
  return httpClient<AgentFlowLayer[]>(endpoints.admin.agents.flow, {
    method: 'PUT',
    body: JSON.stringify(layers),
    authToken,
  });
}
