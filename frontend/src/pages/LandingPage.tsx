import React from "react";
import { Link } from "react-router-dom";
import {
  Activity,
  Shield,
  Bot,
  Database,
  ArrowRight,
  TrendingUp,
  Cpu,
  Layers,
  FileCheck,
  Lock,
} from "lucide-react";

export const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-[var(--color-bg-primary)] text-[var(--color-text-primary)] flex flex-col">
      {/* Top Bar Navigation */}
      <header className="sticky top-0 z-50 border-b border-[var(--color-border-default)] bg-[var(--color-bg-surface)]/95 backdrop-blur-md shadow-[var(--shadow-xs)]">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 lg:px-8">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-[var(--color-border-accent)] bg-[var(--color-brand-tint)] shadow-[var(--shadow-xs)]">
              <Activity className="h-5 w-5 text-[var(--color-text-accent)]" />
            </div>
            <div>
              <span className="text-lg font-bold tracking-tight text-[var(--color-text-primary)]">INFRAPLUS</span>
              <span className="ml-2 rounded bg-[var(--color-brand-tint)] px-1.5 py-0.5 text-[10px] font-mono font-semibold text-[var(--color-text-accent)] border border-[var(--color-border-accent)]">
                GOV INTEL
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Link
              to="/login"
              className="rounded-lg px-3.5 py-2 text-xs font-medium text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition"
            >
              Sign In
            </Link>
            <Link
              to="/signup"
              className="inline-flex items-center gap-1.5 rounded-lg bg-[var(--color-brand-primary)] px-4 py-2 text-xs font-semibold text-[var(--color-brand-contrast)] shadow-[var(--shadow-xs)] transition hover:bg-[var(--color-brand-primary-hover)]"
            >
              <span>Access Command Center</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden pt-16 pb-20 lg:pt-24 lg:pb-32">
        <div className="mx-auto max-w-7xl px-4 lg:px-8 text-center relative z-10">
          <div className="inline-flex items-center gap-2 rounded-full border border-[var(--color-border-accent)] bg-[var(--color-brand-tint)] px-3.5 py-1 text-xs font-mono font-medium text-[var(--color-text-accent)] mb-6 shadow-[var(--shadow-xs)]">
            <Shield className="h-3.5 w-3.5 text-[var(--color-brand-primary)]" />
            <span>Government Infrastructure Oversight Standard</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-[var(--color-text-primary)] max-w-4xl mx-auto leading-tight">
            Infrastructure Monitoring &{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#C9A96E] to-[#9A783E]">
              Deterministic Risk Intelligence
            </span>
          </h1>

          <p className="mt-6 text-base sm:text-lg text-[var(--color-text-secondary)] max-w-2xl mx-auto leading-relaxed">
            Real-time project tracking, mathematical risk assessment, and grounded Gemini AI intelligence for national public infrastructure assets.
          </p>

          <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
            <Link
              to="/signup"
              className="inline-flex items-center gap-2 rounded-xl bg-[var(--color-brand-primary)] px-6 py-3 text-sm font-semibold text-[var(--color-brand-contrast)] shadow-[var(--shadow-md)] transition hover:bg-[var(--color-brand-primary-hover)]"
            >
              <span>Initialize Command Portal</span>
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              to="/login"
              className="inline-flex items-center gap-2 rounded-xl border border-[var(--color-border-strong)] bg-[var(--color-bg-surface)] px-6 py-3 text-sm font-semibold text-[var(--color-text-primary)] hover:bg-[var(--color-bg-surface-muted)] hover:border-[var(--color-border-accent)] transition shadow-[var(--shadow-sm)]"
            >
              <span>Officer Sign In</span>
            </Link>
          </div>
        </div>

        {/* Ambient Subtle Background Grid */}
        <div className="absolute inset-0 bg-[radial-gradient(#D8CBB8_1px,transparent_1px)] [background-size:24px_24px] opacity-40 pointer-events-none" />
      </section>

      {/* Authoritative Pipeline Section */}
      <section className="border-t border-[var(--color-border-default)] bg-[var(--color-bg-surface-soft)] py-16">
        <div className="mx-auto max-w-7xl px-4 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <p className="text-xs font-mono uppercase tracking-widest text-[var(--color-text-accent)] font-semibold">
              Execution Architecture
            </p>
            <h2 className="mt-2 text-2xl sm:text-3xl font-bold text-[var(--color-text-primary)] tracking-tight">
              Grounded, Deterministic Intelligence Pipeline
            </h2>
            <p className="mt-3 text-sm text-[var(--color-text-secondary)]">
              Mathematical scoring originates exclusively from the Python Risk Engine. The LLM explains and formulates recommendations without inventing numbers.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="rounded-xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-6 space-y-3 shadow-[var(--shadow-sm)]">
              <div className="rounded-lg border border-[var(--color-success-border)] bg-[var(--color-success-bg)] p-2.5 w-fit text-[var(--color-success-icon)]">
                <Database className="h-5 w-5" />
              </div>
              <p className="text-xs font-mono text-[var(--color-success-text)] font-bold uppercase">1. Ground Truth</p>
              <h3 className="text-sm font-bold text-[var(--color-text-primary)]">Firebase Realtime DB</h3>
              <p className="text-xs text-[var(--color-text-secondary)]">
                Authoritative physical progress, certified schedule milestones, and financial drawdowns.
              </p>
            </div>

            <div className="rounded-xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-6 space-y-3 shadow-[var(--shadow-sm)]">
              <div className="rounded-lg border border-[var(--color-warning-border)] bg-[var(--color-warning-bg)] p-2.5 w-fit text-[var(--color-warning-icon)]">
                <Cpu className="h-5 w-5" />
              </div>
              <p className="text-xs font-mono text-[var(--color-warning-text)] font-bold uppercase">2. Math Scoring</p>
              <h3 className="text-sm font-bold text-[var(--color-text-primary)]">Python Risk Engine</h3>
              <p className="text-xs text-[var(--color-text-secondary)]">
                Deterministic calculation: 35% progress gap, 40% schedule delay, 25% budget utilization.
              </p>
            </div>

            <div className="rounded-xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-6 space-y-3 shadow-[var(--shadow-sm)]">
              <div className="rounded-lg border border-[var(--color-border-accent)] bg-[var(--color-brand-tint)] p-2.5 w-fit text-[var(--color-text-accent)]">
                <Bot className="h-5 w-5" />
              </div>
              <p className="text-xs font-mono text-[var(--color-text-accent)] font-bold uppercase">3. Grounded AI</p>
              <h3 className="text-sm font-bold text-[var(--color-text-primary)]">Google Gemini API</h3>
              <p className="text-xs text-[var(--color-text-secondary)]">
                Officer-facing executive summaries and actionable mitigation steps grounded in project facts.
              </p>
            </div>

            <div className="rounded-xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-6 space-y-3 shadow-[var(--shadow-sm)]">
              <div className="rounded-lg border border-[var(--color-info-border)] bg-[var(--color-info-bg)] p-2.5 w-fit text-[var(--color-info-icon)]">
                <Layers className="h-5 w-5" />
              </div>
              <p className="text-xs font-mono text-[var(--color-info-text)] font-bold uppercase">4. Oversight 360°</p>
              <h3 className="text-sm font-bold text-[var(--color-text-primary)]">Command Dashboard</h3>
              <p className="text-xs text-[var(--color-text-secondary)]">
                Unified visibility across financial health, physical progress, timelines, and document clearances.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Core Capabilities */}
      <section className="py-20">
        <div className="mx-auto max-w-7xl px-4 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-2xl sm:text-3xl font-bold text-[var(--color-text-primary)] tracking-tight">
              Enterprise Project 360° Command Suite
            </h2>
            <p className="mt-3 text-sm text-[var(--color-text-secondary)]">
              Complete oversight across all infrastructure sectors: Roads, Health, Water, Education, Housing, and Energy.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="rounded-2xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-6 space-y-3 shadow-[var(--shadow-sm)]">
              <TrendingUp className="h-6 w-6 text-[var(--color-brand-primary)]" />
              <h3 className="text-base font-semibold text-[var(--color-text-primary)]">Progress & Delay Analytics</h3>
              <p className="text-xs text-[var(--color-text-secondary)] leading-relaxed">
                Real-time tracking of certified physical execution vs scheduled baseline, highlighting critical path delays before they compound.
              </p>
            </div>

            <div className="rounded-2xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-6 space-y-3 shadow-[var(--shadow-sm)]">
              <FileCheck className="h-6 w-6 text-[var(--color-success-icon)]" />
              <h3 className="text-base font-semibold text-[var(--color-text-primary)]">Cloud Document Clearances</h3>
              <p className="text-xs text-[var(--color-text-secondary)] leading-relaxed">
                Centralized storage for environmental clearances, audit reports, structural blueprints, and contractor invoices with verified metadata in Firebase.
              </p>
            </div>

            <div className="rounded-2xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-6 space-y-3 shadow-[var(--shadow-sm)]">
              <Lock className="h-6 w-6 text-[var(--color-warning-icon)]" />
              <h3 className="text-base font-semibold text-[var(--color-text-primary)]">Government-Grade Security</h3>
              <p className="text-xs text-[var(--color-text-secondary)] leading-relaxed">
                Server-side Firebase token validation on FastAPI endpoints, verified email workflows, and zero exposure of private keys.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto border-t border-[var(--color-border-default)] bg-[var(--color-bg-surface)] py-8 text-center text-xs text-[var(--color-text-secondary)]">
        <div className="mx-auto max-w-7xl px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p>© {new Date().getFullYear()} INFRAPLUS. National Infrastructure Project Monitoring Platform.</p>
          <div className="flex items-center gap-4 font-mono text-[11px] text-[var(--color-text-tertiary)]">
            <span>Firebase Realtime Database</span>
            <span>•</span>
            <span>FastAPI Python Engine</span>
            <span>•</span>
            <span>Gemini AI Intelligence</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
