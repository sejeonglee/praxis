import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import Ajv from 'ajv';

import type {
  Action,
  ActionEnvelope,
  AgentEnvelope,
  FinalAnswer,
  FinalEnvelope,
  Progress,
  ProgressEnvelope,
} from '../types';

const schemaPath = resolve(__dirname, '../agent-io.schema.json');
const schema = JSON.parse(readFileSync(schemaPath, 'utf-8'));

const openapiPath = resolve(__dirname, '../acp.openapi.yaml');

function compileValidator() {
  const ajv = new Ajv({ allErrors: true });
  return ajv.compile(schema);
}

describe('Agent I/O schema', () => {
  it('accepts a valid progress envelope', () => {
    const validate = compileValidator();

    const message: ProgressEnvelope = {
      version: '1.0',
      id: 'run-123',
      timestamp: '2025-01-01T00:00:00Z',
      kind: 'progress',
      metadata: { sequence: 1 },
      body: {
        status: 'running',
        message: 'Collecting context',
        progress: 0.25,
        step: 1,
        details: { tokens: 42 },
      },
    };

    expect(validate(message)).toBe(true);
  });

  it('rejects progress envelopes outside the allowed shape', () => {
    const validate = compileValidator();

    const invalid = {
      version: '1.0',
      id: 'run-123',
      timestamp: '2025-01-01T00:00:00Z',
      kind: 'progress',
      body: {
        status: 'running',
        message: 'Oops',
        progress: 2,
        extra: true,
      },
    };

    expect(validate(invalid)).toBe(false);
    expect(validate.errors).toBeTruthy();
  });

  it('rejects final envelopes without an error on failure outcome', () => {
    const validate = compileValidator();

    const invalid = {
      version: '1.0',
      id: 'run-123',
      timestamp: '2025-01-01T00:00:00Z',
      kind: 'final',
      body: {
        outcome: 'failure',
        message: 'Could not complete request',
      },
    };

    expect(validate(invalid)).toBe(false);
  });
});

describe('TypeScript contract surface', () => {
  it('matches schema-compatible runtime shapes', () => {
    const progress: Progress = {
      status: 'pending',
      message: 'Queued',
    };

    const action: Action = {
      name: 'search',
      input: { query: 'lithium supply chain' },
    };

    const final: FinalAnswer = {
      outcome: 'success',
      message: 'Completed',
      citations: ['doc-1'],
    };

    const envelope: AgentEnvelope = {
      version: '1.0',
      id: 'run-abc',
      timestamp: '2025-01-01T00:00:00Z',
      kind: 'action',
      body: action,
    } satisfies ActionEnvelope;

    const doneEnvelope: AgentEnvelope = {
      version: '1.0',
      id: 'run-abc',
      timestamp: '2025-01-01T00:00:00Z',
      kind: 'final',
      body: {
        outcome: 'failure',
        message: 'Tool crashed',
        error: 'Traceback...'
      },
    } satisfies FinalEnvelope;

    expect(progress.status).toBe('pending');
    expect(action.name).toBe('search');
    expect(final.outcome).toBe('success');
    expect(envelope.kind).toBe('action');
    expect(doneEnvelope.body.error).toContain('Traceback');
    // @ts-expect-error - a failed final answer must include the error field
    const invalidFinal: FinalAnswer = { outcome: 'failure', message: 'bad' };
    expect(invalidFinal).toBeDefined();
  });
});

describe('OpenAPI definition', () => {
  it('parses and exposes the expected endpoints', () => {
    const raw = readFileSync(openapiPath, 'utf-8');
    const doc = JSON.parse(raw);

    expect(doc.openapi).toBe('3.1.0');
    expect(Object.keys(doc.paths)).toEqual(expect.arrayContaining(['/stream', '/invoke', '/action']));
    expect(doc.components.schemas.AgentEnvelope.$ref).toBe('./agent-io.schema.json');
    const streamSchema =
      doc.paths['/stream'].get.responses['200'].content['text/event-stream'].schema;
    expect(streamSchema.properties.data.$ref).toBe('#/components/schemas/AgentEnvelope');
  });

  it('is OpenAPI compliant', async () => {
    const raw = readFileSync(openapiPath, 'utf-8');
    expect(() => JSON.parse(raw)).not.toThrow();
  });
});
