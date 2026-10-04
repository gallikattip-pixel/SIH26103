import React from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";

interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = "Connection Error",
  message,
  onRetry,
}) => {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-[var(--color-danger-border)] bg-[var(--color-danger-bg)] p-8 text-center shadow-[var(--shadow-xs)]">
      <div className="rounded-full border border-[var(--color-danger-border)] bg-[var(--color-bg-surface)] p-3 text-[var(--color-danger-icon)]">
        <AlertTriangle className="h-7 w-7 animate-pulse text-[var(--color-danger-icon)]" />
      </div>
      <h3 className="mt-3 text-base font-semibold text-[var(--color-danger-text)]">{title}</h3>
      <p className="mt-1 max-w-lg text-sm text-[var(--color-danger-text)] font-mono text-xs opacity-90">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-4 inline-flex items-center gap-2 rounded-lg bg-[var(--button-danger-bg)] px-3.5 py-2 text-xs font-semibold text-[var(--button-danger-text)] transition hover:bg-[var(--button-danger-hover)] shadow-[var(--shadow-xs)]"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          Retry Request
        </button>
      )}
    </div>
  );
};
