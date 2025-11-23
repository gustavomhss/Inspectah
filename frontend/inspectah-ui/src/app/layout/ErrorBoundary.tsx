import React, { Component, type ErrorInfo, type ReactNode } from 'react';
import ErrorMessage from '../../shared/components/ErrorMessage';
import { LoggerContext } from '../providers/LoggerProvider';

interface ErrorBoundaryProps {
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  message?: string;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  static contextType = LoggerContext;

  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, message: error.message };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    const logger = this.context as React.ContextType<typeof LoggerContext> | undefined;
    logger?.logError(error, { scope: 'error_boundary', info });
  }

  handleReset = () => {
    this.setState({ hasError: false, message: undefined });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      return (
        <div className="mx-auto mt-12 max-w-2xl" role="alert">
          <ErrorMessage
            title="Algo deu errado na interface"
            message={this.state.message || 'Tente novamente em instantes.'}
            onRetry={this.handleReset}
          />
        </div>
      );
    }

    return this.props.children;
  }
}
