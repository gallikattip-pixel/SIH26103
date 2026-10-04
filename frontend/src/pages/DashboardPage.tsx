import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  FolderKanban,
  ShieldAlert,
  Clock,
  IndianRupee,
  Activity,
  AlertTriangle,
  ArrowRight,
} from "lucide-react";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip as RechartsTooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts";

import type { DashboardSummary } from "../types";
import { fetchDashboard } from "../services/api";
import { KpiCard } from "../components/common/KpiCard";
import { EmptyState } from "../components/common/EmptyState";
import { ErrorState } from "../components/common/ErrorState";
import { CardSkeleton, TableSkeleton } from "../components/common/LoadingSkeleton";
import { RiskBadge } from "../components/common/RiskBadge";

export const DashboardPage: React.FC = () => {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchDashboard();
      setData(res);
    } catch (err: any) {
      setError(err.message || "Failed to load dashboard metrics from Firebase.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <CardSkeleton />
          <CardSkeleton />
          <CardSkeleton />
          <CardSkeleton />
        </div>
        <TableSkeleton rows={6} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="py-12">
        <ErrorState
          title="Database Connectivity Error"
          message={error}
          onRetry={loadData}
        />
      </div>
    );
  }

  if (!data || data.total_projects === 0) {
    return (
      <div className="py-12">
        <EmptyState
          title="No Infrastructure Projects Available"
          description="The Firebase Realtime Database is connected, but contains zero active project records. Once projects are submitted by nodal agencies, real-time analytics will render here."
        />
      </div>
    );
  }

  const riskPieData = [
    { name: "High Risk", value: data.risk_distribution.high_count, color: "#A85047" },
    { name: "Medium Risk", value: data.risk_distribution.medium_count, color: "#B08332" },
    { name: "Low Risk", value: data.risk_distribution.low_count, color: "#477F57" },
  ].filter((d) => d.value > 0);

  const sectorChartData = data.sectors.map((s) => ({
    name: s.sector,
    count: s.count,
    avgProgress: s.avg_progress,
  }));

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[var(--color-border-subtle)] pb-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[var(--color-text-primary)]">
            Executive Oversight Command Center
          </h1>
          <p className="text-xs text-[var(--color-text-tertiary)] font-mono mt-0.5">
            Real-time portfolio telemetry powered by Firebase RTDB & Python Risk Engine
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Link
            to="/ai-assistant"
            className="inline-flex items-center gap-1.5 rounded-lg border border-[var(--color-border-accent)] bg-[var(--color-brand-tint)] px-3 py-1.5 text-xs font-mono font-medium text-[var(--color-text-accent)] transition hover:bg-[var(--color-bg-accent-hover)] shadow-[var(--shadow-xs)]"
          >
            <span>Ask AI Assistant</span>
            <ArrowRight className="h-3 w-3" />
          </Link>
        </div>
      </div>

      {/* Top 5 KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <KpiCard
          title="Total Projects"
          value={data.total_projects}
          subtitle="Monitored in RTDB"
          icon={FolderKanban}
          highlightColor="cyan"
        />
        <KpiCard
          title="High-Risk Projects"
          value={data.high_risk_projects}
          subtitle="Score ≥ 70/100"
          icon={ShieldAlert}
          badge={{ text: "ALERT", variant: "high" }}
          highlightColor="rose"
        />
        <KpiCard
          title="Delayed Projects"
          value={data.delayed_projects_count}
          subtitle="Schedule variance > 0"
          icon={Clock}
          highlightColor="amber"
        />
        <KpiCard
          title="Avg Progress"
          value={`${data.average_progress}%`}
          subtitle="Physical delivery"
          icon={Activity}
          highlightColor="emerald"
        />
        <KpiCard
          title="Budget Expended"
          value={`₹${Math.round(data.total_expended_budget_crore)} Cr`}
          subtitle={`of ₹${Math.round(data.total_sanctioned_budget_crore)} Cr sanctioned`}
          icon={IndianRupee}
          highlightColor="blue"
        />
      </div>

      {/* Charts Section: Risk Donut & Sector Bar */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Risk Distribution Donut */}
        <div className="lg:col-span-5 rounded-2xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-5 shadow-[var(--shadow-sm)]">
          <div className="flex items-center justify-between border-b border-[var(--color-border-subtle)] pb-3">
            <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-[var(--color-text-primary)]">
              Risk Distribution
            </h3>
            <span className="text-[11px] font-mono text-[var(--color-text-tertiary)]">
              {data.total_projects} Projects
            </span>
          </div>

          <div className="h-56 mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={riskPieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={85}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {riskPieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <RechartsTooltip
                  contentStyle={{
                    backgroundColor: "#FFFFFF",
                    borderColor: "#E8E0D2",
                    fontSize: "12px",
                    borderRadius: "8px",
                    boxShadow: "0 4px 12px rgba(71, 61, 45, 0.08)",
                  }}
                  itemStyle={{ color: "#2B2925" }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="flex justify-center gap-6 pt-2 border-t border-[var(--color-border-subtle)] text-xs font-mono">
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-[var(--color-danger-icon)]" />
              <span className="text-[var(--color-text-secondary)]">High: {data.risk_distribution.high_count}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-[var(--color-warning-icon)]" />
              <span className="text-[var(--color-text-secondary)]">Med: {data.risk_distribution.medium_count}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-[var(--color-success-icon)]" />
              <span className="text-[var(--color-text-secondary)]">Low: {data.risk_distribution.low_count}</span>
            </div>
          </div>
        </div>

        {/* Sector Breakdown Bar Chart */}
        <div className="lg:col-span-7 rounded-2xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-5 shadow-[var(--shadow-sm)]">
          <div className="flex items-center justify-between border-b border-[var(--color-border-subtle)] pb-3">
            <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-[var(--color-text-primary)]">
              Portfolio Distribution by Sector
            </h3>
            <span className="text-[11px] font-mono text-[var(--color-text-tertiary)]">
              Project Count & Avg Progress
            </span>
          </div>

          <div className="h-56 mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={sectorChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E8E0D2" />
                <XAxis dataKey="name" stroke="#817A6F" fontSize={11} tickLine={false} />
                <YAxis stroke="#817A6F" fontSize={11} tickLine={false} />
                <RechartsTooltip
                  contentStyle={{
                    backgroundColor: "#FFFFFF",
                    borderColor: "#E8E0D2",
                    fontSize: "12px",
                    borderRadius: "8px",
                    boxShadow: "0 4px 12px rgba(71, 61, 45, 0.08)",
                  }}
                  itemStyle={{ color: "#2B2925" }}
                />
                <Bar dataKey="avgProgress" name="Avg Progress %" fill="#C9A96E" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="flex justify-between items-center pt-2 border-t border-[var(--color-border-subtle)] text-[11px] font-mono text-[var(--color-text-tertiary)]">
            <span>Bar height indicates certified average physical progress</span>
            <span>{data.sectors.length} Sectors Active</span>
          </div>
        </div>
      </div>

      {/* Early Warning Alerts Radar */}
      {data.early_warnings.length > 0 && (
        <div className="rounded-2xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-5 shadow-[var(--shadow-sm)] space-y-3">
          <div className="flex items-center gap-2 border-b border-[var(--color-border-subtle)] pb-3">
            <AlertTriangle className="h-4 w-4 text-[var(--color-warning-icon)] animate-pulse" />
            <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-[var(--color-text-primary)]">
              Automated Early Warning Alerts ({data.early_warnings.length})
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {data.early_warnings.map((warn, idx) => (
              <div
                key={idx}
                className="rounded-xl border border-[var(--color-danger-border)] bg-[var(--color-danger-bg)]/40 p-3.5 space-y-1.5 transition hover:border-[var(--color-danger-border)] shadow-[var(--shadow-xs)]"
              >
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono font-bold text-[var(--color-danger-text)] uppercase rounded bg-[var(--color-danger-bg)] px-1.5 py-0.5 border border-[var(--color-danger-border)]">
                    {warn.warning_type.replace("_", " ")}
                  </span>
                  <span className="text-[11px] font-mono text-[var(--color-text-primary)] font-bold">
                    {warn.metric_value}
                  </span>
                </div>
                <p className="text-xs font-semibold text-[var(--color-text-primary)] truncate">{warn.project_name}</p>
                <p className="text-[11px] text-[var(--color-text-secondary)] leading-snug">{warn.description}</p>
                <Link
                  to={`/projects/${warn.project_id}`}
                  className="inline-flex items-center gap-1 text-[11px] font-mono text-[var(--color-text-accent)] hover:text-[var(--color-text-accent-hover)] font-semibold pt-1"
                >
                  <span>Investigate {warn.project_id}</span>
                  <ArrowRight className="h-3 w-3" />
                </Link>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Priority Highest-Risk Projects Table */}
      <div className="rounded-2xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-5 shadow-[var(--shadow-sm)] space-y-4">
        <div className="flex items-center justify-between border-b border-[var(--color-border-subtle)] pb-3">
          <div className="flex items-center gap-2">
            <ShieldAlert className="h-4 w-4 text-[var(--color-danger-icon)]" />
            <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-[var(--color-text-primary)]">
              Highest Risk Infrastructure Projects (Priority Escalation)
            </h3>
          </div>
          <Link
            to="/projects"
            className="text-xs font-mono text-[var(--color-text-accent)] hover:text-[var(--color-text-accent-hover)] font-semibold flex items-center gap-1"
          >
            <span>View All Projects</span>
            <ArrowRight className="h-3 w-3" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-[var(--color-text-primary)]">
            <thead className="border-b border-[var(--color-border-default)] bg-[var(--color-bg-surface-muted)] text-[11px] font-mono uppercase text-[var(--color-text-tertiary)]">
              <tr>
                <th className="py-2.5 px-3">Project ID</th>
                <th className="py-2.5 px-3">Project Title</th>
                <th className="py-2.5 px-3">Sector</th>
                <th className="py-2.5 px-3">Progress</th>
                <th className="py-2.5 px-3">Delay</th>
                <th className="py-2.5 px-3">Risk Assessment</th>
                <th className="py-2.5 px-3 text-right">360° Review</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--color-border-subtle)]">
              {data.highest_risk_projects.map((p) => (
                <tr key={p.project_id} className="hover:bg-[var(--color-bg-surface-soft)] transition">
                  <td className="py-3 px-3 font-mono font-bold text-[var(--color-text-accent)]">{p.project_id}</td>
                  <td className="py-3 px-3">
                    <div className="font-semibold text-[var(--color-text-primary)]">{p.name}</div>
                    <div className="text-[11px] text-[var(--color-text-tertiary)]">{p.location}</div>
                  </td>
                  <td className="py-3 px-3 font-mono text-[var(--color-text-secondary)]">{p.sector}</td>
                  <td className="py-3 px-3 font-mono">
                    <span className="font-bold text-[var(--color-text-primary)]">{p.progress}%</span>
                    <span className="text-[var(--color-text-tertiary)] ml-1">(Plan: {p.planned_progress}%)</span>
                  </td>
                  <td className="py-3 px-3 font-mono">
                    {p.delay_days > 0 ? (
                      <span className="text-[var(--color-warning-text)] font-semibold">{p.delay_days} days</span>
                    ) : (
                      <span className="text-[var(--color-success-text)] font-semibold">On Time</span>
                    )}
                  </td>
                  <td className="py-3 px-3">
                    <RiskBadge level={p.risk.overall_level} score={p.risk.overall_score} size="sm" />
                  </td>
                  <td className="py-3 px-3 text-right">
                    <Link
                      to={`/projects/${p.project_id}`}
                      className="inline-flex items-center gap-1 rounded-lg border border-[var(--color-border-strong)] bg-[var(--color-bg-surface)] px-2.5 py-1 text-[11px] font-medium text-[var(--color-text-primary)] shadow-[var(--shadow-xs)] transition hover:border-[var(--color-brand-primary)] hover:bg-[var(--color-brand-tint)] hover:text-[var(--color-text-accent)]"
                    >
                      <span>Analyze</span>
                      <ArrowRight className="h-3 w-3" />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
