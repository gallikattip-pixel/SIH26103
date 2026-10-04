import React from "react";
import {
  MapPin,
  Building2,
  Calendar,
  IndianRupee,
  Layers,
  AlertOctagon,
  CheckCircle2,
} from "lucide-react";
import type { ProjectDetail360 } from "../../types";

export const OverviewTab: React.FC<{ detail: ProjectDetail360 }> = ({ detail }) => {
  const { project, risk, financial, progress, timeline } = detail;

  return (
    <div className="space-y-6">
      {/* Executive Key Information Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="rounded-xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-4 shadow-[var(--shadow-sm)]">
          <div className="flex items-center gap-2 text-xs font-mono text-[var(--color-text-secondary)] uppercase">
            <Layers className="h-4 w-4 text-[var(--color-brand-primary)]" />
            <span>Infrastructure Sector</span>
          </div>
          <p className="mt-2 text-lg font-bold text-[var(--color-text-primary)]">{project.sector}</p>
          <p className="mt-0.5 text-xs text-[var(--color-text-tertiary)]">Classified National Asset</p>
        </div>

        <div className="rounded-xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-4 shadow-[var(--shadow-sm)]">
          <div className="flex items-center gap-2 text-xs font-mono text-[var(--color-text-secondary)] uppercase">
            <MapPin className="h-4 w-4 text-[var(--color-brand-primary)]" />
            <span>Jurisdiction</span>
          </div>
          <p className="mt-2 text-lg font-bold text-[var(--color-text-primary)]">{project.location}</p>
          <p className="mt-0.5 text-xs text-[var(--color-text-tertiary)]">State Administration</p>
        </div>

        <div className="rounded-xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-4 shadow-[var(--shadow-sm)]">
          <div className="flex items-center gap-2 text-xs font-mono text-[var(--color-text-secondary)] uppercase">
            <Building2 className="h-4 w-4 text-[var(--color-brand-primary)]" />
            <span>Primary Contractor</span>
          </div>
          <p className="mt-2 text-lg font-bold text-[var(--color-text-primary)] truncate">{project.contractor}</p>
          <p className="mt-0.5 text-xs text-[var(--color-text-tertiary)]">Executing Entity</p>
        </div>

        <div className="rounded-xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-4 shadow-[var(--shadow-sm)]">
          <div className="flex items-center gap-2 text-xs font-mono text-[var(--color-text-secondary)] uppercase">
            <IndianRupee className="h-4 w-4 text-[var(--color-brand-primary)]" />
            <span>Sanctioned Budget</span>
          </div>
          <p className="mt-2 text-lg font-bold text-[var(--color-text-primary)] font-mono">
            ₹{project.budget_total_crore} Cr
          </p>
          <p className="mt-0.5 text-xs text-[var(--color-text-tertiary)]">{project.budget_used}% utilized</p>
        </div>
      </div>

      {/* Two-Column Status Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Executive Risk Assessment Card */}
        <div className="rounded-xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-6 space-y-4 shadow-[var(--shadow-sm)]">
          <div className="flex items-center justify-between border-b border-[var(--color-border-subtle)] pb-3">
            <h4 className="text-sm font-semibold text-[var(--color-text-primary)] uppercase tracking-wider font-mono">
              Risk Engine Assessment
            </h4>
            <span
              className={`rounded-full px-2.5 py-0.5 text-xs font-mono font-bold border ${
                risk.overall_level === "HIGH"
                  ? "bg-[var(--color-danger-bg)] text-[var(--color-danger-text)] border-[var(--color-danger-border)]"
                  : risk.overall_level === "MEDIUM"
                  ? "bg-[var(--color-warning-bg)] text-[var(--color-warning-text)] border-[var(--color-warning-border)]"
                  : "bg-[var(--color-success-bg)] text-[var(--color-success-text)] border-[var(--color-success-border)]"
              }`}
            >
              {risk.overall_level} RISK ({risk.overall_score}/100)
            </span>
          </div>

          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-xs font-mono mb-1">
                <span className="text-[var(--color-text-secondary)]">Schedule Delay Component (40% weight):</span>
                <span className="text-[var(--color-text-primary)] font-bold">{risk.delay_risk}/100</span>
              </div>
              <div className="h-2 w-full rounded-full bg-[var(--color-bg-secondary)]">
                <div
                  className="h-full rounded-full bg-[var(--color-brand-primary)]"
                  style={{ width: `${risk.delay_risk}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-mono mb-1">
                <span className="text-[var(--color-text-secondary)]">Progress Gap Component (35% weight):</span>
                <span className="text-[var(--color-text-primary)] font-bold">{risk.progress_risk}/100</span>
              </div>
              <div className="h-2 w-full rounded-full bg-[var(--color-bg-secondary)]">
                <div
                  className="h-full rounded-full bg-[var(--color-brand-primary)]"
                  style={{ width: `${risk.progress_risk}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-mono mb-1">
                <span className="text-[var(--color-text-secondary)]">Budget Utilization Component (25% weight):</span>
                <span className="text-[var(--color-text-primary)] font-bold">{risk.budget_risk}/100</span>
              </div>
              <div className="h-2 w-full rounded-full bg-[var(--color-bg-secondary)]">
                <div
                  className="h-full rounded-full bg-[var(--color-brand-primary)]"
                  style={{ width: `${risk.budget_risk}%` }}
                />
              </div>
            </div>
          </div>

          <div className="pt-2">
            <p className="text-xs font-mono text-[var(--color-text-secondary)] mb-2">Identified Risk Factors:</p>
            <div className="flex flex-wrap gap-2">
              {risk.major_factors.map((factor, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center gap-1.5 rounded-lg border border-[var(--color-border-default)] bg-[var(--color-bg-surface-soft)] px-2.5 py-1 text-xs text-[var(--color-text-secondary)]"
                >
                  <AlertOctagon className="h-3 w-3 text-[var(--color-warning-icon)]" />
                  <span>{factor}</span>
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Execution Snapshot Card */}
        <div className="rounded-xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-6 space-y-4 shadow-[var(--shadow-sm)]">
          <div className="border-b border-[var(--color-border-subtle)] pb-3">
            <h4 className="text-sm font-semibold text-[var(--color-text-primary)] uppercase tracking-wider font-mono">
              Execution & Milestone Status
            </h4>
          </div>

          <div className="space-y-4">
            <div className="flex items-start gap-3 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface-soft)] p-3">
              <CheckCircle2 className="h-5 w-5 text-[var(--color-success-icon)] shrink-0 mt-0.5" />
              <div>
                <p className="text-xs font-bold text-[var(--color-text-primary)]">Physical vs Planned Status</p>
                <p className="text-xs text-[var(--color-text-secondary)]">
                  Actual progress is {progress.actual_progress}% against planned {progress.planned_progress}%.
                  {progress.progress_gap > 0 ? (
                    <span className="text-[var(--color-warning-text)] font-semibold ml-1">
                      Lagging by {progress.progress_gap} percentage points.
                    </span>
                  ) : (
                    <span className="text-[var(--color-success-text)] font-semibold ml-1">
                      Executing on schedule.
                    </span>
                  )}
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface-soft)] p-3">
              <Calendar className="h-5 w-5 text-[var(--color-brand-primary)] shrink-0 mt-0.5" />
              <div>
                <p className="text-xs font-bold text-[var(--color-text-primary)]">Schedule Variance</p>
                <p className="text-xs text-[var(--color-text-secondary)]">
                  Current delay:{" "}
                  <span className="font-mono text-[var(--color-text-primary)] font-semibold">
                    {timeline.delay_days} days
                  </span>
                  . {timeline.estimated_impact}
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface-soft)] p-3">
              <IndianRupee className="h-5 w-5 text-[var(--color-warning-icon)] shrink-0 mt-0.5" />
              <div>
                <p className="text-xs font-bold text-[var(--color-text-primary)]">Financial Execution Ratio</p>
                <p className="text-xs text-[var(--color-text-secondary)]">
                  Total expended:{" "}
                  <span className="font-mono text-[var(--color-text-primary)] font-semibold">
                    ₹{financial.budget_expended_crore} Cr
                  </span>{" "}
                  ({financial.budget_used_percent}%). Spend ahead of work:{" "}
                  <span className="font-mono text-[var(--color-text-secondary)]">
                    {financial.spend_ahead_of_work}%
                  </span>
                  .
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
