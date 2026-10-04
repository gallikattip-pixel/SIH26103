import React from "react";
import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  FolderKanban,
  ShieldCheck,
  Bot,
  Database,
  Cpu,
} from "lucide-react";

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const navItems = [
    { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
    { to: "/projects", label: "Projects Explorer", icon: FolderKanban },
    { to: "/risk-engine", label: "Risk Engine Audit", icon: ShieldCheck },
    { to: "/ai-assistant", label: "AI Intelligence Hub", icon: Bot },
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-30 bg-[var(--overlay)] backdrop-blur-sm lg:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={`fixed bottom-0 top-16 z-30 flex w-64 flex-col border-r border-[var(--color-border-default)] bg-[var(--color-bg-surface)] transition-transform duration-200 lg:static lg:translate-x-0 ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* Navigation Menu */}
        <nav className="flex-1 space-y-1.5 p-4">
          <p className="px-3 pb-2 text-[11px] font-mono font-semibold uppercase tracking-wider text-[var(--color-text-tertiary)]">
            Platform Navigation
          </p>

          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={onClose}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3.5 py-2.5 text-sm font-medium transition-all ${
                    isActive
                      ? "border border-[var(--color-border-accent)] bg-[var(--color-bg-accent)] text-[var(--color-brand-contrast)] font-semibold shadow-[var(--shadow-xs)]"
                      : "text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-surface-muted)] hover:text-[var(--color-text-primary)] border border-transparent"
                  }`
                }
              >
                <Icon className="h-4 w-4 shrink-0" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

        {/* System Integrity & Source of Truth Badge */}
        <div className="border-t border-[var(--color-border-default)] p-4">
          <div className="rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface-soft)] p-3.5 space-y-2">
            <div className="flex items-center gap-2">
              <Database className="h-3.5 w-3.5 text-[var(--color-success-icon)]" />
              <span className="text-[11px] font-mono text-[var(--color-text-primary)] font-semibold">
                Firebase RTDB
              </span>
            </div>
            <p className="text-[10px] text-[var(--color-text-tertiary)] leading-tight">
              Production source of truth. Zero synthetic data.
            </p>

            <div className="flex items-center gap-2 pt-1">
              <Cpu className="h-3.5 w-3.5 text-[var(--color-brand-primary)]" />
              <span className="text-[11px] font-mono text-[var(--color-text-primary)] font-semibold">
                Deterministic Risk
              </span>
            </div>
            <p className="text-[10px] text-[var(--color-text-tertiary)] leading-tight">
              Python Risk Engine mathematical scoring.
            </p>
          </div>
        </div>
      </aside>
    </>
  );
};
