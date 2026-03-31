---
applyTo: "**/*.{ts,tsx,js,jsx}"
excludeAgent: "coding-agent"
---
# Viero Shuttle (Turborepo Monorepo)

## Stack
Turborepo with pnpm workspaces:
- apps/api: NestJS 11 + TypeORM (NOT Prisma)
- apps/web: Next.js 14 + React 18
- apps/mobile: React Native 0.81 + Expo 54

## Note
Transitional repo. Focus on standard code quality:
- Security: no hardcoded secrets, no injection, auth on all endpoints
- Correctness: null checks, error handling, async/await patterns
- TypeScript: no any, proper typing, explicit return types on exports
