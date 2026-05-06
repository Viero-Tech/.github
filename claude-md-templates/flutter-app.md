# Flutter App: Project Context

> Loaded automatically by Claude Code (including the GitHub reviewer action).
> This file is the source of truth for code-review behavior on this repo.

## Stack

- **Flutter 3.x / Dart 3.x**
- **State management:** BLoC (or Cubit for simple state)
- **HTTP:** Dio with interceptors for auth token injection and refresh
- **Models:** freezed + json_serializable (immutable data classes)
- **DI:** get_it service locator
- **Secure storage:** flutter_secure_storage (never SharedPreferences for tokens)

## Layout

```
lib/
├── core/
│   ├── di/                # get_it registration
│   ├── network/           # Dio + interceptors
│   └── storage/           # flutter_secure_storage wrappers
├── features/<feature>/
│   ├── bloc/ or cubit/
│   ├── models/            # freezed + json_serializable
│   ├── repository/
│   └── view/              # screens + widgets
└── l10n/                  # ARB files
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
- Formatting (`dart format`)
- Static analysis (`dart analyze`)
- Test failures (`flutter test`)

### Do NOT review (auto-generated)
- `*.g.dart` (json_serializable)
- `*.freezed.dart` (freezed)
- `pubspec.lock`
- `build/**`
- `ios/Pods/**`, `android/.gradle/**`

## Required Patterns

| Pattern | Required form |
|---|---|
| State | BLoC for non-trivial state, Cubit for simple, never plain `setState` for business state |
| Navigation | GoRouter or Navigator 2.0 (not deprecated `Navigator.push` with anonymous routes) |
| HTTP | Dio with auth interceptor; never add raw `Authorization` headers per call |
| Models | freezed + json_serializable (never hand-write `copyWith` or `fromJson`) |
| DI | get_it (services registered at startup; never construct in widget build) |
| Sensitive storage | flutter_secure_storage for tokens and secrets |
| Lifecycle | every controller, stream, animation has matching `dispose()` |
| Localization | l10n; no hardcoded user-facing strings |
| Network | every call has explicit timeout and retry/error handling |

## Flag as CRITICAL

- Hardcoded API URLs or secrets in Dart code
- Storing tokens or sensitive data in SharedPreferences (must use flutter_secure_storage)
- Forced null assertion (`!`) without a guard
- Platform channel calls without `try/catch`
- Secrets or API keys in any `.dart` file or `assets/`

## Flag as IMPORTANT

- Widgets over 100 lines (suggest extraction)
- `setState` in screens where BLoC exists (suggest routing through Cubit)
- Missing `dispose()` on controllers, streams, or animation controllers
- Network calls without timeout or retry
- Hardcoded user-facing strings not in l10n

## Architecture Facts

- get_it is the service locator. Services registered once at startup, retrieved by type. Never construct a service inside a widget build method.
- Dio interceptors handle token injection and automatic refresh. Adding raw `Authorization` headers in individual calls bypasses the interceptor and breaks token refresh.
- freezed classes are immutable. The generated `*.freezed.dart` and `*.g.dart` files must not be edited manually.
- BLoC events and states must be immutable. Mutating state objects in place is a silent defect; the `StreamController` will not emit and the UI will not rebuild.
- `flutter_secure_storage` uses Keychain on iOS and EncryptedSharedPreferences on Android. SharedPreferences is plaintext on Android.

## Style

- Widgets max ~100 lines (extract if larger)
- One widget per file for top-level widgets
- Booleans prefixed `is`, `has`, `can`, `should`
- Snake_case file names: `order_card.dart`, not `OrderCard.dart`
- **No em-dashes** in markdown, code comments, or commit messages. Use commas, periods, colons, parentheses.
