import { render, screen } from '@testing-library/react';
import ResultContainer from '../modules/consult/components/ResultContainer';
import type { ConsultationStatus } from '../core/api/api-types';

const successStatus: ConsultationStatus = {
  kind: 'success',
  question: 'Existe risco?',
  result: {
    answer: 'Resposta simulada',
    riskLevel: 'medium',
    riskScore: 0.45,
    riskFlags: ['Poucas fontes confiáveis'],
    evidences: [
      {
        id: 'ev1',
        sourceName: 'Fonte A',
        sourceType: 'artigo',
        description: 'Descrição da evidência',
        link: 'https://example.com',
      },
    ],
  },
};

describe('ResultContainer', () => {
  it('renders empty state when idle', () => {
    render(<ResultContainer status={{ kind: 'idle' }} />);
    expect(screen.getByText(/Pronto para consultar/i)).toBeInTheDocument();
  });

  it('renders loading state when submitting', () => {
    render(<ResultContainer status={{ kind: 'submitting', question: 'teste' }} />);
    expect(screen.getByRole('status', { hidden: true })).toHaveAttribute('aria-busy', 'true');
  });

  it('renders error state', () => {
    render(<ResultContainer status={{ kind: 'error', message: 'Falha' }} />);
    expect(screen.getByText(/Não conseguimos concluir a consulta/i)).toBeInTheDocument();
  });

  it('renders success state with answer and evidence', () => {
    render(<ResultContainer status={successStatus} />);
    expect(screen.getByText('Resposta simulada')).toBeInTheDocument();
    expect(screen.getByText(/Fonte A/)).toBeInTheDocument();
    expect(screen.getByText(/Risco moderado/i)).toBeInTheDocument();
  });
});
