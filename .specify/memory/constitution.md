<!--
Sync Impact Report
Version change: 0.0.0 → 1.0.0
Modified principles:
- Template Principle 1 → Spec-Driven Development (OBJECTIVE-first)
- Template Principle 2 → Red→Green Discipline
- Template Principle 3 → Dual-Client Parity & Release Gates
- Template Principle 4 → Observability-First Execution
- Template Principle 5 → Secure Multi-Profile Delivery
Added sections:
- Operational Directives
- Workflow & Quality Gates
Removed sections:
- None
Templates requiring updates:
- ✅ .specify/templates/plan-template.md (Constitution Check gates + deployment parity prompts)
- ✅ .specify/templates/spec-template.md (Constitutional constraint checklist)
- ✅ .specify/templates/tasks-template.md (TDD enforcement and telemetry/security tasks)
Follow-up TODOs:
- TODO(RATIFICATION_DATE): Confirm original adoption date from project history.
-->

# Praxis Constitution

## Core Principles

### 1. Spec-Driven Development (OBJECTIVE-first)
OBJECTIVE.md is the single source of truth for requirements, contracts, and
deployment expectations. Ambiguities are resolved by amending the spec, not by
ad-hoc code. Every change must cite the governing contract, keep schemas and
types in sync, and document deviations before implementation to prevent drift.

### 2. Red→Green Discipline
Work follows strict TDD: write the failing unit and mocking E2E tests, observe
RED, implement the minimal code to turn tests GREEN, then refactor with the
suite green. Commits remain atomic, each representing a RED→GREEN transition or
a scoped refactor, ensuring the repository stays shippable at all times.

### 3. Dual-Client Parity & Release Gates
The real OpenAI-compatible LLM client and the deterministic mock share one
interface and are switchable via `LLM_CLIENT=mock|openai` (CI defaults to
`mock`). Unit and mocking E2E suites run before every push, and pipelines block
merges on any failure. Tests that require external egress run only when explicitly
opted-in via environment flags, otherwise they skip to keep CI deterministic.

### 4. Observability-First Execution
All prompts, tool calls, sandbox executions, and network interactions emit
OpenTelemetry + OpenLLMetry spans that capture tokens, cost, latency, model or
tool identifiers, budgets, and event IDs. Attribute filters prevent secret
leakage, sampling rules are documented, and instrumentation is treated as part
of the Definition of Done so that regressions are instantly diagnosable.

### 5. Secure Multi-Profile Delivery
Local-Solo, Local-Multi, and K8s-Multi profiles expose the same contract,
behavior, and gates; autoscaling is mandatory on K8s. Secrets honor their
`secretsScope`, are never logged, and network egress is allowlisted whenever
`net=on`. MCP servers and external integrations are version-pinned, artifacts
are content-addressable whenever practical, and package management uses `uv`
for Python plus `pnpm` for Node/TypeScript with reviewed lockfiles.

## Operational Directives

- **Testing Gates**: Run the full unit suite and the mocking E2E suite locally
  before opening or updating a PR. CI reruns both suites and blocks on failure.
- **Package Management**: Python environments are created exclusively with
  `uv`. JavaScript/TypeScript workspaces use `pnpm`. Lockfiles are reviewed and
  cannot be regenerated without explaining dependency intent.
- **Clients & Network Use**: Keep both LLM clients healthy. Default to the mock
  in CI for determinism. Any test that needs remote egress must depend on an
  explicit env flag (skipped otherwise) and document the target allowlist entry.
- **Observability**: Telemetry spans cover prompts, tool calls, sandboxes,
  network interactions, and budget updates. Include correlation IDs so Local
  and Multi-profile traces stitch across services.
- **Security & Safety**: Secrets stay within their declared scope, with no
  logging or telemetry leakage. Egress is deny-by-default. MCP integrations are
  version-pinned and reviewed before upgrade. Artifacts and datasets should be
  content-addressable to ensure reproducibility and integrity.
- **Deployment Profiles**: Local-Solo optimizes for CLI and debugging,
  Local-Multi uses Docker Compose with inter-process networking, and K8s-Multi
  runs multi-node pods with autoscaling. Profile-specific overrides must not
  change canonical API or behavior, only the operational scaffolding.

## Workflow & Quality Gates

- **Commit & Branch Hygiene**: Prefer small commits containing one conceptual
  change. Each commit either captures a failing test (RED) or the corresponding
  fix/refactor (GREEN). Keep branches short-lived and rebased to retain a green
  mainline.
- **Stop-the-Line Policy**: If either the unit or mocking E2E suite fails on
  `main` or a release branch, all feature work pauses until the build is green.
  Every bug fix adds a regression test before shipping.
- **Definition of Done**:
  - Build succeeds; unit + mocking E2E suites pass locally and in CI.
  - VSCode debugging works for Python (`uv` runner) and Node (`pnpm test`).
  - Telemetry spans exist for prompts, tool calls, and sandbox runs.
  - HIL actions meet the ≤500 ms SLA inside mock E2E tests.
  - Changes align with OBJECTIVE.md and all deployment profiles.
- **Spec Governance**: Changes to OBJECTIVE.md start with a PR that adds or
  updates tests demonstrating the gap (RED) before modifying implementation.
  When code deviates from the spec, either fix the code or update the spec +
  tests with an explicit rationale.

## Governance

This constitution supersedes all other development practices in the repository.
Amendments require (1) an approved OBJECTIVE/spec update when applicable,
(2) updated tests showing RED→GREEN, (3) documentation of telemetry/security
impact, and (4) review acknowledgment that Local-Solo, Local-Multi, and
K8s-Multi profiles remain contract-compatible.

Versioning follows semantic rules: MAJOR for incompatible governance changes,
MINOR for new principles or materially expanded guidance, PATCH for clarifying
edits. Compliance reviews verify that every feature plan references the
Principles, Operational Directives, Workflow gates, and Definition of Done.

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE): Confirm historical adoption date. | **Last Amended**: 2025-11-10
