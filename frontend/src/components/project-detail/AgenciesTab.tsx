import React from "react";
import { Building, Briefcase, UserCheck, ShieldCheck, Mail, Network } from "lucide-react";
import type { AgencyRecord } from "../../types";

export const AgenciesTab: React.FC<{ agencies: AgencyRecord }> = ({ agencies }) => {
  return (
    <div className="rounded-xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-6 space-y-6 shadow-[var(--shadow-sm)]">
      <div className="border-b border-[var(--color-border-subtle)] pb-3">
        <h4 className="text-sm font-semibold text-[var(--color-text-primary)] uppercase tracking-wider font-mono">
          Nodal Agencies & Contractor Directory
        </h4>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface-soft)] p-4 space-y-1 shadow-[var(--shadow-xs)]">
          <div className="flex items-center gap-2 text-xs font-mono text-[var(--color-text-accent)] uppercase">
            <Building className="h-4 w-4 text-[var(--color-brand-primary)]" />
            <span>Executing Department / Agency</span>
          </div>
          <p className="text-sm font-bold text-[var(--color-text-primary)] pt-1">{agencies.executing_agency}</p>
          <p className="text-xs text-[var(--color-text-tertiary)]">Primary Sanctioning Authority</p>
        </div>

        <div className="rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface-soft)] p-4 space-y-1 shadow-[var(--shadow-xs)]">
          <div className="flex items-center gap-2 text-xs font-mono text-[var(--color-text-accent)] uppercase">
            <Briefcase className="h-4 w-4 text-[var(--color-brand-primary)]" />
            <span>Primary Contractor</span>
          </div>
          <p className="text-sm font-bold text-[var(--color-text-primary)] pt-1">{agencies.contractor}</p>
          <p className="text-xs text-[var(--color-text-tertiary)]">Awarded Execution Partner</p>
        </div>

        <div className="rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface-soft)] p-4 space-y-1 shadow-[var(--shadow-xs)]">
          <div className="flex items-center gap-2 text-xs font-mono text-[var(--color-text-accent)] uppercase">
            <UserCheck className="h-4 w-4 text-[var(--color-brand-primary)]" />
            <span>Nodal Supervising Officer</span>
          </div>
          <p className="text-sm font-bold text-[var(--color-text-primary)] pt-1">{agencies.nodal_officer}</p>
          <p className="text-xs text-[var(--color-text-tertiary)]">On-Site Government Representative</p>
        </div>

        <div className="rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface-soft)] p-4 space-y-1 shadow-[var(--shadow-xs)]">
          <div className="flex items-center gap-2 text-xs font-mono text-[var(--color-text-accent)] uppercase">
            <ShieldCheck className="h-4 w-4 text-[var(--color-brand-primary)]" />
            <span>Supervising Quality Consultant</span>
          </div>
          <p className="text-sm font-bold text-[var(--color-text-primary)] pt-1">{agencies.supervising_consultant}</p>
          <p className="text-xs text-[var(--color-text-tertiary)]">Independent Quality Auditor</p>
        </div>
      </div>

      <div className="rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface-muted)] p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2">
          <Network className="h-4 w-4 text-[var(--color-success-icon)]" />
          <span className="text-[var(--color-text-secondary)] font-mono">
            Division: {agencies.monitoring_division}
          </span>
        </div>
        {agencies.contact_email && (
          <div className="flex items-center gap-2 text-[var(--color-text-accent)] font-mono">
            <Mail className="h-4 w-4 text-[var(--color-brand-primary)]" />
            <span>{agencies.contact_email}</span>
          </div>
        )}
      </div>
    </div>
  );
};
