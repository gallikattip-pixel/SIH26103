import React from "react";
import { CheckCircle2, Clock, AlertCircle, Circle } from "lucide-react";
import type { MilestoneRecord } from "../../types";

export const MilestonesTab: React.FC<{ milestones: MilestoneRecord[] }> = ({ milestones }) => {
  return (
    <div className="rounded-xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-6 space-y-4 shadow-[var(--shadow-sm)]">
      <div className="flex items-center justify-between border-b border-[var(--color-border-subtle)] pb-3">
        <h4 className="text-sm font-semibold text-[var(--color-text-primary)] uppercase tracking-wider font-mono">
          Project Milestones & Deliverables
        </h4>
        <span className="text-xs font-mono text-[var(--color-text-tertiary)]">
          {milestones.filter((m) => m.status === "COMPLETED").length} of {milestones.length} Completed
        </span>
      </div>

      <div className="space-y-3 pt-2">
        {milestones.map((m, idx) => {
          let statusColor = "text-[var(--color-text-tertiary)] border-[var(--color-border-subtle)] bg-[var(--color-bg-surface-muted)]";
          let StatusIcon = Circle;

          if (m.status === "COMPLETED") {
            statusColor = "text-[var(--color-success-text)] border-[var(--color-success-border)] bg-[var(--color-success-bg)]";
            StatusIcon = CheckCircle2;
          } else if (m.status === "IN_PROGRESS") {
            statusColor = "text-[var(--color-brand-contrast)] border-[var(--color-border-accent)] bg-[var(--color-brand-tint)]";
            StatusIcon = Clock;
          } else if (m.status === "DELAYED") {
            statusColor = "text-[var(--color-danger-text)] border-[var(--color-danger-border)] bg-[var(--color-danger-bg)]";
            StatusIcon = AlertCircle;
          }

          return (
            <div
              key={m.id || idx}
              className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface-soft)] p-4 transition hover:border-[var(--color-border-accent)] shadow-[var(--shadow-xs)]"
            >
              <div className="flex items-start gap-3">
                <div className={`mt-0.5 rounded-md border p-1.5 ${statusColor}`}>
                  <StatusIcon className="h-4 w-4" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-bold text-[var(--color-text-accent)]">{m.id}</span>
                    <span className="text-xs font-semibold text-[var(--color-text-primary)]">{m.title}</span>
                    {m.critical && (
                      <span className="rounded bg-[var(--color-danger-bg)] border border-[var(--color-danger-border)] px-1.5 py-0.2 text-[10px] font-mono text-[var(--color-danger-text)] font-semibold">
                        CRITICAL
                      </span>
                    )}
                  </div>
                  <p className="text-[11px] font-mono text-[var(--color-text-tertiary)] mt-1">
                    Target Phase: {m.target_date}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-4 self-end sm:self-center">
                <div className="text-right">
                  <div className="text-xs font-mono font-bold text-[var(--color-text-primary)]">
                    {Math.round(m.completion_percent)}%
                  </div>
                  <div className="h-1.5 w-24 rounded-full bg-[var(--color-bg-secondary)] overflow-hidden mt-1">
                    <div
                      className="h-full rounded-full bg-[var(--color-brand-primary)]"
                      style={{ width: `${Math.min(100, m.completion_percent)}%` }}
                    />
                  </div>
                </div>

                <span
                  className={`text-[10px] font-mono font-bold uppercase rounded-md px-2 py-0.5 border ${statusColor}`}
                >
                  {m.status}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
