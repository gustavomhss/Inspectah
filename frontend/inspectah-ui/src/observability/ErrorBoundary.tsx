import { Component, type ErrorInfo, type ReactNode } from 'react';
import { logUiError } from './logEvents';

interface ErrorBoundaryProps {
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  message?: string;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, message: error.message };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    logUiError(error, info);
  }

  handleReset = () => {
    this.setState({ hasError: false, message: undefined });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      return (
        <div className="mx-auto mt-12 max-w-2xl rounded-xl border border-white/10 bg-white/5 p-6 text-slate-50 shadow-card" role="alert">
          <h2 className="text-xl font-semibold text-white">Algo deu errado na interface</h2>
          <p className="mt-2 text-sm text-slate-200">{this.state.message || 'Tente novamente em instantes.'}</p>
          <button
            type="button"
            onClick={this.handleReset}
            className="mt-4 inline-flex items-center gap-2 rounded-md bg-white/10 px-4 py-2 text-sm font-semibold text-white transition hover:bg-white/20 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-300"
          >
            Tentar novamente
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
