/**
 * S40-FE-005: Truth Status Badges
 *
 * Badges for displaying truth states, decision types, and gates.
 */

import { clsx } from 'clsx';
import type {
  TruthState,
  DecisionType,
  StateBadgeVariant,
  STATE_BADGE_MAP,
  DECISION_BADGE_MAP,
  GATE_BADGE_MAP,
} from '../types';

type BadgeSize = 'sm' | 'md' | 'lg';

// Variant styles matching spovest theme
const variantStyles: Record<StateBadgeVariant, string> = {
  success: 'bg-emerald-400/10 text-emerald-400',
  warning: 'bg-yellow-400/10 text-yellow-400',
  danger: 'bg-red-400/10 text-red-400',
  info: 'bg-cyan-400/10 text-cyan-400',
  default: 'bg-slate-700 text-slate-300',
};

const sizeStyles: Record<BadgeSize, string> = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-1 text-xs',
  lg: 'px-3 py-1.5 text-sm',
};

// State to variant mapping
const stateVariantMap: Record<string, StateBadgeVariant> = {
  UNKNOWN: 'default',
  CLAIMED: 'info',
  UNDER_REVIEW: 'warning',
  PROVISIONAL: 'warning',
  ESTABLISHED_FACT: 'success',
  UNDER_DISPUTE: 'warning',
  RETRACTED: 'danger',
  PENDING: 'info',
  PROMOTED: 'success',
  CONTESTABLE: 'warning',
  REJECTED: 'danger',
  BLOCKED: 'danger',
  DEGRADED: 'default',
  unknown: 'default',
};

// Decision to variant mapping
const decisionVariantMap: Record<string, StateBadgeVariant> = {
  APPROVE: 'success',
  REJECT: 'danger',
  ESCALATE: 'warning',
  BLOCK: 'danger',
  DEGRADE: 'default',
  PROMOTE: 'success',
};

// Gate to variant mapping
const gateVariantMap: Record<string, StateBadgeVariant> = {
  G0: 'info',
  G1: 'info',
  G2: 'warning',
  G3: 'warning',
  G4: 'success',
  NOGO: 'danger',
};

// ===== State Badge =====
interface StateBadgeProps {
  state: TruthState | string;
  size?: BadgeSize;
  showDot?: boolean;
  className?: string;
}

export function TruthStateBadge({
  state,
  size = 'md',
  showDot = false,
  className,
}: StateBadgeProps) {
  const variant = stateVariantMap[state] || 'default';
  const displayState = state || 'unknown';

  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1.5 font-medium rounded-full uppercase',
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
    >
      {showDot && (
        <span
          className={clsx(
            'w-1.5 h-1.5 rounded-full',
            variant === 'success' && 'bg-emerald-400',
            variant === 'warning' && 'bg-yellow-400',
            variant === 'danger' && 'bg-red-400',
            variant === 'info' && 'bg-cyan-400',
            variant === 'default' && 'bg-slate-400'
          )}
        />
      )}
      {displayState}
    </span>
  );
}

// ===== Decision Type Badge =====
interface DecisionBadgeProps {
  decision: DecisionType | string;
  size?: BadgeSize;
  className?: string;
}

export function DecisionTypeBadge({
  decision,
  size = 'md',
  className,
}: DecisionBadgeProps) {
  const variant = decisionVariantMap[decision] || 'default';
  const displayDecision = decision || 'unknown';

  return (
    <span
      className={clsx(
        'inline-flex items-center font-medium rounded-full uppercase',
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
    >
      {displayDecision}
    </span>
  );
}

// ===== Gate Badge =====
interface GateBadgeProps {
  gate: string;
  size?: BadgeSize;
  className?: string;
}

export function GateBadge({ gate, size = 'md', className }: GateBadgeProps) {
  const variant = gateVariantMap[gate] || 'info';
  const displayGate = gate || 'G0';

  return (
    <span
      className={clsx(
        'inline-flex items-center font-medium rounded-full',
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
    >
      {displayGate}
    </span>
  );
}

// ===== Provenance Badge =====
interface ProvenanceBadgeProps {
  isValid: boolean;
  size?: BadgeSize;
  className?: string;
}

export function ProvenanceBadge({
  isValid,
  size = 'sm',
  className,
}: ProvenanceBadgeProps) {
  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1 font-medium rounded-full',
        isValid
          ? 'bg-emerald-400/10 text-emerald-400'
          : 'bg-red-400/10 text-red-400',
        sizeStyles[size],
        className
      )}
    >
      {isValid ? (
        <>
          <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
              clipRule="evenodd"
            />
          </svg>
          Provenance Valid
        </>
      ) : (
        <>
          <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
              clipRule="evenodd"
            />
          </svg>
          No Provenance
        </>
      )}
    </span>
  );
}

// ===== Latency Badge =====
interface LatencyBadgeProps {
  latencyMs: number | null | undefined;
  threshold?: number; // ms threshold for warning
  size?: BadgeSize;
  className?: string;
}

export function LatencyBadge({
  latencyMs,
  threshold = 100,
  size = 'sm',
  className,
}: LatencyBadgeProps) {
  if (latencyMs === null || latencyMs === undefined) {
    return null;
  }

  const isSlowVariant: StateBadgeVariant = latencyMs > threshold ? 'warning' : 'success';

  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1 font-mono font-medium rounded-full',
        variantStyles[isSlowVariant],
        sizeStyles[size],
        className
      )}
    >
      <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
        <path
          fillRule="evenodd"
          d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
          clipRule="evenodd"
        />
      </svg>
      {latencyMs}ms
    </span>
  );
}

// ===== E40.5 Status Badge =====
interface E405BadgeProps {
  status: 'OK' | 'VIOLATED' | 'SKIPPED' | string | null | undefined;
  size?: BadgeSize;
  className?: string;
}

export function E405Badge({ status, size = 'sm', className }: E405BadgeProps) {
  if (!status) {
    return null;
  }

  const variantMap: Record<string, StateBadgeVariant> = {
    OK: 'success',
    PASS: 'success',
    VIOLATED: 'danger',
    FAIL: 'danger',
    SKIPPED: 'default',
  };

  const variant = variantMap[status] || 'default';

  return (
    <span
      className={clsx(
        'inline-flex items-center font-medium rounded-full',
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
    >
      E40.5: {status}
    </span>
  );
}
