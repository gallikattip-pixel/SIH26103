export interface ProjectRecord {
  project_id: string;
  name: string;
  location: string;
  sector: string;
  progress: number;
  planned_progress: number;
  delay_days: number;
  budget_used: number;
  budget_total_crore: number;
  contractor: string;
}

export interface RiskBreakdown {
  progress_gap: number;
  progress_risk: number;
  delay_risk: number;
  budget_risk: number;
  overall_score: number;
  overall_level: "HIGH" | "MEDIUM" | "LOW" | string;
  major_factors: string[];
  metrics: {
    progress: number;
    planned_progress: number;
    delay_days: number;
    budget_used: number;
  };
}

export interface ProjectListItem extends ProjectRecord {
  risk: RiskBreakdown;
}

export interface FinancialMetrics {
  project_id: string;
  budget_total_crore: number;
  budget_used_percent: number;
  budget_expended_crore: number;
  budget_remaining_crore: number;
  spend_ahead_of_work: number;
  financial_health: "ON_BUDGET" | "MODERATE_RISK" | "CRITICAL_DEFICIT" | string;
  budget_risk: number;
}

export interface ProgressMetrics {
  project_id: string;
  actual_progress: number;
  planned_progress: number;
  progress_gap: number;
  status: "ON_SCHEDULE" | "AHEAD_OF_PLAN" | "MODERATELY_BEHIND" | "SIGNIFICANTLY_BEHIND" | string;
  progress_risk: number;
}

export interface TimelineMetrics {
  project_id: string;
  delay_days: number;
  delay_risk: number;
  schedule_status: "ON_TIME" | "MINOR_DELAY" | "MODERATE_DELAY" | "CRITICAL_DELAY" | string;
  recovery_urgency: "NONE" | "LOW" | "MEDIUM" | "HIGH" | string;
  estimated_impact: string;
}

export interface MilestoneRecord {
  id: string;
  title: string;
  target_date: string;
  status: "COMPLETED" | "IN_PROGRESS" | "DELAYED" | "PENDING" | string;
  completion_percent: number;
  critical: boolean;
}

export interface AgencyRecord {
  executing_agency: string;
  contractor: string;
  nodal_officer: string;
  supervising_consultant: string;
  monitoring_division: string;
  contact_email?: string;
}

export interface DocumentRecord {
  id: string;
  project_id: string;
  filename: string;
  title: string;
  file_type: string;
  file_size_kb: number;
  uploaded_at: string;
  download_url: string;
}

export interface ProjectDetail360 {
  project: ProjectRecord;
  risk: RiskBreakdown;
  financial: FinancialMetrics;
  progress: ProgressMetrics;
  timeline: TimelineMetrics;
  milestones: MilestoneRecord[];
  agencies: AgencyRecord;
  documents: DocumentRecord[];
}

export interface RiskDistribution {
  high_count: number;
  medium_count: number;
  low_count: number;
  total: number;
}

export interface SectorStat {
  sector: string;
  count: number;
  avg_progress: number;
  high_risk_count: number;
}

export interface EarlyWarning {
  project_id: string;
  project_name: string;
  warning_type: string;
  severity: "CRITICAL" | "HIGH" | "WARNING" | string;
  description: string;
  metric_value: string;
}

export interface DashboardSummary {
  total_projects: number;
  high_risk_projects: number;
  medium_risk_projects: number;
  low_risk_projects: number;
  delayed_projects_count: number;
  average_progress: number;
  total_sanctioned_budget_crore: number;
  total_expended_budget_crore: number;
  risk_distribution: RiskDistribution;
  sectors: SectorStat[];
  early_warnings: EarlyWarning[];
  highest_risk_projects: ProjectListItem[];
}

export interface ProjectRiskSummary {
  project_id: string;
  project_name: string;
  risk_level: string;
  risk_score: number;
}

export interface ChatRequest {
  project_id?: string;
  question: string;
}

export interface ChatResponse {
  answer: string;
  risk_level: string;
  risk_score: number;
  major_factors: string[];
  recommended_actions: string[];
  projects: ProjectRiskSummary[];
}

export interface AuthUser {
  uid: string;
  email: string | null;
  displayName: string | null;
  emailVerified: boolean;
}

export interface RiskSnapshot {
  overall_score: number;
  overall_level: string;
  progress_risk: number;
  delay_risk: number;
  budget_risk: number;
  progress_gap: number;
  major_factors: string[];
}

export interface ProjectSnapshot {
  project_id: string;
  snapshot_period: string;
  recorded_at: string;
  progress: number;
  planned_progress: number;
  delay_days: number;
  budget_used: number;
  budget_total_crore: number;
  contractor: string;
  sector: string;
  location: string;
  risk_snapshot?: RiskSnapshot;
}

export interface SnapshotCreateRequest {
  snapshot_period?: string;
}

export interface SnapshotListResponse {
  project_id: string;
  snapshots: ProjectSnapshot[];
  total_count: number;
}

export interface ProjectOutcome {
  project_id: string;
  completion_status: "COMPLETED" | "TERMINATED" | "SUSPENDED" | "ON_HOLD";
  actual_completion_date: string;
  planned_completion_date?: string;
  final_progress: number;
  final_delay_days: number;
  final_budget_used: number;
  final_budget_variance_percent?: number;
  final_cost_crore?: number;
  recorded_at: string;
  recorded_by_uid: string;
  notes?: string;
}

export interface ProjectOutcomeCreateRequest {
  completion_status: "COMPLETED" | "TERMINATED" | "SUSPENDED" | "ON_HOLD";
  actual_completion_date: string;
  planned_completion_date?: string;
  final_progress: number;
  final_budget_used: number;
  final_budget_variance_percent?: number;
  final_cost_crore?: number;
  notes?: string;
}

export interface ProjectOutcomeResponse {
  project_id: string;
  outcome: ProjectOutcome | null;
}
