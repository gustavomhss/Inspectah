import { endpoints } from '@/core/api/endpoints';
import { httpClient } from '@/core/api/http-client';
import type {
  Flow,
  FlowCreatePayload,
  FlowExecution,
  FlowExecutionDetail,
  FlowReplaceAgentPayload,
  FlowReprocessPayload,
  FlowTemplate,
  FlowUpdateStatePayload,
} from './types';

export async function listFlows(): Promise<Flow[]> {
  const data = await httpClient<Flow[]>(endpoints.admin.flows.list);
  return data || [];
}

export async function listFlowTemplates(): Promise<FlowTemplate[]> {
  const data = await httpClient<FlowTemplate[]>(endpoints.admin.flows.templates);
  return data || [];
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
