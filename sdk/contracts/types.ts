export type AgentEnvelopeVersion = '1.0';

export type AgentEnvelopeKind = 'progress' | 'action' | 'final';

export type JsonPrimitive = string | number | boolean | null;
export type JsonValue = JsonPrimitive | JsonObject | JsonArray;
export type JsonArray = JsonValue[];
export interface JsonObject {
  [key: string]: JsonValue;
}

export type ProgressStatus = 'pending' | 'running' | 'blocked' | 'complete';

export interface AgentEnvelopeBase {
  version: AgentEnvelopeVersion;
  id: string;
  timestamp: string;
  kind: AgentEnvelopeKind;
  metadata?: Record<string, string | number | boolean>;
}

export interface ProgressBody {
  status: ProgressStatus;
  message: string;
  progress?: number;
  step?: number;
  details?: Record<string, unknown>;
}

export interface ActionBody {
  id?: string;
  name: string;
  input: JsonValue;
  reason?: string;
  expectReply?: boolean;
}

export interface FinalSuccessBody {
  outcome: 'success';
  message: string;
  citations?: string[];
  data?: Record<string, unknown>;
}

export interface FinalFailureBody {
  outcome: 'failure';
  message: string;
  error: string;
  citations?: string[];
  data?: Record<string, unknown>;
}

export type FinalBody = FinalSuccessBody | FinalFailureBody;

export interface ProgressEnvelope extends AgentEnvelopeBase {
  kind: 'progress';
  body: ProgressBody;
}

export interface ActionEnvelope extends AgentEnvelopeBase {
  kind: 'action';
  body: ActionBody;
}

export interface FinalEnvelope extends AgentEnvelopeBase {
  kind: 'final';
  body: FinalBody;
}

export type AgentEnvelope = ProgressEnvelope | ActionEnvelope | FinalEnvelope;

export type AgentStreamEvent = AgentEnvelope;

export interface ActionInvocationResponse {
  id: string;
  envelope: AgentEnvelope;
}

export type FinalAnswer = FinalBody;

export type Progress = ProgressBody;

export type Action = ActionBody;
