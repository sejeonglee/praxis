# Workspace Documentation

This document explains how the pnpm workspace discovers packages under `/apps/*` and `/sdk/*`.

## Adding a Package

1. Create a new folder under either `apps/` or `sdk/`.
2. Add a `package.json` with a unique `name` (use the `@praxis/` scope).
3. Run `pnpm install` (or `./scripts/bootstrap.workspace.sh`) to refresh the workspace graph.
4. Confirm discovery via `pnpm ls --depth 0`.

No edits to `pnpm-workspace.yaml` are required—globs already include these folders.

## Troubleshooting

- **Package missing from `pnpm ls`:** Ensure the directory contains a valid `package.json` and is not ignored by `.npmrc` overrides.
- **TypeScript config errors:** Check `tsconfig.base.json` for paths. Packages should create a local `tsconfig.json` extending the base file.
- **Installation loops:** Use `pnpm install --filter <name>` to debug a single package.
