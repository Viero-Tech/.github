---
applyTo: "**"
excludeAgent: "coding-agent"
---
# Code Review Standards

## Behavior
- Only flag issues you are certain about. When in doubt, stay silent.
- Prefer fewer, higher-quality comments over comprehensive coverage.
- Format: problem (1 line), why it matters (1 line), suggested fix (code snippet).
- Severity: CRITICAL (blocks merge) | IMPORTANT (discuss) | SUGGESTION (optional).
- Only comment on code changed or directly affected by this PR. Do not flag pre-existing issues.

## Priority Areas
- Security: injection, hardcoded secrets, missing auth, eval(), raw SQL
- Correctness: logic errors, null/undefined, race conditions, resource leaks
- Architecture: pattern violations, missing error handling, broken contracts

## Do NOT Flag (CI Handles These)
- Formatting, import order, unused variables (ESLint/ruff/dart analyze)
- Type errors (TypeScript compiler / Dart analyzer)
- Test failures (Jest/pytest/flutter test)

## Do NOT Review (Auto-Generated)
- app/api-client/**, generated/**, *.generated.ts, prisma/client/**
- Lock files (pnpm-lock.yaml, package-lock.json, pubspec.lock)
- .env.example, Dockerfile (unless security-relevant)

## Project-Wide Conventions
- IDs: always autoincrement integers, never UUID
- Deletion: always soft delete (isActive = false), never hard delete
- Package manager: pnpm for Node.js repos. Flag npm/yarn as CRITICAL.
- Booleans: prefix with is/has/can/should
- Functions: verb + noun (createOrder, validateInput)
- Max 3 parameters per function. Use object/DTO if more.
- Early returns over deep nesting
