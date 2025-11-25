import { render, screen } from '@testing-library/react';
import IngestionModeBadge from '../IngestionModeBadge';
import IngestionStatusBadge from '../IngestionStatusBadge';
import IngestionTimeline from '../IngestionTimeline';
import IngestionProgressBar from '../IngestionProgressBar';
import type { IngestionRun } from '../../../../core/api/api-types';

describe('Ingestion components', () => {
  it('renderiza modo manual/automático', () => {
    const { rerender } = render(<IngestionModeBadge mode="MANUAL_ONLY" />);
    expect(screen.getByText(/Manual/)).toBeInTheDocument();
    rerender(<IngestionModeBadge mode="AUTOMATIC" />);
    expect(screen.getByText(/Automático/)).toBeInTheDocument();
  });

  it('exibe labels de status', () => {
    const { rerender } = render(<IngestionStatusBadge status="RUNNING" />);
    expect(screen.getByText(/Em andamento/)).toBeInTheDocument();
    rerender(<IngestionStatusBadge status="SUCCESS" />);
    expect(screen.getByText(/Sucesso/)).toBeInTheDocument();
    rerender(<IngestionStatusBadge status={undefined} showNever />);
    expect(screen.getByText(/Nunca rodou/)).toBeInTheDocument();
  });

  it('ordena runs na timeline', () => {
    const runs: IngestionRun[] = [
      { id: 'run_b', source_id: 's', status: 'SUCCESS', trigger: 'M', started_at: '2024-01-02T00:00:00Z' },
      { id: 'run_a', source_id: 's', status: 'FAIL', trigger: 'M', started_at: '2024-01-01T00:00:00Z' },
    ];
    render(<IngestionTimeline runs={runs} />);
    const buttons = screen.getAllByRole('button');
    expect(buttons[0]).toHaveAttribute('aria-label', expect.stringContaining('run_a'));
  });

  it('exibe barra de progresso coerente com status', () => {
    render(<IngestionProgressBar status="RUNNING" progress={45} />);
    expect(screen.getByText(/45%/)).toBeInTheDocument();
    const { rerender } = render(<IngestionProgressBar status="SUCCESS" progress={100} />);
    rerender(<IngestionProgressBar status="FAIL" progress={100} />);
    expect(screen.getByText(/Falhou/)).toBeInTheDocument();
  });
});
