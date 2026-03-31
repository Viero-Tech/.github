---
applyTo: "**/*.{ts,tsx}"
excludeAgent: "coding-agent"
---
# Viero Next.js Frontend

## Stack
Next.js 16, React 19, HeroUI, Tailwind CSS 4, Formik + Yup, next-intl, TypeScript

## Patterns
- UI: HeroUI components (Table, Button, Input, Chip, Dropdown, Pagination, Modal)
- i18n: next-intl with useTranslations(""), messages at messages/{en,ar}.json
- API: auto-generated OpenAPI client at app/api-client/ (do NOT review generated files)
- Forms: Formik + Yup validation schemas
- Notifications: useNotification() with showAsyncNotification()
- Routing: useLocalePath() for locale-aware navigation
- Permissions: protectPerm() for UI permission checks
- Drawers: useDrawer() for detail panels
- Smart/dumb split: containers fetch data, presentational components render

## Flag as CRITICAL
- dangerouslySetInnerHTML without sanitization
- Hardcoded API URLs (must use environment variables)
- Missing key prop on list renders
- Direct DOM manipulation instead of React state

## Flag as IMPORTANT
- Components over 150 lines (suggest extraction)
- Prop drilling more than 2 levels (suggest context or composition)
- Missing error boundaries on async components
- Missing loading states on data fetches
