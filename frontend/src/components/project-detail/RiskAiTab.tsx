import React, { useState } from "react";
import {
  ShieldAlert,
  Bot,
  Send,
  Loader2,
  CheckCircle2,
} from "lucide-react";
import type { ChatResponse, ProjectDetail360 } from "../../types";
import { sendAiChat } from "../../services/api";

export const RiskAiTab: React.FC<{ detail: ProjectDetail360 }> = ({ detail }) => {
  const { project, risk } = detail;
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [chatResponse, setChatResponse] = useState<ChatResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const suggestedQuestions = [
    "Why is this project at high risk?",
    "What are the major causes of delay?",
    "How is this project progressing?",
    "What are the main financial risks?",
    "What should be reviewed first?",
  ];

  const handleAsk = async (qText: string) => {
    const q = qText.trim();
    if (!q) return;

    setLoading(true);
    setError(null);
    try {
      const resp = await sendAiChat({
        project_id: project.project_id,
        question: q,
      });
      setChatResponse(resp);
    } catch (err: any) {
      setError(err.message || "Failed to generate AI analysis.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Risk Engine Mathematical Card */}
      <div className="rounded-xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-6 space-y-4 shadow-[var(--shadow-sm)]">
        <div className="flex items-center justify-between border-b border-[var(--color-border-subtle)] pb-3">
          <div className="flex items-center gap-2">
            <ShieldAlert className="h-5 w-5 text-[var(--color-warning-icon)]" />
            <h4 className="text-sm font-semibold text-[var(--color-text-primary)] uppercase tracking-wider font-mono">
              Deterministic Risk Engine — Authoritative Scores
            </h4>
          </div>
          <span className="text-xs font-mono text-[var(--color-text-tertiary)]">
            Source: Python Risk Engine
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 pt-2">
          <div className="rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface-soft)] p-4">
            <p className="text-xs font-mono text-[var(--color-text-secondary)]">Progress Risk (35% wt)</p>
            <p className="mt-1 text-2xl font-bold font-mono text-[var(--color-text-primary)]">{risk.progress_risk}/100</p>
            <p className="text-[11px] text-[var(--color-text-tertiary)] mt-1 font-mono">Gap: {risk.progress_gap}%</p>
          </div>

          <div className="rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface-soft)] p-4">
            <p className="text-xs font-mono text-[var(--color-text-secondary)]">Delay Risk (40% wt)</p>
            <p className="mt-1 text-2xl font-bold font-mono text-[var(--color-text-primary)]">{risk.delay_risk}/100</p>
            <p className="text-[11px] text-[var(--color-text-tertiary)] mt-1 font-mono">{project.delay_days} days delay</p>
          </div>

          <div className="rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface-soft)] p-4">
            <p className="text-xs font-mono text-[var(--color-text-secondary)]">Budget Risk (25% wt)</p>
            <p className="mt-1 text-2xl font-bold font-mono text-[var(--color-text-primary)]">{risk.budget_risk}/100</p>
            <p className="text-[11px] text-[var(--color-text-tertiary)] mt-1 font-mono">{project.budget_used}% utilized</p>
          </div>

          <div className="rounded-lg border border-[var(--color-border-accent)] bg-[var(--color-brand-tint)] p-4">
            <p className="text-xs font-mono text-[var(--color-text-accent)] font-semibold">Composite Risk Score</p>
            <p className="mt-1 text-3xl font-bold font-mono text-[var(--color-text-primary)]">
              {risk.overall_score}/100
            </p>
            <p className="text-[11px] font-mono text-[var(--color-text-accent)] font-bold mt-1">
              LEVEL: {risk.overall_level}
            </p>
          </div>
        </div>

        <div className="rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface-muted)] p-3.5 text-xs text-[var(--color-text-secondary)] font-mono">
          Formula: overall_score = round(0.35 × {risk.progress_risk} + 0.40 × {risk.delay_risk} + 0.25 × {risk.budget_risk}) = {risk.overall_score}
        </div>
      </div>

      {/* Embedded Project AI Assistant */}
      <div className="rounded-xl border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] p-6 space-y-4 shadow-[var(--shadow-sm)]">
        <div className="flex items-center gap-2 border-b border-[var(--color-border-subtle)] pb-3">
          <Bot className="h-5 w-5 text-[var(--color-brand-primary)]" />
          <h4 className="text-sm font-semibold text-[var(--color-text-primary)] uppercase tracking-wider font-mono">
            Grounded Project Intelligence Assistant
          </h4>
        </div>

        <p className="text-xs text-[var(--color-text-secondary)]">
          Ask questions grounded strictly in this project's verified data. The AI explains the deterministic risk calculations and formulates executive recommendations.
        </p>

        {/* Suggested Prompts */}
        <div className="flex flex-wrap gap-2 pt-1">
          {suggestedQuestions.map((q, idx) => (
            <button
              key={idx}
              onClick={() => {
                setQuestion(q);
                handleAsk(q);
              }}
              disabled={loading}
              className="rounded-full border border-[var(--color-border-strong)] bg-[var(--color-bg-surface)] px-3 py-1 text-xs text-[var(--color-text-secondary)] hover:border-[var(--color-brand-primary)] hover:bg-[var(--color-brand-tint)] hover:text-[var(--color-text-accent)] transition shadow-[var(--shadow-xs)]"
            >
              {q}
            </button>
          ))}
        </div>

        {/* Input Form */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleAsk(question);
          }}
          className="flex gap-2 pt-2"
        >
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question about this project's progress, delay, or risk..."
            className="flex-1 rounded-lg border border-[var(--ai-input-border)] bg-[var(--ai-input-bg)] px-3.5 py-2 text-xs text-[var(--color-text-primary)] placeholder-[var(--input-placeholder)] focus:border-[var(--color-brand-primary)] focus:outline-none"
          />
          <button
            type="submit"
            disabled={loading || !question.trim()}
            className="inline-flex items-center gap-1.5 rounded-lg bg-[var(--color-brand-primary)] px-4 py-2 text-xs font-semibold text-[var(--color-brand-contrast)] shadow-[var(--shadow-xs)] transition hover:bg-[var(--color-brand-primary-hover)] disabled:opacity-50"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
            <span>Analyze</span>
          </button>
        </form>

        {/* AI Response Display */}
        {error && (
          <div className="rounded-lg border border-[var(--color-danger-border)] bg-[var(--color-danger-bg)] p-4 text-xs text-[var(--color-danger-text)]">
            {error}
          </div>
        )}

        {chatResponse && (
          <div className="rounded-xl border border-[var(--color-border-accent)] bg-[var(--color-bg-surface-soft)] p-5 space-y-4 shadow-[var(--shadow-xs)]">
            <div className="flex items-center justify-between border-b border-[var(--color-border-subtle)] pb-2">
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-[var(--color-brand-primary)] animate-pulse" />
                <span className="text-xs font-mono font-bold text-[var(--color-text-accent)]">
                  Grounded Intelligence Response
                </span>
              </div>
              <span className="text-[11px] font-mono text-[var(--color-text-tertiary)]">
                Risk Verified: {chatResponse.risk_score}/100 ({chatResponse.risk_level})
              </span>
            </div>

            <p className="text-xs text-[var(--color-text-primary)] leading-relaxed whitespace-pre-line">
              {chatResponse.answer}
            </p>

            {chatResponse.recommended_actions && chatResponse.recommended_actions.length > 0 && (
              <div className="pt-2 border-t border-[var(--color-border-subtle)]">
                <p className="text-xs font-mono uppercase tracking-wider text-[var(--color-text-secondary)] mb-2">
                  Recommended Executive Actions:
                </p>
                <div className="space-y-1.5">
                  {chatResponse.recommended_actions.map((act, i) => (
                    <div key={i} className="flex items-start gap-2 text-xs text-[var(--color-text-secondary)]">
                      <CheckCircle2 className="h-3.5 w-3.5 text-[var(--color-success-icon)] shrink-0 mt-0.5" />
                      <span>{act}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
