import { useState } from 'react';
import type { AgentTrace } from '../../../core/api/api-types';

interface StepData {
  step_kind?: string;
  summary?: string;
  id?: string;
  timestamp?: string;
  duration_ms?: number;
  metadata?: Record<string, unknown>;
}

export default function TraceSummary({ trace }: { trace: AgentTrace }) {
  const [expanded, setExpanded] = useState(false);
  const stepData: StepData[] = trace.steps_json ? (JSON.parse(trace.steps_json) as StepData[]) : [];
  const steps =
    Array.isArray(stepData) && stepData.length > 0 && typeof stepData[0] === 'object'
      ? stepData
      : [];

  return (
    <div className="text-xs text-slate-300 space-y-2">
      <div className="flex items-center gap-2 flex-wrap">
        <span className="rounded-full bg-white/5 px-2 py-1">Risk: {trace.risk_level || 'unknown'}</span>
        <span className="rounded-full bg-white/5 px-2 py-1">Claim: {trace.claim_id || '–'}</span>
        <span className="rounded-full bg-white/5 px-2 py-1">Steps: {trace.steps_count ?? steps.length}</span>
      </div>

      {steps.length > 0 && (
        <div>
          <button
            type="button"
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-1 text-sky-400 hover:text-sky-300 transition-colors"
          >
            <span>{expanded ? '▼' : '▶'}</span>
            <span>{expanded ? 'Ocultar steps' : 'Ver steps detalhados'}</span>
          </button>

          {expanded && (
            <div className="mt-2 space-y-2 pl-4 border-l border-white/10">
              {steps.map((step, idx) => (
                <div key={idx} className="rounded bg-white/5 p-2">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-slate-200">
                      {idx + 1}. {step.step_kind || 'step'}
                    </span>
                    {step.duration_ms !== undefined && (
                      <span className="text-slate-500">{step.duration_ms}ms</span>
                    )}
                  </div>
                  {step.summary && (
                    <p className="mt-1 text-slate-400">{step.summary}</p>
                  )}
                  {step.timestamp && (
                    <p className="mt-1 text-slate-500 text-[10px]">
                      {new Date(step.timestamp).toLocaleString()}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {steps.length === 0 && (
        <p className="text-slate-500 italic">Nenhum step registrado</p>
      )}
    </div>
  );
}
