/**
 * Tests for ExplainTreeView component (T-TEST-UNIT-004)
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, within } from '@testing-library/react';
import { ExplainTreeView } from '../../modules/explain/components/ExplainTreeView';
import type { ExplanationNode } from '../../modules/explain/types';

// Mock tree data
const createMockTree = (): ExplanationNode => ({
  id: 'root',
  step: {
    id: 'root_step',
    type: 'verdict',
    label: 'Final Verdict',
    description: 'This claim has been determined to be false.',
    confidence: 0.85,
    sources: ['source_1', 'source_2'],
  },
  children: [
    {
      id: 'child_1',
      step: {
        id: 'child_1_step',
        type: 'evidence',
        label: 'Evidence Analysis',
        description: 'Analyzed 5 sources',
        confidence: 0.9,
        sources: ['src_a'],
      },
      children: [],
      depth: 1,
    },
    {
      id: 'child_2',
      step: {
        id: 'child_2_step',
        type: 'inference',
        label: 'Logical Inference',
        description: 'Applied deductive reasoning',
        confidence: 0.75,
      },
      children: [
        {
          id: 'grandchild_1',
          step: {
            id: 'grandchild_1_step',
            type: 'rule',
            label: 'Rule Application',
            description: 'Applied fact-checking rule',
            confidence: 0.95,
          },
          children: [],
          depth: 2,
        },
      ],
      depth: 1,
    },
  ],
  depth: 0,
});

describe('ExplainTreeView', () => {
  describe('rendering', () => {
    it('should render empty state when tree is null', () => {
      render(
        <ExplainTreeView
          tree={null}
          expandedNodes={new Set()}
          selectedNode={null}
          onToggle={vi.fn()}
          onSelect={vi.fn()}
        />
      );

      expect(screen.getByTestId('empty-tree')).toBeInTheDocument();
      expect(screen.getByText('No explanation available')).toBeInTheDocument();
    });

    it('should render tree with root node', () => {
      const tree = createMockTree();

      render(
        <ExplainTreeView
          tree={tree}
          expandedNodes={new Set()}
          selectedNode={null}
          onToggle={vi.fn()}
          onSelect={vi.fn()}
        />
      );

      expect(screen.getByTestId('explain-tree-view')).toBeInTheDocument();
      expect(screen.getByTestId('tree-node-root')).toBeInTheDocument();
      expect(screen.getByText('Final Verdict')).toBeInTheDocument();
    });

    it('should show header with node count', () => {
      const tree = createMockTree();

      render(
        <ExplainTreeView
          tree={tree}
          expandedNodes={new Set()}
          selectedNode={null}
          onToggle={vi.fn()}
          onSelect={vi.fn()}
        />
      );

      expect(screen.getByText('Reasoning Tree')).toBeInTheDocument();
      expect(screen.getByText(/4 nodes/)).toBeInTheDocument(); // root + 2 children + 1 grandchild
    });

    it('should show expanded count', () => {
      const tree = createMockTree();

      render(
        <ExplainTreeView
          tree={tree}
          expandedNodes={new Set(['root', 'child_2'])}
          selectedNode={null}
          onToggle={vi.fn()}
          onSelect={vi.fn()}
        />
      );

      expect(screen.getByText(/2 expanded/)).toBeInTheDocument();
    });
  });

  describe('expansion', () => {
    it('should show expand button for nodes with children', () => {
      const tree = createMockTree();

      render(
        <ExplainTreeView
          tree={tree}
          expandedNodes={new Set()}
          selectedNode={null}
          onToggle={vi.fn()}
          onSelect={vi.fn()}
        />
      );

      expect(screen.getByTestId('toggle-root')).toBeInTheDocument();
    });

    it('should call onToggle when expand button is clicked', () => {
      const tree = createMockTree();
      const onToggle = vi.fn();

      render(
        <ExplainTreeView
          tree={tree}
          expandedNodes={new Set()}
          selectedNode={null}
          onToggle={onToggle}
          onSelect={vi.fn()}
        />
      );

      fireEvent.click(screen.getByTestId('toggle-root'));
      expect(onToggle).toHaveBeenCalledWith('root');
    });

    it('should show children when node is expanded', () => {
      const tree = createMockTree();

      render(
        <ExplainTreeView
          tree={tree}
          expandedNodes={new Set(['root'])}
          selectedNode={null}
          onToggle={vi.fn()}
          onSelect={vi.fn()}
        />
      );

      expect(screen.getByTestId('tree-node-child_1')).toBeInTheDocument();
      expect(screen.getByTestId('tree-node-child_2')).toBeInTheDocument();
    });

    it('should hide children when node is collapsed', () => {
      const tree = createMockTree();

      render(
        <ExplainTreeView
          tree={tree}
          expandedNodes={new Set()}
          selectedNode={null}
          onToggle={vi.fn()}
          onSelect={vi.fn()}
        />
      );

      expect(screen.queryByTestId('tree-node-child_1')).not.toBeInTheDocument();
      expect(screen.queryByTestId('tree-node-child_2')).not.toBeInTheDocument();
    });

    it('should show nested children when parent is expanded', () => {
      const tree = createMockTree();

      render(
        <ExplainTreeView
          tree={tree}
          expandedNodes={new Set(['root', 'child_2'])}
          selectedNode={null}
          onToggle={vi.fn()}
          onSelect={vi.fn()}
        />
      );

      expect(screen.getByTestId('tree-node-grandchild_1')).toBeInTheDocument();
    });
  });

  describe('selection', () => {
    it('should call onSelect when node is clicked', () => {
      const tree = createMockTree();
      const onSelect = vi.fn();

      render(
        <ExplainTreeView
          tree={tree}
          expandedNodes={new Set()}
          selectedNode={null}
          onToggle={vi.fn()}
          onSelect={onSelect}
        />
      );

      const nodeElement = screen.getByTestId('tree-node-root');
      fireEvent.click(within(nodeElement).getByRole('treeitem'));

      expect(onSelect).toHaveBeenCalledWith(tree);
    });

    it('should show description when node is selected', () => {
      const tree = createMockTree();

      render(
        <ExplainTreeView
          tree={tree}
          expandedNodes={new Set()}
          selectedNode={tree}
          onToggle={vi.fn()}
          onSelect={vi.fn()}
        />
      );

      expect(screen.getByTestId('description-root')).toBeInTheDocument();
      expect(
        screen.getByText('This claim has been determined to be false.')
      ).toBeInTheDocument();
    });

    it('should show sources in description when available', () => {
      const tree = createMockTree();

      render(
        <ExplainTreeView
          tree={tree}
          expandedNodes={new Set()}
          selectedNode={tree}
          onToggle={vi.fn()}
          onSelect={vi.fn()}
        />
      );

      expect(screen.getByText(/source_1, source_2/)).toBeInTheDocument();
    });

    it('should highlight selected node', () => {
      const tree = createMockTree();

      render(
        <ExplainTreeView
          tree={tree}
          expandedNodes={new Set()}
          selectedNode={tree}
          onToggle={vi.fn()}
          onSelect={vi.fn()}
        />
      );

      const treeItem = within(screen.getByTestId('tree-node-root')).getByRole('treeitem');
      expect(treeItem).toHaveClass('bg-blue-100');
    });
  });

  describe('confidence display', () => {
    it('should show confidence when showConfidence is true', () => {
      const tree = createMockTree();

      render(
        <ExplainTreeView
          tree={tree}
          expandedNodes={new Set()}
          selectedNode={null}
          onToggle={vi.fn()}
          onSelect={vi.fn()}
          showConfidence
        />
      );

      expect(screen.getByTestId('confidence-root')).toBeInTheDocument();
      expect(screen.getByText('85%')).toBeInTheDocument();
    });

    it('should hide confidence when showConfidence is false', () => {
      const tree = createMockTree();

      render(
        <ExplainTreeView
          tree={tree}
          expandedNodes={new Set()}
          selectedNode={null}
          onToggle={vi.fn()}
          onSelect={vi.fn()}
          showConfidence={false}
        />
      );

      expect(screen.queryByTestId('confidence-root')).not.toBeInTheDocument();
    });
  });

  describe('drilldown', () => {
    it('should show drilldown button when onDrilldown is provided', () => {
      const tree = createMockTree();

      render(
        <ExplainTreeView
          tree={tree}
          expandedNodes={new Set()}
          selectedNode={null}
          onToggle={vi.fn()}
          onSelect={vi.fn()}
          onDrilldown={vi.fn()}
        />
      );

      expect(screen.getByTestId('drilldown-root')).toBeInTheDocument();
    });

    it('should call onDrilldown when drilldown button is clicked', () => {
      const tree = createMockTree();
      const onDrilldown = vi.fn();

      render(
        <ExplainTreeView
          tree={tree}
          expandedNodes={new Set()}
          selectedNode={null}
          onToggle={vi.fn()}
          onSelect={vi.fn()}
          onDrilldown={onDrilldown}
        />
      );

      fireEvent.click(screen.getByTestId('drilldown-root'));
      expect(onDrilldown).toHaveBeenCalledWith('root');
    });

    it('should not show drilldown button when onDrilldown is not provided', () => {
      const tree = createMockTree();

      render(
        <ExplainTreeView
          tree={tree}
          expandedNodes={new Set()}
          selectedNode={null}
          onToggle={vi.fn()}
          onSelect={vi.fn()}
        />
      );

      expect(screen.queryByTestId('drilldown-root')).not.toBeInTheDocument();
    });
  });

  describe('keyboard navigation', () => {
    it('should call onSelect on Enter key', () => {
      const tree = createMockTree();
      const onSelect = vi.fn();

      render(
        <ExplainTreeView
          tree={tree}
          expandedNodes={new Set()}
          selectedNode={null}
          onToggle={vi.fn()}
          onSelect={onSelect}
        />
      );

      const treeItem = within(screen.getByTestId('tree-node-root')).getByRole('treeitem');
      fireEvent.keyDown(treeItem, { key: 'Enter' });

      expect(onSelect).toHaveBeenCalledWith(tree);
    });

    it('should expand on ArrowRight when collapsed', () => {
      const tree = createMockTree();
      const onToggle = vi.fn();

      render(
        <ExplainTreeView
          tree={tree}
          expandedNodes={new Set()}
          selectedNode={null}
          onToggle={onToggle}
          onSelect={vi.fn()}
        />
      );

      const treeItem = within(screen.getByTestId('tree-node-root')).getByRole('treeitem');
      fireEvent.keyDown(treeItem, { key: 'ArrowRight' });

      expect(onToggle).toHaveBeenCalledWith('root');
    });

    it('should collapse on ArrowLeft when expanded', () => {
      const tree = createMockTree();
      const onToggle = vi.fn();

      render(
        <ExplainTreeView
          tree={tree}
          expandedNodes={new Set(['root'])}
          selectedNode={null}
          onToggle={onToggle}
          onSelect={vi.fn()}
        />
      );

      // Get the first treeitem (root's direct treeitem, not children's)
      const treeItems = within(screen.getByTestId('tree-node-root')).getAllByRole('treeitem');
      fireEvent.keyDown(treeItems[0], { key: 'ArrowLeft' });

      expect(onToggle).toHaveBeenCalledWith('root');
    });
  });

  describe('max depth', () => {
    it('should respect maxDepth when expanding', () => {
      const tree = createMockTree();

      render(
        <ExplainTreeView
          tree={tree}
          expandedNodes={new Set(['root', 'child_2'])}
          selectedNode={null}
          onToggle={vi.fn()}
          onSelect={vi.fn()}
          maxDepth={1}
        />
      );

      // Should show first level children
      expect(screen.getByTestId('tree-node-child_1')).toBeInTheDocument();
      expect(screen.getByTestId('tree-node-child_2')).toBeInTheDocument();

      // Should not show grandchildren (depth 2 > maxDepth 1)
      expect(screen.queryByTestId('tree-node-grandchild_1')).not.toBeInTheDocument();
    });

    it('should show all levels when maxDepth is 0', () => {
      const tree = createMockTree();

      render(
        <ExplainTreeView
          tree={tree}
          expandedNodes={new Set(['root', 'child_2'])}
          selectedNode={null}
          onToggle={vi.fn()}
          onSelect={vi.fn()}
          maxDepth={0}
        />
      );

      expect(screen.getByTestId('tree-node-grandchild_1')).toBeInTheDocument();
    });
  });

  describe('accessibility', () => {
    it('should have tree role', () => {
      const tree = createMockTree();

      render(
        <ExplainTreeView
          tree={tree}
          expandedNodes={new Set()}
          selectedNode={null}
          onToggle={vi.fn()}
          onSelect={vi.fn()}
        />
      );

      expect(screen.getByRole('tree')).toBeInTheDocument();
    });

    it('should have treeitem role for nodes', () => {
      const tree = createMockTree();

      render(
        <ExplainTreeView
          tree={tree}
          expandedNodes={new Set()}
          selectedNode={null}
          onToggle={vi.fn()}
          onSelect={vi.fn()}
        />
      );

      expect(screen.getByRole('treeitem')).toBeInTheDocument();
    });

    it('should have aria-expanded on expandable nodes', () => {
      const tree = createMockTree();

      render(
        <ExplainTreeView
          tree={tree}
          expandedNodes={new Set(['root'])}
          selectedNode={null}
          onToggle={vi.fn()}
          onSelect={vi.fn()}
        />
      );

      // Get the first treeitem (root's direct treeitem, not children's)
      const treeItems = within(screen.getByTestId('tree-node-root')).getAllByRole('treeitem');
      expect(treeItems[0]).toHaveAttribute('aria-expanded', 'true');
    });

    it('should have aria-selected on selected node', () => {
      const tree = createMockTree();

      render(
        <ExplainTreeView
          tree={tree}
          expandedNodes={new Set()}
          selectedNode={tree}
          onToggle={vi.fn()}
          onSelect={vi.fn()}
        />
      );

      const treeItem = within(screen.getByTestId('tree-node-root')).getByRole('treeitem');
      expect(treeItem).toHaveAttribute('aria-selected', 'true');
    });
  });

  describe('custom className', () => {
    it('should apply custom className', () => {
      const tree = createMockTree();

      render(
        <ExplainTreeView
          tree={tree}
          expandedNodes={new Set()}
          selectedNode={null}
          onToggle={vi.fn()}
          onSelect={vi.fn()}
          className="custom-class"
        />
      );

      expect(screen.getByTestId('explain-tree-view')).toHaveClass('custom-class');
    });
  });
});
