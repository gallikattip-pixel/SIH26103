import React, { useEffect, useState, useMemo } from "react";
import { Plus } from "lucide-react";
import type { ProjectListItem } from "../types";
import { fetchProjects, type ProjectQueryParams } from "../services/api";
import { ProjectFilterBar } from "../components/projects/ProjectFilterBar";
import { ProjectCard } from "../components/projects/ProjectCard";
import { ProjectTable } from "../components/projects/ProjectTable";
import { CreateProjectModal } from "../components/projects/CreateProjectModal";
import { TableSkeleton } from "../components/common/LoadingSkeleton";
import { EmptyState } from "../components/common/EmptyState";
import { ErrorState } from "../components/common/ErrorState";

export const ProjectsPage: React.FC = () => {
  const [projects, setProjects] = useState<ProjectListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<"grid" | "table">("grid");
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [successBanner, setSuccessBanner] = useState<string | null>(null);
  const [filters, setFilters] = useState<ProjectQueryParams>({
    search: "",
    sector: "all",
    risk_level: "all",
    delayed_only: false,
    sort_by: "risk_score",
    order: "desc",
  });

  const loadProjects = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchProjects(filters);
      setProjects(data);
    } catch (err: any) {
      setError(err.message || "Failed to load projects from Firebase.");
    } finally {
      setLoading(false);
    }
  };

  const handleProjectCreated = (newProject: ProjectListItem) => {
    setProjects((prev) => [newProject, ...prev]);
    setSuccessBanner(`Project ${newProject.project_id} ("${newProject.name}") registered successfully with risk score ${newProject.risk.overall_score}!`);
    setTimeout(() => setSuccessBanner(null), 6000);
  };

  useEffect(() => {
    loadProjects();
  }, [filters.sector, filters.risk_level, filters.delayed_only, filters.sort_by, filters.order]);

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      loadProjects();
    }, 250);
    return () => clearTimeout(timer);
  }, [filters.search]);

  // Unique sector list
  const availableSectors = useMemo(() => {
    const set = new Set<string>();
    projects.forEach((p) => {
      if (p.sector) set.add(p.sector);
    });
    return Array.from(set).sort();
  }, [projects]);

  return (
    <div className="space-y-6">
      {/* Title & Action */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[var(--color-border-subtle)] pb-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[var(--color-text-primary)]">
            Infrastructure Projects Explorer
          </h1>
          <p className="text-xs text-[var(--color-text-tertiary)] font-mono mt-0.5">
            Real-time project inventory with deterministic risk telemetry ({projects.length} loaded)
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="inline-flex items-center gap-1.5 rounded-xl bg-[var(--color-brand-primary)] px-4 py-2 text-xs font-semibold text-[var(--color-brand-contrast)] hover:bg-[var(--color-brand-primary-hover)] shadow-warm-xs transition shrink-0"
          >
            <Plus className="h-4 w-4" />
            <span>New Project</span>
          </button>
        </div>
      </div>

      {/* Success Notification Banner */}
      {successBanner && (
        <div className="flex items-center justify-between rounded-xl border border-[var(--color-success-border)] bg-[var(--color-success-bg)] p-3 text-xs text-[var(--color-success-text)] animate-in fade-in slide-in-from-top-2">
          <p className="font-medium">{successBanner}</p>
          <button
            onClick={() => setSuccessBanner(null)}
            className="text-xs font-bold hover:underline ml-3"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Filter Controls */}
      <ProjectFilterBar
        filters={filters}
        onChange={setFilters}
        viewMode={viewMode}
        onToggleView={setViewMode}
        sectors={availableSectors}
      />

      {/* Main Content Area */}
      {loading ? (
        <TableSkeleton rows={8} />
      ) : error ? (
        <ErrorState
          title="Database Connection Error"
          message={error}
          onRetry={loadProjects}
        />
      ) : projects.length === 0 ? (
        <EmptyState
          title="No Matching Infrastructure Projects Found"
          description={
            filters.search || filters.sector !== "all" || filters.risk_level !== "all"
              ? "No project records match your current filter parameters. Try clearing your search or expanding risk level selections."
              : "No infrastructure projects are currently available in the database."
          }
          action={
            filters.search || filters.sector !== "all" || filters.risk_level !== "all"
              ? {
                  label: "Reset All Filters",
                  onClick: () =>
                    setFilters({
                      search: "",
                      sector: "all",
                      risk_level: "all",
                      delayed_only: false,
                      sort_by: "risk_score",
                      order: "desc",
                    }),
                }
              : {
                  label: "Register New Project",
                  onClick: () => setIsCreateModalOpen(true),
                }
          }
        />
      ) : viewMode === "grid" ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {projects.map((project) => (
            <ProjectCard key={project.project_id} project={project} />
          ))}
        </div>
      ) : (
        <ProjectTable projects={projects} />
      )}

      {/* Register Project Modal */}
      <CreateProjectModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSuccess={handleProjectCreated}
        existingSectors={availableSectors}
      />
    </div>
  );
};
