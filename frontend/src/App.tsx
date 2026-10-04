import React, { Suspense, lazy } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { AppLayout } from "./components/layout/AppLayout";
import { ProtectedRoute } from "./components/layout/ProtectedRoute";
import { GuestRoute } from "./components/layout/GuestRoute";

// Primary landing entry point kept statically imported for immediate render
import { LandingPage } from "./pages/LandingPage";

// Route-level code splitting: pages loaded on-demand
const LoginPage = lazy(() => import("./pages/LoginPage").then(m => ({ default: m.LoginPage })));
const SignupPage = lazy(() => import("./pages/SignupPage").then(m => ({ default: m.SignupPage })));
const VerifyEmailPage = lazy(() => import("./pages/VerifyEmailPage").then(m => ({ default: m.VerifyEmailPage })));
const ForgotPasswordPage = lazy(() => import("./pages/ForgotPasswordPage").then(m => ({ default: m.ForgotPasswordPage })));
const DashboardPage = lazy(() => import("./pages/DashboardPage").then(m => ({ default: m.DashboardPage })));
const ProjectsPage = lazy(() => import("./pages/ProjectsPage").then(m => ({ default: m.ProjectsPage })));
const ProjectDetailPage = lazy(() => import("./pages/ProjectDetailPage").then(m => ({ default: m.ProjectDetailPage })));
const RiskEnginePage = lazy(() => import("./pages/RiskEnginePage").then(m => ({ default: m.RiskEnginePage })));
const AiAssistantPage = lazy(() => import("./pages/AiAssistantPage").then(m => ({ default: m.AiAssistantPage })));
const NotFoundPage = lazy(() => import("./pages/NotFoundPage").then(m => ({ default: m.NotFoundPage })));

const ModuleLoadingFallback: React.FC = () => (
  <div className="flex h-screen w-full items-center justify-center bg-[var(--color-bg-primary)] font-mono text-xs text-[var(--color-text-secondary)]">
    <div className="flex items-center space-x-2">
      <div className="h-4 w-4 animate-spin rounded-full border-2 border-emerald-500 border-t-transparent" />
      <span>Loading INFRAPLUS module...</span>
    </div>
  </div>
);

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Suspense fallback={<ModuleLoadingFallback />}>
          <Routes>
            {/* Public Landing */}
            <Route path="/" element={<LandingPage />} />

            {/* Authentication Guest Routes */}
            <Route
              path="/login"
              element={
                <GuestRoute>
                  <LoginPage />
                </GuestRoute>
              }
            />
            <Route
              path="/signup"
              element={
                <GuestRoute>
                  <SignupPage />
                </GuestRoute>
              }
            />
            <Route
              path="/forgot-password"
              element={
                <GuestRoute>
                  <ForgotPasswordPage />
                </GuestRoute>
              }
            />
            <Route path="/verify-email" element={<VerifyEmailPage />} />

            {/* Protected Application Suite */}
            <Route
              element={
                <ProtectedRoute>
                  <AppLayout />
                </ProtectedRoute>
              }
            >
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/projects" element={<ProjectsPage />} />
              <Route path="/projects/:id" element={<ProjectDetailPage />} />
              <Route path="/risk-engine" element={<RiskEnginePage />} />
              <Route path="/ai-assistant" element={<AiAssistantPage />} />
            </Route>

            {/* Fallback 404 */}
            <Route path="/404" element={<NotFoundPage />} />
            <Route path="*" element={<Navigate to="/404" replace />} />
          </Routes>
        </Suspense>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
