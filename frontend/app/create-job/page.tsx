"use client";

import { FormEvent, useState } from "react";
import { useAccount, useWriteContract } from "wagmi";
import { ArrowRight, ClipboardCheck, Coins } from "lucide-react";
import { useRouter } from "next/navigation";

import { getCreateJobContractArgs } from "@/lib/chain";
import { env } from "@/lib/env";
import { syncJob } from "@/lib/api";

export default function CreateJobPage() {
  const router = useRouter();
  const { address } = useAccount();
  const { writeContractAsync, isPending } = useWriteContract();
  const [title, setTitle] = useState("WCT token flow risk review");
  const [description, setDescription] = useState(
    "Analyze WCT token flow and identify bridge, multisig, holder concentration, and risk signals.",
  );
  const [taskType, setTaskType] = useState("token");
  const [target, setTarget] = useState("WCT");
  const [budget, setBudget] = useState("25");
  const [deadline, setDeadline] = useState("");
  const [mode, setMode] = useState<"chain" | "mock">("mock");
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);

    try {
      const shouldUseChain = mode === "chain" && env.erc8183ContractAddress;
      let chainJobId = Date.now().toString();
      let txHash = `mock-create-${chainJobId}`;

      if (shouldUseChain) {
        const hash = await writeContractAsync(getCreateJobContractArgs(description));
        txHash = hash;
      }

      await syncJob({
        chain_job_id: chainJobId,
        client_address: address || "0xDemoClient000000000000000000000000000000000",
        provider_address: env.alphatraceAgentAddress,
        description: `${title}. ${description} Target: ${target}. Task type: ${taskType}. Deadline: ${deadline || "none"}.`,
        budget,
        tx_hash: txHash,
      });

      router.push(`/jobs/${chainJobId}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create job");
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_340px]">
      <form onSubmit={onSubmit} className="panel space-y-5">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-moss">Create research job</p>
          <h1 className="mt-2 text-2xl font-semibold">New AlphaTrace request</h1>
        </div>

        <label className="block space-y-2">
          <span className="label">Task title</span>
          <input className="field" value={title} onChange={(event) => setTitle(event.target.value)} />
        </label>

        <label className="block space-y-2">
          <span className="label">Task description</span>
          <textarea
            className="field min-h-32"
            value={description}
            onChange={(event) => setDescription(event.target.value)}
          />
        </label>

        <div className="grid gap-4 md:grid-cols-2">
          <label className="block space-y-2">
            <span className="label">Task type</span>
            <select className="field" value={taskType} onChange={(event) => setTaskType(event.target.value)}>
              <option value="token">Token flow</option>
              <option value="wallet">Wallet intelligence</option>
              <option value="project">Project research</option>
            </select>
          </label>
          <label className="block space-y-2">
            <span className="label">Target</span>
            <input className="field" value={target} onChange={(event) => setTarget(event.target.value)} />
          </label>
          <label className="block space-y-2">
            <span className="label">Budget USDC</span>
            <input className="field" value={budget} onChange={(event) => setBudget(event.target.value)} />
          </label>
          <label className="block space-y-2">
            <span className="label">Deadline</span>
            <input className="field" type="datetime-local" value={deadline} onChange={(event) => setDeadline(event.target.value)} />
          </label>
        </div>

        <div className="flex flex-wrap gap-2">
          <button type="button" className={mode === "mock" ? "button-primary" : "button-secondary"} onClick={() => setMode("mock")}>
            <ClipboardCheck size={16} /> Demo sync
          </button>
          <button type="button" className={mode === "chain" ? "button-primary" : "button-secondary"} onClick={() => setMode("chain")}>
            <Coins size={16} /> Create on Arc
          </button>
        </div>

        {error ? <p className="rounded-md bg-coral/10 p-3 text-sm text-coral">{error}</p> : null}

        <button className="button-primary" disabled={isPending}>
          {isPending ? "Creating..." : "Create Job"} <ArrowRight size={16} />
        </button>
      </form>

      <aside className="panel h-fit">
        <h2 className="text-lg font-semibold">MVP flow</h2>
        <div className="mt-4 space-y-3 text-sm leading-6 text-ink/65">
          <p>Demo sync creates a local Job and keeps the chain-facing fields visible.</p>
          <p>When Arc contract details are ready, switch to Create on Arc and the page calls the ERC-8183 wrapper.</p>
          <p>After creation, run the Agent from the Job detail page to generate the report hash.</p>
        </div>
      </aside>
    </div>
  );
}

