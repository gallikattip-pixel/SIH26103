import React, { useEffect } from "react";
import { X } from "lucide-react";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  maxWidth?: "sm" | "md" | "lg" | "xl";
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  maxWidth = "md",
}) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const maxW = {
    sm: "max-w-sm",
    md: "max-w-md",
    lg: "max-w-lg",
    xl: "max-w-2xl",
  }[maxWidth];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div
        className="fixed inset-0 bg-[var(--overlay)] backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />
      <div
        className={`relative z-10 w-full ${maxW} overflow-hidden rounded-2xl border border-[var(--modal-border)] bg-[var(--modal-bg)] shadow-[var(--modal-shadow)] transition-all`}
        role="dialog"
        aria-modal="true"
      >
        <div className="flex items-center justify-between border-b border-[var(--color-border-default)] px-6 py-4">
          <h3 className="text-base font-semibold text-[var(--color-text-primary)]">{title}</h3>
          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-[var(--color-text-secondary)] transition hover:bg-[var(--color-bg-secondary)] hover:text-[var(--color-text-primary)]"
            aria-label="Close modal"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
        <div className="p-6 text-[var(--color-text-secondary)]">{children}</div>
      </div>
    </div>
  );
};
