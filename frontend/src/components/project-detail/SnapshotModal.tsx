import React, { useState, useEffect } from "react";
import { Calendar, Loader2, AlertCircle, CheckCircle, Clock } from "lucide-react";
import { Modal } from "../common/Modal";
import { RiskBadge } from "../common/RiskBadge";
import { createProjectSnapshot } from "../../services/api";
import type { ProjectSnapshot, SnapshotCreateRequest, RiskBreakdown, ProjectRecord } from "../../types";

interface SnapshotModalProps {
  isOpen: boolean;
  onClose: () => void;
  project: ProjectRecord;
  risk: RiskBreakdown;
  onSuccess: (snapshot: ProjectSnapshot) => void;
}

export const SnapshotModal: React.FC<SnapshotModalProps> = ({
  isOpen,
  onClose,
  project,
  risk,
  onSuccess,
}) => {
  const [snapshotPeriod, setSnapshotPeriod] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successData, setSuccessData] = useState<ProjectSnapshot | null>(null);

  // Default to current UTC month
  useEffect(() => {
    const now = new Date();
    const year = now.getUTCFullYear();
    const month = String(now.getUTCMonth() + 1).padStart(2, "0");
    setSnapshotPeriod(`${year}-${month}`);
  }, []);

  // Validate period format
  const isValidPeriod = (period: string) => {
    return /^\d{4}-\d{2}$/.test(period);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessData(null);

    if (!isValidPeriod(snapshotPeriod)) {
      setError("Snapshot period must be in YYYY-MM format (e.g., 2026-10).");
      return;
    }

    setLoading(true);

    try {
      const payload: SnapshotCreateRequest = {
        snapshot_period: snapshotPeriod,
      };

      const result = await createProjectSnapshot(project.project_id, payload);
      setSuccessData(result);
      onSuccess(result);
      setTimeout(() => onClose(), 2000);
    } catch (err: any) {
      setError(err.message || "Failed to create snapshot.");
    } finally {
      setLoading(false);
    }
  };

  // Current metrics that will be recorded
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

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Record Project Snapshot"
      maxWidth="lg"
    >
      {successData ? (
        <div className="space-y-4">
          <div className="flex items-center gap-2.5 rounded-xl border border-[var(--color-success-border)] bg-[var(--color-success-bg)] p-4 text-xs text-[var(--color-success-text)]">
            <CheckCircle className="h-5 w-5 shrink-0 text-[var(--color-success-icon)]" />
            <p className="font-medium">Snapshot recorded successfully</p>
          </div>

          <div className="rounded-xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-[var(--color-text-secondary)]">Project</span>
              <span className="text-xs font-mono text-[var(--color-text-primary)]">{project.project_id}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-[var(--color-text-secondary)]">Period</span>
              <span className="text-xs font-mono text-[var(--color-text-primary)]">{successData.snapshot_period}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-[var(--color-text-secondary)]">Recorded At</span>
              <span className="text-xs font-mono text-[var(--color-text-primary)]">
                {new Date(successData.recorded_at).toLocaleString(undefined, {
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

          {/* Snapshot Period Selection */}
          <div>
            <label className="block text-xs font-medium text-[var(--color-text-secondary)] mb-1.5">
              Snapshot Period <span className="text-[var(--color-danger-text)]">*</span>
            </label>
            <div className="relative">
              <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[var(--color-text-tertiary)]" />
              <input
                type="month"
                value={snapshotPeriod}
                onChange={(e) => setSnapshotPeriod(e.target.value)}
                className="w-full pl-10 pr-3 py-2 rounded-lg border border-[var(--input-border)] bg-[var(--input-bg)] px-3 py-2 text-xs font-mono text-[var(--input-text)] placeholder-[var(--input-placeholder)] focus:border-[var(--color-brand-primary)] focus:outline-none"
              />
            </div>
            <p className="mt-1 text-[11px] text-[var(--color-text-tertiary)]">
              Format: YYYY-MM. Defaults to current UTC month. Cannot be changed after creation.
            </p>
          </div>

          {/* Current Metrics Preview - Read Only */}
          <div className="rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface-muted)] p-4 space-y-3">
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-[var(--color-brand-primary)]" />
              <span className="text-xs font-semibold text-[var(--color-text-primary)] uppercase tracking-wider font-mono">
                Current Project Values to be Recorded
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
                  Deterministic Risk Snapshot
                </span>
                <RiskBadge level={currentMetrics.risk_level} score={currentMetrics.risk_score} size="sm" />
              </div>
              <p className="text-[10px] text-[var(--color-text-tertiary)] mt-1 font-mono">
                This risk assessment will be stored with the snapshot for historical auditing.
              </p>
            </div>
          </div>

          {/* Duplicate Warning */}
          <p className="text-[11px] text-[var(--color-warning-text)] bg-[var(--color-warning-bg)] rounded-lg p-2.5 border border-[var(--color-warning-border)]">
            <strong className="font-medium">Note:</strong> A snapshot for this project and period can only be created once.
            If a snapshot already exists for <code className="font-mono">{snapshotPeriod}</code>,
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
                  <span>Record Snapshot</span>
                </>
              )}
            </button>
          </div>
        </form>
      )}
    </Modal>
  );
};