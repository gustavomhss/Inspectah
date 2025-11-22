import ConsultationForm from '../components/consultation/ConsultationForm';
import ResultContainer from '../components/consultation/ResultContainer';
import { useConsultation } from '../hooks/useConsultation';
import type { ConsultationStatus } from '../types/inspectah';

function ConsultationPage() {
  const { status, submitQuestion } = useConsultation();

  const handleRetry = (currentStatus: ConsultationStatus) => {
    if (currentStatus.kind === 'error' && currentStatus.question) {
      submitQuestion(currentStatus.question);
    }
  };

  return (
    <section className="grid gap-6" aria-labelledby="consulta-heading">
      <div className="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-card">
        <ConsultationForm status={status} onSubmit={submitQuestion} />
      </div>
      <ResultContainer status={status} onRetry={() => handleRetry(status)} />
    </section>
  );
}

export default ConsultationPage;
