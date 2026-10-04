import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { MailCheck, RefreshCw, Send, LogOut, CheckCircle2, AlertCircle } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export const VerifyEmailPage: React.FC = () => {
  const { currentUser, resendVerification, refreshUser, logout } = useAuth();
  const [resending, setResending] = useState(false);
  const [checking, setChecking] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleCheckStatus = async () => {
    setChecking(true);
    setMessage(null);
    setError(null);
    try {
      const isVerified = await refreshUser();
      if (isVerified) {
        navigate("/dashboard");
      } else {
        setError("Email is not verified yet. Please check your inbox and click the verification link.");
      }
    } catch (err: any) {
      setError(err.message || "Failed to refresh verification status.");
    } finally {
      setChecking(false);
    }
  };

  const handleResend = async () => {
    setResending(true);
    setMessage(null);
    setError(null);
    try {
      await resendVerification();
      setMessage("Verification email has been resent to your address.");
    } catch (err: any) {
      setError(err.message || "Failed to resend verification email.");
    } finally {
      setResending(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[var(--color-bg-primary)] px-4 py-12">
      <div className="w-full max-w-md space-y-6 rounded-2xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-8 text-center shadow-[var(--shadow-lg)]">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl border border-[var(--color-border-accent)] bg-[var(--color-brand-tint)] shadow-[var(--shadow-xs)]">
          <MailCheck className="h-7 w-7 text-[var(--color-text-accent)]" />
        </div>

        <div>
          <h2 className="text-2xl font-bold tracking-tight text-[var(--color-text-primary)]">
            Verify Official Email
          </h2>
          <p className="mt-2 text-xs text-[var(--color-text-secondary)]">
            A secure verification link was dispatched to:
          </p>
          <p className="mt-1 font-mono text-xs font-semibold text-[var(--color-text-accent)] truncate">
            {currentUser?.email || "your registered email"}
          </p>
        </div>

        <div className="rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface-soft)] p-4 text-xs text-[var(--color-text-secondary)] text-left space-y-2">
          <p className="font-semibold text-[var(--color-text-primary)]">
            Government Security Mandate:
          </p>
          <p>
            Access to infrastructure project analytics and real-time risk scores is restricted to verified departmental accounts. Please click the link in your email to activate portal access.
          </p>
        </div>

        {message && (
          <div className="flex items-center gap-2 rounded-lg border border-[var(--color-success-border)] bg-[var(--color-success-bg)] p-3 text-xs text-[var(--color-success-text)]">
            <CheckCircle2 className="h-4 w-4 shrink-0 text-[var(--color-success-icon)]" />
            <span>{message}</span>
          </div>
        )}

        {error && (
          <div className="flex items-center gap-2 rounded-lg border border-[var(--color-danger-border)] bg-[var(--color-danger-bg)] p-3 text-xs text-[var(--color-danger-text)]">
            <AlertCircle className="h-4 w-4 shrink-0 text-[var(--color-danger-icon)]" />
            <span>{error}</span>
          </div>
        )}

        <div className="space-y-2.5 pt-2">
          <button
            onClick={handleCheckStatus}
            disabled={checking}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-[var(--color-brand-primary)] py-2.5 text-xs font-semibold uppercase tracking-wider text-[var(--color-brand-contrast)] shadow-[var(--shadow-xs)] transition hover:bg-[var(--color-brand-primary-hover)] disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${checking ? "animate-spin" : ""}`} />
            <span>I Have Verified My Email</span>
          </button>

          <button
            onClick={handleResend}
            disabled={resending}
            className="flex w-full items-center justify-center gap-2 rounded-xl border border-[var(--color-border-strong)] bg-[var(--color-bg-surface)] py-2.5 text-xs font-semibold uppercase tracking-wider text-[var(--color-text-primary)] shadow-[var(--shadow-xs)] transition hover:bg-[var(--color-bg-surface-muted)] disabled:opacity-50"
          >
            <Send className="h-3.5 w-3.5" />
            <span>Resend Verification Link</span>
          </button>

          <button
            onClick={handleLogout}
            className="flex w-full items-center justify-center gap-1.5 pt-2 text-xs text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition"
          >
            <LogOut className="h-3.5 w-3.5" />
            <span>Sign Out & Return to Login</span>
          </button>
        </div>
      </div>
    </div>
  );
};
