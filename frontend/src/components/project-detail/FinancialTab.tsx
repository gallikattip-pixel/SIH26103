import React from "react";
import { AlertTriangle, CheckCircle2 } from "lucide-react";
import type { FinancialMetrics, ProjectRecord } from "../../types";

export const FinancialTab: React.FC<{ financial: FinancialMetrics; project: ProjectRecord }> = ({
  financial,
  project,
}) => {
  return (
    <div className="space-y-6">
      {/* 4 Financial KPI cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="rounded-xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-5 shadow-[var(--shadow-sm)]">
          <p className="text-xs font-mono text-[var(--color-text-secondary)] uppercase">Sanctioned Budget</p>
          <p className="mt-2 text-2xl font-bold font-mono text-[var(--color-text-primary)]">
            ₹{financial.budget_total_crore} Cr
          </p>
          <p className="mt-1 text-xs text-[var(--color-text-tertiary)]">Total Sanctioned Allocation</p>
        </div>

        <div className="rounded-xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-5 shadow-[var(--shadow-sm)]">
          <p className="text-xs font-mono text-[var(--color-text-secondary)] uppercase">Cumulative Expenditure</p>
          <p className="mt-2 text-2xl font-bold font-mono text-[var(--color-text-accent)]">
            ₹{financial.budget_expended_crore} Cr
          </p>
          <p className="mt-1 text-xs text-[var(--color-text-tertiary)]">{financial.budget_used_percent}% of sanctioned</p>
        </div>

        <div className="rounded-xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-5 shadow-[var(--shadow-sm)]">
          <p className="text-xs font-mono text-[var(--color-text-secondary)] uppercase">Remaining Funds</p>
          <p className="mt-2 text-2xl font-bold font-mono text-[var(--color-success-text)]">
            ₹{financial.budget_remaining_crore} Cr
          </p>
          <p className="mt-1 text-xs text-[var(--color-text-tertiary)]">Available Disbursable Balance</p>
        </div>

        <div className="rounded-xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-5 shadow-[var(--shadow-sm)]">
          <p className="text-xs font-mono text-[var(--color-text-secondary)] uppercase">Spend vs Physical Progress</p>
          <p className={`mt-2 text-2xl font-bold font-mono ${
            financial.spend_ahead_of_work > 15 ? "text-[var(--color-danger-text)]" : "text-[var(--color-text-primary)]"
          }`}>
            +{financial.spend_ahead_of_work}%
          </p>
          <p className="mt-1 text-xs text-[var(--color-text-tertiary)]">Spending Lead over Execution</p>
        </div>
      </div>

      {/* Financial Health Analysis Card */}
      <div className="rounded-xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-6 space-y-4 shadow-[var(--shadow-sm)]">
        <h4 className="text-sm font-semibold text-[var(--color-text-primary)] uppercase tracking-wider font-mono border-b border-[var(--color-border-subtle)] pb-3">
          Fiscal Health Audit
        </h4>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="space-y-3">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-[var(--color-text-secondary)]">Budget Consumption:</span>
              <span className="text-[var(--color-text-primary)] font-bold">{financial.budget_used_percent}%</span>
            </div>
            <div className="h-3 w-full rounded-full bg-[var(--color-bg-secondary)] overflow-hidden">
              <div
                className={`h-full rounded-full ${
                  financial.budget_used_percent > 85
                    ? "bg-[var(--color-danger-icon)]"
                    : financial.budget_used_percent > 65
                    ? "bg-[var(--color-warning-icon)]"
                    : "bg-[var(--color-brand-primary)]"
                }`}
                style={{ width: `${Math.min(100, financial.budget_used_percent)}%` }}
              />
            </div>

            <div className="flex justify-between text-xs font-mono pt-2">
              <span className="text-[var(--color-text-secondary)]">Physical Work Delivered:</span>
              <span className="text-[var(--color-text-primary)] font-bold">{project.progress}%</span>
            </div>
            <div className="h-3 w-full rounded-full bg-[var(--color-bg-secondary)] overflow-hidden">
              <div
                className="h-full rounded-full bg-[var(--color-success-icon)]"
                style={{ width: `${Math.min(100, project.progress)}%` }}
              />
            </div>
          </div>

          <div className="rounded-lg p-4 flex flex-col justify-center">
            {financial.spend_ahead_of_work >= 20 ? (
              <div className="rounded-lg border border-[var(--color-danger-border)] bg-[var(--color-danger-bg)] p-4 flex items-start gap-3 text-[var(--color-danger-text)]">
                <AlertTriangle className="h-6 w-6 shrink-0 mt-0.5 text-[var(--color-danger-icon)]" />
                <div>
                  <p className="text-xs font-bold text-[var(--color-danger-text)] uppercase font-mono">
                    High Expenditure Discrepancy Flag
                  </p>
                  <p className="text-xs text-[var(--color-danger-text)]/90 mt-1">
                    Financial drawdowns exceed physical milestone delivery by {financial.spend_ahead_of_work} percentage points. An audit of contractor invoices against on-site measurements is strongly recommended.
                  </p>
                </div>
              </div>
            ) : (
              <div className="rounded-lg border border-[var(--color-success-border)] bg-[var(--color-success-bg)] p-4 flex items-start gap-3 text-[var(--color-success-text)]">
                <CheckCircle2 className="h-6 w-6 shrink-0 mt-0.5 text-[var(--color-success-icon)]" />
                <div>
                  <p className="text-xs font-bold text-[var(--color-success-text)] uppercase font-mono">
                    Financials Aligned With Delivery
                  </p>
                  <p className="text-xs text-[var(--color-text-secondary)] mt-1">
                    Expenditure is running proportional to measured physical progress. No critical capital diversion flags detected.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
