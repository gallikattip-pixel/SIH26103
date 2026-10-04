import React, { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { Activity, Lock, Mail, AlertCircle, Loader2 } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { login, isConfigured } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = (location.state as any)?.from?.pathname || "/dashboard";

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await login(email, password);
      navigate(from, { replace: true });
    } catch (err: any) {
      if (err.code === "auth/invalid-credential" || err.code === "auth/user-not-found" || err.code === "auth/wrong-password") {
        setError("Invalid email address or password.");
      } else if (err.code === "auth/too-many-requests") {
        setError("Too many failed attempts. Please wait a moment before trying again.");
      } else {
        setError(err.message || "Failed to sign in. Please verify your credentials.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[var(--color-bg-primary)] px-4 py-12">
      <div className="w-full max-w-md space-y-8 rounded-2xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-8 shadow-[var(--shadow-lg)]">
        {/* Header */}
        <div className="text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl border border-[var(--color-border-accent)] bg-[var(--color-brand-tint)] shadow-[var(--shadow-xs)]">
            <Activity className="h-6 w-6 text-[var(--color-text-accent)]" />
          </div>
          <h2 className="mt-4 text-2xl font-bold tracking-tight text-[var(--color-text-primary)]">
            Officer Authentication
          </h2>
          <p className="mt-1 text-xs text-[var(--color-text-tertiary)] font-mono uppercase tracking-wider">
            INFRAPLUS Infrastructure Oversight Portal
          </p>
        </div>

        {!isConfigured && (
          <div className="rounded-lg border border-[var(--color-warning-border)] bg-[var(--color-warning-bg)] p-3.5 text-xs text-[var(--color-warning-text)]">
            <p className="font-semibold">Notice: Firebase Credentials Pending</p>
            <p className="mt-0.5 text-[var(--color-warning-text)]/90 text-[11px]">
              Set your Firebase Web App credentials in frontend/.env to enable live authentication.
            </p>
          </div>
        )}

        {/* Error Banner */}
        {error && (
          <div className="flex items-start gap-2 rounded-lg border border-[var(--color-danger-border)] bg-[var(--color-danger-bg)] p-3.5 text-xs text-[var(--color-danger-text)]">
            <AlertCircle className="h-4 w-4 shrink-0 text-[var(--color-danger-icon)] mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-mono uppercase tracking-wider text-[var(--color-text-secondary)] mb-1.5">
              Official Email Address
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

          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs font-mono uppercase tracking-wider text-[var(--color-text-secondary)]">
                Password
              </label>
              <Link
                to="/forgot-password"
                className="text-[11px] font-semibold text-[var(--color-text-accent)] hover:text-[var(--color-text-accent-hover)]"
              >
                Forgot password?
              </Link>
            </div>
            <div className="relative">
              <Lock className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--input-placeholder)]" />
              <input
                type="password"
                required
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full rounded-lg border border-[var(--input-border)] bg-[var(--input-bg)] py-2.5 pl-10 pr-4 text-xs text-[var(--input-text)] placeholder-[var(--input-placeholder)] focus:border-[var(--color-brand-primary)] focus:outline-none shadow-[var(--shadow-xs)]"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="mt-6 flex w-full items-center justify-center gap-2 rounded-xl bg-[var(--color-brand-primary)] py-2.5 text-xs font-semibold uppercase tracking-wider text-[var(--color-brand-contrast)] shadow-[var(--shadow-xs)] transition hover:bg-[var(--color-brand-primary-hover)] disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Authenticating...</span>
              </>
            ) : (
              <span>Sign In</span>
            )}
          </button>
        </form>

        <div className="text-center text-xs text-[var(--color-text-secondary)] border-t border-[var(--color-border-subtle)] pt-4">
          <span>New supervising officer? </span>
          <Link to="/signup" className="font-semibold text-[var(--color-text-accent)] hover:text-[var(--color-text-accent-hover)]">
            Create an Account
          </Link>
        </div>
      </div>
    </div>
  );
};
