import { render, type RenderOptions } from '@testing-library/react';
import type { ReactElement, ReactNode } from 'react';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider } from '../app/providers/AuthProvider';
import { LoggerProvider } from '../app/providers/LoggerProvider';

interface WrapperOptions {
  route?: string;
  withRouter?: boolean;
}

export function renderWithProviders(
  ui: ReactElement,
  { route = '/', ...options }: WrapperOptions & Omit<RenderOptions, 'wrapper'> = {},
) {
  function Wrapper({ children }: { children: ReactNode }) {
    return (
      <MemoryRouter initialEntries={[route]}>
        <AuthProvider>
          <LoggerProvider>{children}</LoggerProvider>
        </AuthProvider>
      </MemoryRouter>
    );
  }

  return render(ui, { wrapper: Wrapper, ...options });
}
