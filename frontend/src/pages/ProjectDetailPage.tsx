import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  ArrowLeft,
  LayoutDashboard,
  IndianRupee,
  Activity,
  Calendar,
  CheckSquare,
  Building,
  FileText,
  ShieldAlert,
  History,
  Flag,
} from "lucide-react";

import type { ProjectDetail360 } from "../types";
import { fetchProjectDetail } from "../services/api";
import { DetailSkeleton } from "../components/common/LoadingSkeleton";
import { ErrorState } from "../components/common/ErrorState";
import { RiskBadge } from "../components/common/RiskBadge";

import { OverviewTab } from "../components/project-detail/OverviewTab";
import { FinancialTab } from "../components/project-detail/FinancialTab";
import { ProgressTab } from "../components/project-detail/ProgressTab";
import { TimelineTab } from "../components/project-detail/TimelineTab";
import { MilestonesTab } from "../components/project-detail/MilestonesTab";
import { AgenciesTab } from "../components/project-detail/AgenciesTab";
import { DocumentsTab } from "../components/project-detail/DocumentsTab";
import { RiskAiTab } from "../components/project-detail/RiskAiTab";
import { HistoryTab } from "../components/project-detail/HistoryTab";
import { SnapshotModal } from "../components/project-detail/SnapshotModal";
import { OutcomeModal } from "../components/project-detail/OutcomeModal";

type TabKey =
  | "overview"
  | "financial"
  | "progress"
  | "timeline"
  | "milestones"
  | "agencies"
  | "documents"
  | "risk_ai"
  | "history";

export const ProjectDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [detail, setDetail] = useState<ProjectDetail360 | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabKey>("overview");

  const loadProject = async () => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetchProjectDetail(id);
      setDetail(res);
    } catch (err: any) {
      setError(err.message || "Failed to load project 360° record.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProject();
  }, [id]);

  if (loading) {
    return (
      <div className="py-6">
        <DetailSkeleton />
      </div>
    );
  }

  if (error || !detail) {
    return (
      <div className="py-12">
        <ErrorState
          title="Project Record Not Found"
          message={error || `Project '${id}' is not present in the database.`}
          onRetry={loadProject}
        />
        <div className="text-center mt-4">
          <Link
            to="/projects"
            className="inline-flex items-center gap-1.5 text-xs text-[var(--color-text-accent)] hover:text-[var(--color-brand-primary)] font-medium"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>Back to Projects Explorer</span>
          </Link>
        </div>
      </div>
    );
  }

  const { project, risk } = detail;
  const [showSnapshotModal, setShowSnapshotModal] = useState(false);
  const [showOutcomeModal, setShowOutcomeModal] = useState(false);

  const handleSnapshotCreated = () => {
    setShowSnapshotModal(false);
    loadProject(); // Refresh to update any cached data
  };

  const handleOutcomeCreated = () => {
    setShowOutcomeModal(false);
    loadProject(); // Refresh to update any cached data
  };

  const tabs: { key: TabKey; label: string; icon: React.FC<{ className?: string }> }[] = [
    { key: "overview", label: "Overview", icon: LayoutDashboard },
    { key: "financial", label: "Financial", icon: IndianRupee },
    { key: "progress", label: "Physical Progress", icon: Activity },
    { key: "timeline", label: "Timeline & Delays", icon: Calendar },
    { key: "milestones", label: "Milestones", icon: CheckSquare },
    { key: "agencies", label: "Agencies & Contractors", icon: Building },
    { key: "documents", label: "Documents", icon: FileText },
    { key: "risk_ai", label: "Risk & AI Analysis", icon: ShieldAlert },
    { key: "history", label: "History", icon: History },
  ];

  return (
    <div className="space-y-6">
      {/* Breadcrumbs & Header Bar */}
      <div>
        <Link
          to="/projects"
          className="inline-flex items-center gap-1.5 text-xs font-mono text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition mb-3"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          <span>Back to Projects Explorer</span>
        </Link>

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[var(--color-border-subtle)] pb-5">
          <div>
            <div className="flex items-center gap-2.5">
              <span className="rounded-lg border border-[var(--color-border-accent)] bg-[var(--color-brand-tint)] px-2.5 py-1 text-xs font-mono font-bold text-[var(--color-text-accent)] shadow-[var(--shadow-xs)]">
                {project.project_id}
              </span>
              <span className="rounded-lg border border-[var(--color-border-default)] bg-[var(--color-bg-surface-muted)] px-2.5 py-1 text-xs font-mono text-[var(--color-text-secondary)]">
                {project.sector}
              </span>
              <span className="text-xs text-[var(--color-border-strong)] font-mono">•</span>
              <span className="text-xs text-[var(--color-text-tertiary)]">{project.location}</span>
            </div>
            <h1 className="mt-2 text-2xl sm:text-3xl font-bold tracking-tight text-[var(--color-text-primary)]">
              {project.name}
            </h1>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowSnapshotModal(true)}
              className="inline-flex items-center gap-1.5 rounded-lg border border-[var(--color-border-default)] bg-[var(--color-bg-surface-soft)] px-3 py-1.5 text-xs font-medium text-[var(--color-text-primary)] hover:bg-[var(--color-bg-accent)] hover:border-[var(--color-brand-primary)] transition shadow-[var(--shadow-xs)]"
            >
              <History className="h-3.5 w-3.5" />
              <span>Record Snapshot</span>
            </button>
            <button
              onClick={() => setShowOutcomeModal(true)}
              className="inline-flex items-center gap-1.5 rounded-lg border border-[var(--color-border-default)] bg-[var(--color-bg-surface-soft)] px-3 py-1.5 text-xs font-medium text-[var(--color-text-primary)] hover:bg-[var(--color-bg-accent)] hover:border-[var(--color-brand-primary)] transition shadow-[var(--shadow-xs)]"
            >
              <Flag className="h-3.5 w-3.5" />
              <span>Record Outcome</span>
            </button>
            <RiskBadge
              level={risk.overall_level}
              score={risk.overall_score}
              size="lg"
            />
          </div>
        </div>
      </div>

      {/* 360 Navigation Tabs */}
      <div className="border-b border-[var(--color-border-default)] overflow-x-auto">
        <nav className="flex space-x-2 pb-px" aria-label="Tabs">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.key;
            return (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`flex items-center gap-2 whitespace-nowrap border-b-2 py-3 px-3.5 text-xs font-medium transition ${
                  isActive
                    ? "border-[var(--color-brand-primary)] text-[var(--color-brand-contrast)] bg-[var(--color-bg-accent)] font-semibold"
                    : "border-transparent text-[var(--color-text-secondary)] hover:border-[var(--color-border-strong)] hover:text-[var(--color-text-primary)]"
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Active Tab Content */}
      <div className="pt-2">
        {activeTab === "overview" && <OverviewTab detail={detail} />}
        {activeTab === "financial" && <FinancialTab financial={detail.financial} project={project} />}
        {activeTab === "progress" && <ProgressTab progress={detail.progress} />}
        {activeTab === "timeline" && <TimelineTab timeline={detail.timeline} />}
        {activeTab === "milestones" && <MilestonesTab milestones={detail.milestones} />}
        {activeTab === "agencies" && <AgenciesTab agencies={detail.agencies} />}
        {activeTab === "documents" && (
          <DocumentsTab projectId={project.project_id} initialDocuments={detail.documents} />
        )}
        {activeTab === "risk_ai" && <RiskAiTab detail={detail} />}
        {activeTab === "history" && <HistoryTab projectId={project.project_id} projectName={project.name} />}
      </div>

      <SnapshotModal
        isOpen={showSnapshotModal}
        onClose={() => setShowSnapshotModal(false)}
        project={project}
        risk={risk}
        onSuccess={handleSnapshotCreated}
      />

      <OutcomeModal
        isOpen={showOutcomeModal}
        onClose={() => setShowOutcomeModal(false)}
        project={project}
        risk={risk}
        onSuccess={handleOutcomeCreated}
      />
    </div>
  );
};
