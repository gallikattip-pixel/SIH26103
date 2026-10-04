import React from "react";

interface RiskBadgeProps {
  level: "HIGH" | "MEDIUM" | "LOW" | string;
  score?: number;
  size?: "sm" | "md" | "lg";
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({ level, score, size = "md" }) => {
  const normLevel = (level || "UNKNOWN").toUpperCase();

  let bg = "var(--color-bg-secondary)";
  let border = "var(--color-border-default)";
  let text = "var(--color-text-secondary)";
  let dot = "var(--color-text-muted)";
  let isPulse = false;

  if (normLevel === "HIGH") {
    bg = "var(--color-risk-high-bg)";
    border = "var(--color-risk-high-border)";
    text = "var(--color-risk-high-text)";
    dot = "var(--color-risk-high-accent)";
    isPulse = true;
  } else if (normLevel === "MEDIUM") {
    bg = "var(--color-risk-medium-bg)";
    border = "var(--color-risk-medium-border)";
    text = "var(--color-risk-medium-text)";
    dot = "var(--color-risk-medium-accent)";
  } else if (normLevel === "LOW") {
    bg = "var(--color-risk-low-bg)";
    border = "var(--color-risk-low-border)";
    text = "var(--color-risk-low-text)";
    dot = "var(--color-risk-low-accent)";
  }

  const sizeClasses = {
    sm: "text-[11px] px-2 py-0.5 gap-1.5",
    md: "text-xs px-2.5 py-1 gap-2 font-medium",
    lg: "text-sm px-3.5 py-1.5 gap-2.5 font-semibold",
  }[size];

  return (
    <span
      style={{ backgroundColor: bg, borderColor: border, color: text }}
      className={`inline-flex items-center rounded-full border tracking-wide font-mono uppercase ${sizeClasses}`}
    >
      <span
        style={{ backgroundColor: dot }}
        className={`w-1.5 h-1.5 rounded-full ${isPulse ? "animate-pulse" : ""}`}
      />
      <span className="font-semibold">{normLevel}</span>
      {score !== undefined && (
        <span className="font-bold opacity-90 ml-0.5">({score})</span>
      )}
    </span>
  );
};
