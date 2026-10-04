import React from "react";
import { AlertCircle, CheckCircle } from "lucide-react";
import type { ProgressMetrics } from "../../types";

export const ProgressTab: React.FC<{ progress: ProgressMetrics }> = ({ progress }) => {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="rounded-xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-5 shadow-[var(--shadow-sm)]">
          <p className="text-xs font-mono text-[var(--color-text-secondary)] uppercase">Actual Progress</p>
          <p className="mt-2 text-3xl font-bold font-mono text-[var(--color-text-primary)]">
            {progress.actual_progress}%
          </p>
          <p className="mt-1 text-xs text-[var(--color-text-tertiary)]">Certified Ground Verification</p>
        </div>

        <div className="rounded-xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-5 shadow-[var(--shadow-sm)]">
          <p className="text-xs font-mono text-[var(--color-text-secondary)] uppercase">Planned Target</p>
          <p className="mt-2 text-3xl font-bold font-mono text-[var(--color-text-accent)]">
            {progress.planned_progress}%
          </p>
          <p className="mt-1 text-xs text-[var(--color-text-tertiary)]">Scheduled Sanction Baseline</p>
        </div>

        <div className="rounded-xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-5 shadow-[var(--shadow-sm)]">
          <p className="text-xs font-mono text-[var(--color-text-secondary)] uppercase">Execution Variance (Gap)</p>
          <p
            className={`mt-2 text-3xl font-bold font-mono ${
              progress.progress_gap > 0 ? "text-[var(--color-warning-text)]" : "text-[var(--color-success-text)]"
            }`}
          >
            {progress.progress_gap > 0 ? `-${progress.progress_gap}%` : "0% (On Track)"}
          </p>
          <p className="mt-1 text-xs text-[var(--color-text-tertiary)]">Deviation from Baseline</p>
        </div>
      </div>

      {/* Progress Breakdown Visual */}
      <div className="rounded-xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-6 space-y-4 shadow-[var(--shadow-sm)]">
        <h4 className="text-sm font-semibold text-[var(--color-text-primary)] uppercase tracking-wider font-mono border-b border-[var(--color-border-subtle)] pb-3">
          Physical Execution Trajectory
        </h4>

        <div className="space-y-4 pt-2">
          <div>
            <div className="flex justify-between text-xs font-mono mb-1.5">
              <span className="text-[var(--color-text-secondary)] font-semibold">Actual Physical Progress:</span>
              <span className="text-[var(--color-text-primary)] font-bold">{progress.actual_progress}%</span>
            </div>
            <div className="h-4 w-full rounded-full bg-[var(--color-bg-secondary)] overflow-hidden">
              <div
                className="h-full rounded-full bg-[var(--color-brand-primary)]"
                style={{ width: `${Math.min(100, progress.actual_progress)}%` }}
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between text-xs font-mono mb-1.5">
              <span className="text-[var(--color-text-secondary)] font-semibold">Planned Schedule Target:</span>
              <span className="text-[var(--color-text-accent)] font-bold">{progress.planned_progress}%</span>
            </div>
            <div className="h-4 w-full rounded-full bg-[var(--color-bg-secondary)] overflow-hidden">
              <div
                className="h-full rounded-full bg-[var(--color-border-strong)]"
                style={{ width: `${Math.min(100, progress.planned_progress)}%` }}
              />
            </div>
          </div>
        </div>

        <div className="mt-6 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface-soft)] p-4">
          <div className="flex items-start gap-3">
            {progress.progress_gap > 10 ? (
              <AlertCircle className="h-5 w-5 text-[var(--color-warning-icon)] shrink-0 mt-0.5" />
            ) : (
              <CheckCircle className="h-5 w-5 text-[var(--color-success-icon)] shrink-0 mt-0.5" />
            )}
            <div>
              <p className="text-xs font-bold text-[var(--color-text-primary)] font-mono uppercase">
                Progress Status: {progress.status}
              </p>
              <p className="text-xs text-[var(--color-text-secondary)] mt-1">
                Progress Risk Score: <span className="text-[var(--color-text-primary)] font-bold font-mono">{progress.progress_risk}/100</span>.
                {progress.progress_gap > 0
                  ? ` Project execution is lagging ${progress.progress_gap} percentage points behind schedule. Contractor performance and material supplies should be reviewed.`
                  : " Project is tracking to planned milestones without physical delays."}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
