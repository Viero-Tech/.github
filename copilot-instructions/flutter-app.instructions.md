---
applyTo: "**/*.dart"
excludeAgent: "coding-agent"
---
# Viero Flutter App

## Stack
Flutter 3.x, Dart, BLoC/Cubit state management

## Patterns
- State management: BLoC pattern with Cubit for simple state
- Navigation: GoRouter or Navigator 2.0
- API: Dio HTTP client with interceptors for auth tokens
- Models: freezed + json_serializable for immutable data classes
- DI: get_it for service locator pattern

## Flag as CRITICAL
- Hardcoded API URLs or secrets in Dart code
- Missing null safety (non-nullable types without checks)
- Platform channel calls without error handling
- Storing sensitive data in SharedPreferences (use flutter_secure_storage)

## Flag as IMPORTANT
- Widgets over 100 lines (suggest extraction)
- setState in complex state scenarios (suggest BLoC)
- Missing dispose() on controllers, streams, animations
- Network calls without timeout or retry logic
- Missing localization (hardcoded user-facing strings)
