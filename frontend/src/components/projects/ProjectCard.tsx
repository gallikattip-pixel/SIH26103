import React from "react";
import { Link } from "react-router-dom";
import { MapPin, Building2, Clock, IndianRupee, ArrowRight } from "lucide-react";
import type { ProjectListItem } from "../../types";
import { RiskBadge } from "../common/RiskBadge";

export const ProjectCard: React.FC<{ project: ProjectListItem }> = ({ project }) => {
  const isDelayed = project.delay_days > 0;
  const progressGap = Math.round((project.planned_progress - project.progress) * 10) / 10;

  return (
    <div className="group relative flex flex-col justify-between rounded-xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-5 shadow-[var(--shadow-sm)] transition-all hover:border-[var(--color-border-accent)] hover:shadow-[var(--shadow-md)]">
      <div>
        {/* Header: ID, Sector & Risk Badge */}
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className="rounded-md border border-[var(--color-border-accent)] bg-[var(--color-brand-tint)] px-2 py-0.5 text-xs font-mono font-bold text-[var(--color-text-accent)]">
              {project.project_id}
            </span>
            <span className="rounded-md border border-[var(--color-border-default)] bg-[var(--color-bg-surface-muted)] px-2 py-0.5 text-[11px] font-mono text-[var(--color-text-secondary)]">
              {project.sector}
            </span>
          </div>
          <RiskBadge
            level={project.risk.overall_level}
            score={project.risk.overall_score}
            size="sm"
          />
        </div>

        {/* Project Name & Location */}
        <h4 className="mt-3 text-sm font-semibold text-[var(--color-text-primary)] group-hover:text-[var(--color-brand-primary)] transition-colors line-clamp-1">
          {project.name}
        </h4>
        <div className="mt-1 flex items-center gap-1.5 text-xs text-[var(--color-text-secondary)]">
          <MapPin className="h-3.5 w-3.5 text-[var(--color-text-tertiary)] shrink-0" />
          <span className="truncate">{project.location}</span>
        </div>

        {/* Progress Bar & Indicators */}
        <div className="mt-4 space-y-1.5">
          <div className="flex justify-between text-xs font-mono">
            <span className="text-[var(--color-text-secondary)]">Physical Progress:</span>
            <span className="text-[var(--color-text-primary)] font-bold">{project.progress}%</span>
          </div>
          <div className="h-2 w-full overflow-hidden rounded-full bg-[var(--color-bg-secondary)]">
            <div
              className={`h-full transition-all duration-500 rounded-full ${
                project.risk.overall_level === "HIGH"
                  ? "bg-[var(--color-danger-icon)]"
                  : project.risk.overall_level === "MEDIUM"
                  ? "bg-[var(--color-warning-icon)]"
                  : "bg-[var(--color-success-icon)]"
              }`}
              style={{ width: `${Math.min(100, Math.max(0, project.progress))}%` }}
            />
          </div>
          <div className="flex justify-between text-[11px] font-mono text-[var(--color-text-tertiary)]">
            <span>Planned: {project.planned_progress}%</span>
            {progressGap > 0 ? (
              <span className="text-[var(--color-warning-text)] font-semibold">Lag: {progressGap}%</span>
            ) : (
              <span className="text-[var(--color-success-text)] font-semibold">On Schedule</span>
            )}
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="mt-4 grid grid-cols-2 gap-2 border-t border-[var(--color-border-subtle)] pt-3 text-xs">
          <div className="flex items-center gap-1.5 text-[var(--color-text-secondary)]">
            <Clock className={`h-3.5 w-3.5 ${isDelayed ? "text-[var(--color-warning-icon)]" : "text-[var(--color-text-tertiary)]"}`} />
            <span className="font-mono">
              {isDelayed ? `${project.delay_days}d delay` : "Zero delay"}
            </span>
          </div>
          <div className="flex items-center gap-1.5 text-[var(--color-text-secondary)]">
            <IndianRupee className="h-3.5 w-3.5 text-[var(--color-text-tertiary)]" />
            <span className="font-mono font-medium">₹{project.budget_total_crore} Cr</span>
          </div>
        </div>

        {/* Contractor */}
        <div className="mt-2.5 flex items-center gap-1.5 text-[11px] text-[var(--color-text-tertiary)] truncate">
          <Building2 className="h-3.5 w-3.5 text-[var(--color-text-muted)] shrink-0" />
          <span className="truncate">{project.contractor}</span>
        </div>
      </div>

      {/* Footer action */}
      <Link
        to={`/projects/${project.project_id}`}
        className="mt-4 inline-flex w-full items-center justify-center gap-1.5 rounded-lg border border-[var(--color-border-strong)] bg-[var(--color-bg-surface)] py-2 text-xs font-medium text-[var(--color-text-primary)] shadow-[var(--shadow-xs)] transition hover:border-[var(--color-brand-primary)] hover:bg-[var(--color-brand-tint)] hover:text-[var(--color-text-accent)]"
      >
        <span>Project 360° View</span>
        <ArrowRight className="h-3.5 w-3.5" />
      </Link>
    </div>
  );
};
