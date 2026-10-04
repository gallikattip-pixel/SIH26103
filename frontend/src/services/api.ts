import type {
  ChatRequest,
  ChatResponse,
  DashboardSummary,
  DocumentRecord,
  FinancialMetrics,
  MilestoneRecord,
  ProgressMetrics,
  ProjectDetail360,
  ProjectListItem,
  ProjectRecord,
  RiskBreakdown,
  TimelineMetrics,
} from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

let authToken: string | null = null;

export const setAuthToken = (token: string | null) => {
  authToken = token;
};

const getHeaders = (isMultipart = false): HeadersInit => {
  const headers: Record<string, string> = {};
  if (!isMultipart) {
    headers["Content-Type"] = "application/json";
  }
  if (authToken) {
    headers["Authorization"] = `Bearer ${authToken}`;
  }
  return headers;
};

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const requestId = response.headers.get("X-Request-ID");
    let errorDetail = `Request failed with status ${response.status}`;
    try {
      const errJson = await response.json();
      if (errJson.detail) {
        errorDetail = errJson.detail;
      }
    } catch {
      // ignore non-json error
    }
    const error: any = new Error(errorDetail);
    if (requestId) {
      error.requestId = requestId;
    }
    throw error;
  }
  return response.json();
}


export const fetchHealth = async () => {
  const res = await fetch(`${API_BASE_URL}/health`);
  return handleResponse<any>(res);
};

export const fetchDashboard = async (): Promise<DashboardSummary> => {
  const res = await fetch(`${API_BASE_URL}/api/dashboard`, {
    headers: getHeaders(),
  });
  return handleResponse<DashboardSummary>(res);
};

export interface ProjectQueryParams {
  search?: string;
  sector?: string;
  risk_level?: string;
  delayed_only?: boolean;
  sort_by?: string;
  order?: "asc" | "desc";
}

export const fetchProjects = async (params: ProjectQueryParams = {}): Promise<ProjectListItem[]> => {
  const query = new URLSearchParams();
  if (params.search) query.append("search", params.search);
  if (params.sector) query.append("sector", params.sector);
  if (params.risk_level) query.append("risk_level", params.risk_level);
  if (params.delayed_only) query.append("delayed_only", "true");
  if (params.sort_by) query.append("sort_by", params.sort_by);
  if (params.order) query.append("order", params.order);

  const url = `${API_BASE_URL}/projects${query.toString() ? `?${query.toString()}` : ""}`;
  const res = await fetch(url, { headers: getHeaders() });
  return handleResponse<ProjectListItem[]>(res);
};

export const createProject = async (project: ProjectRecord): Promise<ProjectListItem> => {
  const res = await fetch(`${API_BASE_URL}/projects`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(project),
  });
  return handleResponse<ProjectListItem>(res);
};

export const fetchProjectDetail = async (projectId: string): Promise<ProjectDetail360> => {
  const res = await fetch(`${API_BASE_URL}/projects/${encodeURIComponent(projectId)}`, {
    headers: getHeaders(),
  });
  return handleResponse<ProjectDetail360>(res);
};

export const fetchProjectRisk = async (projectId: string): Promise<RiskBreakdown> => {
  const res = await fetch(`${API_BASE_URL}/projects/${encodeURIComponent(projectId)}/risk`, {
    headers: getHeaders(),
  });
  return handleResponse<RiskBreakdown>(res);
};

export const fetchProjectFinancial = async (projectId: string): Promise<FinancialMetrics> => {
  const res = await fetch(`${API_BASE_URL}/projects/${encodeURIComponent(projectId)}/financial`, {
    headers: getHeaders(),
  });
  return handleResponse<FinancialMetrics>(res);
};

export const fetchProjectProgress = async (projectId: string): Promise<ProgressMetrics> => {
  const res = await fetch(`${API_BASE_URL}/projects/${encodeURIComponent(projectId)}/progress`, {
    headers: getHeaders(),
  });
  return handleResponse<ProgressMetrics>(res);
};

export const fetchProjectTimeline = async (projectId: string): Promise<TimelineMetrics> => {
  const res = await fetch(`${API_BASE_URL}/projects/${encodeURIComponent(projectId)}/timeline`, {
    headers: getHeaders(),
  });
  return handleResponse<TimelineMetrics>(res);
};

export const fetchProjectMilestones = async (projectId: string): Promise<MilestoneRecord[]> => {
  const res = await fetch(`${API_BASE_URL}/projects/${encodeURIComponent(projectId)}/milestones`, {
    headers: getHeaders(),
  });
  return handleResponse<MilestoneRecord[]>(res);
};

export const fetchProjectAgencies = async (projectId: string) => {
  const res = await fetch(`${API_BASE_URL}/projects/${encodeURIComponent(projectId)}/agencies`, {
    headers: getHeaders(),
  });
  return handleResponse<any>(res);
};

export const fetchProjectDocuments = async (projectId: string): Promise<DocumentRecord[]> => {
  const res = await fetch(`${API_BASE_URL}/projects/${encodeURIComponent(projectId)}/documents`, {
    headers: getHeaders(),
  });
  return handleResponse<DocumentRecord[]>(res);
};

export const uploadProjectDocument = async (
  projectId: string,
  file: File,
  title?: string
): Promise<DocumentRecord> => {
  const formData = new FormData();
  formData.append("file", file);
  if (title) formData.append("title", title);

  const res = await fetch(`${API_BASE_URL}/projects/${encodeURIComponent(projectId)}/documents/upload`, {
    method: "POST",
    headers: getHeaders(true),
    body: formData,
  });
  return handleResponse<DocumentRecord>(res);
};

export const deleteProjectDocument = async (projectId: string, documentId: string) => {
  const res = await fetch(
    `${API_BASE_URL}/projects/${encodeURIComponent(projectId)}/documents/${encodeURIComponent(documentId)}`,
    {
      method: "DELETE",
      headers: getHeaders(),
    }
  );
  return handleResponse<{ status: string; document_id: string }>(res);
};

export const sendAiChat = async (payload: ChatRequest): Promise<ChatResponse> => {
  const res = await fetch(`${API_BASE_URL}/api/ai/chat`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(payload),
  });
  return handleResponse<ChatResponse>(res);
};
