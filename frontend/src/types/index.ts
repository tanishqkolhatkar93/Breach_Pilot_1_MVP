export type TargetType = 'local_vulnerable' | 'local_secure' | 'remote_http';

export type Severity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';

export type PublishingStatus = 
  | 'SUBMITTED' 
  | 'TESTING' 
  | 'BLOCKED' 
  | 'PENDING_HUMAN_APPROVAL' 
  | 'APPROVED' 
  | 'PUBLISHED';

export interface Finding {
  id: string;
  test_id: string;
  category: string;
  severity: Severity;
  title: string;
  description: string;
  evidence: string;
  confidence: number;
  remediation?: string;
}

export interface MetricSummary {
  total_cases: number;
  attack_success_rate: number;
  unsafe_request_refusal_rate: number;
  safe_task_pass_rate: number;
  total_attacks: number;
  successful_attacks: number;
  blocked_attacks: number;
  legitimate_tasks: number;
  passed_legitimate_tasks: number;
}

export interface AuditSessionSummary {
  session_id: string;
  agent_id: string;
  agent_name: string;
  risk_score: number;
  recommendation: 'BLOCK' | 'REVIEW' | 'APPROVE';
  decision_rationale: string[];
  metrics: MetricSummary;
  findings: Finding[];
  final_status: PublishingStatus;
  execution_logs: Array<{
    timestamp: string;
    phase: string;
    action: string;
    details: string;
  }>;
}

