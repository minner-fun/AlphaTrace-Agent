import Link from "next/link";
import { ArrowRight, BadgeCheck, Database, ShieldCheck } from "lucide-react";

import { env } from "@/lib/env";

const signals = [
  { label: "Identity", value: "ERC-8004", icon: BadgeCheck },
  { label: "Jobs", value: "ERC-8183", icon: Database },
  { label: "Delivery", value: "Report hash", icon: ShieldCheck },
];

export default function HomePage() {
  return (
    <div className="space-y-8">
      <section className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="flex min-h-[360px] flex-col justify-center rounded-md bg-ink p-8 text-paper">
          <p className="text-sm font-semibold uppercase tracking-wide text-amber">Arc Testnet agent console</p>
          <h1 className="mt-4 max-w-3xl text-4xl font-semibold leading-tight md:text-5xl">
            AlphaTrace Agent
          </h1>
          <p className="mt-4 max-w-2xl text-base leading-7 text-paper/75">
            Request Web3 research, run an off-chain market intelligence agent, submit a verifiable report hash,
            and settle the job through Arc agent infrastructure.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link href="/create-job" className="button-primary bg-amber text-ink hover:bg-mint">
              Create Research Job <ArrowRight size={16} />
            </Link>
            <Link href="/agent" className="button-secondary border-paper/20 bg-transparent text-paper hover:bg-paper/10">
              Agent Profile
            </Link>
          </div>
        </div>
        <div className="panel flex flex-col justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-moss">Agent status</p>
            <p className="mt-3 text-2xl font-semibold">Online for demo jobs</p>
            <p className="mt-2 break-all text-sm text-ink/60">{env.alphatraceAgentAddress}</p>
          </div>
          <div className="mt-8 grid gap-3">
            {signals.map((signal) => (
              <div key={signal.label} className="flex items-center justify-between rounded-md border border-ink/10 p-3">
                <div className="flex items-center gap-3">
                  <signal.icon className="text-moss" size={18} />
                  <span className="text-sm text-ink/60">{signal.label}</span>
                </div>
                <span className="text-sm font-semibold">{signal.value}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {[
          ["Request", "Create an ERC-8183 research job for token, wallet, or project analysis."],
          ["Analyze", "Run the AlphaTrace worker with mock WCT data and structured risk scoring."],
          ["Verify", "Store the full report off-chain and submit only its keccak hash as proof."],
        ].map(([title, body]) => (
          <div key={title} className="panel">
            <h2 className="text-lg font-semibold">{title}</h2>
            <p className="mt-2 text-sm leading-6 text-ink/65">{body}</p>
          </div>
        ))}
      </section>
    </div>
  );
}

