/**
 * S39-W4: useClaimExplanation Hook (T-TEST-UNIT-002)
 *
 * Hook for fetching and managing claim explanations.
 */

import { useCallback, useEffect, useState, useRef } from 'react';
import { useStore } from '../../../core/store';
import type {
  ClaimExplanation,
  DrilldownRequest,
  ExplanationComparison,
  ExplanationNode,
  ExportFormat,
} from '../types';

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

/**
 * Hook options
 */
export interface UseClaimExplanationOptions {
  /** Auto-fetch on mount */
  autoFetch?: boolean;
  /** Cache TTL in ms */
  cacheTTL?: number;
  /** Initial drill depth */
  initialDepth?: number;
}

/**
 * Hook state
 */
export interface UseClaimExplanationState {
  /** The explanation data */
  explanation: ClaimExplanation | null;
  /** Loading state */
  isLoading: boolean;
  /** Error if any */
  error: Error | null;
  /** Expanded nodes in the tree */
  expandedNodes: Set<string>;
  /** Selected node for drilldown */
  selectedNode: ExplanationNode | null;
}

/**
 * Hook return type
 */
export interface UseClaimExplanationReturn extends UseClaimExplanationState {
  /** Fetch explanation for a claim */
  fetchExplanation: (claimId: string) => Promise<void>;
  /** Drilldown into a specific node */
  drilldown: (nodeId: string) => Promise<void>;
  /** Expand a node */
  expandNode: (nodeId: string) => void;
  /** Collapse a node */
  collapseNode: (nodeId: string) => void;
  /** Toggle node expansion */
  toggleNode: (nodeId: string) => void;
  /** Expand all nodes */
  expandAll: () => void;
  /** Collapse all nodes */
  collapseAll: () => void;
  /** Select a node */
  selectNode: (node: ExplanationNode | null) => void;
  /** Compare with another explanation */
  compare: (otherClaimId: string) => Promise<ExplanationComparison | null>;
  /** Export explanation */
  exportExplanation: (format: ExportFormat) => Promise<Blob | null>;
  /** Refresh explanation */
  refresh: () => Promise<void>;
  /** Clear state */
  clear: () => void;
}

/**
 * Collect all node IDs from tree
 */
function collectNodeIds(node: ExplanationNode): string[] {
  const ids = [node.id];
  for (const child of node.children) {
    ids.push(...collectNodeIds(child));
  }
  return ids;
}

/**
 * Hook for claim explanations
 */
export function useClaimExplanation(
  claimId?: string,
  options: UseClaimExplanationOptions = {}
): UseClaimExplanationReturn {
  const { autoFetch = true, cacheTTL = 5 * 60 * 1000, initialDepth = 3 } = options;

  const { state: storeState, dispatch } = useStore();
  const [explanation, setExplanation] = useState<ClaimExplanation | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());
  const [selectedNode, setSelectedNode] = useState<ExplanationNode | null>(null);

  const currentClaimIdRef = useRef<string | undefined>(claimId);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Fetch explanation from API
  const fetchExplanation = useCallback(
    async (id: string) => {
      // Check cache first
      const cacheKey = `explanation_${id}`;
      const cached = storeState.cache[cacheKey];
      if (cached && Date.now() - cached.timestamp < cacheTTL) {
        setExplanation(cached.data as ClaimExplanation);
        // Auto-expand first few levels
        const tree = (cached.data as ClaimExplanation).tree;
        if (tree) {
          const allIds = collectNodeIds(tree);
          const toExpand = allIds.filter((_, idx) => idx < initialDepth * 2);
          setExpandedNodes(new Set(toExpand));
        }
        return;
      }

      // Cancel previous request
      abortControllerRef.current?.abort();
      abortControllerRef.current = new AbortController();

      setIsLoading(true);
      setError(null);

      try {
        const response = await fetch(`${API_BASE}/api/explain/${id}`, {
          signal: abortControllerRef.current.signal,
        });

        if (!response.ok) {
          throw new Error(`Failed to fetch explanation: ${response.statusText}`);
        }

        const data: ClaimExplanation = await response.json();
        setExplanation(data);

        // Cache the result
        dispatch({
          type: 'SET_CACHE',
          payload: { key: cacheKey, data, ttl: cacheTTL },
        });

        // Auto-expand first few levels
        if (data.tree) {
          const allIds = collectNodeIds(data.tree);
          const toExpand = allIds.filter((_, idx) => idx < initialDepth * 2);
          setExpandedNodes(new Set(toExpand));
        }

        currentClaimIdRef.current = id;
      } catch (err) {
        if ((err as Error).name !== 'AbortError') {
          setError(err as Error);
        }
      } finally {
        setIsLoading(false);
      }
    },
    [storeState.cache, cacheTTL, initialDepth, dispatch]
  );

  // Drilldown into specific node
  const drilldown = useCallback(
    async (nodeId: string) => {
      if (!currentClaimIdRef.current) return;

      setIsLoading(true);
      setError(null);

      try {
        const request: DrilldownRequest = {
          claim_id: currentClaimIdRef.current,
          node_id: nodeId,
          depth: initialDepth,
        };

        const response = await fetch(`${API_BASE}/api/explain/drilldown`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(request),
        });

        if (!response.ok) {
          throw new Error(`Drilldown failed: ${response.statusText}`);
        }

        const data: ExplanationNode = await response.json();

        // Update the tree with new drilldown data
        if (explanation) {
          const updatedExplanation = updateNodeInTree(explanation, nodeId, data);
          setExplanation(updatedExplanation);
        }

        // Expand the drilled-down node
        setExpandedNodes((prev) => new Set([...prev, nodeId]));
      } catch (err) {
        setError(err as Error);
      } finally {
        setIsLoading(false);
      }
    },
    [explanation, initialDepth]
  );

  // Node expansion methods
  const expandNode = useCallback((nodeId: string) => {
    setExpandedNodes((prev) => new Set([...prev, nodeId]));
  }, []);

  const collapseNode = useCallback((nodeId: string) => {
    setExpandedNodes((prev) => {
      const next = new Set(prev);
      next.delete(nodeId);
      return next;
    });
  }, []);

  const toggleNode = useCallback((nodeId: string) => {
    setExpandedNodes((prev) => {
      const next = new Set(prev);
      if (next.has(nodeId)) {
        next.delete(nodeId);
      } else {
        next.add(nodeId);
      }
      return next;
    });
  }, []);

  const expandAll = useCallback(() => {
    if (!explanation?.tree) return;
    const allIds = collectNodeIds(explanation.tree);
    setExpandedNodes(new Set(allIds));
  }, [explanation]);

  const collapseAll = useCallback(() => {
    setExpandedNodes(new Set());
  }, []);

  // Select node
  const selectNode = useCallback((node: ExplanationNode | null) => {
    setSelectedNode(node);
  }, []);

  // Compare explanations
  const compare = useCallback(
    async (otherClaimId: string): Promise<ExplanationComparison | null> => {
      if (!currentClaimIdRef.current) return null;

      try {
        const response = await fetch(`${API_BASE}/api/explain/compare`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            claim_id_a: currentClaimIdRef.current,
            claim_id_b: otherClaimId,
          }),
        });

        if (!response.ok) {
          throw new Error(`Comparison failed: ${response.statusText}`);
        }

        return await response.json();
      } catch (err) {
        setError(err as Error);
        return null;
      }
    },
    []
  );

  // Export explanation
  const exportExplanation = useCallback(
    async (format: ExportFormat): Promise<Blob | null> => {
      if (!currentClaimIdRef.current) return null;

      try {
        const response = await fetch(
          `${API_BASE}/api/explain/${currentClaimIdRef.current}/export?format=${format}`
        );

        if (!response.ok) {
          throw new Error(`Export failed: ${response.statusText}`);
        }

        return await response.blob();
      } catch (err) {
        setError(err as Error);
        return null;
      }
    },
    []
  );

  // Refresh
  const refresh = useCallback(async () => {
    if (currentClaimIdRef.current) {
      // Invalidate cache
      dispatch({
        type: 'INVALIDATE_CACHE',
        payload: `explanation_${currentClaimIdRef.current}`,
      });
      await fetchExplanation(currentClaimIdRef.current);
    }
  }, [fetchExplanation, dispatch]);

  // Clear state
  const clear = useCallback(() => {
    setExplanation(null);
    setError(null);
    setExpandedNodes(new Set());
    setSelectedNode(null);
    currentClaimIdRef.current = undefined;
  }, []);

  // Auto-fetch on mount or when claimId changes
  useEffect(() => {
    if (autoFetch && claimId) {
      fetchExplanation(claimId);
    }

    return () => {
      abortControllerRef.current?.abort();
    };
  }, [claimId, autoFetch, fetchExplanation]);

  return {
    explanation,
    isLoading,
    error,
    expandedNodes,
    selectedNode,
    fetchExplanation,
    drilldown,
    expandNode,
    collapseNode,
    toggleNode,
    expandAll,
    collapseAll,
    selectNode,
    compare,
    exportExplanation,
    refresh,
    clear,
  };
}

/**
 * Helper to update a node in the tree
 */
function updateNodeInTree(
  explanation: ClaimExplanation,
  nodeId: string,
  newNode: ExplanationNode
): ClaimExplanation {
  function updateNode(node: ExplanationNode): ExplanationNode {
    if (node.id === nodeId) {
      return { ...node, ...newNode };
    }
    return {
      ...node,
      children: node.children.map(updateNode),
    };
  }

  return {
    ...explanation,
    tree: updateNode(explanation.tree),
  };
}

export default useClaimExplanation;
