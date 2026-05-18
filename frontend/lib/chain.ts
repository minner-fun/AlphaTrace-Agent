import { env } from "@/lib/env";
import { erc8183Abi } from "@/config/erc8183";

export function getCreateJobContractArgs(description: string) {
  if (!env.erc8183ContractAddress) {
    throw new Error("NEXT_PUBLIC_ERC8183_CONTRACT_ADDRESS is not configured");
  }

  return {
    address: env.erc8183ContractAddress as `0x${string}`,
    abi: erc8183Abi,
    functionName: "createJob",
    args: [env.alphatraceAgentAddress as `0x${string}`, description, "ipfs://alphatrace-job-metadata"],
  } as const;
}

export function getCompleteJobContractArgs(jobId: string) {
  if (!env.erc8183ContractAddress) {
    throw new Error("NEXT_PUBLIC_ERC8183_CONTRACT_ADDRESS is not configured");
  }

  return {
    address: env.erc8183ContractAddress as `0x${string}`,
    abi: erc8183Abi,
    functionName: "complete",
    args: [BigInt(jobId)],
  } as const;
}

export function getFundJobContractArgs(jobId: string) {
  if (!env.erc8183ContractAddress) {
    throw new Error("NEXT_PUBLIC_ERC8183_CONTRACT_ADDRESS is not configured");
  }

  return {
    address: env.erc8183ContractAddress as `0x${string}`,
    abi: erc8183Abi,
    functionName: "fund",
    args: [BigInt(jobId)],
  } as const;
}
