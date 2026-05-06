# Next.js Frontend: Project Context

> Loaded automatically by Claude Code (including the GitHub reviewer action).
> This file is the source of truth for code-review behavior on this repo.

## Stack

- **Next.js 16** + **React 19** + TypeScript (strict)
- **UI:** HeroUI + **Tailwind CSS 4**
- **i18n:** next-intl, bilingual EN/AR with RTL
- **Forms:** Formik + Yup
- **API client:** auto-generated via `openapi-typescript-codegen` from backend Swagger
- **Package manager:** pnpm only

## Layout

```
app/
├── [lang]/
│   └── (dashboard)/<section>/<page>/
│       ├── page.tsx              # wrapped in ClientOnly
│       ├── <entity>-table.tsx
│       ├── create/page.tsx + create-<entity>-form.tsx
│       └── edit/[id]/page.tsx + edit-<entity>-form.tsx
├── api-client/                   # AUTO-GENERATED, never edit
└── components/, hooks/, lib/, providers/
messages/
├── en.json
└── ar.json
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
- `app/api-client/**` (regenerated from Swagger)
- `*.generated.ts`
- Lock files (`pnpm-lock.yaml`)
- `.env.example`, `Dockerfile` unless security-relevant

## Required Patterns

| Pattern | Required form |
|---|---|
| UI primitives | HeroUI components only (`Table`, `Button`, `Input`, `Chip`, `Modal`, `Spinner`) |
| Translations | `useTranslations("")` from next-intl, all strings in `messages/{en,ar}.json` |
| API calls | Auto-generated `<Entity>Service` from `app/api-client/`, never raw fetch for tenant APIs |
| Forms | Formik + Yup validation |
| Notifications | `useNotification()` with `showAsyncNotification()` for all API calls |
| Routing | `useLocalePath()` for locale-aware navigation |
| Permissions | `protectPerm()` for UI permission checks |
| Smart/dumb split | Containers fetch, presentational components render |
| Page wrapping | `page.tsx` wrapped in `ClientOnly` |

## Flag as CRITICAL

- `dangerouslySetInnerHTML` without sanitization
- Hardcoded API URLs (must use environment variables)
- Missing `key` prop on list renders
- Direct DOM manipulation instead of React state
- npm or yarn instead of pnpm
- Edits to `app/api-client/**` (auto-generated, must regenerate from Swagger)

## Flag as IMPORTANT

- Components over 150 lines (suggest extraction)
- Prop drilling more than 2 levels (suggest context or composition)
- Missing error boundaries on async components
- Missing loading states on data fetches
- Hardcoded display strings not in `messages/{en,ar}.json`
- `useLocalePath()` not used for internal navigation (locale prefix would be missing)
- `protectPerm()` missing on privileged UI elements

## Architecture Facts

- The API client at `app/api-client/` is auto-generated from the backend Swagger spec. Editing it manually is wasted work; changes disappear on next regeneration.
- The app is bilingual (Arabic + English) with RTL layout for Arabic. Any user-facing string hardcoded in JSX is a defect.
- `useLocalePath()` wraps Next.js `usePathname`/`useRouter` with the current locale prefix. Raw `router.push('/foo')` strips the prefix and breaks navigation.
- `protectPerm()` is a thin client-side check for UX (hide buttons). Backend enforces real permission. Do not treat it as security.
- Page components wrap in `ClientOnly` because the app uses `[lang]` dynamic segments and some HeroUI components are SSR-incompatible.

## Style

- Components max ~150 lines (extract if larger)
- Max 3 props per component for unrelated values; use an options object otherwise
- Booleans prefixed `is`, `has`, `can`, `should`
- Hooks prefixed `use` and live in `hooks/use-<kebab>.ts`
- **No em-dashes** in markdown, code comments, or commit messages. Use commas, periods, colons, parentheses.
