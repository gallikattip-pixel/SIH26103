import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  ShieldAlert,
  LogOut,
  User as UserIcon,
  Menu,
  X,
  Bot,
  Activity,
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";

interface NavbarProps {
  onToggleSidebar?: () => void;
  isSidebarOpen?: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ onToggleSidebar, isSidebarOpen }) => {
  const { currentUser, logout } = useAuth();
  const [showDropdown, setShowDropdown] = useState(false);
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <header className="sticky top-0 z-40 border-b border-[var(--color-border-default)] bg-[var(--color-bg-surface)]/95 backdrop-blur-md shadow-[var(--shadow-xs)]">
      <div className="flex h-16 items-center justify-between px-4 lg:px-8">
        {/* Left: Brand and Mobile Toggle */}
        <div className="flex items-center gap-3">
          {onToggleSidebar && (
            <button
              onClick={onToggleSidebar}
              className="rounded-lg p-2 text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-surface-muted)] hover:text-[var(--color-text-primary)] lg:hidden transition"
              aria-label="Toggle navigation"
            >
              {isSidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          )}

          <Link to="/dashboard" className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-[var(--color-border-accent)] bg-[var(--color-brand-tint)] shadow-[var(--shadow-xs)]">
              <Activity className="h-5 w-5 text-[var(--color-text-accent)]" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-lg font-bold tracking-tight text-[var(--color-text-primary)]">INFRAPLUS</span>
                <span className="rounded bg-[var(--color-brand-tint)] px-1.5 py-0.5 text-[10px] font-mono font-semibold tracking-wider text-[var(--color-text-accent)] border border-[var(--color-border-accent)]">
                  GOV INTEL
                </span>
              </div>
              <p className="hidden text-[10px] font-mono tracking-wider text-[var(--color-text-tertiary)] uppercase sm:block">
                Project Risk & Intelligence
              </p>
            </div>
          </Link>
        </div>

        {/* Right: Quick actions and user profile */}
        <div className="flex items-center gap-3">
          <Link
            to="/ai-assistant"
            className="hidden sm:inline-flex items-center gap-1.5 rounded-lg border border-[var(--color-border-accent)] bg-[var(--color-brand-tint)] px-3 py-1.5 text-xs font-medium text-[var(--color-text-accent)] transition hover:bg-[var(--color-bg-accent-hover)]"
          >
            <Bot className="h-4 w-4 text-[var(--color-text-accent)]" />
            <span>AI Assistant</span>
          </Link>

          <Link
            to="/risk-engine"
            className="hidden md:inline-flex items-center gap-1.5 rounded-lg border border-[var(--color-border-default)] bg-[var(--color-bg-surface-soft)] px-3 py-1.5 text-xs font-medium text-[var(--color-text-secondary)] transition hover:bg-[var(--color-bg-surface-muted)] hover:text-[var(--color-text-primary)]"
          >
            <ShieldAlert className="h-4 w-4 text-[var(--color-warning-icon)]" />
            <span>Risk Engine</span>
          </Link>

          {/* User Account / Profile */}
          {currentUser ? (
            <div className="relative">
              <button
                onClick={() => setShowDropdown(!showDropdown)}
                className="flex items-center gap-2 rounded-full border border-[var(--color-border-strong)] bg-[var(--color-bg-surface)] py-1 pl-1 pr-3 text-xs text-[var(--color-text-primary)] shadow-[var(--shadow-xs)] transition hover:border-[var(--color-border-accent)]"
              >
                <div className="flex h-7 w-7 items-center justify-center rounded-full bg-[var(--color-brand-tint)] text-[var(--color-text-accent)] font-bold border border-[var(--color-border-accent)]">
                  {currentUser.displayName ? currentUser.displayName[0].toUpperCase() : <UserIcon className="h-4 w-4" />}
                </div>
                <span className="max-w-[120px] truncate hidden md:inline font-medium">
                  {currentUser.displayName || currentUser.email}
                </span>
              </button>

              {showDropdown && (
                <div className="absolute right-0 mt-2 w-56 rounded-xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-2 shadow-[var(--shadow-modal)] z-50">
                  <div className="border-b border-[var(--color-border-subtle)] px-3 py-2">
                    <p className="text-xs font-semibold text-[var(--color-text-primary)] truncate">
                      {currentUser.displayName || "Officer"}
                    </p>
                    <p className="text-[11px] text-[var(--color-text-tertiary)] truncate font-mono">
                      {currentUser.email}
                    </p>
                  </div>
                  <div className="pt-1">
                    <button
                      onClick={handleLogout}
                      className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-xs text-[var(--color-danger-text)] transition hover:bg-[var(--color-danger-bg)] font-medium"
                    >
                      <LogOut className="h-4 w-4 text-[var(--color-danger-icon)]" />
                      Sign Out
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link
                to="/login"
                className="rounded-lg px-3 py-1.5 text-xs font-medium text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
              >
                Sign In
              </Link>
              <Link
                to="/signup"
                className="rounded-lg bg-[var(--color-brand-primary)] px-3.5 py-1.5 text-xs font-semibold text-[var(--color-brand-contrast)] shadow-[var(--shadow-xs)] transition hover:bg-[var(--color-brand-primary-hover)]"
              >
                Register
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
