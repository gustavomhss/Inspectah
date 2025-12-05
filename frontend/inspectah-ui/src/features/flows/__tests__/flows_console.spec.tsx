import { act, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { FlowsListPage } from '../FlowsListPage';
import { FlowDetailPage } from '../FlowDetailPage';
import * as api from '../api';
import type { Flow } from '../types';

const flushPromises = () => new Promise((resolve) => setTimeout(resolve, 0));

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
    vi.spyOn(api, 'listFlowVersions').mockResolvedValue([]);
    vi.spyOn(api, 'listFlowOperations').mockResolvedValue([]);
    vi.spyOn(api, 'listOpsCockpitFlows').mockResolvedValue([]);
    await act(async () => {
      render(
        <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <FlowsListPage />
        </MemoryRouter>,
      );
    });
    expect(await screen.findByText('Fluxo Noticias')).toBeInTheDocument();
    expect(await screen.findByText('noticia_texto')).toBeInTheDocument();
  });

  it('permite navegar para detalhe e acionar mudança de estado', async () => {
    vi.spyOn(api, 'listFlowTemplates').mockResolvedValue([]);
    vi.spyOn(api, 'getFlow').mockResolvedValue({
      ...sampleFlows[0],
      steps: [],
    });
    vi.spyOn(api, 'listFlowExecutions').mockResolvedValue([]);
    vi.spyOn(api, 'listFlowVersions').mockResolvedValue([]);
    vi.spyOn(api, 'listFlowOperations').mockResolvedValue([]);
    vi.spyOn(api, 'listOpsCockpitFlows').mockResolvedValue([]);
    vi.spyOn(api, 'updateFlowState').mockResolvedValue({ ...sampleFlows[0], estado: 'em_teste', steps: [] });

    await act(async () => {
      render(
        <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }} initialEntries={['/flows/f1']}>
          <Routes>
            <Route path="/flows/:flowId" element={<FlowDetailPage />} />
          </Routes>
        </MemoryRouter>,
      );
      await flushPromises();
    });

    expect(await screen.findByText('Fluxo Noticias')).toBeInTheDocument();
    const button = screen.getByRole('button', { name: /Marcar em teste/i });
    await act(async () => {
      await userEvent.click(button);
      await flushPromises();
    });
    expect(api.updateFlowState).toHaveBeenCalled();
  });
});
