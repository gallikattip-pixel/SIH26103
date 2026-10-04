import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Activity, Lock, Mail, User, Building2, AlertCircle, Loader2 } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export const SignupPage: React.FC = () => {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [organization, setOrganization] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { signup, isConfigured } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters long.");
      return;
    }

    setLoading(true);

    try {
      const displayName = organization ? `${name} (${organization})` : name;
      await signup(email, password, displayName);
      navigate("/verify-email");
    } catch (err: any) {
      if (err.code === "auth/email-already-in-use") {
        setError("An account with this email address already exists.");
      } else {
        setError(err.message || "Failed to create account. Please check your details.");
      }
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
            Officer Registration
          </h2>
          <p className="mt-1 text-xs text-[var(--color-text-tertiary)] font-mono uppercase tracking-wider">
            Register for Infrastructure Monitoring Access
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

        {error && (
          <div className="flex items-start gap-2 rounded-lg border border-[var(--color-danger-border)] bg-[var(--color-danger-bg)] p-3.5 text-xs text-[var(--color-danger-text)]">
            <AlertCircle className="h-4 w-4 shrink-0 text-[var(--color-danger-icon)] mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-3.5">
          <div>
            <label className="block text-xs font-mono uppercase tracking-wider text-[var(--color-text-secondary)] mb-1">
              Full Officer Name
            </label>
            <div className="relative">
              <User className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--input-placeholder)]" />
              <input
                type="text"
                required
                autoComplete="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Dr. Rajesh Sharma"
                className="w-full rounded-lg border border-[var(--input-border)] bg-[var(--input-bg)] py-2.5 pl-10 pr-4 text-xs text-[var(--input-text)] placeholder-[var(--input-placeholder)] focus:border-[var(--color-brand-primary)] focus:outline-none shadow-[var(--shadow-xs)]"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-mono uppercase tracking-wider text-[var(--color-text-secondary)] mb-1">
              Organization / Department
            </label>
            <div className="relative">
              <Building2 className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--input-placeholder)]" />
              <input
                type="text"
                value={organization}
                onChange={(e) => setOrganization(e.target.value)}
                placeholder="State Highway Authority"
                className="w-full rounded-lg border border-[var(--input-border)] bg-[var(--input-bg)] py-2.5 pl-10 pr-4 text-xs text-[var(--input-text)] placeholder-[var(--input-placeholder)] focus:border-[var(--color-brand-primary)] focus:outline-none shadow-[var(--shadow-xs)]"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-mono uppercase tracking-wider text-[var(--color-text-secondary)] mb-1">
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

          <div>
            <label className="block text-xs font-mono uppercase tracking-wider text-[var(--color-text-secondary)] mb-1">
              Password (min. 6 characters)
            </label>
            <div className="relative">
              <Lock className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--input-placeholder)]" />
              <input
                type="password"
                required
                autoComplete="new-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full rounded-lg border border-[var(--input-border)] bg-[var(--input-bg)] py-2.5 pl-10 pr-4 text-xs text-[var(--input-text)] placeholder-[var(--input-placeholder)] focus:border-[var(--color-brand-primary)] focus:outline-none shadow-[var(--shadow-xs)]"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-mono uppercase tracking-wider text-[var(--color-text-secondary)] mb-1">
              Confirm Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--input-placeholder)]" />
              <input
                type="password"
                required
                autoComplete="new-password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full rounded-lg border border-[var(--input-border)] bg-[var(--input-bg)] py-2.5 pl-10 pr-4 text-xs text-[var(--input-text)] placeholder-[var(--input-placeholder)] focus:border-[var(--color-brand-primary)] focus:outline-none shadow-[var(--shadow-xs)]"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl bg-[var(--color-brand-primary)] py-2.5 text-xs font-semibold uppercase tracking-wider text-[var(--color-brand-contrast)] shadow-[var(--shadow-xs)] transition hover:bg-[var(--color-brand-primary-hover)] disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Registering Account...</span>
              </>
            ) : (
              <span>Create Account</span>
            )}
          </button>
        </form>

        <div className="text-center text-xs text-[var(--color-text-secondary)] border-t border-[var(--color-border-subtle)] pt-4">
          <span>Already registered? </span>
          <Link to="/login" className="font-semibold text-[var(--color-text-accent)] hover:text-[var(--color-text-accent-hover)]">
            Sign In Here
          </Link>
        </div>
      </div>
    </div>
  );
};
