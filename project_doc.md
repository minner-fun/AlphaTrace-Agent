下面这份可以直接复制给 **Codex / Cursor / Claude Code**，让它按文档初步实现项目。

---

# AlphaTrace Agent 项目开发文档

## 1. 项目概述

项目名称：**AlphaTrace Agent**

AlphaTrace 是一个基于 **Arc Testnet + ERC-8004 + ERC-8183** 的 Web3 市场情报 AI Agent。用户可以在前端提交研究任务，例如分析某个代币、钱包、项目或链上资金流。任务会通过 ERC-8183 创建为链上 Job，并使用 USDC 托管预算。AlphaTrace Agent 在链下执行爬虫、链上数据查询、数据分析和 LLM 推理，最终生成结构化 JSON 报告，并把报告 hash 提交回 Arc 链上作为交付证明。

ERC-8004 用于 Agent 链上身份、声誉和验证；ERC-8183 用于定义 Job、托管支付、提交交付物和完成结算。ERC-8004 的官方 EIP 描述其目标是让不同组织之间的 agent 可以在无需预先信任的情况下被发现、选择和交互；ERC-8183 定义的是带 escrowed budget 的 Job 状态机，状态包括 Open、Funded、Submitted 和 Terminal。([Ethereum Improvement Proposals][1])

Arc 官方教程已经提供了在 Arc Testnet 注册 ERC-8004 Agent，以及用 ERC-8183 创建 Job、fund、submit、complete 的开发流程。([docs.arc.network][2])

---

## 2. 项目一句话介绍

> AlphaTrace is an ERC-8004 registered AI market intelligence agent that accepts ERC-8183 research jobs, analyzes Web3 market signals off-chain, submits verifiable report hashes on Arc, and settles tasks in USDC.

中文：

> AlphaTrace 是一个基于 ERC-8004 注册身份的 Web3 市场情报 Agent。用户通过 ERC-8183 给 Agent 创建研究任务，Agent 在线下完成爬虫和数据分析后生成报告，并把报告 hash 提交到 Arc 链上完成交付证明和 USDC 结算。

---

## 3. 核心业务流程

### 3.1 用户侧流程

```text
用户打开网站
  ↓
连接钱包
  ↓
填写研究任务
例如：Analyze WCT token flow and multisig risk
  ↓
前端调用 ERC-8183 合约 createJob
  ↓
Agent 设置任务价格 / budget
  ↓
用户 approve USDC
  ↓
用户 fund job
  ↓
等待 Agent 执行
  ↓
查看 Agent 生成的 JSON 报告
  ↓
用户 complete job
  ↓
用户给 Agent 打分 / 反馈
```

### 3.2 Agent 侧流程

```text
AlphaTrace Agent 已通过 ERC-8004 注册身份
  ↓
监听 ERC-8183 Job
  ↓
发现 provider 是 AlphaTrace Agent 的新任务
  ↓
读取 job description
  ↓
解析任务类型
  ↓
执行链下爬虫 / 链上数据分析 / LLM 推理
  ↓
生成 report.json
  ↓
保存 report.json 到本地数据库 / IPFS / Supabase
  ↓
计算 report hash
  ↓
Agent 钱包调用 ERC-8183 submit(jobId, reportHash)
  ↓
等待用户 complete
  ↓
用户反馈写入 ERC-8004 ReputationRegistry
```

---

## 4. 技术栈建议

### 前端

使用：

```text
Next.js
React
TypeScript
Tailwind CSS
wagmi
viem
RainbowKit 或 ConnectKit
```

前端主要负责：

```text
钱包连接
任务表单
创建 Job
Fund Job
展示 Job 状态
展示报告
Complete Job
用户反馈
```

---

### 后端

使用：

```text
Python
FastAPI
SQLAlchemy
SQLite / PostgreSQL
web3.py
httpx
pydantic
```

后端主要负责：

```text
同步链上 Job
执行 Agent 任务
调用爬虫模块
调用链上数据分析模块
调用 LLM
保存报告
计算 hash
提交 deliverable hash 到 Arc
提供报告查询 API
```

---

### 链上交互

使用：

```text
Arc Testnet
ERC-8004 IdentityRegistry / ReputationRegistry / ValidationRegistry
ERC-8183 Job Contract
USDC on Arc Testnet
```

---

## 5. 项目模块划分

建议目录结构：

```text
alphatrace-agent/
  frontend/
    app/
    components/
    lib/
    hooks/
    config/
    package.json

  backend/
    app/
      main.py
      config.py
      database.py

      api/
        jobs.py
        reports.py
        agent.py

      chain/
        arc_client.py
        erc8183_client.py
        erc8004_client.py
        event_listener.py

      agent/
        worker.py
        task_parser.py
        report_generator.py
        scoring.py

      crawlers/
        token_crawler.py
        wallet_crawler.py
        project_crawler.py
        social_crawler.py

      analysis/
        token_flow.py
        wallet_analysis.py
        multisig_analysis.py
        risk_analysis.py

      storage/
        report_store.py
        hash.py

      models/
        job.py
        report.py
        feedback.py

    requirements.txt
    .env.example

  contracts/
    abis/
      ERC8183.json
      IdentityRegistry.json
      ReputationRegistry.json

  docs/
    architecture.md
    demo-script.md
    api.md

  README.md
```

---

## 6. 核心数据模型

### 6.1 Job 表

```sql
CREATE TABLE agent_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chain_job_id TEXT UNIQUE NOT NULL,
    client_address TEXT NOT NULL,
    provider_address TEXT NOT NULL,
    evaluator_address TEXT,
    description TEXT NOT NULL,
    status TEXT NOT NULL,
    budget TEXT,
    tx_hash TEXT,
    created_at DATETIME,
    updated_at DATETIME
);
```

### 6.2 Report 表

```sql
CREATE TABLE reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chain_job_id TEXT UNIQUE NOT NULL,
    report_json TEXT NOT NULL,
    report_hash TEXT NOT NULL,
    report_uri TEXT,
    submit_tx_hash TEXT,
    summary TEXT,
    confidence INTEGER,
    risk_score INTEGER,
    created_at DATETIME
);
```

### 6.3 Feedback 表

```sql
CREATE TABLE feedbacks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chain_job_id TEXT NOT NULL,
    user_address TEXT NOT NULL,
    score INTEGER NOT NULL,
    comment TEXT,
    reputation_tx_hash TEXT,
    created_at DATETIME
);
```

---

## 7. Report JSON 标准格式

Agent 最终生成的报告必须是结构化 JSON。

示例：

```json
{
  "job_id": "12",
  "agent": {
    "name": "AlphaTrace Agent",
    "type": "market_intelligence",
    "version": "0.1.0"
  },
  "task": {
    "raw_description": "Analyze WCT token flow and multisig risk",
    "task_type": "token_flow_analysis",
    "target": "WCT"
  },
  "summary": "WCT shows significant token movement from initial distribution addresses to bridge-related and multisig-controlled wallets.",
  "evidence": [
    {
      "type": "token_transfer",
      "title": "Large transfer detected",
      "description": "A large WCT transfer was detected from the initial distribution wallet.",
      "source": "onchain",
      "tx_hash": "0x..."
    },
    {
      "type": "multisig_risk",
      "title": "Major supply controlled by multisig",
      "description": "A high percentage of token supply appears to be controlled by multisig-related wallets.",
      "source": "onchain",
      "address": "0x..."
    }
  ],
  "analysis": {
    "token_flow": "Mint / distribution wallet -> bridge-related address -> multisig or treasury wallet.",
    "holder_concentration": "High",
    "multisig_risk": "Medium to High",
    "market_signal": "Monitor"
  },
  "scores": {
    "confidence": 82,
    "risk_score": 76,
    "alpha_score": 68
  },
  "recommendation": {
    "action": "Monitor",
    "reason": "Large supply movement and multisig concentration require further tracking before action."
  },
  "generated_at": "2026-05-18T00:00:00Z"
}
```

---

## 8. Hash 计算规则

为了保证前后端和链上 hash 一致，必须使用稳定序列化。

Python 示例：

```python
import json
from eth_utils import keccak

def normalize_report(report: dict) -> str:
    return json.dumps(
        report,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False
    )

def hash_report(report: dict) -> str:
    normalized = normalize_report(report)
    return "0x" + keccak(text=normalized).hex()
```

注意：

```text
同一个 report JSON 必须得到同一个 hash
hash 提交到 ERC-8183 submit()
完整 JSON 存在后端数据库或 IPFS
链上不存完整 JSON
```

---

## 9. 后端 API 设计

### 9.1 创建本地 Job 记录

```http
POST /api/jobs/sync
```

请求：

```json
{
  "chain_job_id": "12",
  "client_address": "0x...",
  "provider_address": "0x...",
  "description": "Analyze WCT token flow and multisig risk",
  "tx_hash": "0x..."
}
```

作用：

```text
前端 createJob 成功后，把 jobId 同步给后端
MVP 阶段可先用这种方式，不必一开始做完整 event listener
```

---

### 9.2 运行 Agent 任务

```http
POST /api/jobs/{job_id}/run
```

作用：

```text
读取链上 Job
解析 description
执行 Agent worker
生成报告
保存报告
计算 hash
提交 submit(jobId, reportHash)
```

返回：

```json
{
  "chain_job_id": "12",
  "status": "submitted",
  "report_hash": "0x...",
  "report_id": 1,
  "submit_tx_hash": "0x..."
}
```

---

### 9.3 查询 Job 状态

```http
GET /api/jobs/{job_id}
```

返回：

```json
{
  "chain_job_id": "12",
  "status": "submitted",
  "description": "Analyze WCT token flow and multisig risk",
  "report_hash": "0x...",
  "submit_tx_hash": "0x..."
}
```

---

### 9.4 查询报告

```http
GET /api/reports/{job_id}
```

返回：

```json
{
  "chain_job_id": "12",
  "report": {},
  "report_hash": "0x...",
  "verified": true
}
```

---

### 9.5 提交反馈

```http
POST /api/jobs/{job_id}/feedback
```

请求：

```json
{
  "user_address": "0x...",
  "score": 90,
  "comment": "The report is useful and well-structured."
}
```

作用：

```text
保存本地反馈
可选：调用 ERC-8004 ReputationRegistry 记录声誉事件
```

---

## 10. Agent Worker 设计

核心入口：

```python
async def run_alpha_trace_job(chain_job_id: str):
    job = await get_job_from_db_or_chain(chain_job_id)

    task = parse_task(job.description)

    if task.task_type == "token_flow_analysis":
        raw_data = await analyze_token_flow_task(task)
    elif task.task_type == "wallet_analysis":
        raw_data = await analyze_wallet_task(task)
    elif task.task_type == "project_research":
        raw_data = await analyze_project_task(task)
    else:
        raw_data = await generic_research_task(task)

    report = await generate_report(job, task, raw_data)

    report_hash = hash_report(report)

    await save_report(
        chain_job_id=chain_job_id,
        report_json=report,
        report_hash=report_hash
    )

    submit_tx_hash = await submit_deliverable_to_arc(
        chain_job_id=chain_job_id,
        report_hash=report_hash
    )

    return {
        "chain_job_id": chain_job_id,
        "report_hash": report_hash,
        "submit_tx_hash": submit_tx_hash
    }
```

---

## 11. Task Parser 设计

先做简单规则解析，不要一开始做复杂 NLP。

```python
def parse_task(description: str) -> dict:
    text = description.lower()

    if "wct" in text or "token flow" in text or "multisig" in text:
        return {
            "task_type": "token_flow_analysis",
            "target": "WCT"
        }

    if "wallet" in text or "smart money" in text:
        return {
            "task_type": "wallet_analysis",
            "target": extract_wallet_address(description)
        }

    if "airdrop" in text or "project" in text:
        return {
            "task_type": "project_research",
            "target": extract_project_name(description)
        }

    return {
        "task_type": "generic_market_research",
        "target": None
    }
```

---

## 12. MVP 阶段的 WCT 分析可以先做模拟数据

由于黑客松时间只有一周，MVP 可以先做一版可运行闭环：

```text
用户提交 WCT 分析任务
后端识别 WCT
读取 mock_wct_data.json
调用 report_generator 生成结构化报告
计算 hash
提交到 Arc
前端展示报告
用户 complete job
用户反馈
```

后续再替换成真实数据源：

```text
区块浏览器 API
RPC Transfer logs
The Graph
Dune API
Covalent / Alchemy / QuickNode
项目官网 / 文档 / 社媒数据
```

---

## 13. 前端页面设计

### 13.1 首页

路径：

```text
/
```

内容：

```text
项目介绍
AlphaTrace Agent 状态
Agent address
ERC-8004 identity 信息
Create Research Job 按钮
```

---

### 13.2 创建任务页

路径：

```text
/create-job
```

表单字段：

```text
任务标题
任务描述
任务类型
目标对象：token / wallet / project
预算金额
截止时间
```

示例任务：

```text
Analyze WCT token flow and identify bridge, multisig, holder concentration, and risk signals.
```

按钮：

```text
Create Job on Arc
Fund Job with USDC
```

---

### 13.3 Job 详情页

路径：

```text
/jobs/[jobId]
```

展示：

```text
Job ID
Client address
Provider address
Evaluator address
Description
Budget
Current status
Create tx
Fund tx
Submit tx
Complete tx
```

如果报告已生成，展示：

```text
Report summary
Confidence score
Risk score
Evidence list
Recommendation
Report hash
Hash verification result
```

按钮：

```text
Run Agent
Refresh Status
Complete Job
Submit Feedback
```

MVP 阶段可以保留 `Run Agent` 按钮，方便 demo 手动触发后端执行。

---

### 13.4 Agent Profile 页

路径：

```text
/agent
```

展示：

```text
AlphaTrace Agent
Agent address
ERC-8004 identity ID
Metadata
Capabilities
Completed jobs
Average score
Reputation events
```

---

## 14. 链上交互设计

### 14.1 ERC-8004 注册 Agent

MVP 只需要完成一次注册。

Agent metadata 示例：

```json
{
  "name": "AlphaTrace Agent",
  "description": "An AI market intelligence agent for Web3 token, wallet, and project research.",
  "type": "market_intelligence_agent",
  "capabilities": [
    "token_flow_analysis",
    "wallet_analysis",
    "multisig_risk_analysis",
    "project_research",
    "alpha_report_generation"
  ],
  "version": "0.1.0"
}
```

注册完成后，把以下内容写入 `.env`：

```env
ALPHATRACE_AGENT_ADDRESS=0x...
ALPHATRACE_AGENT_ID=...
ALPHATRACE_AGENT_METADATA_URI=...
```

---

### 14.2 ERC-8183 Job 生命周期

需要实现或调用以下能力：

```text
createJob
setBudget
fund
submit
complete
getJob
```

MVP 可以按官方教程现成 ABI 来调用。

核心状态：

```text
Open
Funded
Submitted
Completed / Rejected / Expired
```

---

## 15. 环境变量

后端 `.env.example`：

```env
ARC_RPC_URL=
ARC_CHAIN_ID=
PRIVATE_KEY_AGENT=
PRIVATE_KEY_REPUTATION_RECORDER=

ERC8183_CONTRACT_ADDRESS=
IDENTITY_REGISTRY_ADDRESS=
REPUTATION_REGISTRY_ADDRESS=
VALIDATION_REGISTRY_ADDRESS=
USDC_ADDRESS=

DATABASE_URL=sqlite:///./alphatrace.db

OPENAI_API_KEY=
LLM_PROVIDER=openai

REPORT_STORAGE=database
```

前端 `.env.local.example`：

```env
NEXT_PUBLIC_ARC_RPC_URL=
NEXT_PUBLIC_ARC_CHAIN_ID=
NEXT_PUBLIC_ERC8183_CONTRACT_ADDRESS=
NEXT_PUBLIC_USDC_ADDRESS=
NEXT_PUBLIC_ALPHATRACE_AGENT_ADDRESS=
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

---

## 16. README 需要包含的内容

README 必须写清楚：

```text
What is AlphaTrace
Why Arc
How ERC-8004 is used
How ERC-8183 is used
Architecture
Local setup
Demo flow
Contract addresses
Screenshots
Future roadmap
```

---

## 17. Demo 流程

黑客松视频可以按这个流程：

```text
1. 展示 AlphaTrace Agent Profile
2. 说明 Agent 已通过 ERC-8004 注册身份
3. 用户创建 WCT research job
4. 用户 fund job with USDC
5. 后端 Agent 执行任务
6. 爬虫 / 分析模块生成 JSON report
7. Agent submit report hash to ERC-8183
8. 前端展示报告和 hash verification
9. 用户 complete job
10. 用户给 Agent feedback
```

---

## 18. MVP 优先级

### 第一优先级：必须完成

```text
前端连接钱包
创建 ERC-8183 Job
后端同步 Job
后端执行 mock WCT 分析
生成 report.json
计算 report hash
Agent submit report hash
前端展示报告
README 和 demo 视频
```

### 第二优先级：尽量完成

```text
USDC fund job
complete job
用户反馈
ERC-8004 ReputationRegistry 记录反馈
Agent Profile 页面
```

### 第三优先级：有时间再做

```text
真实链上 WCT 数据采集
IPFS 存储报告
完整 event listener
多任务队列
多 Agent 协作
报告订阅系统
```

---

## 19. 给 Codex 的实现要求

请根据以上文档实现一个 MVP 项目，要求：

```text
1. 使用 monorepo 结构，包含 frontend 和 backend。
2. frontend 使用 Next.js + TypeScript + Tailwind + wagmi/viem。
3. backend 使用 FastAPI + SQLAlchemy + web3.py。
4. 先实现 mock WCT 分析，不需要一开始接真实数据源。
5. 实现 Job 创建后的后端同步接口。
6. 实现 Agent Worker，能够根据 job description 生成结构化 report.json。
7. 实现 report hash 计算。
8. 实现 submit deliverable hash 到 Arc 的函数，合约地址和 ABI 从环境变量和 contracts/abis 读取。
9. 前端要有 create job 页面、job detail 页面、agent profile 页面。
10. 所有链上调用需要封装到单独模块，不要写死在页面里。
11. 所有配置通过 .env 管理。
12. 代码要能本地运行，README 写清楚启动步骤。
```

---

## 20. 最终项目定位

AlphaTrace 不是普通的 AI 报告生成器，而是：

```text
一个拥有 ERC-8004 链上身份的 Web3 市场情报 Agent
通过 ERC-8183 接收研究任务
在线下执行爬虫、链上分析和 LLM 推理
用 report hash 完成链上交付证明
通过 USDC 完成 Agent 任务结算
通过用户反馈积累 Agent 声誉
```

一句话：

> AlphaTrace turns Web3 research into an on-chain agent job: request, fund, analyze, submit, verify, settle, and rate.

[1]: https://eips.ethereum.org/EIPS/eip-8004?utm_source=chatgpt.com "ERC-8004: Trustless Agents"
[2]: https://docs.arc.network/arc/tutorials/register-your-first-ai-agent?utm_source=chatgpt.com "Register your first AI agent - Arc Docs"
