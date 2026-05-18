export const env = {
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000",
  arcRpcUrl: process.env.NEXT_PUBLIC_ARC_RPC_URL || "http://localhost:8545",
  arcChainId: Number(process.env.NEXT_PUBLIC_ARC_CHAIN_ID || 0),
  erc8183ContractAddress: process.env.NEXT_PUBLIC_ERC8183_CONTRACT_ADDRESS || "",
  alphatraceAgentAddress:
    process.env.NEXT_PUBLIC_ALPHATRACE_AGENT_ADDRESS || "0x0000000000000000000000000000000000000000",
  walletConnectProjectId: process.env.NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID || "",
};

