import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

export const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { currentUser, loading, isEmailVerified, isConfigured } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-[var(--color-bg-primary)]">
        <div className="flex flex-col items-center gap-3">
          <div className="h-10 w-10 animate-spin rounded-full border-2 border-[var(--color-brand-primary)] border-t-transparent" />
          <p className="text-xs font-mono tracking-widest text-[var(--color-text-secondary)] uppercase">
            Verifying Session...
          </p>
        </div>
      </div>
    );
  }

  // If Firebase is configured, enforce auth and email verification
  if (isConfigured) {
    if (!currentUser) {
      return <Navigate to="/login" state={{ from: location }} replace />;
    }

    if (!isEmailVerified) {
      return <Navigate to="/verify-email" replace />;
    }
  }

  return <>{children}</>;
};
