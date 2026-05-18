export type JobResponse = {
  chain_job_id: string;
  client_address: string;
  provider_address: string;
  evaluator_address?: string | null;
  description: string;
  status: string;
  budget?: string | null;
  tx_hash?: string | null;
  report_hash?: string | null;
  submit_tx_hash?: string | null;
};

export type ReportResponse = {
  chain_job_id: string;
  report: {
    summary: string;
    evidence: Array<Record<string, string>>;
    analysis: Record<string, string>;
    scores: {
      confidence: number;
      risk_score: number;
      alpha_score: number;
    };
    recommendation: {
      action: string;
      reason: string;
    };
  };
  report_hash: string;
  verified: boolean;
  submit_tx_hash?: string | null;
};

export type AgentProfile = {
  name: string;
  address: string;
  identity_id: string;
  metadata_uri: string;
  type: string;
  capabilities: string[];
  version: string;
  status: string;
};

