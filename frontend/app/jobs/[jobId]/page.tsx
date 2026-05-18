"use client";

import { FormEvent, useEffect, useState } from "react";
import { useAccount, useWriteContract } from "wagmi";
import { CheckCircle2, RefreshCw, Send, Star } from "lucide-react";

import { getCompleteJobContractArgs } from "@/lib/chain";
import { getJob, getReport, runAgent, submitFeedback } from "@/lib/api";
import type { JobResponse, ReportResponse } from "@/lib/types";

export default function JobDetailPage({ params }: { params: { jobId: string } }) {
  const { address } = useAccount();
  const { writeContractAsync, isPending } = useWriteContract();
  const [job, setJob] = useState<JobResponse | null>(null);
  const [report, setReport] = useState<ReportResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [score, setScore] = useState(90);
  const [comment, setComment] = useState("The report is useful and well-structured.");

  async function refresh() {
    setError(null);
    try {
      const nextJob = await getJob(params.jobId);
      setJob(nextJob);
      try {
        setReport(await getReport(params.jobId));
      } catch {
        setReport(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load job");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void refresh();
  }, [params.jobId]);

  async function handleRunAgent() {
    setError(null);
    try {
      await runAgent(params.jobId);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to run agent");
    }
  }

  async function handleComplete() {
    setError(null);
    try {
      await writeContractAsync(getCompleteJobContractArgs(params.jobId));
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Complete job failed. Check contract config and wallet network.");
    }
  }

  async function handleFeedback(event: FormEvent) {
    event.preventDefault();
    setError(null);
    try {
      await submitFeedback(params.jobId, {
        user_address: address || "0xDemoClient000000000000000000000000000000000",
        score,
        comment,
      });
      setComment("Feedback submitted.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Feedback failed");
    }
  }

  if (loading) {
    return <div className="panel">Loading job...</div>;
  }

  if (!job) {
    return <div className="panel">Job not found.</div>;
  }

  return (
    <div className="space-y-6">
      <section className="panel">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-moss">Job detail</p>
            <h1 className="mt-2 text-2xl font-semibold">Research Job #{job.chain_job_id}</h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-ink/65">{job.description}</p>
          </div>
          <span className="rounded-md bg-mint px-3 py-1 text-sm font-semibold text-moss">{job.status}</span>
        </div>

        <div className="mt-6 grid gap-3 md:grid-cols-2">
          {[
            ["Client", job.client_address],
            ["Provider", job.provider_address],
            ["Budget", job.budget || "Not set"],
            ["Create tx", job.tx_hash || "Not available"],
            ["Report hash", job.report_hash || "Pending"],
            ["Submit tx", job.submit_tx_hash || "Pending"],
          ].map(([label, value]) => (
            <div key={label} className="rounded-md border border-ink/10 p-3">
              <p className="text-xs uppercase tracking-wide text-ink/45">{label}</p>
              <p className="mt-1 break-all text-sm font-medium">{value}</p>
            </div>
          ))}
        </div>

        {error ? <p className="mt-4 rounded-md bg-coral/10 p-3 text-sm text-coral">{error}</p> : null}

        <div className="mt-6 flex flex-wrap gap-3">
          <button className="button-primary" onClick={handleRunAgent}>
            <Send size={16} /> Run Agent
          </button>
          <button className="button-secondary" onClick={refresh}>
            <RefreshCw size={16} /> Refresh
          </button>
          <button className="button-secondary" disabled={isPending} onClick={handleComplete}>
            <CheckCircle2 size={16} /> Complete Job
          </button>
        </div>
      </section>

      {report ? (
        <section className="grid gap-6 lg:grid-cols-[1fr_340px]">
          <div className="panel">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-sm font-semibold uppercase tracking-wide text-moss">Report</p>
                <h2 className="mt-2 text-xl font-semibold">AlphaTrace analysis</h2>
              </div>
              <span className="rounded-md bg-mint px-3 py-1 text-sm font-semibold text-moss">
                {report.verified ? "Hash verified" : "Hash mismatch"}
              </span>
            </div>
            <p className="mt-4 text-sm leading-6 text-ink/70">{report.report.summary}</p>

            <div className="mt-6 grid gap-3 md:grid-cols-3">
              {[
                ["Confidence", report.report.scores.confidence],
                ["Risk", report.report.scores.risk_score],
                ["Alpha", report.report.scores.alpha_score],
              ].map(([label, value]) => (
                <div key={label} className="rounded-md border border-ink/10 p-4">
                  <p className="text-xs uppercase tracking-wide text-ink/45">{label}</p>
                  <p className="mt-2 text-2xl font-semibold">{value}</p>
                </div>
              ))}
            </div>

            <h3 className="mt-6 text-sm font-semibold uppercase tracking-wide text-ink/50">Evidence</h3>
            <div className="mt-3 space-y-3">
              {report.report.evidence.map((item, index) => (
                <div key={`${item.title}-${index}`} className="rounded-md border border-ink/10 p-4">
                  <p className="font-semibold">{item.title}</p>
                  <p className="mt-1 text-sm leading-6 text-ink/65">{item.description}</p>
                  <p className="mt-2 break-all text-xs text-ink/45">{item.tx_hash || item.address || item.source}</p>
                </div>
              ))}
            </div>
          </div>

          <aside className="space-y-6">
            <div className="panel">
              <h2 className="text-lg font-semibold">Recommendation</h2>
              <p className="mt-3 text-2xl font-semibold text-moss">{report.report.recommendation.action}</p>
              <p className="mt-2 text-sm leading-6 text-ink/65">{report.report.recommendation.reason}</p>
            </div>
            <form onSubmit={handleFeedback} className="panel space-y-4">
              <h2 className="flex items-center gap-2 text-lg font-semibold">
                <Star size={18} /> Feedback
              </h2>
              <label className="block space-y-2">
                <span className="label">Score</span>
                <input className="field" type="number" min={0} max={100} value={score} onChange={(event) => setScore(Number(event.target.value))} />
              </label>
              <label className="block space-y-2">
                <span className="label">Comment</span>
                <textarea className="field min-h-24" value={comment} onChange={(event) => setComment(event.target.value)} />
              </label>
              <button className="button-primary">Submit Feedback</button>
            </form>
          </aside>
        </section>
      ) : (
        <section className="panel">
          <h2 className="text-lg font-semibold">No report yet</h2>
          <p className="mt-2 text-sm text-ink/65">Run the Agent to generate the structured JSON report and submit hash.</p>
        </section>
      )}
    </div>
  );
}

