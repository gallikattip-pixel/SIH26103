import React from "react";
import type { LucideIcon } from "lucide-react";

interface KpiCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  badge?: {
    text: string;
    variant: "high" | "medium" | "low" | "neutral" | "cyan";
  };
  highlightColor?: "cyan" | "emerald" | "amber" | "rose" | "blue";
}

export const KpiCard: React.FC<KpiCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  badge,
  highlightColor = "cyan",
}) => {
  const iconColors = {
    cyan: "text-[var(--color-text-accent)] bg-[var(--color-bg-accent)] border-[var(--color-border-accent)]",
    emerald: "text-[var(--color-success-text)] bg-[var(--color-success-bg)] border-[var(--color-success-border)]",
    amber: "text-[var(--color-warning-text)] bg-[var(--color-warning-bg)] border-[var(--color-warning-border)]",
    rose: "text-[var(--color-danger-text)] bg-[var(--color-danger-bg)] border-[var(--color-danger-border)]",
    blue: "text-[var(--color-info-text)] bg-[var(--color-info-bg)] border-[var(--color-info-border)]",
  }[highlightColor];

  const badgeStyles = {
    high: "bg-[var(--color-danger-bg)] text-[var(--color-danger-text)] border-[var(--color-danger-border)]",
    medium: "bg-[var(--color-warning-bg)] text-[var(--color-warning-text)] border-[var(--color-warning-border)]",
    low: "bg-[var(--color-success-bg)] text-[var(--color-success-text)] border-[var(--color-success-border)]",
    cyan: "bg-[var(--color-bg-accent)] text-[var(--color-text-accent)] border-[var(--color-border-accent)]",
    neutral: "bg-[var(--color-bg-secondary)] text-[var(--color-text-secondary)] border-[var(--color-border-default)]",
  }[badge?.variant || "neutral"];

  return (
    <div className="relative overflow-hidden rounded-xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-5 shadow-[var(--shadow-sm)] transition-all hover:border-[var(--color-border-accent)] hover:shadow-[var(--shadow-md)]">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-[var(--color-text-tertiary)] font-mono">
            {title}
          </p>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl lg:text-3xl font-bold tracking-tight text-[var(--color-text-primary)] font-mono">
              {value}
            </span>
            {badge && (
              <span className={`text-[11px] font-mono px-2 py-0.5 rounded-full border ${badgeStyles}`}>
                {badge.text}
              </span>
            )}
          </div>
          {subtitle && (
            <p className="mt-1 text-xs text-[var(--color-text-secondary)]">{subtitle}</p>
          )}
        </div>
        <div className={`rounded-lg border p-2.5 ${iconColors}`}>
          <Icon className="h-5 w-5" />
        </div>
      </div>
      <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-[var(--color-brand-light)] to-transparent" />
    </div>
  );
};
