# Python AI Service: Project Context

> Loaded automatically by Claude Code (including the GitHub reviewer action).
> This file is the source of truth for code-review behavior on this repo.

## Stack

- **Python 3.10+** + **FastAPI** + **Pydantic v2**
- **Async I/O:** `httpx.AsyncClient` for outbound HTTP, never blocking `requests`
- **Algorithms:** OR-Tools (route optimization, constraint satisfaction)
- **Config:** Pydantic `BaseSettings`
- **Logging:** Python `logging` in structured JSON

## Layout

```
app/
├── main.py                  # FastAPI app, startup, middleware
├── config.py                # BaseSettings
├── routers/                 # APIRouter modules per resource
├── services/                # business logic
├── models/                  # Pydantic request/response schemas
├── algorithms/              # OR-Tools wrappers
└── utils/
tests/
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
- Formatting (`ruff format`, `black`)
- Lint (`ruff`, `flake8`)
- Test failures (`pytest`)
- Type errors (mypy or pyright if configured)

### Do NOT review (auto-generated)
- `__pycache__/**`, `*.pyc`
- `.venv/**`, `venv/**`
- Lock files (`poetry.lock`, `requirements.lock`)
- Auto-generated protobuf or OpenAPI files

## Required Patterns

| Pattern | Required form |
|---|---|
| Endpoint validation | Pydantic models on every public endpoint |
| Async I/O | `async def` on every I/O-bound endpoint, `await` outbound HTTP via httpx |
| Config | `BaseSettings` for all env vars, validated at startup |
| Type hints | Required on all function signatures (params and return type) |
| Logging | `logging` module, structured JSON, never `print()` |
| Algorithms | OR-Tools parameters documented with units in comments |
| Error handling | external API calls wrapped in `try/except` with explicit logging and HTTP status mapping |
| Secrets | environment variables only, validated via `BaseSettings` |
| Dependencies | pinned in `requirements.txt` or `pyproject.toml` |

## Flag as CRITICAL

- Raw SQL without parameterization (SQL injection)
- `eval()` or `exec()` with any input
- Hardcoded secrets or API keys
- Missing input validation on any public endpoint (no Pydantic model)
- `pickle.loads()` on untrusted data (arbitrary code execution)
- Sync I/O (`requests.get()`, blocking file reads) inside `async def` endpoints

## Flag as IMPORTANT

- Missing type hints on function signatures
- Sync I/O inside an async context (blocks event loop)
- Missing error handling on external API/service calls
- Missing rate limiting on public endpoints
- Environment variables accessed without `BaseSettings` validation
- `print()` instead of structured logging

## Architecture Facts

- OR-Tools is a constraint satisfaction / vehicle routing solver. Algorithm parameters (fleet size, time windows, capacity) must have explicit units in comments. "max 50" is ambiguous; "max 50 vehicles" is not.
- FastAPI's `async def` endpoints run in the event loop. A single `requests.get()` call inside an `async def` blocks every other request for its duration. Use `httpx.AsyncClient` for async HTTP.
- Pydantic v2 uses `model_validator` and `field_validator` (not v1's `@validator`). Mixed v1/v2 syntax in the same project is a silent correctness risk.
- AI services are stateless compute nodes. No session state, no in-memory caches that persist across requests unless explicitly designed.
- `BaseSettings` reads env vars at class instantiation. Accessing `os.environ.get('X')` directly bypasses startup validation and silently returns `None` in misconfigured environments.

## Style

- Functions max ~30 lines
- Max 4 parameters per function (use a Pydantic model if more)
- Booleans prefixed `is_`, `has_`, `can_`, `should_`
- Snake_case for functions and variables, PascalCase for classes
- **No em-dashes** in markdown, code comments, or commit messages. Use commas, periods, colons, parentheses.
