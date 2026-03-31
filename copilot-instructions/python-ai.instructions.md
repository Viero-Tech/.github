---
applyTo: "**/*.py"
excludeAgent: "coding-agent"
---
# Viero AI Service

## Stack
Python 3.10+, FastAPI, Pydantic 2, OR-Tools

## Patterns
- API: FastAPI with Pydantic models for request/response validation
- Async: use async endpoints for I/O-bound operations
- Config: Pydantic BaseSettings for environment configuration (all env vars validated at startup)
- Logging: Python logging module, structured JSON format

## Flag as CRITICAL
- SQL injection (raw queries without parameterization)
- eval() or exec() with any input
- Hardcoded secrets or API keys
- Missing input validation on endpoints
- Pickle deserialization of untrusted data

## Flag as IMPORTANT
- Missing type hints on function signatures
- Sync I/O in async context (blocking the event loop)
- Missing error handling on external API calls
- Missing rate limiting on public endpoints
- Environment variables accessed without Pydantic BaseSettings validation
