#!/usr/bin/env bash
# Generates the file lib/greeting.dart imports, so lint and test pass only
# when ci-flutter runs setup-script before flutter pub get.
set -euo pipefail
if [ -n "${API_SPEC_FILE:-}" ]; then
  echo "::error::API_SPEC_FILE is set although no api-spec-repository was passed"
  exit 1
fi
printf "const greetingWord = 'Hello';\n" > lib/generated.dart
