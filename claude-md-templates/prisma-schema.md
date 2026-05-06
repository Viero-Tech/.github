# Prisma Schema: Project Context

> Loaded automatically by Claude Code (including the GitHub reviewer action).
> This file is the source of truth for code-review behavior on this repo.

## Stack

- **Prisma 6/7** schema (standalone repo shared by tenant backends)
- **PostgreSQL 16**
- **multiSchema** preview feature on tenants that need it
- **Package manager:** pnpm

## Layout

```
prisma/
├── schema.prisma            # source of truth
├── migrations/
│   ├── <timestamp>_<name>/
│   │   └── migration.sql
│   └── migration_lock.toml
└── seed.ts                  # optional, deterministic
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
- Formatting (`prisma format`)
- Schema validity (`prisma validate` runs in CI)

### Do NOT review (auto-generated)
- `prisma/client/**`
- `node_modules/**`
- Lock files (`pnpm-lock.yaml`)

## Required Patterns

| Pattern | Required form |
|---|---|
| Primary key | `Int @id @default(autoincrement())` (never UUID) |
| Soft delete | `isActive Boolean @default(true)` on every model |
| Timestamps | `createdAt DateTime @default(now())` and `updatedAt DateTime @updatedAt` |
| Bilingual fields | `name` plus `nameAr` for any user-facing label field |
| Relations | always explicit: `@relation(fields: [...], references: [id])` |
| Enums | declared in schema, `UPPER_SNAKE_CASE` values |
| Indexes | `@@index` on every foreign-key field plus other frequently queried fields |
| Migrations | every schema edit ships with a corresponding migration in `prisma/migrations/` |

## Flag as CRITICAL

- Any model missing `isActive`
- Any model missing `createdAt` or `updatedAt`
- UUID as primary key
- Hard delete patterns in any consumer service code referencing this schema
- Missing `@relation` on foreign keys
- Circular relations without explicit naming (causes Prisma build failure)
- Schema changes without a corresponding migration file

## Flag as IMPORTANT

- Missing `@@index` on foreign-key fields (full-table-scan joins at scale)
- Nullable fields that could have defaults instead
- Missing bilingual (`name`/`nameAr`) on user-facing models
- Enum values not in `UPPER_SNAKE_CASE`
- Undocumented nullable: a nullable field without a comment explaining the semantics

## Architecture Facts

- This is a standalone schema repo shared across tenant backends. A schema change here is a breaking change to every consumer. Migrations must be backward-compatible or coordinated with all consumers.
- The schema is the contract between the centralized Prisma package and the NestJS backend. Removing a field or renaming a column without a migration plus a consumer update causes runtime failures.
- `multiSchema` preview feature may be active on some tenants (e.g. IDP uses `idp` and `idp_views`). Models in read-only view schemas must be annotated `@@schema("idp_views")` and must not receive write operations.
- `@@index` on foreign keys is not automatic in Prisma. Omitting it creates full-table-scan joins at scale.

## Style

- Field names: camelCase
- Model names: PascalCase, singular
- Enum names: PascalCase, values UPPER_SNAKE_CASE
- Index names: `idx_<table>_<columns>`
- Unique constraint names: `uq_<table>_<columns>`
- **No em-dashes** in markdown, code comments, or commit messages. Use commas, periods, colons, parentheses.
