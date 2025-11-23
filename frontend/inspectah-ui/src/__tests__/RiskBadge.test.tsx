import { render, screen } from '@testing-library/react';
import RiskBadge from '../modules/consult/components/RiskBadge';
import type { RiskLevel } from '../core/api/api-types';

describe('RiskBadge', () => {
  it('renders labels and styles for each risk level', () => {
    const expectations: Record<RiskLevel, RegExp> = {
      low: /Risco baixo/i,
      medium: /Risco moderado/i,
      high: /Risco alto/i,
      unknown: /Risco incerto/i,
    };
    (Object.keys(expectations) as RiskLevel[]).forEach((level) => {
      const { unmount } = render(<RiskBadge riskLevel={level} riskScore={0.42} />);
      expect(screen.getByText(expectations[level])).toBeInTheDocument();
      unmount();
    });
  });

  it('shows score when provided', () => {
    render(<RiskBadge riskLevel="low" riskScore={0.87} />);
    expect(screen.getByText(/Score 0\.87/i)).toBeInTheDocument();
  });
});
