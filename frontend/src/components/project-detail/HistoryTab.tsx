import React, { useEffect, useState } from "react";
import { History, TrendingUp, BarChart2, Flag, Calendar } from "lucide-react";
import { fetchProjectSnapshots, fetchProjectOutcome } from "../../services/api";
import { RiskBadge } from "../common/RiskBadge";
import { EmptyState } from "../common/EmptyState";
import { ErrorState } from "../common/ErrorState";
import type { ProjectSnapshot, ProjectOutcome } from "../../types";

interface HistoryTabProps {
  projectId: string;
  projectName: string;
}

export const HistoryTab: React.FC<HistoryTabProps> = ({ projectId, projectName }) => {
  const [snapshots, setSnapshots] = useState<ProjectSnapshot[]>([]);
  const [outcome, setOutcome] = useState<ProjectOutcome | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [snapshotsRes, outcomeRes] = await Promise.all([
        fetchProjectSnapshots(projectId),
        fetchProjectOutcome(projectId),
      ]);
      setSnapshots(snapshotsRes.snapshots);
      setOutcome(outcomeRes.outcome);
    } catch (err: any) {
      setError(err.message || "Failed to load history.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [projectId]);

  if (loading) {
    return (
      <div className="py-8 space-y-4">
        <div className="flex items-center gap-2 animate-pulse">
          <BarChart2 className="h-4 w-4 text-[var(--color-brand-primary)]" />
          <span className="text-xs font-mono text-[var(--color-text-secondary)]">Loading snapshot history...</span>
        </div>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-20 bg-[var(--color-bg-surface-muted)] rounded-xl animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <ErrorState
        title="Unable to Load History"
        message={error}
        onRetry={loadData}
      />
    );
  }

  if (snapshots.length === 0) {
    return (
      <EmptyState
        title="No Historical Snapshots Recorded"
        description={
          `No snapshots have been recorded for ${projectName} yet. ` +
          `Authorized officers can record snapshots from the Project 360° view.`
        }
        icon={History}
      />
    );
  }

  // Sort snapshots chronologically (newest first for display)
  const sortedSnapshots = [...snapshots].sort(
    (a, b) => new Date(b.recorded_at).getTime() - new Date(a.recorded_at).getTime()
  );

  // For trend chart, sort oldest first
  const trendSnapshots = [...snapshots].sort(
    (a, b) => new Date(a.recorded_at).getTime() - new Date(b.recorded_at).getTime()
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[var(--color-border-default)] pb-4">
        <div className="flex items-center gap-2">
          <History className="h-5 w-5 text-[var(--color-brand-primary)]" />
          <h2 className="text-lg font-semibold text-[var(--color-text-primary)]">
            Historical Snapshot Timeline
          </h2>
        </div>
        <span className="text-xs font-mono text-[var(--color-text-tertiary)]">
          {snapshots.length} snapshot{snapshots.length !== 1 ? "s" : ""} recorded
        </span>
      </div>

      {/* Project Outcome - show if exists */}
      {outcome && (
        <div className="rounded-2xl border border-[var(--color-border-accent)] bg-[var(--color-brand-tint)] p-4 shadow-[var(--shadow-sm)]">
          <div className="flex items-center gap-2 border-b border-[var(--color-border-subtle)] pb-3 mb-4">
            <Flag className="h-4 w-4 text-[var(--color-brand-primary)]" />
            <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-[var(--color-text-primary)]">
              Project Completion Outcome
            </h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
            <div className="rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)] p-3">
              <span className="text-[10px] font-mono text-[var(--color-text-tertiary)]">Status</span>
              <div className="flex items-center gap-2 mt-1">
                <span className="font-mono text-[var(--color-text-primary)]">{outcome.completion_status}</span>
                <span className="text-[var(--color-text-tertiary)] font-mono text-[10px]">Final</span>
              </div>
            </div>
            <div className="rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)] p-3">
              <span className="text-[10px] font-mono text-[var(--color-text-tertiary)]">Actual Completion</span>
              <div className="flex items-center justify-between mt-1">
                <span className="font-mono text-[var(--color-text-primary)]">{outcome.actual_completion_date}</span>
                <Calendar className="h-3.5 w-3.5 text-[var(--color-text-tertiary)]" />
              </div>
            </div>
            <div className="rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)] p-3">
              <span className="text-[10px] font-mono text-[var(--color-text-tertiary)]">Final Delay</span>
              <div className="flex items-center justify-between mt-1">
                <span className="font-mono text-[var(--color-text-primary)]">{outcome.final_delay_days} days</span>
                <span className="text-[var(--color-text-tertiary)] font-mono text-[10px]">Schedule</span>
              </div>
            </div>
            <div className="rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)] p-3">
              <span className="text-[10px] font-mono text-[var(--color-text-tertiary)]">Final Budget</span>
              <div className="flex items-center justify-between mt-1">
                <span className="font-mono text-[var(--color-text-primary)]">{outcome.final_budget_used}%</span>
                <span className="text-[var(--color-text-tertiary)] font-mono text-[10px]">Utilization</span>
              </div>
            </div>
          </div>

          {outcome.planned_completion_date && (
            <div className="rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)] p-3 mb-4">
              <span className="text-[10px] font-mono text-[var(--color-text-tertiary)]">Planned Completion</span>
              <div className="flex items-center justify-between mt-1">
                <span className="font-mono text-[var(--color-text-primary)]">{outcome.planned_completion_date}</span>
                <Calendar className="h-3.5 w-3.5 text-[var(--color-text-tertiary)]" />
              </div>
            </div>
          )}

          {outcome.final_cost_crore !== undefined && outcome.final_cost_crore !== null && (
            <div className="rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)] p-3 mb-4">
              <span className="text-[10px] font-mono text-[var(--color-text-tertiary)]">Final Cost</span>
              <div className="flex items-center justify-between mt-1">
                <span className="font-mono text-[var(--color-text-primary)]">₹{outcome.final_cost_crore} Cr</span>
                {outcome.final_budget_variance_percent !== undefined && outcome.final_budget_variance_percent !== null && (
                  <span className={`font-mono text-[10px] ${outcome.final_budget_variance_percent >= 0 ? "text-[var(--color-danger-icon)]" : "text-[var(--color-success-icon)]"}`}>
                    {outcome.final_budget_variance_percent >= 0 ? "+" : ""}{outcome.final_budget_variance_percent.toFixed(2)}% variance
                  </span>
                )}
              </div>
            </div>
          )}

          {outcome.notes && (
            <div className="rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)] p-3">
              <span className="text-[10px] font-mono text-[var(--color-text-tertiary)]">Notes</span>
              <p className="text-[11px] text-[var(--color-text-secondary)] mt-1 font-sans">{outcome.notes}</p>
            </div>
          )}

          <div className="flex items-center justify-between pt-3 border-t border-[var(--color-border-subtle)]">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono text-[var(--color-text-tertiary)]">Recorded</span>
              <span className="text-[11px] font-mono text-[var(--color-text-secondary)]">
                {new Date(outcome.recorded_at).toLocaleString(undefined, {
                  year: "numeric",
                  month: "short",
                  day: "numeric",
                  hour: "2-digit",
                  minute: "2-digit",
                  timeZoneName: "short",
                })}
              </span>
            </div>
            <span className="text-[10px] font-mono text-[var(--color-text-tertiary)]">
              By: {outcome.recorded_by_uid}
            </span>
          </div>
        </div>
      )}

      {/* Trend Chart - only show if we have 2+ snapshots */}
      {trendSnapshots.length >= 2 && (
        <div className="rounded-2xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-5 shadow-[var(--shadow-sm)]">
          <div className="flex items-center gap-2 border-b border-[var(--color-border-subtle)] pb-3 mb-4">
            <TrendingUp className="h-4 w-4 text-[var(--color-brand-primary)]" />
            <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-[var(--color-text-primary)]">
              Historical Trends
            </h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
            <MetricTrend
              label="Progress"
              values={trendSnapshots.map((s) => ({ period: s.snapshot_period, value: s.progress }))}
              unit="%"
              color="var(--color-brand-primary)"
            />
            <MetricTrend
              label="Planned Progress"
              values={trendSnapshots.map((s) => ({ period: s.snapshot_period, value: s.planned_progress }))}
              unit="%"
              color="var(--color-text-tertiary)"
            />
            <MetricTrend
              label="Delay"
              values={trendSnapshots.map((s) => ({ period: s.snapshot_period, value: s.delay_days }))}
              unit=" days"
              color="var(--color-warning-icon)"
            />
            <MetricTrend
              label="Budget Used"
              values={trendSnapshots.map((s) => ({ period: s.snapshot_period, value: s.budget_used }))}
              unit="%"
              color="var(--color-success-icon)"
            />
          </div>

          <p className="text-[10px] text-[var(--color-text-tertiary)] text-center font-mono">
            Data points represent actual recorded observations. Missing months are not interpolated.
          </p>
        </div>
      )}

      {/* Snapshot List */}
      <div className="rounded-2xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] shadow-[var(--shadow-sm)] overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-[var(--color-text-primary)]">
            <thead className="border-b border-[var(--color-table-header-border)] bg-[var(--color-table-header-bg)] text-[10px] font-mono uppercase text-[var(--color-text-secondary)]">
              <tr>
                <th className="py-2.5 px-3">Period</th>
                <th className="py-2.5 px-3">Recorded</th>
                <th className="py-2.5 px-3">Progress</th>
                <th className="py-2.5 px-3">Planned</th>
                <th className="py-2.5 px-3">Delay</th>
                <th className="py-2.5 px-3">Budget Used</th>
                <th className="py-2.5 px-3">Risk</th>
                <th className="py-2.5 px-3">Budget Total</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--color-table-row-border)] font-mono">
              {sortedSnapshots.map((snapshot) => (
                <tr key={snapshot.snapshot_period} className="hover:bg-[var(--color-table-row-hover)] transition">
                  <td className="py-3 px-3 font-bold text-[var(--color-text-accent)]">
                    {snapshot.snapshot_period}
                  </td>
                  <td className="py-3 px-3 font-sans text-[var(--color-text-secondary)]">
                    {new Date(snapshot.recorded_at).toLocaleString(undefined, {
                      year: "numeric",
                      month: "short",
                      day: "numeric",
                      hour: "2-digit",
                      minute: "2-digit",
                      timeZoneName: "short",
                    })}
                  </td>
                  <td className="py-3 px-3">
                    <span className="text-[var(--color-text-primary)]">{snapshot.progress}%</span>
                  </td>
                  <td className="py-3 px-3">
                    <span className="text-[var(--color-text-tertiary)]">{snapshot.planned_progress}%</span>
                  </td>
                  <td className="py-3 px-3">
                    <span className="text-[var(--color-text-primary)]">{snapshot.delay_days} days</span>
                  </td>
                  <td className="py-3 px-3">
                    <span className="text-[var(--color-text-primary)]">{snapshot.budget_used}%</span>
                  </td>
                  <td className="py-3 px-3">
                    {snapshot.risk_snapshot && (
                      <RiskBadge
                        level={snapshot.risk_snapshot.overall_level}
                        score={snapshot.risk_snapshot.overall_score}
                        size="sm"
                      />
                    )}
                  </td>
                  <td className="py-3 px-3 text-[var(--color-text-secondary)]">
                    ₹{snapshot.budget_total_crore} Cr
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Detailed Cards View for Mobile */}
        <div className="block sm:hidden p-4 space-y-3 border-t border-[var(--color-border-subtle)]">
          {sortedSnapshots.map((snapshot) => (
            <div
              key={snapshot.snapshot_period}
              className="rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface-soft)] p-4 space-y-2"
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-[var(--color-text-accent)] font-mono">
                  {snapshot.snapshot_period}
                </span>
                <span className="text-[11px] text-[var(--color-text-tertiary)] font-mono">
                  {new Date(snapshot.recorded_at).toLocaleDateString()}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-[11px]">
                <div>
                  <span className="text-[var(--color-text-tertiary)] font-mono">Progress</span>
                  <div className="flex justify-between mt-0.5">
                    <span className="font-mono">{snapshot.progress}%</span>
                    <span className="text-[var(--color-text-tertiary)]">Actual</span>
                  </div>
                </div>
                <div>
                  <span className="text-[var(--color-text-tertiary)] font-mono">Planned</span>
                  <div className="flex justify-between mt-0.5">
                    <span className="font-mono">{snapshot.planned_progress}%</span>
                  </div>
                </div>
                <div>
                  <span className="text-[var(--color-text-tertiary)] font-mono">Delay</span>
                  <div className="flex justify-between mt-0.5">
                    <span className="font-mono">{snapshot.delay_days} days</span>
                  </div>
                </div>
                <div>
                  <span className="text-[var(--color-text-tertiary)] font-mono">Budget</span>
                  <div className="flex justify-between mt-0.5">
                    <span className="font-mono">{snapshot.budget_used}%</span>
                  </div>
                </div>
                {snapshot.risk_snapshot && (
                  <div className="col-span-2">
                    <span className="text-[var(--color-text-tertiary)] font-mono">Risk</span>
                    <div className="flex items-center gap-2 mt-0.5">
                      <RiskBadge
                        level={snapshot.risk_snapshot.overall_level}
                        score={snapshot.risk_snapshot.overall_score}
                        size="sm"
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Simple metric trend component
interface MetricTrendProps {
  label: string;
  values: { period: string; value: number }[];
  unit: string;
  color: string;
}

const MetricTrend: React.FC<MetricTrendProps> = ({ label, values, unit, color }) => {
  if (values.length < 2) return null;

  const first = values[0].value;
  const last = values[values.length - 1].value;
  const change = last - first;
  const isPositive = change >= 0;

  return (
    <div className="rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface-soft)] p-3 space-y-1">
      <span className="text-[10px] font-mono text-[var(--color-text-tertiary)]">{label}</span>
      <div className="flex items-end justify-between h-20 space-x-1">
        {values.map((v) => (
          <div
            key={v.period}
            className="flex-1 flex flex-col items-center"
            style={{
              height: `${Math.max(4, (v.value / 100) * 100)}%`,
            }}
          >
            <div
              className="w-full rounded-t transition-all"
              style={{
                backgroundColor: color,
                height: `${Math.max(4, (v.value / Math.max(...values.map((x) => x.value), 1)) * 100)}%`,
                minHeight: "4px",
              }}
            />
            <span className="text-[9px] text-[var(--color-text-tertiary)] font-mono mt-1">
              {v.period.split("-")[1]}
            </span>
          </div>
        ))}
      </div>
      <div className="flex items-center justify-between text-[11px]">
        <span className="font-mono text-[var(--color-text-primary)]">
          {last.toFixed(1)}{unit}
        </span>
        <span
          className={`font-mono ${isPositive ? "text-[var(--color-success-icon)]" : "text-[var(--color-danger-icon)]"}`}
        >
          {isPositive ? "+" : ""}{change.toFixed(1)}{unit}
        </span>
      </div>
    </div>
  );
};