import React from "react";
import { Clock, AlertTriangle, CheckCircle } from "lucide-react";
import type { TimelineMetrics } from "../../types";

export const TimelineTab: React.FC<{ timeline: TimelineMetrics }> = ({ timeline }) => {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="rounded-xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-5 shadow-[var(--shadow-sm)]">
          <p className="text-xs font-mono text-[var(--color-text-secondary)] uppercase">Schedule Delay</p>
          <p
            className={`mt-2 text-3xl font-bold font-mono ${
              timeline.delay_days > 0 ? "text-[var(--color-warning-text)]" : "text-[var(--color-success-text)]"
            }`}
          >
            {timeline.delay_days > 0 ? `${timeline.delay_days} Days` : "Zero Delay"}
          </p>
          <p className="mt-1 text-xs text-[var(--color-text-tertiary)]">Recorded Calendar Slippage</p>
        </div>

        <div className="rounded-xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-5 shadow-[var(--shadow-sm)]">
          <p className="text-xs font-mono text-[var(--color-text-secondary)] uppercase">Delay Risk Rating</p>
          <p className="mt-2 text-3xl font-bold font-mono text-[var(--color-text-primary)]">
            {timeline.delay_risk}/100
          </p>
          <p className="mt-1 text-xs text-[var(--color-text-tertiary)]">Python Engine Mathematical Score</p>
        </div>

        <div className="rounded-xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-5 shadow-[var(--shadow-sm)]">
          <p className="text-xs font-mono text-[var(--color-text-secondary)] uppercase">Recovery Urgency</p>
          <p
            className={`mt-2 text-2xl font-bold font-mono uppercase ${
              timeline.recovery_urgency === "HIGH"
                ? "text-[var(--color-danger-text)]"
                : timeline.recovery_urgency === "MEDIUM"
                ? "text-[var(--color-warning-text)]"
                : "text-[var(--color-success-text)]"
            }`}
          >
            {timeline.recovery_urgency} Urgency
          </p>
          <p className="mt-1 text-xs text-[var(--color-text-tertiary)]">Intervention Escalation Tier</p>
        </div>
      </div>

      <div className="rounded-xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-6 space-y-4 shadow-[var(--shadow-sm)]">
        <h4 className="text-sm font-semibold text-[var(--color-text-primary)] uppercase tracking-wider font-mono border-b border-[var(--color-border-subtle)] pb-3">
          Timeline Analysis & Impact Assessment
        </h4>

        <div className="rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface-soft)] p-5 space-y-3">
          <div className="flex items-center gap-2">
            {timeline.delay_days >= 30 ? (
              <AlertTriangle className="h-5 w-5 text-[var(--color-danger-icon)]" />
            ) : timeline.delay_days > 0 ? (
              <Clock className="h-5 w-5 text-[var(--color-warning-icon)]" />
            ) : (
              <CheckCircle className="h-5 w-5 text-[var(--color-success-icon)]" />
            )}
            <span className="text-sm font-bold text-[var(--color-text-primary)] font-mono uppercase">
              Schedule Status: {timeline.schedule_status}
            </span>
          </div>

          <p className="text-xs text-[var(--color-text-secondary)] leading-relaxed">
            {timeline.estimated_impact}
          </p>

          <div className="pt-2 border-t border-[var(--color-border-subtle)] text-[11px] font-mono text-[var(--color-text-tertiary)]">
            Formula: Delay Risk = clamp((delay_days / 90) * 100) = {timeline.delay_risk}/100.
          </div>
        </div>
      </div>
    </div>
  );
};
