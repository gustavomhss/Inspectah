import { endpoints } from '@/core/api/endpoints';
import { httpClient } from '@/core/api/http-client';
import type {
  Flow,
  FlowCreatePayload,
  FlowExecution,
  FlowExecutionDetail,
  FlowOperation,
  FlowVersion,
  FlowCatalogEntry,
  FlowRolloutStatus,
  FlowReplaceAgentPayload,
  FlowReprocessPayload,
  FlowTemplate,
  FlowUpdateStatePayload,
  NewsdataRun,
} from './types';

export async function listFlows(): Promise<Flow[]> {
  const data = await httpClient<Flow[]>(endpoints.admin.flows.list);
  return data || [];
}

export async function listFlowTemplates(): Promise<FlowTemplate[]> {
  const data = await httpClient<FlowTemplate[]>(endpoints.admin.flows.templates);
  return data || [];
}

export async function upsertFlowTemplate(payload: {
  slug: string;
  version: string;
  domain: string;
  entry_type: string;
  description?: string;
  limits?: Record<string, unknown>;
  policies?: Record<string, unknown>[];
  steps: Record<string, unknown>[];
  metadata?: Record<string, unknown>;
  id?: string;
}): Promise<FlowTemplate> {
  const data = await httpClient<FlowTemplate>(endpoints.admin.flows.templates, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  return data;
}

export async function updateFlowTemplate(slug: string, payload: Partial<{
  version: string;
  domain: string;
  entry_type: string;
  description?: string;
  limits?: Record<string, unknown>;
  policies?: Record<string, unknown>[];
  steps: Record<string, unknown>[];
  metadata?: Record<string, unknown>;
  id?: string;
}>): Promise<FlowTemplate> {
  const data = await httpClient<FlowTemplate>(endpoints.admin.flows.templateDetail(slug), {
    method: 'PUT',
    body: JSON.stringify({ slug, ...payload }),
  });
  return data;
}

export async function getFlow(flowId: string): Promise<Flow> {
  const data = await httpClient<Flow>(endpoints.admin.flows.detail(flowId));
  return data;
}

export async function createFlowFromTemplate(payload: FlowCreatePayload): Promise<Flow> {
  const data = await httpClient<Flow>(endpoints.admin.flows.createFromTemplate, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  return data;
}

export async function updateFlowState(flowId: string, payload: FlowUpdateStatePayload): Promise<Flow> {
  const data = await httpClient<Flow>(endpoints.admin.flows.updateState(flowId), {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  return data;
}

export async function replaceFlowAgent(flowId: string, payload: FlowReplaceAgentPayload): Promise<Flow> {
  const data = await httpClient<Flow>(endpoints.admin.flows.replaceAgent(flowId), {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  return data;
}

export async function listFlowExecutions(flowId: string): Promise<FlowExecution[]> {
  const data = await httpClient<FlowExecution[]>(endpoints.admin.flows.executions(flowId));
  return data || [];
}

export async function getFlowExecutionDetail(flowId: string, execId: string): Promise<FlowExecutionDetail> {
  const data = await httpClient<FlowExecutionDetail>(endpoints.admin.flows.executionDetail(flowId, execId));
  return data;
}

export async function reprocessFlowItems(flowId: string, payload: FlowReprocessPayload): Promise<unknown> {
  return httpClient(endpoints.admin.flows.reprocess(flowId), {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function listFlowVersions(flowId: string): Promise<FlowVersion[]> {
  return httpClient<FlowVersion[]>(endpoints.admin.flows.versions(flowId)) ?? [];
}

export async function rollbackFlowVersion(flowId: string, versionId: string): Promise<Flow> {
  return httpClient<Flow>(endpoints.admin.flows.rollback(flowId, versionId), { method: 'POST' });
}

export async function listFlowOperations(flowId: string): Promise<FlowOperation[]> {
  return httpClient<FlowOperation[]>(endpoints.admin.flows.operations(flowId)) ?? [];
}

export async function listFlowCatalog(): Promise<FlowCatalogEntry[]> {
  return httpClient<FlowCatalogEntry[]>(endpoints.admin.flows.catalog) ?? [];
}

export async function startFlowRollout(
  flowId: string,
  payload: { mode: string; test_percentual: number; criteria?: Record<string, unknown>; actor: string; operation_id: string; catalog_hash: string },
): Promise<Flow> {
  const opId = payload.operation_id;
  return httpClient<Flow>(endpoints.admin.flows.rollout(flowId), {
    method: 'POST',
    body: JSON.stringify(payload),
    headers: opId ? { 'x-operation-id': opId } : undefined,
  });
}

export async function promoteFlowRollout(flowId: string, payload: { actor: string; operation_id: string; catalog_hash: string }): Promise<Flow> {
  return httpClient<Flow>(endpoints.admin.flows.rolloutPromote(flowId), {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function rollbackFlowRollout(
  flowId: string,
  payload: { flow_version_id?: string | null; actor: string; operation_id: string; catalog_hash: string },
): Promise<Flow> {
  return httpClient<Flow>(endpoints.admin.flows.rolloutRollback(flowId), {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function getRolloutStatus(flowId: string): Promise<FlowRolloutStatus> {
  return httpClient<FlowRolloutStatus>(endpoints.admin.flows.rolloutStatus(flowId));
}

export async function deleteFlow(flowId: string): Promise<void> {
  await httpClient(endpoints.admin.flows.detail(flowId), { method: 'DELETE' });
}

export async function listOpsCockpitFlows() {
  return httpClient<
    { id: string; slug: string; domain?: string; flow_version_id?: string | null; slos?: { id: string; status?: string }[] }[]
  >(endpoints.admin.opsCockpit.flows);
}

export async function runNewsdataIngest(): Promise<NewsdataRun> {
  return httpClient<NewsdataRun>(endpoints.admin.newsdata.run, {
    method: 'POST',
    headers: { 'x-role': 'ops_ingest' },
    body: JSON.stringify({ trigger_origin: 'ui_console', size: 50, throttle_seconds: 1, max_attempts: 3 }),
  });
}
