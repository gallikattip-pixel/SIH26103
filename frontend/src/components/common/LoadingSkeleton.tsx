import React from "react";

export const TableSkeleton: React.FC<{ rows?: number }> = ({ rows = 5 }) => {
  return (
    <div className="w-full animate-pulse space-y-3 rounded-xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-5 shadow-[var(--shadow-xs)]">
      <div className="h-6 w-1/4 rounded bg-[var(--color-bg-tertiary)]" />
      <div className="space-y-2 pt-3">
        {Array.from({ length: rows }).map((_, idx) => (
          <div key={idx} className="flex gap-4">
            <div className="h-9 w-1/6 rounded bg-[var(--color-bg-secondary)]" />
            <div className="h-9 w-2/6 rounded bg-[var(--color-bg-surface-muted)]" />
            <div className="h-9 w-1/6 rounded bg-[var(--color-bg-secondary)]" />
            <div className="h-9 w-1/6 rounded bg-[var(--color-bg-tertiary)]" />
            <div className="h-9 w-1/6 rounded bg-[var(--color-bg-surface-muted)]" />
          </div>
        ))}
      </div>
    </div>
  );
};

export const CardSkeleton: React.FC = () => {
  return (
    <div className="animate-pulse rounded-xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-5 space-y-3 shadow-[var(--shadow-xs)]">
      <div className="flex justify-between">
        <div className="h-4 w-1/3 rounded bg-[var(--color-bg-secondary)]" />
        <div className="h-8 w-8 rounded-lg bg-[var(--color-bg-tertiary)]" />
      </div>
      <div className="h-8 w-1/2 rounded bg-[var(--color-bg-tertiary)]" />
      <div className="h-3 w-3/4 rounded bg-[var(--color-bg-surface-muted)]" />
    </div>
  );
};

export const DetailSkeleton: React.FC = () => {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="h-10 w-1/3 rounded bg-[var(--color-bg-tertiary)]" />
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="h-28 rounded-xl bg-[var(--color-bg-surface)] border border-[var(--color-border-default)]" />
        <div className="h-28 rounded-xl bg-[var(--color-bg-surface)] border border-[var(--color-border-default)]" />
        <div className="h-28 rounded-xl bg-[var(--color-bg-surface)] border border-[var(--color-border-default)]" />
        <div className="h-28 rounded-xl bg-[var(--color-bg-surface)] border border-[var(--color-border-default)]" />
      </div>
      <div className="h-80 rounded-xl bg-[var(--color-bg-surface)] border border-[var(--color-border-default)]" />
    </div>
  );
};
