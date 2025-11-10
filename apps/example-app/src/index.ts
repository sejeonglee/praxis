export function runExampleApp(): string {
  return 'Example app bootstrapped via pnpm workspace.';
}

if (import.meta.url === `file://${process.argv[1]}`) {
  console.log(runExampleApp());
}
