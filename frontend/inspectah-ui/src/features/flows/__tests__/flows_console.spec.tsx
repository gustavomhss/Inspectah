import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { FlowsListPage } from '../FlowsListPage';
import { FlowDetailPage } from '../FlowDetailPage';
import * as api from '../api';
import type { Flow } from '../types';

const sampleFlows: Flow[] = [
  {
    id: 'f1',
    nome: 'Fluxo Noticias',
    slug: 'fluxo_noticias',
    tipo_entrada: 'noticia_texto',
    estado: 'draft',
    template_origem_id: 'tpl1',
    percentual_teste: 0,
  },
];

describe('Console de Fluxos', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renderiza lista de fluxos', async () => {
    vi.spyOn(api, 'listFlows').mockResolvedValue(sampleFlows);
    vi.spyOn(api, 'listFlowTemplates').mockResolvedValue([]);
    render(
      <MemoryRouter>
        <FlowsListPage />
      </MemoryRouter>,
    );
    await waitFor(() => expect(screen.getByText('Fluxo Noticias')).toBeInTheDocument());
    expect(screen.getByText('noticia_texto')).toBeInTheDocument();
  });

  it('permite navegar para detalhe e acionar mudança de estado', async () => {
    vi.spyOn(api, 'listFlowTemplates').mockResolvedValue([]);
    vi.spyOn(api, 'getFlow').mockResolvedValue({
      ...sampleFlows[0],
      steps: [],
    });
    vi.spyOn(api, 'listFlowExecutions').mockResolvedValue([]);
    vi.spyOn(api, 'updateFlowState').mockResolvedValue({ ...sampleFlows[0], estado: 'em_teste', steps: [] });

    render(
      <MemoryRouter initialEntries={['/flows/f1']}>
        <Routes>
          <Route path="/flows/:flowId" element={<FlowDetailPage />} />
        </Routes>
      </MemoryRouter>,
    );

    await waitFor(() => expect(screen.getByText('Fluxo Noticias')).toBeInTheDocument());
    const button = screen.getByRole('button', { name: /Marcar em teste/i });
    await userEvent.click(button);
    await waitFor(() => expect(api.updateFlowState).toHaveBeenCalled());
  });
});
