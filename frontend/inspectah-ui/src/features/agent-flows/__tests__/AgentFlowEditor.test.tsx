import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import AgentFlowEditor from '../components/AgentFlowEditor';
import type { AgentFlowConfigForm } from '../agentFlowsTypes';

const baseFlow: AgentFlowConfigForm = {
  domain_key: 'news_politics',
  name: 'Fluxo política',
  description: 'Fluxo base',
  is_active: true,
  change_reason: 'seed',
  steps: [
    { position: 1, agent_role: 'interpreter', params: {} },
    { position: 2, agent_role: 'classifier', params: {} },
    { position: 3, agent_role: 'decision_maker', params: { threshold: 0.7 } },
  ],
};

describe('AgentFlowEditor', () => {
  it('renders steps and allows adding a new one', async () => {
    const user = userEvent.setup();
    render(<AgentFlowEditor initialFlow={baseFlow} onSave={async () => {}} saving={false} error={null} clearError={() => {}} />);

    expect(screen.getByText('#1')).toBeInTheDocument();
    expect(screen.getByText('#3')).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /Adicionar passo/i }));
    expect(screen.getByText('#4')).toBeInTheDocument();
  });

  it('shows backend errors', () => {
    render(
      <AgentFlowEditor
        initialFlow={baseFlow}
        onSave={async () => {}}
        saving={false}
        error="Missing required roles"
        clearError={() => {}}
      />,
    );
    expect(screen.getByText(/Missing required roles/i)).toBeInTheDocument();
  });
});
