import React from "react";
import { Search, Filter, ArrowUpDown, LayoutGrid, List } from "lucide-react";
import type { ProjectQueryParams } from "../../services/api";

interface ProjectFilterBarProps {
  filters: ProjectQueryParams;
  onChange: (newFilters: ProjectQueryParams) => void;
  viewMode: "grid" | "table";
  onToggleView: (mode: "grid" | "table") => void;
  sectors: string[];
}

export const ProjectFilterBar: React.FC<ProjectFilterBarProps> = ({
  filters,
  onChange,
  viewMode,
  onToggleView,
  sectors,
}) => {
  return (
    <div className="flex flex-col gap-3 rounded-xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-4 shadow-[var(--shadow-sm)]">
      <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
        {/* Search Bar */}
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--input-placeholder)]" />
          <input
            type="text"
            placeholder="Search by ID, name, contractor, location..."
            value={filters.search || ""}
            onChange={(e) => onChange({ ...filters, search: e.target.value })}
            className="w-full rounded-lg border border-[var(--input-border)] bg-[var(--input-bg)] py-2 pl-10 pr-4 text-xs text-[var(--input-text)] placeholder-[var(--input-placeholder)] transition focus:border-[var(--color-brand-primary)] focus:outline-none"
          />
        </div>

        {/* View Mode Toggle */}
        <div className="flex items-center gap-1 self-end md:self-auto rounded-lg border border-[var(--color-border-default)] bg-[var(--color-bg-surface-muted)] p-1">
          <button
            onClick={() => onToggleView("grid")}
            className={`rounded-md p-1.5 transition ${
              viewMode === "grid"
                ? "bg-[var(--color-brand-tint)] text-[var(--color-text-accent)] border border-[var(--color-border-accent)] shadow-[var(--shadow-xs)]"
                : "text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
            }`}
            title="Grid View"
            aria-label="Grid View"
          >
            <LayoutGrid className="h-4 w-4" />
          </button>
          <button
            onClick={() => onToggleView("table")}
            className={`rounded-md p-1.5 transition ${
              viewMode === "table"
                ? "bg-[var(--color-brand-tint)] text-[var(--color-text-accent)] border border-[var(--color-border-accent)] shadow-[var(--shadow-xs)]"
                : "text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
            }`}
            title="Table View"
            aria-label="Table View"
          >
            <List className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Filter Controls Row */}
      <div className="flex flex-wrap items-center gap-2.5 pt-2 border-t border-[var(--color-border-subtle)]">
        <div className="flex items-center gap-1.5 text-xs text-[var(--color-text-secondary)] font-mono">
          <Filter className="h-3.5 w-3.5 text-[var(--color-text-accent)]" />
          <span>FILTERS:</span>
        </div>

        {/* Risk Level Filter */}
        <select
          value={filters.risk_level || "all"}
          onChange={(e) => onChange({ ...filters, risk_level: e.target.value })}
          className="rounded-lg border border-[var(--input-border)] bg-[var(--input-bg)] px-2.5 py-1.5 text-xs text-[var(--color-text-primary)] focus:border-[var(--color-brand-primary)] focus:outline-none"
        >
          <option value="all">All Risk Levels</option>
          <option value="HIGH">High Risk Only</option>
          <option value="MEDIUM">Medium Risk Only</option>
          <option value="LOW">Low Risk Only</option>
        </select>

        {/* Sector Filter */}
        <select
          value={filters.sector || "all"}
          onChange={(e) => onChange({ ...filters, sector: e.target.value })}
          className="rounded-lg border border-[var(--input-border)] bg-[var(--input-bg)] px-2.5 py-1.5 text-xs text-[var(--color-text-primary)] focus:border-[var(--color-brand-primary)] focus:outline-none"
        >
          <option value="all">All Sectors</option>
          {sectors.map((sec) => (
            <option key={sec} value={sec}>
              {sec}
            </option>
          ))}
        </select>

        {/* Delayed Toggle */}
        <label className="flex cursor-pointer items-center gap-2 rounded-lg border border-[var(--color-border-default)] bg-[var(--color-bg-surface-soft)] px-3 py-1.5 text-xs text-[var(--color-text-secondary)] transition hover:border-[var(--color-border-accent)] hover:text-[var(--color-text-primary)]">
          <input
            type="checkbox"
            checked={Boolean(filters.delayed_only)}
            onChange={(e) => onChange({ ...filters, delayed_only: e.target.checked })}
            className="rounded border-[var(--input-border)] accent-[var(--color-brand-primary)] focus:ring-0 focus:ring-offset-0"
          />
          <span>Delayed Only</span>
        </label>

        {/* Sort Field */}
        <div className="ml-auto flex items-center gap-1.5">
          <ArrowUpDown className="h-3.5 w-3.5 text-[var(--color-text-tertiary)]" />
          <select
            value={filters.sort_by || "risk_score"}
            onChange={(e) => onChange({ ...filters, sort_by: e.target.value })}
            className="rounded-lg border border-[var(--input-border)] bg-[var(--input-bg)] px-2.5 py-1.5 text-xs text-[var(--color-text-primary)] focus:border-[var(--color-brand-primary)] focus:outline-none font-mono"
          >
            <option value="risk_score">Sort: Risk Score</option>
            <option value="delay">Sort: Delay Days</option>
            <option value="progress_gap">Sort: Progress Gap</option>
            <option value="budget">Sort: Total Budget</option>
            <option value="name">Sort: Project Name</option>
          </select>
        </div>
      </div>
    </div>
  );
};
