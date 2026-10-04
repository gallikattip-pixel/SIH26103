import React from "react";
import { Link } from "react-router-dom";
import { AlertOctagon, ArrowLeft } from "lucide-react";

export const NotFoundPage: React.FC = () => {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center text-center px-4">
      <div className="rounded-2xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-10 max-w-md w-full shadow-warm-lg">
        <AlertOctagon className="mx-auto h-12 w-12 text-[var(--color-brand-primary)] mb-4" />
        <h2 className="text-2xl font-bold text-[var(--color-text-primary)] font-mono">404 — Not Found</h2>
        <p className="mt-2 text-xs text-[var(--color-text-secondary)]">
          The requested portal resource or endpoint does not exist.
        </p>
        <Link
          to="/dashboard"
          className="mt-6 inline-flex items-center gap-2 rounded-xl bg-[var(--color-brand-primary)] px-4 py-2 text-xs font-semibold text-[var(--color-brand-contrast)] hover:bg-[var(--color-brand-hover)] shadow-warm-xs transition"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Return to Dashboard</span>
        </Link>
      </div>
    </div>
  );
};
