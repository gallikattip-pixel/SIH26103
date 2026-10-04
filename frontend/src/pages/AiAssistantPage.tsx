import React, { useState } from "react";
import {
  Bot,
  Send,
  Loader2,
  CheckCircle2,
  User,
  Sparkles,
} from "lucide-react";
import type { ChatResponse } from "../types";
import { sendAiChat } from "../services/api";

interface MessageItem {
  id: string;
  sender: "user" | "ai";
  question?: string;
  response?: ChatResponse;
  timestamp: string;
}

export const AiAssistantPage: React.FC = () => {
  const [inputQuery, setInputQuery] = useState("");
  const [projectIdInput, setProjectIdInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<MessageItem[]>([
    {
      id: "initial-msg",
      sender: "ai",
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      response: {
        answer:
          "Welcome to the INFRAPLUS AI Intelligence Center. I am grounded in live project data and the authoritative Python Risk Engine. You can ask cross-project analytics questions or query a specific project by entering its ID.",
        risk_level: "GROUNDED",
        risk_score: 0,
        major_factors: [],
        recommended_actions: [
          "Ask: 'Which project has the highest risk?'",
          "Ask: 'Which projects are most delayed?'",
          "Ask: 'Which projects have budget problems?'",
          "Specify Project ID 'P42' and ask: 'Why is this project at high risk?'",
        ],
        projects: [],
      },
    },
  ]);

  const quickPrompts = [
    { label: "Highest-Risk Project", q: "Which project has the highest risk?", pId: "" },
    { label: "Most Delayed Projects", q: "Which projects have the highest delay?", pId: "" },
    { label: "Budget Overrun Flags", q: "Which projects have budget problems?", pId: "" },
    { label: "Projects Behind Schedule", q: "Which projects are lagging behind planned schedule?", pId: "" },
    { label: "Analyze Project P42", q: "Why is this project at high risk?", pId: "P42" },
    { label: "Project P01 Status", q: "Summarize the execution status of this project.", pId: "P01" },
  ];

  const handleSend = async (queryText: string, pIdText?: string) => {
    const q = queryText.trim();
    if (!q) return;

    const activeProjectId = (pIdText !== undefined ? pIdText : projectIdInput).trim().toUpperCase();

    const userMsg: MessageItem = {
      id: `usr-${messages.length + 1}-${Math.random().toString(36).slice(2, 7)}`,
      sender: "user",
      question: activeProjectId ? `[Project ${activeProjectId}] ${q}` : q,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputQuery("");
    setLoading(true);

    try {
      const resp = await sendAiChat({
        project_id: activeProjectId || undefined,
        question: q,
      });

      const aiMsg: MessageItem = {
        id: `ai-${messages.length + 2}-${Math.random().toString(36).slice(2, 7)}`,
        sender: "ai",
        response: resp,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };

      setMessages((prev) => [...prev, aiMsg]);
    } catch (err: any) {
      const errorMsg: MessageItem = {
        id: `err-${messages.length + 2}-${Math.random().toString(36).slice(2, 7)}`,
        sender: "ai",
        response: {
          answer: `Analysis Error: ${err.message || "Failed to generate response."}`,
          risk_level: "ERROR",
          risk_score: 0,
          major_factors: [],
          recommended_actions: ["Please ensure backend server is operational and project ID is valid."],
          projects: [],
        },
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8.5rem)] space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[var(--color-border-default)] pb-3 shrink-0">
        <div>
          <div className="flex items-center gap-2 text-[var(--color-text-accent)] mb-1">
            <Bot className="h-4 w-4" />
            <span className="text-xs font-mono font-semibold uppercase tracking-wider">
              Gemini + Python Grounded Intelligence
            </span>
          </div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[var(--color-text-primary)]">
            AI Project Intelligence Hub
          </h1>
        </div>
      </div>

      {/* Suggested Query Pills */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 shrink-0">
        <span className="text-xs font-mono text-[var(--color-text-tertiary)] uppercase flex items-center gap-1 shrink-0">
          <Sparkles className="h-3.5 w-3.5 text-[var(--color-brand-primary)]" />
          <span>PROMPTS:</span>
        </span>
        {quickPrompts.map((item, idx) => (
          <button
            key={idx}
            disabled={loading}
            onClick={() => {
              setProjectIdInput(item.pId);
              setInputQuery(item.q);
              handleSend(item.q, item.pId);
            }}
            className="rounded-full border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] px-3 py-1 text-xs text-[var(--color-text-primary)] hover:border-[var(--color-brand-primary)] hover:bg-[var(--color-bg-accent)] transition shrink-0 shadow-warm-xs"
          >
            {item.label}
          </button>
        ))}
      </div>

      {/* Chat Messages Feed */}
      <div className="flex-1 overflow-y-auto space-y-4 rounded-2xl border border-[var(--ai-border)] bg-[var(--ai-bg)] p-4 lg:p-6 shadow-warm-xs">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-3 ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
          >
            {msg.sender === "ai" && (
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-[var(--color-border-gold)] bg-[var(--color-brand-tint)] text-[var(--color-brand-dark)] shadow-warm-xs">
                <Bot className="h-4 w-4" />
              </div>
            )}

            <div
              className={`max-w-2xl rounded-2xl p-4 text-xs space-y-3 shadow-warm-xs ${
                msg.sender === "user"
                  ? "bg-[var(--ai-user-message-bg)] border border-[var(--ai-user-message-border)] text-[var(--color-text-primary)] rounded-tr-none font-medium"
                  : "border border-[var(--ai-assistant-message-border)] bg-[var(--ai-assistant-message-bg)] text-[var(--color-text-primary)] rounded-tl-none"
              }`}
            >
              {msg.sender === "user" ? (
                <p className="text-sm">{msg.question}</p>
              ) : (
                <>
                  <div className="flex items-center justify-between border-b border-[var(--color-border-subtle)] pb-2">
                    <span className="font-mono text-[11px] font-bold text-[var(--color-text-accent)] uppercase tracking-wider">
                      Authoritative Analysis
                    </span>
                    {msg.response?.risk_level && msg.response.risk_level !== "GROUNDED" && (
                      <span className="font-mono text-[10px] rounded bg-[var(--color-bg-surface-muted)] px-2 py-0.5 border border-[var(--color-border-default)] text-[var(--color-text-primary)] font-bold">
                        RISK: {msg.response.risk_score}/100 ({msg.response.risk_level})
                      </span>
                    )}
                  </div>

                  <p className="text-xs text-[var(--color-text-primary)] leading-relaxed whitespace-pre-line">
                    {msg.response?.answer}
                  </p>

                  {/* Multi-project summaries if available */}
                  {msg.response?.projects && msg.response.projects.length > 0 && (
                    <div className="pt-2 border-t border-[var(--color-border-subtle)] space-y-1.5">
                      <p className="text-[11px] font-mono text-[var(--color-text-secondary)] uppercase">
                        Identified Projects:
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {msg.response.projects.map((p) => (
                          <span
                            key={p.project_id}
                            className="rounded-md border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface-soft)] px-2.5 py-1 text-[11px] font-mono text-[var(--color-text-primary)]"
                          >
                            <span className="font-bold text-[var(--color-text-accent)]">{p.project_id}</span> • Score: {p.risk_score} ({p.risk_level})
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Recommended Actions */}
                  {msg.response?.recommended_actions && msg.response.recommended_actions.length > 0 && (
                    <div className="pt-2 border-t border-[var(--color-border-subtle)] space-y-1.5">
                      <p className="text-[11px] font-mono uppercase text-[var(--color-text-secondary)]">
                        Recommended Mitigation Actions:
                      </p>
                      <div className="space-y-1">
                        {msg.response.recommended_actions.map((act, i) => (
                          <div key={i} className="flex items-start gap-2 text-[var(--color-text-primary)]">
                            <CheckCircle2 className="h-3.5 w-3.5 text-[var(--color-success-icon)] shrink-0 mt-0.5" />
                            <span>{act}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              )}
              <div className="text-right text-[10px] font-mono text-[var(--color-text-tertiary)]">{msg.timestamp}</div>
            </div>

            {msg.sender === "user" && (
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-[var(--ai-user-message-border)] bg-[var(--ai-user-message-bg)] text-[var(--color-text-primary)] shadow-warm-xs">
                <User className="h-4 w-4" />
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Input Box */}
      <div className="rounded-2xl border border-[var(--ai-border)] bg-[var(--ai-surface)] p-3 shadow-warm-sm shrink-0">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend(inputQuery);
          }}
          className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2"
        >
          {/* Optional Project ID Input */}
          <div className="w-full sm:w-36 shrink-0">
            <input
              type="text"
              placeholder="Project ID (opt)"
              value={projectIdInput}
              onChange={(e) => setProjectIdInput(e.target.value)}
              className="w-full rounded-lg border border-[var(--ai-input-border)] bg-[var(--ai-input-bg)] px-3 py-2 text-xs font-mono uppercase text-[var(--color-text-primary)] placeholder-[var(--color-text-tertiary)] focus:border-[var(--ai-accent)] focus:outline-none"
            />
          </div>

          {/* Main Question Input */}
          <input
            type="text"
            required
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            placeholder="Ask a question grounded in real project data (e.g., 'Why is P42 at high risk?')..."
            className="flex-1 rounded-lg border border-[var(--ai-input-border)] bg-[var(--ai-input-bg)] px-3.5 py-2 text-xs text-[var(--color-text-primary)] placeholder-[var(--color-text-tertiary)] focus:border-[var(--ai-accent)] focus:outline-none"
          />

          <button
            type="submit"
            disabled={loading || !inputQuery.trim()}
            className="inline-flex items-center justify-center gap-1.5 rounded-lg bg-[var(--ai-accent)] px-5 py-2 text-xs font-semibold text-[var(--color-brand-contrast)] shadow-warm-xs transition hover:bg-[var(--ai-accent-hover)] disabled:opacity-50 shrink-0"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
            <span>Query AI</span>
          </button>
        </form>
      </div>
    </div>
  );
};
