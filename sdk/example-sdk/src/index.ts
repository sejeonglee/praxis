export type WorkspaceProbe = {
  packageName: string;
  path: string;
};

export function summarizeWorkspace(probes: WorkspaceProbe[]): string {
  if (!Array.isArray(probes) || probes.length === 0) {
    return 'No packages detected';
  }
  const names = probes.map((probe) => probe.packageName).join(', ');
  return `Discovered packages: ${names}`;
}
