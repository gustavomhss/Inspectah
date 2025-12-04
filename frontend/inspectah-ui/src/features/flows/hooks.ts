import { useCallback, useEffect, useState } from 'react';
import {
  createFlowFromTemplate,
  getFlow,
  getFlowExecutionDetail,
  listFlowExecutions,
  listFlows,
  listFlowTemplates,
  replaceFlowAgent,
  reprocessFlowItems,
  updateFlowState,
} from './api';
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

export function useFlowsList() {
  const [items, setItems] = useState<Flow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listFlows();
      setItems(data);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void reload();
  }, [reload]);

  return { items, loading, error, reload, setItems };
}

export function useFlowDetail(flowId: string | null) {
  const [flow, setFlow] = useState<Flow | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!flowId) return;
    setLoading(true);
    setError(null);
    getFlow(flowId)
      .then((data) => setFlow(data))
      .catch((err) => setError((err as Error).message))
      .finally(() => setLoading(false));
  }, [flowId]);

  return { flow, setFlow, loading, error };
}

export function useFlowExecutions(flowId: string | null) {
  const [executions, setExecutions] = useState<FlowExecution[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!flowId) return;
    setLoading(true);
    setError(null);
    listFlowExecutions(flowId)
      .then((data) => setExecutions(data))
      .catch((err) => setError((err as Error).message))
      .finally(() => setLoading(false));
  }, [flowId]);

  return { executions, loading, error, setExecutions };
}

export function useFlowTemplates() {
  const [templates, setTemplates] = useState<FlowTemplate[]>([]);
  useEffect(() => {
    listFlowTemplates().then(setTemplates).catch(() => setTemplates([]));
  }, []);
  return templates;
}

export function useFlowActions(flowId: string | null, onUpdated?: (flow: Flow) => void) {
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updateStateAction = useCallback(
    async (payload: FlowUpdateStatePayload) => {
      if (!flowId) return;
      setSaving(true);
      setError(null);
      try {
        const updated = await updateFlowState(flowId, payload);
        onUpdated?.(updated);
        return updated;
      } catch (err) {
        setError((err as Error).message);
        throw err;
      } finally {
        setSaving(false);
      }
    },
    [flowId, onUpdated],
  );

  const replaceAgentAction = useCallback(
    async (payload: FlowReplaceAgentPayload) => {
      if (!flowId) return;
      setSaving(true);
      setError(null);
      try {
        const updated = await replaceFlowAgent(flowId, payload);
        onUpdated?.(updated);
        return updated;
      } catch (err) {
        setError((err as Error).message);
        throw err;
      } finally {
        setSaving(false);
      }
    },
    [flowId, onUpdated],
  );

  const reprocessAction = useCallback(
    async (payload: FlowReprocessPayload) => {
      if (!flowId) return;
      setSaving(true);
      setError(null);
      try {
        await reprocessFlowItems(flowId, payload);
      } catch (err) {
        setError((err as Error).message);
        throw err;
      } finally {
        setSaving(false);
      }
    },
    [flowId],
  );

  return { updateStateAction, replaceAgentAction, reprocessAction, saving, error, setError };
}

export function useCreateFlow(onCreated?: (flow: Flow) => void) {
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const create = useCallback(
    async (payload: FlowCreatePayload) => {
      setSaving(true);
      setError(null);
      try {
        const created = await createFlowFromTemplate(payload);
        onCreated?.(created);
        return created;
      } catch (err) {
        setError((err as Error).message);
        throw err;
      } finally {
        setSaving(false);
      }
    },
    [onCreated],
  );

  return { create, saving, error, setError };
}

export function useExecutionDetail(flowId: string | null, executionId: string | null) {
  const [detail, setDetail] = useState<FlowExecutionDetail | null>(null);
  useEffect(() => {
    if (!flowId || !executionId) return;
    getFlowExecutionDetail(flowId, executionId)
      .then(setDetail)
      .catch(() => setDetail(null));
  }, [flowId, executionId]);
  return detail;
}
