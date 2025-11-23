import { BrowserRouter } from 'react-router-dom';
import { ErrorBoundary } from './app/layout/ErrorBoundary';
import { AuthProvider } from './app/providers/AuthProvider';
import { LoggerProvider } from './app/providers/LoggerProvider';
import { AppRoutes } from './app/routes';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <LoggerProvider>
          <ErrorBoundary>
            <AppRoutes />
          </ErrorBoundary>
        </LoggerProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
