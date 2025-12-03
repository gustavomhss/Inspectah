import { endpoints } from '@/core/api/endpoints';
import { httpClient } from '@/core/api/http-client';
import type { AgentFlowConfig, AgentFlowConfigForm, AgentFlowError } from './agentFlowsTypes';

function normalizeFlow(flow: AgentFlowConfig): AgentFlowConfig {
  const steps = (flow.steps || []).map((s) => ({
    ...s,
    params: s.params || {},
    required: s.required ?? true,
    can_fail_soft: s.can_fail_soft ?? false,
  }));
  return {
    ...flow,
    name: flow.name || '',
    description: flow.description || '',
    steps,
  };
}

export async function listAgentFlows(authToken?: string): Promise<AgentFlowConfig[]> {
  const response = await httpClient<AgentFlowConfig[]>(endpoints.admin.agents.flowsAdmin, { authToken });
  return (response || []).map(normalizeFlow);
}

export async function getAgentFlowById(flowId: string, authToken?: string): Promise<AgentFlowConfig> {
  const response = await httpClient<AgentFlowConfig>(endpoints.admin.agents.flowAdminDetail(flowId), { authToken });
  return normalizeFlow(response);
}

export async function getAgentFlowByDomain(domainKey: string, authToken?: string): Promise<AgentFlowConfig> {
  const response = await httpClient<AgentFlowConfig>(endpoints.admin.agents.flowAdminByDomain(domainKey), { authToken });
  return normalizeFlow(response);
}

export async function createAgentFlow(payload: AgentFlowConfigForm, authToken?: string): Promise<AgentFlowConfig> {
  const response = await httpClient<AgentFlowConfig | AgentFlowError>(endpoints.admin.agents.flowsAdmin, {
    method: 'POST',
    body: JSON.stringify(payload),
    authToken,
  });
  if ((response as AgentFlowError).errors) {
    throw new Error((response as AgentFlowError).errors.join('; '));
  }
  return normalizeFlow(response as AgentFlowConfig);
}

export async function updateAgentFlow(flowId: string, payload: AgentFlowConfigForm, authToken?: string): Promise<AgentFlowConfig> {
  const response = await httpClient<AgentFlowConfig | AgentFlowError>(endpoints.admin.agents.flowAdminDetail(flowId), {
    method: 'PUT',
    body: JSON.stringify(payload),
    authToken,
  });
  if ((response as AgentFlowError).errors) {
    throw new Error((response as AgentFlowError).errors.join('; '));
  }
  return normalizeFlow(response as AgentFlowConfig);
}

export async function deleteAgentFlow(flowId: string, authToken?: string): Promise<void> {
  await httpClient(endpoints.admin.agents.flowAdminDetail(flowId), { method: 'DELETE', authToken });
}
