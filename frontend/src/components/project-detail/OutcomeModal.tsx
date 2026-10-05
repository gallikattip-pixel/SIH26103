import React, { useState, useEffect } from "react";
import { Calendar, Loader2, AlertCircle, CheckCircle, Clock, Flag } from "lucide-react";
import { Modal } from "../common/Modal";
import { RiskBadge } from "../common/RiskBadge";
import { createProjectOutcome } from "../../services/api";
import type { ProjectOutcomeCreateRequest, ProjectOutcomeResponse, RiskBreakdown, ProjectRecord } from "../../types";

interface OutcomeModalProps {
  isOpen: boolean;
  onClose: () => void;
  project: ProjectRecord;
  risk: RiskBreakdown;
  onSuccess: (outcome: ProjectOutcomeResponse) => void;
}

export const OutcomeModal: React.FC<OutcomeModalProps> = ({
  isOpen,
  onClose,
  project,
  risk,
  onSuccess,
}) => {
  const [formData, setFormData] = useState<ProjectOutcomeCreateRequest>({
    completion_status: "COMPLETED",
    actual_completion_date: "",
    planned_completion_date: "",
    final_progress: project.progress,
    final_budget_used: project.budget_used,
    final_budget_variance_percent: undefined,
    final_cost_crore: undefined,
    notes: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successData, setSuccessData] = useState<ProjectOutcomeResponse | null>(null);

  // Default actual completion date to today
  useEffect(() => {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, "0");
    const day = String(now.getDate()).padStart(2, "0");
    setFormData((prev) => ({ ...prev, actual_completion_date: `${year}-${month}-${day}` }));
  }, []);

  // Validate date format
  const isValidDate = (date: string) => {
    return /^\d{4}-\d{2}-\d{2}$/.test(date);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessData(null);

    if (!isValidDate(formData.actual_completion_date)) {
      setError("Actual completion date must be in YYYY-MM-DD format.");
      return;
    }

    if (formData.planned_completion_date && !isValidDate(formData.planned_completion_date)) {
      setError("Planned completion date must be in YYYY-MM-DD format.");
      return;
    }

    if (formData.final_progress < 0 || formData.final_progress > 100) {
      setError("Final progress must be between 0% and 100%.");
      return;
    }

    if (formData.final_budget_used < 0 || formData.final_budget_used > 100) {
      setError("Final budget used must be between 0% and 100%.");
      return;
    }

    setLoading(true);

    try {
      const result = await createProjectOutcome(project.project_id, formData);
      setSuccessData(result);
      onSuccess(result);
      setTimeout(() => onClose(), 2000);
    } catch (err: any) {
      setError(err.message || "Failed to record outcome.");
    } finally {
      setLoading(false);
    }
  };

  // Current metrics preview
  const currentMetrics = {
    progress: project.progress,
    planned_progress: project.planned_progress,
    delay_days: project.delay_days,
    budget_used: project.budget_used,
    budget_total_crore: project.budget_total_crore,
    contractor: project.contractor,
    sector: project.sector,
    location: project.location,
    risk_score: risk.overall_score,
    risk_level: risk.overall_level,
  };

  // Compute derived delay if both dates provided
  const computedDelay = (() => {
    if (formData.planned_completion_date && formData.actual_completion_date) {
      try {
        const planned = new Date(formData.planned_completion_date);
        const actual = new Date(formData.actual_completion_date);
        const diff = Math.max(0, Math.round((actual.getTime() - planned.getTime()) / (1000 * 60 * 60 * 24)));
        return diff;
      } catch {
        return null;
      }
    }
    return null;
  })();

  // Compute budget variance if final cost provided
  const computedBudgetVariance = (() => {
    if (formData.final_cost_crore !== undefined && formData.final_cost_crore !== null && project.budget_total_crore > 0) {
      return ((formData.final_cost_crore - project.budget_total_crore) / project.budget_total_crore) * 100;
    }
    return null;
  })();

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Record Project Completion Outcome"
      maxWidth="lg"
    >
      {successData ? (
        <div className="space-y-4">
          <div className="flex items-center gap-2.5 rounded-xl border border-[var(--color-success-border)] bg-[var(--color-success-bg)] p-4 text-xs text-[var(--color-success-text)]">
            <CheckCircle className="h-5 w-5 shrink-0 text-[var(--color-success-icon)]" />
            <p className="font-medium">Completion outcome recorded successfully</p>
          </div>

          <div className="rounded-xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-[var(--color-text-secondary)]">Project</span>
              <span className="text-xs font-mono text-[var(--color-text-primary)]">{project.project_id}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-[var(--color-text-secondary)]">Status</span>
              <span className="text-xs font-mono text-[var(--color-text-primary)]">{successData.outcome?.completion_status}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-[var(--color-text-secondary)]">Actual Completion</span>
              <span className="text-xs font-mono text-[var(--color-text-primary)]">{successData.outcome?.actual_completion_date}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-[var(--color-text-secondary)]">Recorded At</span>
              <span className="text-xs font-mono text-[var(--color-text-primary)]">
                {new Date(successData.outcome?.recorded_at || "").toLocaleString(undefined, {
                  year: "numeric",
                  month: "short",
                  day: "numeric",
                  hour: "2-digit",
                  minute: "2-digit",
                  timeZoneName: "short",
                })}
              </span>
            </div>
          </div>

          <div className="flex items-center justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="inline-flex items-center gap-1.5 rounded-lg bg-[var(--color-brand-primary)] px-4 py-2 text-xs font-semibold text-[var(--color-brand-contrast)] hover:bg-[var(--color-brand-primary-hover)] shadow-[var(--shadow-xs)] transition"
            >
              <CheckCircle className="h-3.5 w-3.5" />
              <span>Done</span>
            </button>
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="flex items-start gap-2.5 rounded-xl border border-[var(--color-danger-border)] bg-[var(--color-danger-bg)] p-3 text-xs text-[var(--color-danger-text)]">
              <AlertCircle className="h-4 w-4 shrink-0 mt-0.5 text-[var(--color-danger-icon)]" />
              <p>{error}</p>
            </div>
          )}

          {/* Completion Status */}
          <div>
            <label className="block text-xs font-medium text-[var(--color-text-secondary)] mb-1.5">
              Completion Status <span className="text-[var(--color-danger-text)]">*</span>
            </label>
            <select
              value={formData.completion_status}
              onChange={(e) => setFormData({ ...formData, completion_status: e.target.value as "COMPLETED" | "TERMINATED" | "SUSPENDED" | "ON_HOLD" })}
              className="w-full rounded-lg border border-[var(--input-border)] bg-[var(--input-bg)] px-3 py-2 text-xs text-[var(--input-text)] focus:border-[var(--color-brand-primary)] focus:outline-none"
            >
              <option value="COMPLETED">COMPLETED</option>
              <option value="TERMINATED">TERMINATED</option>
              <option value="SUSPENDED">SUSPENDED</option>
              <option value="ON_HOLD">ON_HOLD</option>
            </select>
            <p className="mt-1 text-[11px] text-[var(--color-text-tertiary)]">
              COMPLETED = fully finished. TERMINATED = stopped permanently. SUSPENDED = paused. ON_HOLD = awaiting decision.
            </p>
          </div>

          {/* Actual Completion Date */}
          <div>
            <label className="block text-xs font-medium text-[var(--color-text-secondary)] mb-1.5">
              Actual Completion Date <span className="text-[var(--color-danger-text)]">*</span>
            </label>
            <div className="relative">
              <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[var(--color-text-tertiary)]" />
              <input
                type="date"
                value={formData.actual_completion_date}
                onChange={(e) => setFormData({ ...formData, actual_completion_date: e.target.value })}
                className="w-full pl-10 pr-3 py-2 rounded-lg border border-[var(--input-border)] bg-[var(--input-bg)] px-3 py-2 text-xs font-mono text-[var(--input-text)] placeholder-[var(--input-placeholder)] focus:border-[var(--color-brand-primary)] focus:outline-none"
              />
            </div>
            <p className="mt-1 text-[11px] text-[var(--color-text-tertiary)]">
              Format: YYYY-MM-DD. The actual date the project reached its final status.
            </p>
          </div>

          {/* Planned Completion Date */}
          <div>
            <label className="block text-xs font-medium text-[var(--color-text-secondary)] mb-1.5">
              Planned Completion Date
            </label>
            <div className="relative">
              <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[var(--color-text-tertiary)]" />
              <input
                type="date"
                value={formData.planned_completion_date}
                onChange={(e) => setFormData({ ...formData, planned_completion_date: e.target.value })}
                className="w-full pl-10 pr-3 py-2 rounded-lg border border-[var(--input-border)] bg-[var(--input-bg)] px-3 py-2 text-xs font-mono text-[var(--input-text)] placeholder-[var(--input-placeholder)] focus:border-[var(--color-brand-primary)] focus:outline-none"
              />
            </div>
            <p className="mt-1 text-[11px] text-[var(--color-text-tertiary)]">
              Format: YYYY-MM-DD. Original target completion date (optional, used to compute delay).
            </p>
          </div>

          {/* Computed Delay Preview */}
          {computedDelay !== null && (
            <div className="rounded-lg border border-[var(--color-border-accent)] bg-[var(--color-brand-tint)] p-3 text-[11px]">
              <div className="flex items-center gap-2">
                <Clock className="h-3.5 w-3.5 text-[var(--color-brand-primary)]" />
                <span className="font-medium text-[var(--color-text-accent)]">Computed Schedule Delay</span>
              </div>
              <p className="mt-1 font-mono text-[var(--color-text-primary)]">
                {computedDelay} days delay (Actual - Planned)
              </p>
            </div>
          )}

          {/* Final Progress */}
          <div>
            <label className="block text-xs font-medium text-[var(--color-text-secondary)] mb-1.5">
              Final Physical Progress (%) <span className="text-[var(--color-danger-text)]">*</span>
            </label>
            <input
              type="number"
              min="0"
              max="100"
              step="0.1"
              value={formData.final_progress}
              onChange={(e) => setFormData({ ...formData, final_progress: parseFloat(e.target.value) || 0 })}
              className="w-full rounded-lg border border-[var(--input-border)] bg-[var(--input-bg)] px-3 py-2 text-xs font-mono text-[var(--input-text)] focus:border-[var(--color-brand-primary)] focus:outline-none"
            />
          </div>

          {/* Final Budget Used */}
          <div>
            <label className="block text-xs font-medium text-[var(--color-text-secondary)] mb-1.5">
              Final Budget Utilization (%) <span className="text-[var(--color-danger-text)]">*</span>
            </label>
            <input
              type="number"
              min="0"
              max="100"
              step="0.1"
              value={formData.final_budget_used}
              onChange={(e) => setFormData({ ...formData, final_budget_used: parseFloat(e.target.value) || 0 })}
              className="w-full rounded-lg border border-[var(--input-border)] bg-[var(--input-bg)] px-3 py-2 text-xs font-mono text-[var(--input-text)] focus:border-[var(--color-brand-primary)] focus:outline-none"
            />
          </div>

          {/* Final Cost (for variance calculation) */}
          <div>
            <label className="block text-xs font-medium text-[var(--color-text-secondary)] mb-1.5">
              Final Actual Cost (₹ Crore)
            </label>
            <input
              type="number"
              min="0"
              step="0.1"
              value={formData.final_cost_crore ?? ""}
              onChange={(e) => setFormData({ ...formData, final_cost_crore: e.target.value ? parseFloat(e.target.value) : undefined })}
              className="w-full rounded-lg border border-[var(--input-border)] bg-[var(--input-bg)] px-3 py-2 text-xs font-mono text-[var(--input-text)] focus:border-[var(--color-brand-primary)] focus:outline-none"
            />
            <p className="mt-1 text-[11px] text-[var(--color-text-tertiary)]">
              Optional. If provided, budget variance will be computed from sanctioned budget.
            </p>
          </div>

          {/* Computed Budget Variance Preview */}
          {computedBudgetVariance !== null && (
            <div className="rounded-lg border border-[var(--color-border-accent)] bg-[var(--color-brand-tint)] p-3 text-[11px]">
              <div className="flex items-center gap-2">
                <Flag className="h-3.5 w-3.5 text-[var(--color-brand-primary)]" />
                <span className="font-medium text-[var(--color-text-accent)]">Computed Budget Variance</span>
              </div>
              <p className="mt-1 font-mono text-[var(--color-text-primary)]">
                {computedBudgetVariance >= 0 ? "+" : ""}{computedBudgetVariance.toFixed(2)}% variance from sanctioned budget
              </p>
            </div>
          )}

          {/* Notes */}
          <div>
            <label className="block text-xs font-medium text-[var(--color-text-secondary)] mb-1.5">
              Notes
            </label>
            <textarea
              value={formData.notes || ""}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              rows={3}
              className="w-full rounded-lg border border-[var(--input-border)] bg-[var(--input-bg)] px-3 py-2 text-xs text-[var(--input-text)] placeholder-[var(--input-placeholder)] focus:border-[var(--color-brand-primary)] focus:outline-none resize-none"
              placeholder="Optional notes about the completion..."
            />
          </div>

          {/* Current Project Values */}
          <div className="rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface-muted)] p-4 space-y-3">
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-[var(--color-brand-primary)]" />
              <span className="text-xs font-semibold text-[var(--color-text-primary)] uppercase tracking-wider font-mono">
                Current Project Values (Reference)
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-[11px]">
              <div className="rounded border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)] p-2.5">
                <span className="text-[var(--color-text-tertiary)] font-mono">Progress</span>
                <div className="flex items-center justify-between mt-0.5">
                  <span className="font-mono text-[var(--color-text-primary)]">{currentMetrics.progress}%</span>
                  <span className="text-[var(--color-text-tertiary)]">Actual</span>
                </div>
              </div>

              <div className="rounded border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)] p-2.5">
                <span className="text-[var(--color-text-tertiary)] font-mono">Planned Progress</span>
                <div className="flex items-center justify-between mt-0.5">
                  <span className="font-mono text-[var(--color-text-primary)]">{currentMetrics.planned_progress}%</span>
                  <span className="text-[var(--color-text-tertiary)]">Planned</span>
                </div>
              </div>

              <div className="rounded border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)] p-2.5">
                <span className="text-[var(--color-text-tertiary)] font-mono">Schedule Delay</span>
                <div className="flex items-center justify-between mt-0.5">
                  <span className="font-mono text-[var(--color-text-primary)]">{currentMetrics.delay_days} days</span>
                  <span className="text-[var(--color-text-tertiary)]">Delay</span>
                </div>
              </div>

              <div className="rounded border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)] p-2.5">
                <span className="text-[var(--color-text-tertiary)] font-mono">Budget Used</span>
                <div className="flex items-center justify-between mt-0.5">
                  <span className="font-mono text-[var(--color-text-primary)]">{currentMetrics.budget_used}%</span>
                  <span className="text-[var(--color-text-tertiary)]">Utilization</span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-[11px] pt-2 border-t border-[var(--color-border-subtle)]">
              <div className="rounded border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)] p-2.5">
                <span className="text-[var(--color-text-tertiary)] font-mono">Budget Total</span>
                <div className="flex items-center justify-between mt-0.5">
                  <span className="font-mono text-[var(--color-text-primary)]">₹{currentMetrics.budget_total_crore} Cr</span>
                  <span className="text-[var(--color-text-tertiary)]">Sanctioned</span>
                </div>
              </div>

              <div className="rounded border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)] p-2.5">
                <span className="text-[var(--color-text-tertiary)] font-mono">Contractor</span>
                <div className="flex items-center justify-between mt-0.5">
                  <span className="font-mono text-[var(--color-text-primary)] truncate">{currentMetrics.contractor}</span>
                </div>
              </div>
            </div>

            {/* Current Risk Snapshot */}
            <div className="rounded border border-[var(--color-border-accent)] bg-[var(--color-brand-tint)] p-3 pt-2 border-t border-[var(--color-border-subtle)]">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-mono text-[var(--color-text-accent)] font-semibold">
                  Deterministic Risk Snapshot (Current)
                </span>
                <RiskBadge level={currentMetrics.risk_level} score={currentMetrics.risk_score} size="sm" />
              </div>
              <p className="text-[10px] text-[var(--color-text-tertiary)] mt-1 font-mono">
                This risk assessment reflects the current project state, not the final outcome.
              </p>
            </div>
          </div>

          {/* Immutability Warning */}
          <p className="text-[11px] text-[var(--color-warning-text)] bg-[var(--color-warning-bg)] rounded-lg p-2.5 border border-[var(--color-warning-border)]">
            <strong className="font-medium">Note:</strong> A project outcome can only be recorded once and is immutable.
            If an outcome already exists for <code className="font-mono">{project.project_id}</code>,
            the operation will fail. Use explicit correction mechanism if update is required.
          </p>

          {/* Actions */}
          <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-[var(--color-border-default)]">
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              className="rounded-lg border border-[var(--button-secondary-border)] bg-[var(--button-secondary-bg)] px-4 py-2 text-xs font-semibold text-[var(--button-secondary-text)] hover:bg-[var(--button-secondary-hover)] transition disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center gap-1.5 rounded-lg bg-[var(--color-brand-primary)] px-5 py-2 text-xs font-semibold text-[var(--color-brand-contrast)] hover:bg-[var(--color-brand-hover)] shadow-[var(--shadow-xs)] transition disabled:opacity-50"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Recording...</span>
                </>
              ) : (
                <>
                  <CheckCircle className="h-4 w-4" />
                  <span>Record Outcome</span>
                </>
              )}
            </button>
          </div>
        </form>
      )}
    </Modal>
  );
};