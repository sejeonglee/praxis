import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';

const filePath = fileURLToPath(import.meta.url);
const testsDir = dirname(filePath);
const sdkDir = dirname(testsDir);
const repoRoot = dirname(dirname(sdkDir));

describe('workspace discovery', () => {
  it('registers example app and sdk packages', () => {
    const appPkg = JSON.parse(
      readFileSync(join(repoRoot, 'apps', 'example-app', 'package.json'), 'utf8'),
    );
    const sdkPkg = JSON.parse(
      readFileSync(join(repoRoot, 'sdk', 'example-sdk', 'package.json'), 'utf8'),
    );

    expect(appPkg.name).toBe('@praxis/example-app');
    expect(sdkPkg.name).toBe('@praxis/example-sdk');
  });
});
