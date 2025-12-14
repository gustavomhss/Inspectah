/**
 * Guardian Pages Tests — S37
 *
 * Tests for Guardian Cockpit and related components.
 */

import { rest } from 'msw';
import { Route, Routes } from 'react-router-dom';
import { screen, waitFor, fireEvent } from '@testing-library/react';
import GuardianCockpitPage from '../../modules/guardian/pages/GuardianCockpitPage';
import { renderWithProviders } from '../test-utils';
import { server } from '../mocks/server';

const BASE_URL = 'http://localhost:8000';

// Mock data
const mockMetrics = {
  decisions_submitted: 100,
  decisions_approved: 80,
  decisions_rejected: 15,
  decisions_timed_out: 5,
  avg_latency_ms: 150.5,
  pending_decisions: 10,
  awaiting_review: 3,
  awaiting_quorum: 2,
};

const mockDecisions = [
  {
    id: 'dec_001',
    claim_id: 'claim_001',
    claim_summary: 'Lula foi condenado pelo TRF4',
    evidence_summary: ['Acórdão TRF4', 'Reportagem Folha'],
    domain: 'politics',
    gate: 'G7',
    proposed_state: 'verified',
    status: 'awaiting_review',
    policy_name: 'pilot_politics_v1',
    committee_id: null,
    final_state: null,
    final_reason: null,
    created_at: '2024-01-15T10:00:00Z',
    updated_at: '2024-01-15T10:00:00Z',
    completed_at: null,
  },
  {
    id: 'dec_002',
    claim_id: 'claim_002',
    claim_summary: 'Taxa Selic subiu para 11%',
    evidence_summary: ['Comunicado COPOM'],
    domain: 'economia',
    gate: 'G7',
    proposed_state: 'verified',
    status: 'approved',
    policy_name: 'economia_v1',
    committee_id: null,
    final_state: 'verified',
    final_reason: 'Auto-approved by policy',
    created_at: '2024-01-14T10:00:00Z',
    updated_at: '2024-01-14T10:01:00Z',
    completed_at: '2024-01-14T10:01:00Z',
  },
];

const mockPolicies = [
  {
    name: 'pilot_politics_v1',
    domain: 'politics',
    gate: 'G7',
    version: '1.0.0',
    requirements: 4,
    rules: 5,
  },
  {
    name: 'economia_v1',
    domain: 'economia',
    gate: 'G7',
    version: '1.0.0',
    requirements: 4,
    rules: 6,
  },
];

const mockPolicyDetail = {
  name: 'pilot_politics_v1',
  domain: 'politics',
  gate: 'G7',
  version: '1.0.0',
  requirements: [
    { field: 'sources', operator: '>=', value: 2, modifier: 'independent' },
    { field: 'evidence_strength', operator: '>=', value: 0.6, modifier: null },
    { field: 'no_contradiction', operator: '=', value: true, modifier: 'strong' },
    { field: 'temporal_consistency', operator: '=', value: true, modifier: null },
  ],
  rules: [
    { condition_field: 'high_confidence', condition_operator: '=', condition_value: true, action: 'auto_approve', action_params: {} },
    { condition_field: 'low_confidence', condition_operator: '=', condition_value: true, action: 'human_review', action_params: {} },
    { condition_field: 'disputed', condition_operator: '=', condition_value: true, action: 'human_review', action_params: {} },
    { condition_field: 'risk_level', condition_operator: '=', condition_value: 'high', action: 'committee_quorum', action_params: { quorum: 3 } },
    { condition_field: 'no_evidence', condition_operator: '=', condition_value: true, action: 'flag_for_review', action_params: {} },
  ],
  metadata: {},
};

describe('GuardianCockpitPage', () => {
  beforeEach(() => {
    // Set up default handlers
    server.use(
      rest.get(`${BASE_URL}/api/guardian/metrics`, (_req, res, ctx) =>
        res(ctx.status(200), ctx.json(mockMetrics))
      ),
      rest.get(`${BASE_URL}/api/guardian/decisions`, (_req, res, ctx) =>
        res(ctx.status(200), ctx.json(mockDecisions))
      ),
      rest.get(`${BASE_URL}/api/guardian/decisions/awaiting-review`, (_req, res, ctx) =>
        res(ctx.status(200), ctx.json([mockDecisions[0]]))
      ),
      rest.get(`${BASE_URL}/api/guardian/policies`, (_req, res, ctx) =>
        res(ctx.status(200), ctx.json(mockPolicies))
      ),
      rest.get(`${BASE_URL}/api/guardian/policies/:name`, (_req, res, ctx) =>
        res(ctx.status(200), ctx.json(mockPolicyDetail))
      ),
    );
  });

  it('renders cockpit with metrics', async () => {
    renderWithProviders(
      <Routes>
        <Route path="/admin/guardian" element={<GuardianCockpitPage />} />
      </Routes>,
      { route: '/admin/guardian' },
    );

    await waitFor(() => {
      expect(screen.getByText(/Guardian Cockpit/i)).toBeInTheDocument();
    });

    // Check metrics are displayed
    await waitFor(() => {
      expect(screen.getByText('100')).toBeInTheDocument(); // decisions_submitted
    });
  });

  it('displays policies list', async () => {
    renderWithProviders(
      <Routes>
        <Route path="/admin/guardian" element={<GuardianCockpitPage />} />
      </Routes>,
      { route: '/admin/guardian' },
    );

    // Wait for policies section to load
    await waitFor(
      () => {
        expect(screen.getByText(/Políticas Ativas/)).toBeInTheDocument();
      },
      { timeout: 3000 },
    );

    // Check that policy cards are rendered (via "Clique para ver detalhes" text)
    await waitFor(
      () => {
        const policyCards = screen.getAllByText(/Clique para ver detalhes/);
        expect(policyCards.length).toBeGreaterThanOrEqual(1);
      },
      { timeout: 3000 },
    );
  });

  it('displays decisions with claim summary', async () => {
    renderWithProviders(
      <Routes>
        <Route path="/admin/guardian" element={<GuardianCockpitPage />} />
      </Routes>,
      { route: '/admin/guardian' },
    );

    await waitFor(() => {
      expect(screen.getByText(/Lula foi condenado pelo TRF4/)).toBeInTheDocument();
    });
  });

  it('displays evidence summary on decision cards', async () => {
    renderWithProviders(
      <Routes>
        <Route path="/admin/guardian" element={<GuardianCockpitPage />} />
      </Routes>,
      { route: '/admin/guardian' },
    );

    await waitFor(() => {
      expect(screen.getByText(/Acórdão TRF4/)).toBeInTheDocument();
      expect(screen.getByText(/Reportagem Folha/)).toBeInTheDocument();
    });
  });

  it('opens policy details modal when clicking a policy', async () => {
    renderWithProviders(
      <Routes>
        <Route path="/admin/guardian" element={<GuardianCockpitPage />} />
      </Routes>,
      { route: '/admin/guardian' },
    );

    // Wait for policies to load
    await waitFor(
      () => {
        const policyCards = screen.getAllByText(/Clique para ver detalhes/);
        expect(policyCards.length).toBeGreaterThan(0);
      },
      { timeout: 3000 },
    );

    // Click on first policy card
    const policyCards = screen.getAllByText(/Clique para ver detalhes/);
    fireEvent.click(policyCards[0]);

    // Wait for modal with requirements
    await waitFor(
      () => {
        expect(screen.getByText(/Requisitos \(REQUIRE\)/i)).toBeInTheDocument();
      },
      { timeout: 3000 },
    );
  });

  it('shows rules in policy modal', async () => {
    renderWithProviders(
      <Routes>
        <Route path="/admin/guardian" element={<GuardianCockpitPage />} />
      </Routes>,
      { route: '/admin/guardian' },
    );

    // Wait for policies to load
    await waitFor(
      () => {
        const policyCards = screen.getAllByText(/Clique para ver detalhes/);
        expect(policyCards.length).toBeGreaterThan(0);
      },
      { timeout: 3000 },
    );

    // Click on first policy card
    const policyCards = screen.getAllByText(/Clique para ver detalhes/);
    fireEvent.click(policyCards[0]);

    // Wait for rules section
    await waitFor(
      () => {
        expect(screen.getByText(/Regras \(ON\.\.\.THEN\)/i)).toBeInTheDocument();
      },
      { timeout: 3000 },
    );
  });

  it('switches tabs correctly', async () => {
    renderWithProviders(
      <Routes>
        <Route path="/admin/guardian" element={<GuardianCockpitPage />} />
      </Routes>,
      { route: '/admin/guardian' },
    );

    await waitFor(() => {
      expect(screen.getByText(/Visão Geral/)).toBeInTheDocument();
    });

    // Click on Pending tab
    fireEvent.click(screen.getByText(/Pendentes/));

    await waitFor(() => {
      expect(screen.getByText(/Decisões Pendentes/)).toBeInTheDocument();
    });

    // Click on Completed tab (using role to be more specific)
    const completedTab = screen.getByRole('button', { name: /Concluídas/ });
    fireEvent.click(completedTab);

    await waitFor(() => {
      expect(screen.getByText(/Decisões Concluídas/)).toBeInTheDocument();
    });
  });

  it('handles API errors gracefully', async () => {
    server.use(
      rest.get(`${BASE_URL}/api/guardian/metrics`, (_req, res, ctx) =>
        res(ctx.status(500), ctx.json({ error: 'Server error' }))
      ),
    );

    renderWithProviders(
      <Routes>
        <Route path="/admin/guardian" element={<GuardianCockpitPage />} />
      </Routes>,
      { route: '/admin/guardian' },
    );

    await waitFor(() => {
      expect(screen.getByText(/Erro/i)).toBeInTheDocument();
    });
  });
});
