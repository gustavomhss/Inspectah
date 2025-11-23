import PageContainer from '../../../shared/layout/PageContainer';
import PageHeader from '../../../shared/layout/PageHeader';
import ConsultationForm from '../components/ConsultationForm';
import ResultContainer from '../components/ResultContainer';
import { useConsultQuery } from '../hooks/useConsultQuery';
import type { ConsultationStatus } from '../../../core/api/api-types';

function ConsultPage() {
  const { status, submitQuestion } = useConsultQuery();

  const handleRetry = (currentStatus: ConsultationStatus) => {
    if (currentStatus.kind === 'error' && currentStatus.question) {
      submitQuestion(currentStatus.question);
    }
  };

  return (
    <section className="grid gap-6" aria-labelledby="consulta-heading">
      <PageHeader
        title="Consulta pública"
        subtitle="Pergunte sobre fatos/casos/temas e veja resposta consolidada, risco e estado de verdade."
      />
      <PageContainer>
        <ConsultationForm status={status} onSubmit={submitQuestion} />
      </PageContainer>
      <PageContainer>
        <ResultContainer status={status} onRetry={() => handleRetry(status)} />
      </PageContainer>
    </section>
  );
}

export default ConsultPage;
