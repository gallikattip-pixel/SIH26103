import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

export const GuestRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { currentUser, loading, isEmailVerified, isConfigured } = useAuth();

  if (loading) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-[var(--color-bg-primary)]">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-[var(--color-brand-primary)] border-t-transparent" />
      </div>
    );
  }

  if (isConfigured && currentUser && isEmailVerified) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
};
