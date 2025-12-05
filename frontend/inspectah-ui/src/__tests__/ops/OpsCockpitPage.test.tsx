import { Route, Routes } from 'react-router-dom';
import { screen, waitFor } from '@testing-library/react';
import OpsCockpitPage from '../../modules/ops/pages/OpsCockpitPage';
import { renderWithProviders } from '../test-utils';

describe('OpsCockpitPage', () => {
  it('renderiza overview, componentes, SLOs e incidentes', async () => {
    renderWithProviders(
      <Routes>
        <Route path="/admin/ops/cockpit" element={<OpsCockpitPage />} />
      </Routes>,
      { route: '/admin/ops/cockpit' },
    );

    await waitFor(() => {
      expect(screen.getByText(/OracleOps Cockpit v1/i)).toBeInTheDocument();
      expect(screen.getAllByText('fonte_noticias_principal').length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText('pipeline_noticias').length).toBeGreaterThanOrEqual(1);
      expect(screen.getByText('s33_slo_recencia_fonte_noticias')).toBeInTheDocument();
      expect(screen.getByText('inc1')).toBeInTheDocument();
    });
  });
});
