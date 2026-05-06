# NestJS Backend: Project Context

> Loaded automatically by Claude Code (including the GitHub reviewer action).
> This file is the source of truth for code-review behavior on this repo.

## Stack

- **NestJS 11** + TypeScript (strict mode, no `any`)
- **Prisma 6/7** + PostgreSQL 16
- **Auth:** Passport + JWT
- **Docs:** Swagger (auto-generated)
- **Package manager:** pnpm only (npm or yarn: flag CRITICAL)

## Layout

```
src/app/<module>/
├── <module>.module.ts
├── <module>.controller.ts
├── <module>.service.ts
├── dto/
│   ├── create-<x>.dto.ts
│   └── update-<x>.dto.ts
└── responses/
    └── <x>-response.ts
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
- Formatting, import order, unused variables (ESLint)
- Type errors (TypeScript compiler fails CI on its own)
- Test failures (Jest reports inline)

### Do NOT review (auto-generated)
- `app/api-client/**`, `generated/**`, `*.generated.ts`, `prisma/client/**`
- Lock files (`pnpm-lock.yaml`)
- `.env.example`, `Dockerfile` unless security-relevant

## Required Patterns

| Pattern | Required form |
|---|---|
| Auth guard | `@HasPermissions(['permName'], 'or')` on every endpoint |
| User context | `@User() user: UserMeta` |
| ID param | `@Param('id', new ParseIntPipe()) id: number` |
| DTOs | class-validator decorators + `@ApiProperty()` |
| Prisma | inject as `private prisma: PrismaService` |
| Pagination | `PaginationDto` (skip/take), response `{ data: T[], rows, take, skip }` |
| Errors | `throw new HttpErrorByCode[400]({ error: 'message' })` |
| Swagger | `@ApiTags`, `@ApiOkResponse`, `@ApiCreatedResponse` |
| Logger | `private readonly logger = new Logger(ServiceName.name)` |
| Module registration | new modules imported in `app.module.ts` |
| Env vars | validated at startup via `ConfigModule` |

## Flag as CRITICAL

- Missing `@HasPermissions` on any endpoint
- Raw SQL without parameterization
- Hard delete instead of soft delete (`isActive = false`)
- Missing `ParseIntPipe` on ID params
- Logging passwords, tokens, API keys, PII
- `eval()` or `new Function()` with any input
- Concurrent writes to same entity without `$transaction` or optimistic locking
- Read-then-write patterns without proper transaction isolation
- Schema (`prisma/schema.prisma`) edits without a corresponding migration in `prisma/migrations/`
- npm or yarn used instead of pnpm

## Flag as IMPORTANT

- Missing error handling on external API/service calls
- Missing Swagger decorators on endpoints
- Environment variables accessed without `ConfigModule` validation
- New module not imported in `app.module.ts`
- Function longer than ~40 lines
- `findFirst` without a comment explaining why `findUnique` cannot be used

## Architecture Facts

- **AuthModule is `@Global()`** in most Viero NestJS services. `JwtModule` is re-exported, `PermissionsGuard` is registered as a provider+export. New modules consuming `@HasPermissions` do not need to import `AuthModule` again.
- Pagination is always skip/take (not cursor-based). The response envelope `{ data, rows, take, skip }` is consumed by the frontend's auto-generated API client. Changing the shape is a breaking contract change.
- Env vars must be validated at startup via `ConfigModule`. Accessing `process.env.X` directly bypasses startup validation and silently gives `undefined` in production.
- Every new module must appear in `app.module.ts` `imports:[]`. Failing to do so silently prevents injection and shows up only at runtime.
- Prefer `findUnique` over `findFirst` when targeting a unique index. New code with `findFirst` should carry a comment explaining why.

## Style

- Functions max ~20 lines (hard flag at 40)
- Max 3 parameters per function. Use a DTO or options object if more.
- Booleans prefixed `is`, `has`, `can`, `should`.
- Naming: verb plus noun (`getActiveDriversByCity`, not `getData`).
- **No em-dashes** in markdown, code comments, or commit messages. Use commas, periods, colons, parentheses.
