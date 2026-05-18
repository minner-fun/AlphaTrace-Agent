"use client";

import { useEffect, useState } from "react";
import { BadgeCheck, Cpu, Fingerprint, Shield } from "lucide-react";

import { getAgentProfile } from "@/lib/api";
import type { AgentProfile } from "@/lib/types";

export default function AgentPage() {
  const [profile, setProfile] = useState<AgentProfile | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getAgentProfile().then(setProfile).catch((err) => setError(err instanceof Error ? err.message : "Failed to load profile"));
  }, []);

  if (error) {
    return <div className="panel text-coral">{error}</div>;
  }

  if (!profile) {
    return <div className="panel">Loading agent profile...</div>;
  }

  return (
    <div className="space-y-6">
      <section className="panel">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-moss">ERC-8004 identity</p>
            <h1 className="mt-2 text-3xl font-semibold">{profile.name}</h1>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-ink/65">
              A market intelligence agent for token flow, wallet behavior, multisig risk, and project research.
            </p>
          </div>
          <span className="rounded-md bg-mint px-3 py-1 text-sm font-semibold text-moss">{profile.status}</span>
        </div>

        <div className="mt-6 grid gap-3 md:grid-cols-3">
          <div className="rounded-md border border-ink/10 p-4">
            <Fingerprint className="text-moss" size={20} />
            <p className="mt-3 text-xs uppercase tracking-wide text-ink/45">Agent address</p>
            <p className="mt-1 break-all text-sm font-medium">{profile.address}</p>
          </div>
          <div className="rounded-md border border-ink/10 p-4">
            <BadgeCheck className="text-moss" size={20} />
            <p className="mt-3 text-xs uppercase tracking-wide text-ink/45">Identity ID</p>
            <p className="mt-1 break-all text-sm font-medium">{profile.identity_id}</p>
          </div>
          <div className="rounded-md border border-ink/10 p-4">
            <Shield className="text-moss" size={20} />
            <p className="mt-3 text-xs uppercase tracking-wide text-ink/45">Metadata</p>
            <p className="mt-1 break-all text-sm font-medium">{profile.metadata_uri}</p>
          </div>
        </div>
      </section>

      <section className="panel">
        <h2 className="flex items-center gap-2 text-lg font-semibold">
          <Cpu size={18} /> Capabilities
        </h2>
        <div className="mt-4 flex flex-wrap gap-2">
          {profile.capabilities.map((capability) => (
            <span key={capability} className="rounded-md border border-ink/10 bg-white px-3 py-2 text-sm text-ink/70">
              {capability}
            </span>
          ))}
        </div>
      </section>
    </div>
  );
}

