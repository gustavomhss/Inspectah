import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { rest } from 'msw';
import { act } from 'react';
import ConsultPage from '../modules/consult/pages/ConsultPage';
import { server } from './mocks/server';
import { renderWithProviders } from './test-utils';
import { buildResponse, errorHandler, highRiskHandler, unknownRiskHandler } from './mocks/handlers';

const API_URL = 'http://localhost:8000/api/consultation';

describe('ConsultationPage', () => {
  it('shows empty state on load', () => {
    renderWithProviders(<ConsultPage />, { withRouter: false });
    expect(screen.getByText(/Pronto para consultar/i)).toBeInTheDocument();
  });

  it('submits a question and renders the response', async () => {
    renderWithProviders(<ConsultPage />, { withRouter: false });
    await act(async () => {
      await userEvent.type(screen.getByLabelText(/Pergunta em linguagem natural/i), 'O fato procede?');
      await userEvent.click(screen.getByRole('button', { name: /Consultar/i }));
    });

    expect(await screen.findByText(/Sim, o fato foi confirmado/i)).toBeInTheDocument();
    expect(screen.getByText(/Risco baixo/i)).toBeInTheDocument();
  });

  it('handles high risk responses', async () => {
    server.use(highRiskHandler);
    renderWithProviders(<ConsultPage />, { withRouter: false });
    await act(async () => {
      await userEvent.type(screen.getByLabelText(/Pergunta em linguagem natural/i), 'Caso de alto risco?');
      await userEvent.click(screen.getByRole('button', { name: /Consultar/i }));
    });

    expect(await screen.findByText(/Risco alto/i)).toBeInTheDocument();
  });

  it('handles unknown risk responses', async () => {
    server.use(unknownRiskHandler);
    renderWithProviders(<ConsultPage />, { withRouter: false });
    await act(async () => {
      await userEvent.type(screen.getByLabelText(/Pergunta em linguagem natural/i), 'Caso incerto?');
      await userEvent.click(screen.getByRole('button', { name: /Consultar/i }));
    });

    expect(await screen.findByText(/Risco incerto/i)).toBeInTheDocument();
    expect(screen.getByText(/Sinais de atenção/)).toBeInTheDocument();
  });

  it('renders error state for backend failures', async () => {
    server.use(errorHandler(500));
    renderWithProviders(<ConsultPage />, { withRouter: false });
    await act(async () => {
      await userEvent.type(screen.getByLabelText(/Pergunta em linguagem natural/i), 'Vai falhar?');
      await userEvent.click(screen.getByRole('button', { name: /Consultar/i }));
    });

    expect(await screen.findByText(/Erro no backend do Inspectah/i)).toBeInTheDocument();
  });

  it('renders error state for network issues', async () => {
    server.use(
      rest.post(API_URL, async (_req, res) => {
        return res.networkError('Network down');
      }),
    );

    renderWithProviders(<ConsultPage />, { withRouter: false });
    await act(async () => {
      await userEvent.type(screen.getByLabelText(/Pergunta em linguagem natural/i), 'Sem rede?');
      await userEvent.click(screen.getByRole('button', { name: /Consultar/i }));
    });

    expect(await screen.findByText(/Não conseguimos falar com o Inspectah agora/i)).toBeInTheDocument();
  });

  it('shows friendly message when response has insufficient data', async () => {
    server.use(
      rest.post(API_URL, async (_req, res, ctx) => {
        return res(ctx.status(200), ctx.json(buildResponse({ risk_level: 'unknown', evidences: [] })));
      }),
    );

    renderWithProviders(<ConsultPage />, { withRouter: false });
    await act(async () => {
      await userEvent.type(screen.getByLabelText(/Pergunta em linguagem natural/i), 'Dados insuficientes?');
      await userEvent.click(screen.getByRole('button', { name: /Consultar/i }));
    });

    expect(await screen.findByText(/Evidências principais/)).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText(/não há evidências suficientes/i)).toBeInTheDocument();
    });
  });
});
