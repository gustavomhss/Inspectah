/**
 * S39-W4: ExplainTreeView Component (T-TEST-UNIT-004)
 *
 * Tree visualization for claim explanation reasoning.
 */

import { type FC, memo, useCallback, useMemo } from 'react';
import type { ExplanationNode } from '../types';

export interface ExplainTreeViewProps {
  /** Root node of the explanation tree */
  tree: ExplanationNode | null;
  /** Set of expanded node IDs */
  expandedNodes: Set<string>;
  /** Selected node */
  selectedNode: ExplanationNode | null;
  /** Callback when node is toggled */
  onToggle: (nodeId: string) => void;
  /** Callback when node is selected */
  onSelect: (node: ExplanationNode) => void;
  /** Callback when drilldown is requested */
  onDrilldown?: (nodeId: string) => void;
  /** Show confidence values */
  showConfidence?: boolean;
  /** Maximum visible depth (0 = unlimited) */
  maxDepth?: number;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Get icon for step type
 */
function getStepIcon(type: string): string {
  switch (type) {
    case 'evidence':
      return '📄';
    case 'inference':
      return '🔍';
    case 'rule':
      return '📏';
    case 'context':
      return '📚';
    case 'verdict':
      return '⚖️';
    default:
      return '•';
  }
}

/**
 * Get confidence color
 */
function getConfidenceColor(confidence: number): string {
  if (confidence >= 0.8) return 'text-green-600';
  if (confidence >= 0.6) return 'text-yellow-600';
  if (confidence >= 0.4) return 'text-orange-600';
  return 'text-red-600';
}

/**
 * Tree node component
 */
interface TreeNodeProps {
  node: ExplanationNode;
  isExpanded: boolean;
  isSelected: boolean;
  onToggle: (nodeId: string) => void;
  onSelect: (node: ExplanationNode) => void;
  onDrilldown?: (nodeId: string) => void;
  expandedNodes: Set<string>;
  showConfidence: boolean;
  maxDepth: number;
  currentDepth: number;
}

const TreeNode: FC<TreeNodeProps> = memo(function TreeNode({
  node,
  isExpanded,
  isSelected,
  onToggle,
  onSelect,
  onDrilldown,
  expandedNodes,
  showConfidence,
  maxDepth,
  currentDepth,
}) {
  const hasChildren = node.children.length > 0;
  const canExpand = maxDepth === 0 || currentDepth < maxDepth;

  const handleToggle = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      onToggle(node.id);
    },
    [node.id, onToggle]
  );

  const handleSelect = useCallback(() => {
    onSelect(node);
  }, [node, onSelect]);

  const handleDrilldown = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      onDrilldown?.(node.id);
    },
    [node.id, onDrilldown]
  );

  return (
    <div className="tree-node" data-testid={`tree-node-${node.id}`}>
      {/* Node content */}
      <div
        className={`
          flex items-center gap-2 p-2 rounded cursor-pointer
          transition-colors duration-150
          ${isSelected ? 'bg-blue-100 ring-1 ring-blue-400' : 'hover:bg-gray-100'}
        `}
        onClick={handleSelect}
        role="treeitem"
        aria-expanded={hasChildren ? isExpanded : undefined}
        aria-selected={isSelected}
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter') handleSelect();
          if (e.key === 'ArrowRight' && hasChildren && !isExpanded) onToggle(node.id);
          if (e.key === 'ArrowLeft' && hasChildren && isExpanded) onToggle(node.id);
        }}
      >
        {/* Expand/collapse button */}
        {hasChildren && canExpand ? (
          <button
            onClick={handleToggle}
            className="w-5 h-5 flex items-center justify-center text-gray-400 hover:text-gray-600"
            aria-label={isExpanded ? 'Collapse' : 'Expand'}
            data-testid={`toggle-${node.id}`}
          >
            <svg
              className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-90' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        ) : (
          <span className="w-5" />
        )}

        {/* Icon */}
        <span className="text-lg" role="img" aria-label={node.step.type}>
          {getStepIcon(node.step.type)}
        </span>

        {/* Label */}
        <span className="flex-1 font-medium text-gray-900">{node.step.label}</span>

        {/* Confidence */}
        {showConfidence && (
          <span
            className={`text-sm font-mono ${getConfidenceColor(node.step.confidence)}`}
            data-testid={`confidence-${node.id}`}
          >
            {(node.step.confidence * 100).toFixed(0)}%
          </span>
        )}

        {/* Drilldown button */}
        {onDrilldown && (
          <button
            onClick={handleDrilldown}
            className="p-1 text-gray-400 hover:text-blue-600 transition-colors"
            aria-label="Drilldown"
            data-testid={`drilldown-${node.id}`}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </button>
        )}
      </div>

      {/* Description (shown when selected) */}
      {isSelected && (
        <div
          className="ml-7 pl-4 py-2 text-sm text-gray-600 border-l-2 border-blue-200"
          data-testid={`description-${node.id}`}
        >
          {node.step.description}
          {node.step.sources && node.step.sources.length > 0 && (
            <div className="mt-1 text-xs text-gray-400">
              Sources: {node.step.sources.join(', ')}
            </div>
          )}
        </div>
      )}

      {/* Children */}
      {hasChildren && isExpanded && canExpand && (
        <div className="ml-5 pl-4 border-l border-gray-200" role="group">
          {node.children.map((child) => (
            <TreeNode
              key={child.id}
              node={child}
              isExpanded={expandedNodes.has(child.id)}
              isSelected={false}
              onToggle={onToggle}
              onSelect={onSelect}
              onDrilldown={onDrilldown}
              expandedNodes={expandedNodes}
              showConfidence={showConfidence}
              maxDepth={maxDepth}
              currentDepth={currentDepth + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
});

/**
 * Empty state
 */
const EmptyState: FC = memo(function EmptyState() {
  return (
    <div
      className="flex flex-col items-center justify-center py-12 text-gray-500"
      data-testid="empty-tree"
    >
      <svg className="w-12 h-12 mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
        />
      </svg>
      <p className="text-sm">No explanation available</p>
    </div>
  );
});

/**
 * Explanation Tree View
 */
export const ExplainTreeView: FC<ExplainTreeViewProps> = memo(function ExplainTreeView({
  tree,
  expandedNodes,
  selectedNode,
  onToggle,
  onSelect,
  onDrilldown,
  showConfidence = true,
  maxDepth = 0,
  className = '',
}) {
  // Count total nodes
  const nodeCount = useMemo(() => {
    if (!tree) return 0;
    function count(node: ExplanationNode): number {
      return 1 + node.children.reduce((sum, child) => sum + count(child), 0);
    }
    return count(tree);
  }, [tree]);

  if (!tree) {
    return (
      <div className={`bg-white rounded-lg border border-gray-200 p-4 ${className}`}>
        <EmptyState />
      </div>
    );
  }

  return (
    <div
      className={`bg-white rounded-lg border border-gray-200 ${className}`}
      data-testid="explain-tree-view"
      role="tree"
      aria-label="Explanation tree"
    >
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
        <h3 className="font-semibold text-gray-900">Reasoning Tree</h3>
        <span className="text-xs text-gray-500">
          {nodeCount} {nodeCount === 1 ? 'node' : 'nodes'} · {expandedNodes.size} expanded
        </span>
      </div>

      {/* Tree content */}
      <div className="p-4">
        <TreeNode
          node={tree}
          isExpanded={expandedNodes.has(tree.id)}
          isSelected={selectedNode?.id === tree.id}
          onToggle={onToggle}
          onSelect={onSelect}
          onDrilldown={onDrilldown}
          expandedNodes={expandedNodes}
          showConfidence={showConfidence}
          maxDepth={maxDepth}
          currentDepth={0}
        />
      </div>
    </div>
  );
});

export default ExplainTreeView;
