# Feature Specification: CLI Event-Driven Environment Setup

**Feature Branch**: `[001-cli-env-setup]`  
**Created**: 2025-11-10  
**Status**: Draft  
**Input**: User description: "OBJECTIVE.md 를 읽고, 요구사항을 모두 이해해주세요. 참고자료들도 모두 참고해주면 좋습니다. 이러한 시스템을 구성한다고 했을 때, client 중에서 CLI 만 먼저 우선적으로 구현하려고 합니다. 그리고 local에서 수행은 되지만 각 구성요소가 message queue를 사이에 둔 event-driven 아키텍처로 구동되게 할 거에요. 이 경우에, LLM, DB 등은 모두 mocking 되어 있다고 가정하고 e2e test를 할 수 있는 script (시나리오 포함), 유닛 테스트, debugging 설정 (.vscode/launch.json)이 될 수 있는 환경을 먼저 셋팅해주세요."

## Clarifications

### Session 2025-11-10

- Q: What delivery guarantee should the message queue enforce between CLI and mocks? → A: At-least-once delivery; CLI deduplicates via event IDs.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run a CLI-driven agent session locally (Priority: P1)

An operator uses the CLI to submit a `start_instruction`, monitors progress, and receives the final response even though all services run locally with mocked LLM/DB components connected over a message queue.

**Why this priority**: Without a reliable CLI entry point, no other client can be validated; this establishes the reference workflow for the entire multi-agent stack.

**Independent Test**: Launch the CLI with a sample instruction and confirm it publishes start events, handles streamed progress updates from the queue, and prints the final answer without requiring web or IDE clients.

**Acceptance Scenarios**:

1. **Given** a local queue broker and configured mocks, **When** the operator runs the CLI with a valid instruction file, **Then** the CLI publishes a start event, subscribes to progress topics, and displays updates in real time.
2. **Given** the CLI is connected to mocked LLM and DB workers, **When** those workers publish observations and final answers, **Then** the CLI acknowledges them and exits with a success status once the final answer arrives.

---

### User Story 2 - Execute scripted end-to-end verification (Priority: P2)

QA engineers run a reusable script that stands up the queue, launches the CLI, triggers mocked services, and asserts that the expected event sequence and outputs occur for the documented scenario.

**Why this priority**: Automated regression is required to keep the agentic workflow stable as the orchestrator changes.

**Independent Test**: Run the script on a clean workstation; it should provision prerequisites, invoke the CLI, compare logged events against the scenario checklist, and produce a single pass/fail result.

**Acceptance Scenarios**:

1. **Given** the script is executed with default settings, **When** it orchestrates CLI launch plus mock responders, **Then** it emits a report that lists each event in order and flags any deviations before exiting.

---

### User Story 3 - Debug and unit test the CLI event flow (Priority: P3)

Developers attach a debugger (via `.vscode/launch.json`) or run unit tests to inspect how the CLI publishes/consumes queue messages and to reproduce failures quickly.

**Why this priority**: Debug and test ergonomics accelerate iteration on the CLI without depending on the full distributed system.

**Independent Test**: Open the workspace in VS Code, choose the provided launch profile, set a breakpoint in the event loop, and verify execution pauses there; run the unit test suite to validate parsing, queuing, and error handling logic.

**Acceptance Scenarios**:

1. **Given** the repo is opened in VS Code, **When** the developer selects the CLI debug configuration and starts it, **Then** the CLI launches with the same environment as regular runs and honors breakpoints before any queue message is processed.
2. **Given** the unit test runner is executed, **When** mocks simulate success and failure responses, **Then** tests pass for success cases and surface descriptive failures for malformed events.

---

### Edge Cases

- What happens when the message queue is unavailable or loses connectivity mid-run? CLI must retry or exit with actionable guidance without leaving orphaned workers.
- How does the system handle mocks that return malformed or delayed events (e.g., missing fields, out-of-order timestamps)? The CLI and scripts must log and quarantine these events without hanging.
- What occurs if multiple CLI sessions run concurrently against the same local queue namespace? Session IDs must remain unique and logs must stay segmented.
- How are long-running instructions handled when budget or timer mid-events arrive from the queue? The CLI must surface the interrupt and stop or resume based on policy.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The CLI MUST accept a `start_instruction`, session metadata, and queue configuration via command flags or config files and validate inputs before publishing any message.
- **FR-002**: The CLI MUST publish start instructions and subsequent user inputs to a local message queue and subscribe to progress/final-answer topics so that plan/act/observe/verify stages remain event-driven even when all services run on one machine, assuming at-least-once delivery and deduplicating messages via event IDs.
- **FR-003**: The local environment MUST include deterministic mock implementations for LLM, DB, and any downstream tools so that CLI workflows complete without external dependencies.
- **FR-004**: The solution MUST provide a documented e2e scenario plus an executable script that stands up the queue, launches CLI + mocks, waits for completion, and asserts that the event log matches the scenario.
- **FR-005**: The CLI MUST emit structured logs (timestamps, event IDs, stages, payload summaries) that can be referenced by both the e2e script and developers during manual runs.
- **FR-006**: A unit test suite MUST cover CLI command parsing, queue connectivity, event subscription handling, retry/timeout logic, and error surfacing for malformed mock responses.
- **FR-007**: A `.vscode/launch.json` configuration MUST exist so that developers can run or attach to the CLI (or the e2e script) with environment variables, arguments, and working directory pre-populated for breakpoints.
- **FR-008**: Documentation MUST clarify how to swap mocks for real services later without changing the CLI contract, ensuring the setup serves as the reference client for future adapters.

### Key Entities *(include if feature involves data)*

- **Session Instruction**: Captures the user’s `start_instruction`, optional mid-event triggers, budget constraints, and identifiers linking a CLI run to downstream orchestrators.
- **Event Envelope**: Represents any message on the queue (plan steps, observations, mid-events, final answers) with mandatory IDs, timestamps, stage labels, and payload summaries.
- **Mock Service Response**: Structured payload returned by mocked LLM/DB components that simulates tool output, latency metrics, and success/error status for consumption by the CLI and orchestrator.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Operators can run the CLI end-to-end on a clean workstation and receive a final answer within 3 minutes for the reference scenario without touching non-CLI tools.
- **SC-002**: The automated e2e script completes three consecutive runs of the documented scenario with zero failures and produces a timestamped report file after each run.
- **SC-003**: Unit tests covering CLI inputs, queue handling, and error cases achieve at least 80% statement coverage and must pass on CI before merging.
- **SC-004**: Using the provided `.vscode/launch.json`, a developer can start a debug session and hit a breakpoint before the first queue response in under 30 seconds, confirmed during internal QA.

## Assumptions & Constraints

- Local execution assumes a lightweight queue broker (e.g., embedded or containerized) accessible without admin privileges; future phases may replace it with shared infrastructure.
- Mocked LLM/DB components should return deterministic responses seeded per scenario to keep regression tests stable.
- Security considerations (secrets scopes, network isolation) follow the broader OBJECTIVE guidelines but can be simplified for local-only runs, provided logs avoid sensitive data.
