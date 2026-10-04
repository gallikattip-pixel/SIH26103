import React from "react";
import { FolderSearch } from "lucide-react";
import type { LucideIcon } from "lucide-react";

interface EmptyStateProps {
  title: string;
  description: string;
  icon?: LucideIcon;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  icon: Icon = FolderSearch,
  action,
}) => {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-[var(--color-border-strong)] bg-[var(--color-bg-surface)] p-10 text-center shadow-[var(--shadow-xs)]">
      <div className="rounded-full border border-[var(--color-border-accent)] bg-[var(--color-bg-accent)] p-4 text-[var(--color-text-accent)]">
        <Icon className="h-8 w-8 text-[var(--color-brand-primary)]" />
      </div>
      <h3 className="mt-4 text-base font-semibold text-[var(--color-text-primary)]">{title}</h3>
      <p className="mt-1 max-w-md text-sm text-[var(--color-text-secondary)]">{description}</p>
      {action && (
        <button
          onClick={action.onClick}
          className="mt-5 inline-flex items-center rounded-lg bg-[var(--button-primary-bg)] px-4 py-2 text-sm font-semibold text-[var(--button-primary-text)] shadow-[var(--shadow-xs)] transition hover:bg-[var(--button-primary-hover)] active:bg-[var(--button-primary-active)] focus:outline-none focus:ring-2 focus:ring-[var(--color-focus-ring)]"
        >
          {action.label}
        </button>
      )}
    </div>
  );
};
