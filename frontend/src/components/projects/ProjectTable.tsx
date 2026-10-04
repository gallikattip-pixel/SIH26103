import React from "react";
import { Link } from "react-router-dom";
import { ArrowRight } from "lucide-react";
import type { ProjectListItem } from "../../types";
import { RiskBadge } from "../common/RiskBadge";

export const ProjectTable: React.FC<{ projects: ProjectListItem[] }> = ({ projects }) => {
  return (
    <div className="overflow-hidden rounded-xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] shadow-[var(--shadow-sm)]">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-[var(--color-text-primary)]">
          <thead className="border-b border-[var(--color-border-default)] bg-[var(--color-bg-surface-muted)] text-[11px] font-mono uppercase tracking-wider text-[var(--color-text-tertiary)]">
            <tr>
              <th className="py-3.5 px-4 font-semibold">Project ID</th>
              <th className="py-3.5 px-4 font-semibold">Title & Location</th>
              <th className="py-3.5 px-4 font-semibold">Sector</th>
              <th className="py-3.5 px-4 font-semibold">Physical Progress</th>
              <th className="py-3.5 px-4 font-semibold">Delay</th>
              <th className="py-3.5 px-4 font-semibold">Budget (Cr)</th>
              <th className="py-3.5 px-4 font-semibold">Deterministic Risk</th>
              <th className="py-3.5 px-4 font-semibold text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--color-border-subtle)]">
            {projects.map((p) => (
              <tr
                key={p.project_id}
                className="transition hover:bg-[var(--color-bg-surface-soft)] group"
              >
                <td className="py-3 px-4 font-mono font-bold text-[var(--color-text-accent)]">
                  {p.project_id}
                </td>
                <td className="py-3 px-4">
                  <div className="font-semibold text-[var(--color-text-primary)] group-hover:text-[var(--color-brand-primary)] transition-colors">
                    {p.name}
                  </div>
                  <div className="text-[11px] text-[var(--color-text-tertiary)]">{p.location}</div>
                </td>
                <td className="py-3 px-4 font-mono text-[var(--color-text-secondary)]">{p.sector}</td>
                <td className="py-3 px-4">
                  <div className="flex items-center gap-2">
                    <span className="w-9 font-mono font-bold text-[var(--color-text-primary)]">
                      {p.progress}%
                    </span>
                    <div className="h-1.5 w-16 overflow-hidden rounded-full bg-[var(--color-bg-secondary)]">
                      <div
                        className={`h-full rounded-full ${
                          p.risk.overall_level === "HIGH"
                            ? "bg-[var(--color-danger-icon)]"
                            : p.risk.overall_level === "MEDIUM"
                            ? "bg-[var(--color-warning-icon)]"
                            : "bg-[var(--color-success-icon)]"
                        }`}
                        style={{ width: `${Math.min(100, Math.max(0, p.progress))}%` }}
                      />
                    </div>
                  </div>
                  <div className="text-[10px] font-mono text-[var(--color-text-tertiary)]">
                    Plan: {p.planned_progress}%
                  </div>
                </td>
                <td className="py-3 px-4 font-mono">
                  {p.delay_days > 0 ? (
                    <span className="text-[var(--color-warning-text)] font-semibold">
                      +{p.delay_days}d
                    </span>
                  ) : (
                    <span className="text-[var(--color-success-text)] font-semibold">On Time</span>
                  )}
                </td>
                <td className="py-3 px-4 font-mono">
                  <div className="text-[var(--color-text-primary)] font-semibold">₹{p.budget_total_crore}</div>
                  <div className="text-[10px] text-[var(--color-text-tertiary)]">{p.budget_used}% used</div>
                </td>
                <td className="py-3 px-4">
                  <RiskBadge
                    level={p.risk.overall_level}
                    score={p.risk.overall_score}
                    size="sm"
                  />
                </td>
                <td className="py-3 px-4 text-right">
                  <Link
                    to={`/projects/${p.project_id}`}
                    className="inline-flex items-center gap-1 rounded-lg border border-[var(--color-border-strong)] bg-[var(--color-bg-surface)] px-2.5 py-1 text-[11px] font-medium text-[var(--color-text-primary)] shadow-[var(--shadow-xs)] transition hover:border-[var(--color-brand-primary)] hover:bg-[var(--color-brand-tint)] hover:text-[var(--color-text-accent)]"
                  >
                    <span>360°</span>
                    <ArrowRight className="h-3 w-3" />
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
