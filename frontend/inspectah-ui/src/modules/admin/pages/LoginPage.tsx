import { FormEvent, useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../../app/providers/AuthProvider';
import { useLogger } from '../../../app/providers/LoggerProvider';
import Button from '../../../shared/components/Button';
import ErrorMessage from '../../../shared/components/ErrorMessage';
import Input from '../../../shared/components/Input';
import PageContainer from '../../../shared/layout/PageContainer';
import PageHeader from '../../../shared/layout/PageHeader';

interface LocationState {
  from?: { pathname?: string };
}

function LoginPage() {
  const { login } = useAuth();
  const { logEvent, logError } = useLogger();
  const navigate = useNavigate();
  const location = useLocation();
  const redirectTo = (location.state as LocationState | undefined)?.from?.pathname || '/admin';

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    logEvent('admin.page_open', { page: 'login' });
  }, [logEvent]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login({ username, password });
      logEvent('navigation', { from: 'login', to: redirectTo });
      navigate(redirectTo, { replace: true });
    } catch (err) {
      const message = (err as Error).message || 'Falha ao autenticar. Tente novamente.';
      setError(message);
      logError(err, { event: 'auth.login_failed' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <PageContainer>
      <PageHeader
        title="Entrar no Inspectah"
        subtitle="Acesso protegido às áreas de admin, timeline e raio-X."
      />
      <form className="mt-4 space-y-4" onSubmit={handleSubmit}>
        <Input
          label="Usuário"
          name="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          autoComplete="username"
          required
        />
        <Input
          label="Senha"
          type="password"
          name="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="current-password"
          required
        />
        {error ? <ErrorMessage message={error} /> : null}
        <div className="flex justify-end">
          <Button type="submit" disabled={loading} aria-busy={loading}>
            {loading ? 'Entrando...' : 'Entrar'}
          </Button>
        </div>
      </form>
    </PageContainer>
  );
}

export default LoginPage;
