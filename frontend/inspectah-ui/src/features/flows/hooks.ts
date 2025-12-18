import { useCallback, useEffect, useState } from 'react';
import {
  createFlowFromTemplate,
  deleteFlow,
  getFlow,
  getFlowExecutionDetail,
  listFlowExecutions,
  listFlows,
  listFlowTemplates,
  listFlowOperations,
  listFlowVersions,
  listOpsCockpitFlows,
  replaceFlowAgent,
  getRolloutStatus,
  listFlowCatalog,
  promoteFlowRollout,
  rollbackFlowRollout,
  startFlowRollout,
  reprocessFlowItems,
  rollbackFlowVersion,
  updateFlowState,
} from './api';
import type {
  Flow,
  FlowCreatePayload,
  FlowExecution,
  FlowExecutionDetail,
  FlowOperation,
  FlowReplaceAgentPayload,
  FlowReprocessPayload,
  FlowVersion,
  FlowTemplate,
  FlowUpdateStatePayload,
  FlowCatalogEntry,
  FlowRolloutStatus,
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
    if (!flowId || flowId === 'new') return;
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
    if (!flowId || flowId === 'new') return;
    setLoading(true);
    setError(null);
    listFlowExecutions(flowId)
      .then((data) => setExecutions(data))
      .catch((err) => setError((err as Error).message))
      .finally(() => setLoading(false));
  }, [flowId]);

  return { executions, loading, error, setExecutions };
}

export function useFlowVersions(flowId: string | null) {
  const [versions, setVersions] = useState<FlowVersion[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!flowId || flowId === 'new') return;
    setLoading(true);
    setError(null);
    listFlowVersions(flowId)
      .then(setVersions)
      .catch((err) => setError((err as Error).message))
      .finally(() => setLoading(false));
  }, [flowId]);

  return { versions, loading, error, setVersions };
}

export function useFlowOperations(flowId: string | null) {
  const [ops, setOps] = useState<FlowOperation[]>([]);
  useEffect(() => {
    if (!flowId || flowId === 'new') return;
    listFlowOperations(flowId)
      .then(setOps)
      .catch(() => setOps([]));
  }, [flowId]);
  return ops;
}

export function useRollback(flowId: string | null, onUpdated?: (flow: Flow) => void) {
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const run = useCallback(
    async (versionId: string) => {
      if (!flowId) return;
      setSaving(true);
      setError(null);
      try {
        const updated = await rollbackFlowVersion(flowId, versionId);
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
  return { run, saving, error };
}

export function useOpsFlows() {
  const [items, setItems] = useState<
    { id: string; slug: string; domain?: string; flow_version_id?: string | null; slos?: { id: string; status?: string }[] }[]
  >([]);
  useEffect(() => {
    listOpsCockpitFlows().then((data) => setItems(data || [])).catch(() => setItems([]));
  }, []);
  return items;
}

export function useFlowTemplates() {
  const [templates, setTemplates] = useState<FlowTemplate[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listFlowTemplates();
      setTemplates(data);
    } catch (err) {
      setTemplates([]);
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void reload();
  }, [reload]);

  return { templates, reload, loading, error };
}

export function useFlowActions(flowId: string | null, onUpdated?: (flow: Flow) => void) {
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);

  const updateStateAction = useCallback(
    async (payload: FlowUpdateStatePayload) => {
      if (!flowId || flowId === 'new') return;
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

  const deleteFlowAction = useCallback(async () => {
    if (!flowId || flowId === 'new') return;
    setDeleting(true);
    setError(null);
    try {
      await deleteFlow(flowId);
      return true;
    } catch (err) {
      setError((err as Error).message);
      throw err;
    } finally {
      setDeleting(false);
    }
  }, [flowId]);

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

  return { updateStateAction, replaceAgentAction, reprocessAction, deleteFlowAction, saving, deleting, error, setError };
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

export function useRollout(flowId: string | null) {
  const [status, setStatus] = useState<FlowRolloutStatus | null>(null);
  const [catalog, setCatalog] = useState<FlowCatalogEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const reload = useCallback(async () => {
    if (!flowId) return;
    setLoading(true);
    try {
      const [st, cat] = await Promise.all([getRolloutStatus(flowId), listFlowCatalog()]);
      setStatus(st);
      setCatalog(cat || []);
    } catch (err) {
      setStatus(null);
    } finally {
      setLoading(false);
    }
  }, [flowId]);
  useEffect(() => {
    if (!flowId) return;
    void reload();
    const t = setInterval(() => {
      void reload();
    }, 5000);
    return () => clearInterval(t);
  }, [flowId, reload]);
  return { status, catalog, setStatus, reload, loading };
}

export function useRolloutActions(flowId: string | null, onUpdated?: (flow: Flow) => void) {
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const start = useCallback(
    async (payload: { mode: string; test_percentual: number; criteria?: Record<string, unknown>; actor: string; operation_id: string; catalog_hash: string }) => {
      if (!flowId) return;
      setSaving(true);
      setError(null);
      try {
        const updated = await startFlowRollout(flowId, payload);
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

  const promote = useCallback(async (payload?: { actor?: string; operation_id?: string; catalog_hash?: string }) => {
    if (!flowId) return;
    setSaving(true);
    setError(null);
    try {
      const updated = await promoteFlowRollout(
        flowId,
        payload as { actor: string; operation_id: string; catalog_hash: string },
      );
      onUpdated?.(updated);
      return updated;
    } catch (err) {
      setError((err as Error).message);
      throw err;
    } finally {
      setSaving(false);
    }
  }, [flowId, onUpdated]);

  const rollback = useCallback(
    async (flowVersionId?: string | null, payload?: { actor?: string; operation_id?: string; catalog_hash?: string }) => {
      if (!flowId) return;
      setSaving(true);
      setError(null);
      try {
        const updated = await rollbackFlowRollout(
          flowId,
          { flow_version_id: flowVersionId, ...(payload || {}) } as {
            flow_version_id?: string | null;
            actor: string;
            operation_id: string;
            catalog_hash: string;
          },
        );
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

  return { start, promote, rollback, saving, error, setError };
}
