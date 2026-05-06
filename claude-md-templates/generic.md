# Generic Project: Project Context

> Loaded automatically by Claude Code (including the GitHub reviewer action).
> This file is the source of truth for code-review behavior on this repo.

## Stack

- **Turborepo** monorepo + **pnpm** workspaces
- Likely apps: NestJS / TypeORM API, Next.js web, React Native (Expo) mobile
- TypeScript strict (no `any`)
- **Package manager:** pnpm only (npm or yarn: flag CRITICAL)

## Layout

```
apps/
├── api/        # backend (NestJS or other)
├── web/        # Next.js
└── mobile/     # React Native / Expo
packages/
└── shared/     # cross-app shared code
turbo.json     # task graph
```

## Code Review Behavior

### Format
For every comment: problem (1 line), why it matters (1 line), suggested fix (code snippet).

### Severity
- **CRITICAL:** blocks merge
- **IMPORTANT:** discuss before merging
- **SUGGESTION:** optional improvement

### Behavior rules
- Only flag issues you are certain about. When in doubt, stay silent.
- Prefer fewer high-quality comments over comprehensive coverage.
- Only comment on code changed or directly affected by this PR. Pre-existing issues do not get flagged.

### Do NOT flag (CI handles these)
- Formatting, import order, unused variables (ESLint, Prettier)
- Type errors (TypeScript compiler fails CI on its own)
- Test failures (Jest, Vitest)

### Do NOT review (auto-generated)
- `node_modules/**`
- Lock files (`pnpm-lock.yaml`)
- `apps/*/dist/**`, `apps/*/.next/**`
- `generated/**`, `*.generated.ts`

## Required Patterns

| Pattern | Required form |
|---|---|
| TypeScript | no `any`, explicit return types on exported functions |
| Async/await | no floating promises, no `then()` chains where `await` is cleaner |
| Error handling | null checks on nullable returns, errors caught and propagated |
| Package manager | pnpm only |
| API auth | every endpoint in `apps/api` has auth middleware/guard |
| TypeORM | parameterized queries via repository or query builder; never raw string concat |
| Cross-platform | Web APIs (`window`, `document`) must not appear in code shared with `apps/mobile` |

## Flag as CRITICAL

- Hardcoded secrets, API keys, or credentials in any app
- Missing auth on any endpoint in `apps/api`
- SQL injection (raw TypeORM queries without parameterization)
- `eval()` or injection-equivalent patterns
- npm or yarn instead of pnpm
- `any` in TypeScript on exported APIs (bypasses type safety across the monorepo)

## Flag as IMPORTANT

- Missing error handling on external API/service calls
- Nullable return without null check at the call site
- Floating promises (unawaited async calls)
- Explicit return types missing on exported functions
- Inline styles or hardcoded layout in `apps/web` (use Tailwind)
- Missing `key` prop on React list renders in `apps/web`

## Architecture Facts

- This is a transitional monorepo. It does not yet have the full Viero convention stack. Apply standard code quality rules rather than tenant-specific patterns.
- `apps/api` may use TypeORM (not Prisma). TypeORM query builder and `createQueryBuilder` are present; raw query injection has more surface area than in Prisma-based backends.
- Three separate runtimes (`api`, `web`, `mobile`) share a pnpm workspace. A change to a shared package in `packages/` can break all three. Flag changes to shared packages as needing cross-app verification.
- Turborepo task graph (`turbo.json`) defines build/test dependencies. Changing `turbo.json` can cause CI to skip dependent builds silently.
- React Native (Expo) has a different runtime from Next.js. Web APIs (`window`, `document`) crash on mobile. Flag any shared code that uses browser-only APIs without a platform guard.

## Style

- Functions max ~30 lines
- Max 3 parameters per function (use an options object if more)
- Booleans prefixed `is`, `has`, `can`, `should`
- **No em-dashes** in markdown, code comments, or commit messages. Use commas, periods, colons, parentheses.
