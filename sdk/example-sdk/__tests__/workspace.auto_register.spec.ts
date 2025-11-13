import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';

const workspaceConfig = readFileSync('pnpm-workspace.yaml', 'utf8');

describe('workspace auto-registration', () => {
  it('includes glob patterns for sdk and apps directories', () => {
    expect(workspaceConfig).toContain("'apps/*'");
    expect(workspaceConfig).toContain("'sdk/*'");
  });
});
