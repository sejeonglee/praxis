# Agentic Multi-Agent System — SDD Spec v1.3

## 0) Purpose & Scope

* **Goal:** Implement a production-grade, multi-agent architecture that natively supports your I/O abstraction and modern agentic patterns (Skills with progressive disclosure, MCP lazy binding, sandbox execution, non-blocking HIL, TTC/budget-aware reasoning, MoA + verifier-first, graph-aware memory, event-driven environment, live evals).
* **I/O Abstraction (normative):**

  * **Inputs:**
    `start_instruction` (goal/constraints)
    `mid_events[]` (human/env/timer/budget interrupts)
    `observations[]` (tool/web/file/api/sandbox results)
  * **Outputs:**
    `progress[]` (plan/thought/log/metrics)
    `actions[]` (tool calls with purpose and expected cost)
    `final_answer` (result + artifacts/citations as needed)

---

## 1) Repository Layout (monorepo)

```
/praxis
  /apps
    /cli            # CLI adapter (SSE/WebSocket): Standalone application
    /web            # Web adapter (Next/React; SSE + WS): Frontend (requires /api)
    /api            # API Server adapter (LiteStar): Backend
  /sdk
    /contracts      # JSON Schemas / TS types / OpenAPI
    /orchestrator   # state graph (Plan/Act/Observe/Verify/Replan)
    /skills         # SKILL.md catalog (desc only at boot)
    /mcp-gateway    # lazy-bound MCP discovery/permissions
    /sandbox-runner # CodeExecute (E2B/Firecracker), MCP client in runtime
    /memory         # GraphRAG/HippoRAG/Zep(Temporal KG)
    /verifier       # PRM / rule / tests (verifier-first)
    /observability  # OpenTelemetry + OpenLLMetry
    /cost           # TTC/budget policies + metering
  /eval
    /are            # ARE (Gaia2) harness
    /swe-bench      # SWE-bench Verified/Live harness
  /infra
    /deploy         # Docker/K8s; MQTT/CloudEvents gateways
    /secrets        # vault, scopes, policies
```

---

## 2) Canonical Contracts (JSON Schemas)

### 2.1 Agent I/O (single envelope)

```json
{
  "$id": "https://agentos/contracts/agent-io.schema.json",
  "type": "object",
  "properties": {
    "input": {
      "type": "object",
      "required": ["start_instruction"],
      "properties": {
        "start_instruction": { "type": "string", "minLength": 1 },
        "mid_events": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["id", "ts", "kind"],
            "properties": {
              "id": { "type": "string", "format": "uuid" },
              "ts": { "type": "string", "description": "ISO-8601" },
              "kind": { "enum": ["human_feedback", "env_update", "timer", "budget_alert"] },
              "payload": {}
            }
          }
        },
        "observations": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["id", "ts", "source"],
            "properties": {
              "id": { "type": "string", "format": "uuid" },
              "ts": { "type": "string", "description": "ISO-8601" },
              "source": { "enum": ["tool", "web", "file", "api", "sandbox"] },
              "uri": { "type": "string" },
              "hash": { "type": "string" },
              "summary": { "type": "string" },
              "content_ref": {
                "type": "object",
                "properties": {
                  "type": { "enum": ["doc", "table", "image", "graph", "artifact"] },
                  "href": { "type": "string" }
                }
              },
              "metrics": {
                "type": "object",
                "properties": {
                  "latency_ms": { "type": "integer", "minimum": 0 },
                  "tokens": { "type": "integer", "minimum": 0 },
                  "cost_usd": { "type": "number", "minimum": 0 }
                }
              }
            }
          }
        }
      }
    },
    "output": {
      "type": "object",
      "required": ["final_answer"],
      "properties": {
        "progress": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["ts", "stage", "note"],
            "properties": {
              "ts": { "type": "string", "description": "ISO-8601" },
              "stage": { "enum": ["plan", "reason", "act", "observe", "verify", "replan"] },
              "note": { "type": "string" },
              "budget_used": {
                "type": "object",
                "properties": {
                  "tokens": { "type": "integer", "minimum": 0 },
                  "cost_usd": { "type": "number", "minimum": 0 },
                  "wall_ms": { "type": "integer", "minimum": 0 }
                }
              },
              "confidence": { "type": "number", "minimum": 0, "maximum": 1 }
            }
          }
        },
        "actions": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["id", "name", "purpose", "args", "expected_cost"],
            "properties": {
              "id": { "type": "string", "format": "uuid" },
              "name": { "type": "string" },
              "server": { "type": "string", "pattern": "^mcp://"},
              "purpose": { "type": "string" },
              "args": { "type": "object" },
              "expected_cost": {
                "type": "object",
                "properties": {
                  "tokens": { "type": "integer", "minimum": 0 },
                  "latency_ms": { "type": "integer", "minimum": 0 },
                  "cost_usd": { "type": "number", "minimum": 0 },
                  "risk": { "enum": ["low", "med", "high"] }
                }
              },
              "policy": {
                "type": "object",
                "properties": {
                  "sandbox_first": { "type": "boolean", "default": true },
                  "egress_whitelist": { "type": "array", "items": { "type": "string" } }
                }
              }
            }
          }
        },
        "final_answer": {
          "type": "object",
          "required": ["text"],
          "properties": {
            "text": { "type": "string" },
            "evidence": {
              "type": "array",
              "items": { "type": "object", "properties": { "uri": { "type": "string" }, "hash": { "type": "string" } } }
            },
            "artifacts": {
              "type": "array",
              "items": { "type": "object", "properties": { "kind": { "type": "string" }, "href": { "type": "string" } } }
            },
            "telemetry": { "type": "object" }
          }
        }
      }
    }
  },
  "required": ["input", "output"]
}
```

### 2.2 Agent-Client Protocol (ACP) — CloudEvents mapping

* Transport MUST be CloudEvents JSON over **SSE** (web), **WebSocket** (interactive), or **MQTT v5** (IoT/mobile).
* Event types (recommended):

  * `agent.event.received` → incoming `mid_events[*]`
  * `agent.progress.created|updated` → `output.progress[*]`
  * `agent.action.proposed` → `output.actions[*]`
  * `agent.observation.appended` → `input.observations[*]`
  * `agent.final.ready` → `output.final_answer`
* Non-blocking HIL MUST be supported via:

  * **Realtime-style**: `response.cancel`, `conversation.item.truncate` semantics
  * **Graph interrupt**: pause/resume checkpoints in orchestrator

---

## 3) Minimal Toolset (Skills-first)

### 3.1 `ReadFile` (progressive disclosure)

```json
{
  "name": "ReadFile",
  "args": { "path": "string", "byteRange": [0, 65535], "maxBytes": 262144 },
  "returns": { "content_base64": "string", "mime": "string" },
  "policy": { "root": "/skills", "readonly": true }
}
```

* Only `name/description` of each Skill MUST be loaded at boot.
* Full `SKILL.md` and references MUST be loaded **on demand** via `ReadFile`.

### 3.2 `CodeExecute` (sandbox-first; MCP client inside the runtime)

```json
{
  "name": "CodeExecute",
  "args": {
    "runtime": "python3.14|node20|bash",
    "code": "string",
    "files": [{"path":"string","content_base64":"string"}],
    "timeout_ms": 60000,
    "net": "on|off",
    "secretsScope": "string"
  },
  "returns": {
    "stdout": "string",
    "stderr": "string",
    "artifacts": [{"path":"string","ref":"string"}]
  },
  "embedded_clients": { "mcp": { "servers": ["tcp://..."], "lazy_connect": true } }
}
```

* Middle artifacts MUST remain in the sandbox; context SHOULD ingest only summaries/metrics.
* MCP tools SHOULD NOT be bulk-exposed to the LLM; call them **from code** inside the sandbox.

---

## 4) Orchestrator: State Graph & Flow

```
Idle → Plan → (Act ↔ Observe)* → Verify → Replan? → Finalize
                       ↑ mid_events / TTC / budget → interrupt/resume
```

* **Plan:** select candidate Skills from catalog; `ReadFile` only when relevant.
* **Act:** convert `actions[]` into code; run via `CodeExecute` (sandbox); call MCP tools from code as needed.
* **Observe:** store logs/artifacts externally; append compact `observations[]`.
* **Verify (verifier-first):** PRM/rules/tests decide continue vs. refine.
* **Replan (TTC):** increase depth/samples only when uncertainty/failure; otherwise fast-path.
* **Interrupt:** honor human/env/timer/budget events; implement non-blocking cancellation/truncation.

---

## 5) TTC / Budget-Aware Reasoning (Policy)

```yaml
# /sdk/cost/policies.yaml
ttc:
  max_tokens_total: 2000000
  per_step:
    default_budget: 2048
    min: 256
    max: 8192
  strategies:
    - name: token-aware-allocation
      when: "hardness in ['easy','medium','hard']"
      action: "allocate_tokens_dynamically()"
    - name: early-exit
      when: "confidence > tau or diminishing_returns()"
      action: "stop_generation()"
    - name: thought-calibration
      action: "calibrate_termination_rule()"
```

---

## 6) MoA + Verifier-First

```
Proposers (k) → Aggregator → Verifier(PRM/tests) → (optional Critic loop) → Finalizer
```

* MoA SHOULD be used when diversity improves robustness; Self-MoA (multi-sample) is allowed.
* Verifier MUST gate deep reasoning: raise depth/samples **only** when uncertain.

---

## 7) Context Curation & Long-Term Memory

* **Externalize originals**: keep raw docs/logs/artifacts in FS/DB/OBJ; inject only **selected** summaries/graphs into prompts.
* Preferred memory backends:

  * **GraphRAG/HippoRAG** for community summarization & multi-hop retrieval.
  * **Zep (Temporal KG)** when session chronology and recency matter.

---

## 8) MCP Gateway (Lazy Binding)

* At boot: index **servers** only (no tool schemas).
* On first use: fetch tool metadata, open session, enforce **allowed-tools** from Skill front-matter and **secretsScope**.
* The LLM SHOULD NOT see thousands of tool definitions; the sandboxed code calls MCP as needed.

---

## 9) HIL & Client Adapters

* **Web/CLI:** stream ACP via SSE/WS; map user actions to `cancel` / `truncate` / `inject`.
* **LangGraph:** implement explicit `interrupt()` checkpoints and resumable state.
* **MQTT (optional):** use QoS1 + message/session expiry for offline resilience.

---

## 10) Observability & Safety

* Use **OpenTelemetry + OpenLLMetry**. Each prompt/toolcall/sandbox exec MUST emit a span with:

  * tokens, cost, latency, model/tool names, success/error, budgets, event IDs.
* Secrets MUST be scoped to `secretsScope`. Egress MUST be allowlisted when `net=on`.
* Every artifact SHOULD be hashed; every MCP server SHOULD be version-pinned.

---

## 11) Evaluation (CI-style)

* **ARE (Gaia2):** weekly runs; measure long-horizon, async, event-driven performance.
* **SWE-bench Verified/Live:** code-agent regression guard; track pass% + compute/latency.

---

## 12) Code Scaffolds (ready to paste)

### 12.1 Type stubs (TypeScript)

```ts
// /sdk/contracts/types.ts
export type MidEventKind = 'human_feedback'|'env_update'|'timer'|'budget_alert';
export interface StartInput { start_instruction: string; mid_events?: any[]; observations?: any[]; }
export interface Progress { ts:string; stage:'plan'|'reason'|'act'|'observe'|'verify'|'replan'; note:string; budget_used?: any; confidence?: number; }
export interface Action { id:string; name:string; server?:string; purpose:string; args:Record<string,any>; expected_cost?: {tokens?:number; latency_ms?:number; cost_usd?:number; risk?:'low'|'med'|'high'}; policy?: any; }
export interface FinalAnswer { text:string; evidence?:{uri:string;hash?:string}[]; artifacts?:{kind:string;href:string}[]; telemetry?:any; }
```

### 12.2 OpenAPI (minimal)

```yaml
# /sdk/contracts/acp.openapi.yaml
paths:
  /stream:
    get: { summary: SSE stream of CloudEvents }
  /invoke:
    post: { summary: Submit start_instruction; returns session id }
  /action:
    post: { summary: HIL actions (cancel|truncate|inject) }
```

### 12.3 Skill template

```md
# /sdk/skills/<skill-name>/SKILL.md
---
name: "web.research"
description: "High-precision research with citations"
allowed-tools: ["ReadFile","CodeExecute"]
policies: { net: "on", secrets: "web-ro" }
triggers:
  - "find latest spec"
  - "compare standards"
---

## Policy
- Prefer primary sources and official docs.

## How-To
1) fetch candidates
2) rank and summarize
3) emit observations with citations

## Examples
...
```

### 12.4 Sandbox runner (Node + E2B, example)

```ts
// /sdk/sandbox-runner/e2b.ts
import { Sandbox } from '@e2b/code-interpreter'
export async function runCode({ code, files=[], net='off', timeout=60000 }) {
  const sb = await Sandbox.create()
  for (const f of files) await sb.files.write(f.path, Buffer.from(f.content_base64, 'base64'))
  const out = await sb.notebook.execCell(code, { timeoutMs: timeout, internetAccess: net === 'on' })
  return { stdout: out.stdout, stderr: out.stderr, artifacts: await sb.files.list('.') }
}
// Inside code you can call MCP tools via an embedded client:
// await callMCPTool('mcp://server', 'tool.name', { ... })
```

### 12.5 SSE endpoint (Next.js example)

```ts
// /apps/web/app/api/stream/route.ts
export const GET = async () => {
  const stream = new ReadableStream({
    start(c) {
      c.enqueue(encodeCE({ type:'agent.progress.created', data:{ ts:new Date().toISOString(), stage:'plan', note:'boot' } }))
    }
  })
  return new Response(stream, { headers: { 'Content-Type': 'text/event-stream' } })
}
```

---

## 13) Deployment Profiles

| Profile     | Runtime                              | Isolation/Security                  | Typical Use                                             |
| ----------- | ------------------------------------ | ----------------------------------- | ------------------------------------------------------- |
| Local-Solo  | single node, single process          | in-process or single container      | local CLI app, debugging sessions, evaluations          |
| Local-Multi | single node, multi process (compose) | per-process/per-container isolation | API server on single host; inter-process comms via IPC/docker network |
| K8s-Multi   | multi-node, multi process (K8s Pods) | pod-level policies, secrets/roles   | production API server; autoscaling and scale-out concurrency |

- Local-Multi: components run as separate processes/containers via Docker Compose; communicate over the compose network.
- K8s-Multi: components deploy as Pods/Deployments; communicate via ClusterIP/Service; enable autoscaling (HPA) for scale-out.
- Local-Solo: optimized for simple CLI flows and local eval; minimal overhead.

---

## 14) Definition of Done (acceptance)

* **Cost:** TTC policies yield ≥ **30% token savings** with ≤ **2pp** accuracy loss (vs. naive).
* **HIL:** cancel/truncate reflected within **≤ 500 ms** end-to-end.
* **Memory:** Graph-aware retrieval improves multi-hop QA / long sessions (A/B on internal set).
* **Live evals:** pass thresholds on **ARE** scenarios and **SWE-bench Verified** with no regressions.
* **Observability:** 100% of prompts/toolcalls/sandbox runs produce OTel spans with tokens/latency/cost.

---

## 15) Quick Start (for Claude Code / OpenAI)

1. Create `/sdk/contracts/agent-io.schema.json` and `/sdk/contracts/types.ts`.
2. Add 3–5 starter Skills (`/sdk/skills/*/SKILL.md`) with only `name/description` at boot.
3. Implement `/sdk/sandbox-runner` (`CodeExecute`) and embed an MCP client.
4. Implement `/sdk/mcp-gateway` lazy discovery + allowlists/secrets scopes.
5. Expose `/apps/web` SSE stream + a minimal Stream UI (progress/actions/final).
6. Add TTC policies under `/sdk/cost/policies.yaml`.
7. Wire `/eval/are` and `/eval/swe-bench` to CI to track live performance.

---

### Normative Notes

* MUST = mandatory for conformance; SHOULD = strongly recommended.
* All timestamps are ISO-8601 strings.
* All money values are USD (float).
* Artifacts MUST be content-addressable (hash) when possible.
* Privacy-first: keep large/raw data in external storage; inject only minimal summaries/refs into prompts.
