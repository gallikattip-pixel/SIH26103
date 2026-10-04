import React, { useState, useMemo } from "react";
import { PlusCircle, AlertCircle, Loader2, Calculator } from "lucide-react";
import { Modal } from "../common/Modal";
import { createProject } from "../../services/api";
import { RiskBadge } from "../common/RiskBadge";
import type { ProjectListItem, ProjectRecord } from "../../types";

interface CreateProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (newProject: ProjectListItem) => void;
  existingSectors?: string[];
}

const DEFAULT_SECTORS = [
  "Roads",
  "Health",
  "Water",
  "Energy",
  "Education",
  "Urban Development",
  "Agriculture",
  "Housing",
  "e-Governance",
];

export const CreateProjectModal: React.FC<CreateProjectModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  existingSectors = [],
}) => {
  const [formData, setFormData] = useState<ProjectRecord>({
    project_id: "",
    name: "",
    location: "",
    sector: "Roads",
    progress: 0,
    planned_progress: 0,
    delay_days: 0,
    budget_used: 0,
    budget_total_crore: 100,
    contractor: "",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sectorOptions = useMemo(() => {
    const set = new Set([...DEFAULT_SECTORS, ...existingSectors.filter(s => s && s !== "all")]);
    return Array.from(set).sort();
  }, [existingSectors]);

  // Real-time risk preview calculated matching Python Risk Engine formula
  const previewRisk = useMemo(() => {
    const gap = Math.max(0, formData.planned_progress - formData.progress);
    const progRisk = Math.min(100, Math.max(0, Math.round(gap * 2.5)));
    const delRisk = Math.min(100, Math.max(0, Math.round((formData.delay_days / 90) * 100)));
    const spendAhead = Math.max(0, formData.budget_used - formData.progress);
    const budRisk = Math.min(100, Math.max(0, Math.round(0.55 * formData.budget_used + 0.45 * spendAhead)));
    const score = Math.min(100, Math.max(0, Math.round(0.35 * progRisk + 0.40 * delRisk + 0.25 * budRisk)));
    const level: "HIGH" | "MEDIUM" | "LOW" = score >= 70 ? "HIGH" : score >= 40 ? "MEDIUM" : "LOW";
    return { score, level, progRisk, delRisk, budRisk };
  }, [formData.progress, formData.planned_progress, formData.delay_days, formData.budget_used]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Basic Validation
    const cleanId = formData.project_id.trim().toUpperCase();
    if (!cleanId) {
      setError("Please provide a valid Project ID (e.g., P43 or NH-66).");
      return;
    }
    if (!formData.name.trim()) {
      setError("Please provide a Project Name.");
      return;
    }
    if (!formData.location.trim()) {
      setError("Please specify the Project Location / State.");
      return;
    }
    if (!formData.contractor.trim()) {
      setError("Please specify the Contractor or Executing Agency.");
      return;
    }
    if (formData.progress < 0 || formData.progress > 100) {
      setError("Physical progress must be between 0% and 100%.");
      return;
    }
    if (formData.planned_progress < 0 || formData.planned_progress > 100) {
      setError("Planned progress must be between 0% and 100%.");
      return;
    }
    if (formData.budget_used < 0 || formData.budget_used > 100) {
      setError("Budget utilization must be between 0% and 100%.");
      return;
    }
    if (formData.budget_total_crore <= 0) {
      setError("Total budget must be a positive number.");
      return;
    }

    setLoading(true);

    try {
      const payload: ProjectRecord = {
        ...formData,
        project_id: cleanId,
        name: formData.name.trim(),
        location: formData.location.trim(),
        sector: formData.sector.trim(),
        contractor: formData.contractor.trim(),
        progress: Number(formData.progress),
        planned_progress: Number(formData.planned_progress),
        delay_days: Number(formData.delay_days),
        budget_used: Number(formData.budget_used),
        budget_total_crore: Number(formData.budget_total_crore),
      };

      const created = await createProject(payload);
      onSuccess(created);
      onClose();
      // Reset form
      setFormData({
        project_id: "",
        name: "",
        location: "",
        sector: "Roads",
        progress: 0,
        planned_progress: 0,
        delay_days: 0,
        budget_used: 0,
        budget_total_crore: 100,
        contractor: "",
      });
    } catch (err: any) {
      setError(err.message || "Failed to register project.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Register New Infrastructure Project" maxWidth="xl">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="flex items-start gap-2.5 rounded-xl border border-[var(--color-danger-border)] bg-[var(--color-danger-bg)] p-3 text-xs text-[var(--color-danger-text)]">
            <AlertCircle className="h-4 w-4 shrink-0 mt-0.5 text-[var(--color-danger-icon)]" />
            <p>{error}</p>
          </div>
        )}

        {/* Live Risk Telemetry Preview */}
        <div className="flex items-center justify-between rounded-xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface-soft)] p-3">
          <div className="flex items-center gap-2">
            <Calculator className="h-4 w-4 text-[var(--color-brand-primary)]" />
            <div>
              <span className="text-xs font-semibold text-[var(--color-text-primary)]">
                Telemetry Preview:
              </span>
              <span className="text-[11px] text-[var(--color-text-tertiary)] block">
                Prog Risk: {previewRisk.progRisk} | Delay Risk: {previewRisk.delRisk} | Budget Risk: {previewRisk.budRisk}
              </span>
            </div>
          </div>
          <RiskBadge level={previewRisk.level} score={previewRisk.score} size="md" />
        </div>

        {/* Row 1: Project ID & Sector */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
              Project ID <span className="text-[var(--color-danger-text)]">*</span>
            </label>
            <input
              type="text"
              required
              placeholder="e.g. P43, NH-66"
              value={formData.project_id}
              onChange={(e) => setFormData({ ...formData, project_id: e.target.value.toUpperCase() })}
              className="w-full rounded-lg border border-[var(--input-border)] bg-[var(--input-bg)] px-3 py-2 text-xs font-mono uppercase text-[var(--input-text)] placeholder-[var(--input-placeholder)] focus:border-[var(--color-brand-primary)] focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
              Sector <span className="text-[var(--color-danger-text)]">*</span>
            </label>
            <select
              value={formData.sector}
              onChange={(e) => setFormData({ ...formData, sector: e.target.value })}
              className="w-full rounded-lg border border-[var(--input-border)] bg-[var(--input-bg)] px-3 py-2 text-xs text-[var(--input-text)] focus:border-[var(--color-brand-primary)] focus:outline-none"
            >
              {sectorOptions.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Row 2: Name */}
        <div>
          <label className="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
            Project Name <span className="text-[var(--color-danger-text)]">*</span>
          </label>
          <input
            type="text"
            required
            placeholder="e.g. National Expressway Package 14 Corridor"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="w-full rounded-lg border border-[var(--input-border)] bg-[var(--input-bg)] px-3 py-2 text-xs text-[var(--input-text)] placeholder-[var(--input-placeholder)] focus:border-[var(--color-brand-primary)] focus:outline-none"
          />
        </div>

        {/* Row 3: Location & Contractor */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
              Location (State/District) <span className="text-[var(--color-danger-text)]">*</span>
            </label>
            <input
              type="text"
              required
              placeholder="e.g. Gujarat, Assam, Delhi"
              value={formData.location}
              onChange={(e) => setFormData({ ...formData, location: e.target.value })}
              className="w-full rounded-lg border border-[var(--input-border)] bg-[var(--input-bg)] px-3 py-2 text-xs text-[var(--input-text)] placeholder-[var(--input-placeholder)] focus:border-[var(--color-brand-primary)] focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
              Lead Contractor / Agency <span className="text-[var(--color-danger-text)]">*</span>
            </label>
            <input
              type="text"
              required
              placeholder="e.g. L&T Infrastructure, NHAI"
              value={formData.contractor}
              onChange={(e) => setFormData({ ...formData, contractor: e.target.value })}
              className="w-full rounded-lg border border-[var(--input-border)] bg-[var(--input-bg)] px-3 py-2 text-xs text-[var(--input-text)] placeholder-[var(--input-placeholder)] focus:border-[var(--color-brand-primary)] focus:outline-none"
            />
          </div>
        </div>

        {/* Row 4: Physical Progress vs Planned Progress */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div>
            <label className="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
              Actual Progress (%)
            </label>
            <input
              type="number"
              min="0"
              max="100"
              step="0.1"
              value={formData.progress}
              onChange={(e) => setFormData({ ...formData, progress: parseFloat(e.target.value) || 0 })}
              className="w-full rounded-lg border border-[var(--input-border)] bg-[var(--input-bg)] px-3 py-2 text-xs font-mono text-[var(--input-text)] focus:border-[var(--color-brand-primary)] focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
              Planned Progress (%)
            </label>
            <input
              type="number"
              min="0"
              max="100"
              step="0.1"
              value={formData.planned_progress}
              onChange={(e) => setFormData({ ...formData, planned_progress: parseFloat(e.target.value) || 0 })}
              className="w-full rounded-lg border border-[var(--input-border)] bg-[var(--input-bg)] px-3 py-2 text-xs font-mono text-[var(--input-text)] focus:border-[var(--color-brand-primary)] focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
              Schedule Delay (Days)
            </label>
            <input
              type="number"
              min="0"
              step="1"
              value={formData.delay_days}
              onChange={(e) => setFormData({ ...formData, delay_days: parseInt(e.target.value) || 0 })}
              className="w-full rounded-lg border border-[var(--input-border)] bg-[var(--input-bg)] px-3 py-2 text-xs font-mono text-[var(--input-text)] focus:border-[var(--color-brand-primary)] focus:outline-none"
            />
          </div>
        </div>

        {/* Row 5: Budget Used & Budget Total */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
              Budget Expended (%)
            </label>
            <input
              type="number"
              min="0"
              max="100"
              step="0.1"
              value={formData.budget_used}
              onChange={(e) => setFormData({ ...formData, budget_used: parseFloat(e.target.value) || 0 })}
              className="w-full rounded-lg border border-[var(--input-border)] bg-[var(--input-bg)] px-3 py-2 text-xs font-mono text-[var(--input-text)] focus:border-[var(--color-brand-primary)] focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
              Total Budget (₹ Crore)
            </label>
            <input
              type="number"
              min="1"
              step="0.5"
              value={formData.budget_total_crore}
              onChange={(e) => setFormData({ ...formData, budget_total_crore: parseFloat(e.target.value) || 0 })}
              className="w-full rounded-lg border border-[var(--input-border)] bg-[var(--input-bg)] px-3 py-2 text-xs font-mono text-[var(--input-text)] focus:border-[var(--color-brand-primary)] focus:outline-none"
            />
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-[var(--color-border-default)]">
          <button
            type="button"
            onClick={onClose}
            disabled={loading}
            className="rounded-lg border border-[var(--button-secondary-border)] bg-[var(--button-secondary-bg)] px-4 py-2 text-xs font-semibold text-[var(--button-secondary-text)] hover:bg-[var(--button-secondary-hover)] transition"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="inline-flex items-center gap-1.5 rounded-lg bg-[var(--color-brand-primary)] px-5 py-2 text-xs font-semibold text-[var(--color-brand-contrast)] hover:bg-[var(--color-brand-hover)] shadow-warm-xs transition disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Registering...</span>
              </>
            ) : (
              <>
                <PlusCircle className="h-4 w-4" />
                <span>Register Project</span>
              </>
            )}
          </button>
        </div>
      </form>
    </Modal>
  );
};
