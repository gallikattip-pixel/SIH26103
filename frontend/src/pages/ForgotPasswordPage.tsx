import React, { useState } from "react";
import { Link } from "react-router-dom";
import { Activity, Mail, ArrowLeft, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export const ForgotPasswordPage: React.FC = () => {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { resetPassword } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await resetPassword(email);
      setSubmitted(true);
    } catch (err: any) {
      setError(err.message || "Failed to send reset link.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[var(--color-bg-primary)] px-4 py-12">
      <div className="w-full max-w-md space-y-6 rounded-2xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-8 shadow-[var(--shadow-lg)]">
        <div className="text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl border border-[var(--color-border-accent)] bg-[var(--color-brand-tint)] shadow-[var(--shadow-xs)]">
            <Activity className="h-6 w-6 text-[var(--color-text-accent)]" />
          </div>
          <h2 className="mt-4 text-2xl font-bold tracking-tight text-[var(--color-text-primary)]">
            Reset Password
          </h2>
          <p className="mt-1 text-xs text-[var(--color-text-tertiary)] font-mono uppercase tracking-wider">
            Enter your official email to receive a recovery link
          </p>
        </div>

        {submitted ? (
          <div className="space-y-4 text-center">
            <div className="flex items-center gap-2 rounded-lg border border-[var(--color-success-border)] bg-[var(--color-success-bg)] p-4 text-xs text-[var(--color-success-text)] text-left">
              <CheckCircle2 className="h-5 w-5 text-[var(--color-success-icon)] shrink-0" />
              <span>
                Password reset instructions dispatched. Check your inbox to set a new password.
              </span>
            </div>
            <Link
              to="/login"
              className="inline-flex items-center gap-2 text-xs font-semibold text-[var(--color-text-accent)] hover:text-[var(--color-text-accent-hover)]"
            >
              <ArrowLeft className="h-4 w-4" />
              <span>Return to Sign In</span>
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="flex items-start gap-2 rounded-lg border border-[var(--color-danger-border)] bg-[var(--color-danger-bg)] p-3.5 text-xs text-[var(--color-danger-text)]">
                <AlertCircle className="h-4 w-4 shrink-0 text-[var(--color-danger-icon)] mt-0.5" />
                <span>{error}</span>
              </div>
            )}

            <div>
              <label className="block text-xs font-mono uppercase tracking-wider text-[var(--color-text-secondary)] mb-1.5">
                Official Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--input-placeholder)]" />
                <input
                  type="email"
                  required
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="officer@infraplus.gov.in"
                  className="w-full rounded-lg border border-[var(--input-border)] bg-[var(--input-bg)] py-2.5 pl-10 pr-4 text-xs text-[var(--input-text)] placeholder-[var(--input-placeholder)] focus:border-[var(--color-brand-primary)] focus:outline-none shadow-[var(--shadow-xs)]"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-[var(--color-brand-primary)] py-2.5 text-xs font-semibold uppercase tracking-wider text-[var(--color-brand-contrast)] shadow-[var(--shadow-xs)] transition hover:bg-[var(--color-brand-primary-hover)] disabled:opacity-50"
            >
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <span>Send Recovery Link</span>}
            </button>

            <div className="text-center pt-2">
              <Link
                to="/login"
                className="inline-flex items-center gap-1.5 text-xs text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition"
              >
                <ArrowLeft className="h-3.5 w-3.5" />
                <span>Back to Sign In</span>
              </Link>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};
