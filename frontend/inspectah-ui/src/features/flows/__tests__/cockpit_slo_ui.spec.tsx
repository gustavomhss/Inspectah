import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { FlowOpsPanel } from '../FlowOpsPanel';
import * as hooks from '../hooks';

describe('FlowOpsPanel', () => {
  it('renderiza SLOs com status', () => {
    vi.spyOn(hooks, 'useOpsFlows').mockReturnValue([
      { id: 'f1', slug: 'fluxo_noticias', flow_version_id: '2', slos: [{ id: 's34_slo_exec_latency_news_v2', status: 'OK' }] },
    ]);

    render(
      <MemoryRouter>
        <FlowOpsPanel flowSlug="fluxo_noticias" flowVersionId="2" />
      </MemoryRouter>,
    );

    expect(screen.getByText(/exec_latency_news_v2/i)).toBeInTheDocument();
    expect(screen.getByText(/OK/i)).toBeInTheDocument();
  });
});
