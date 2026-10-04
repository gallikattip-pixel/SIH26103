import React from "react";
import { Shield, Cpu, Activity } from "lucide-react";

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-[var(--color-border-default)] bg-[var(--color-bg-surface)] py-8 text-[var(--color-text-secondary)] text-xs">
      <div className="mx-auto max-w-7xl px-4 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <Activity className="h-4 w-4 text-[var(--color-brand-primary)]" />
          <span className="font-bold tracking-tight text-[var(--color-text-primary)]">INFRAPLUS</span>
          <span className="text-[var(--color-border-strong)]">|</span>
          <span className="text-[var(--color-text-tertiary)]">Infrastructure Project Monitoring, Risk & AI Platform</span>
        </div>

        <div className="flex items-center gap-6 font-mono text-[11px] text-[var(--color-text-tertiary)]">
          <div className="flex items-center gap-1.5">
            <Shield className="h-3.5 w-3.5 text-[var(--color-success-icon)]" />
            <span className="text-[var(--color-text-secondary)]">Government Enterprise Standard</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Cpu className="h-3.5 w-3.5 text-[var(--color-brand-primary)]" />
            <span className="text-[var(--color-text-secondary)]">Deterministic Risk Engine</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
