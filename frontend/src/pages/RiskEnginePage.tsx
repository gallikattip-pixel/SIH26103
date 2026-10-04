import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ShieldAlert, Cpu, ArrowRight, Code } from "lucide-react";
import type { ProjectListItem } from "../types";
import { fetchProjects } from "../services/api";
import { RiskBadge } from "../components/common/RiskBadge";
import { TableSkeleton } from "../components/common/LoadingSkeleton";
import { ErrorState } from "../components/common/ErrorState";
import { EmptyState } from "../components/common/EmptyState";

export const RiskEnginePage: React.FC = () => {
  const [projects, setProjects] = useState<ProjectListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchProjects({ sort_by: "risk_score", order: "desc" });
      setProjects(data);
    } catch (err: any) {
      setError(err.message || "Failed to load risk engine audits.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="border-b border-[var(--color-border-default)] pb-4">
        <div className="flex items-center gap-2 text-[var(--color-text-accent)] mb-1">
          <Cpu className="h-4 w-4" />
          <span className="text-xs font-mono font-semibold uppercase tracking-wider">
            Deterministic Source of Truth
          </span>
        </div>
        <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[var(--color-text-primary)]">
          Python Risk Engine Audit & Transparency Portal
        </h1>
        <p className="text-xs text-[var(--color-text-secondary)] font-mono mt-0.5">
          Mathematical risk evaluation verified across all active infrastructure projects
        </p>
      </div>

      {/* Formula Transparency Card */}
      <div className="rounded-2xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-6 shadow-warm-sm space-y-4">
        <div className="flex items-center gap-2 border-b border-[var(--color-border-subtle)] pb-3">
          <Code className="h-4 w-4 text-[var(--color-brand-primary)]" />
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-[var(--color-text-primary)]">
            Authoritative Mathematical Formulation
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono">
          <div className="rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface-soft)] p-4 space-y-2">
            <span className="text-[var(--color-text-accent)] font-bold">1. Progress Risk (35% Weight)</span>
            <p className="text-[var(--color-text-secondary)] text-[11px] font-sans">
              Measures variance between planned and physical execution.
            </p>
            <div className="rounded border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface-muted)] p-2 text-[var(--color-text-primary)] text-[11px]">
              gap = planned_progress - progress<br />
              progress_risk = clamp(max(gap, 0) × 2.5)
            </div>
          </div>

          <div className="rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface-soft)] p-4 space-y-2">
            <span className="text-[var(--color-text-accent)] font-bold">2. Delay Risk (40% Weight)</span>
            <p className="text-[var(--color-text-secondary)] text-[11px] font-sans">
              Linear scaling of schedule delay, reaching maximum threshold at 90 days.
            </p>
            <div className="rounded border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface-muted)] p-2 text-[var(--color-text-primary)] text-[11px]">
              delay_risk = clamp((delay_days / 90) × 100)
            </div>
          </div>

          <div className="rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface-soft)] p-4 space-y-2">
            <span className="text-[var(--color-text-accent)] font-bold">3. Budget Risk (25% Weight)</span>
            <p className="text-[var(--color-text-secondary)] text-[11px] font-sans">
              Detects capital drawdowns exceeding verified on-site milestone delivery.
            </p>
            <div className="rounded border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface-muted)] p-2 text-[var(--color-text-primary)] text-[11px]">
              spend_ahead = max(budget_used - progress, 0)<br />
              budget_risk = clamp(0.55×used + 0.45×ahead)
            </div>
          </div>
        </div>

        <div className="rounded-lg border border-[var(--color-border-gold)] bg-[var(--color-brand-tint)] p-3 text-xs text-[var(--color-text-primary)] flex items-center justify-between">
          <span>
            <span className="font-mono text-[var(--color-text-accent)] font-bold">Overall Score: </span>
            <code className="font-mono text-[var(--color-text-primary)] font-semibold">
              overall_score = clamp(0.35 × progress_risk + 0.40 × delay_risk + 0.25 × budget_risk)
            </code>
          </span>
          <span className="font-mono text-[11px] text-[var(--color-text-secondary)] hidden sm:inline">
            HIGH ≥ 70 | MEDIUM ≥ 40 | LOW &lt; 40
          </span>
        </div>
      </div>

      {/* Real Audit Matrix Table */}
      {loading ? (
        <TableSkeleton rows={8} />
      ) : error ? (
        <ErrorState message={error} onRetry={loadData} />
      ) : projects.length === 0 ? (
        <EmptyState
          title="No Projects Available for Risk Audit"
          description="The Firebase Realtime Database is connected, but contains zero project records. Once projects are registered in Firebase, their deterministic risk metrics will appear here."
        />
      ) : (
        <div className="rounded-2xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-5 shadow-warm-sm space-y-4">
          <div className="flex items-center justify-between border-b border-[var(--color-border-subtle)] pb-3">
            <div className="flex items-center gap-2">
              <ShieldAlert className="h-4 w-4 text-[var(--color-warning-icon)]" />
              <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-[var(--color-text-primary)]">
                Live Audit Matrix — All Monitored Projects ({projects.length})
              </h3>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-[var(--color-text-primary)]">
              <thead className="border-b border-[var(--color-table-header-border)] bg-[var(--color-table-header-bg)] text-[11px] font-mono uppercase text-[var(--color-text-secondary)]">
                <tr>
                  <th className="py-2.5 px-3">Project ID</th>
                  <th className="py-2.5 px-3">Project Name</th>
                  <th className="py-2.5 px-3">Progress Risk</th>
                  <th className="py-2.5 px-3">Delay Risk</th>
                  <th className="py-2.5 px-3">Budget Risk</th>
                  <th className="py-2.5 px-3">Overall Score</th>
                  <th className="py-2.5 px-3">Identified Factors</th>
                  <th className="py-2.5 px-3 text-right">Review</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--color-table-row-border)] font-mono">
                {projects.map((p) => (
                  <tr key={p.project_id} className="hover:bg-[var(--color-table-row-hover)] transition">
                    <td className="py-3 px-3 font-bold text-[var(--color-text-accent)]">{p.project_id}</td>
                    <td className="py-3 px-3 font-sans font-medium text-[var(--color-text-primary)] max-w-[180px] truncate">
                      {p.name}
                    </td>
                    <td className="py-3 px-3">
                      <span className="text-[var(--color-text-primary)]">{p.risk.progress_risk}/100</span>
                      <span className="text-[10px] text-[var(--color-text-tertiary)] block">Gap: {p.risk.progress_gap}%</span>
                    </td>
                    <td className="py-3 px-3">
                      <span className="text-[var(--color-text-primary)]">{p.risk.delay_risk}/100</span>
                      <span className="text-[10px] text-[var(--color-text-tertiary)] block">{p.delay_days} days</span>
                    </td>
                    <td className="py-3 px-3">
                      <span className="text-[var(--color-text-primary)]">{p.risk.budget_risk}/100</span>
                      <span className="text-[10px] text-[var(--color-text-tertiary)] block">{p.budget_used}% used</span>
                    </td>
                    <td className="py-3 px-3">
                      <RiskBadge level={p.risk.overall_level} score={p.risk.overall_score} size="sm" />
                    </td>
                    <td className="py-3 px-3 font-sans text-[11px] text-[var(--color-text-secondary)] max-w-[200px] truncate">
                      {p.risk.major_factors.join("; ")}
                    </td>
                    <td className="py-3 px-3 text-right">
                      <Link
                        to={`/projects/${p.project_id}`}
                        className="inline-flex items-center gap-1 rounded border border-[var(--color-border-default)] bg-[var(--color-bg-surface-soft)] px-2.5 py-1 text-[11px] text-[var(--color-text-primary)] hover:border-[var(--color-brand-primary)] hover:bg-[var(--color-bg-accent)] transition"
                      >
                        <span>360°</span>
                        <ArrowRight className="h-3 w-3 text-[var(--color-brand-primary)]" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
