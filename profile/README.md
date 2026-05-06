## Viero Tech

Logistics and fintech platform powering fuel delivery, fleet management, and driver operations across the Middle East.

### Products
- **Fuel Logistics** -- Multi-tenant fuel delivery platform (admin dashboards, driver apps, route optimization)
- **Fleet Cards** -- Fleet fuel card management system
- **Identity Platform** -- Centralized authentication and tenant administration
- **AI Services** -- Route optimization, auto-dispatching, and ETA prediction
- **Shuttle** -- Employee shuttle management

### Tech Stack
NestJS, Next.js, Flutter, FastAPI, PostgreSQL, Prisma, GKE, ArgoCD

### Org-wide CI

Reusable workflows in this repo (consumed via `uses: Viero-Tech/.github/.github/workflows/<name>@main`):

- `reusable-ci-nestjs.yml`, `reusable-ci-nextjs.yml`, `reusable-ci-prisma.yml`, `reusable-ci-flutter.yml`, `reusable-ci-python.yml`, `reusable-ci-generic.yml`: stack-specific lint, typecheck, test
- `reusable-claude-review.yml`: auto-review every PR (opened, synchronize, reopened, ready-for-review). Sticky comment, draft skip, concurrency cancel
- `reusable-claude-mention.yml`: respond to `@claude` mentions in PR comments, reviews, and issues

Per-repo caller stubs live in `per-repo-workflows/`. Drop a stub into a repo's `.github/workflows/` to opt in.

[getviero.com](https://getviero.com)
