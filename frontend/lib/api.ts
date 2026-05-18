import { env } from "@/lib/env";
import type { AgentProfile, JobResponse, ReportResponse } from "@/lib/types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${env.apiBaseUrl}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function syncJob(input: {
  chain_job_id: string;
  client_address: string;
  provider_address: string;
  description: string;
  budget?: string;
  tx_hash?: string;
}) {
  return request<JobResponse>("/api/jobs/sync", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function getJob(jobId: string) {
  return request<JobResponse>(`/api/jobs/${jobId}`);
}

export function runAgent(jobId: string) {
  return request<{ chain_job_id: string; status: string; report_hash: string; report_id: number; submit_tx_hash?: string }>(
    `/api/jobs/${jobId}/run`,
    { method: "POST" },
  );
}

export function getReport(jobId: string) {
  return request<ReportResponse>(`/api/reports/${jobId}`);
}

export function submitFeedback(jobId: string, input: { user_address: string; score: number; comment?: string }) {
  return request(`/api/jobs/${jobId}/feedback`, {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function getAgentProfile() {
  return request<AgentProfile>("/api/agent/profile");
}

