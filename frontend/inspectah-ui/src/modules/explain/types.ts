/**
 * S39-W4: Explanation Types
 *
 * Type definitions for claim explanations and decision trees.
 */

/**
 * Single reasoning step in an explanation
 */
export interface ExplanationStep {
  id: string;
  type: 'evidence' | 'inference' | 'rule' | 'context' | 'verdict';
  label: string;
  description: string;
  confidence: number;
  sources?: string[];
  metadata?: Record<string, unknown>;
}

/**
 * Tree node for explanation visualization
 */
export interface ExplanationNode {
  id: string;
  step: ExplanationStep;
  children: ExplanationNode[];
  depth: number;
  expanded?: boolean;
}

/**
 * Factor contributing to a decision
 */
export interface DecisionFactor {
  id: string;
  name: string;
  weight: number;
  value: number;
  impact: 'positive' | 'negative' | 'neutral';
  description: string;
}

/**
 * Full claim explanation response
 */
export interface ClaimExplanation {
  claim_id: string;
  verdict: string;
  confidence: number;
  summary: string;
  steps: ExplanationStep[];
  factors: DecisionFactor[];
  tree: ExplanationNode;
  generated_at: string;
  model_version: string;
}

/**
 * Drilldown request for specific node
 */
export interface DrilldownRequest {
  claim_id: string;
  node_id: string;
  depth?: number;
}

/**
 * Comparison between two explanations
 */
export interface ExplanationComparison {
  explanation_a: ClaimExplanation;
  explanation_b: ClaimExplanation;
  differences: {
    verdict_changed: boolean;
    confidence_delta: number;
    new_factors: DecisionFactor[];
    removed_factors: DecisionFactor[];
    changed_factors: Array<{
      factor_id: string;
      old_value: number;
      new_value: number;
    }>;
  };
}

/**
 * Export format options
 */
export type ExportFormat = 'json' | 'pdf' | 'markdown';

/**
 * Export request
 */
export interface ExportRequest {
  claim_id: string;
  format: ExportFormat;
  include_tree?: boolean;
  include_factors?: boolean;
}
