# Contributing to Rooted and Rising

## Branch strategy

```
main          ← stable, production-ready code only
develop       ← integration branch; all features merge here first
phase/1-scaffold
phase/2-journal-agent
phase/3-library-agent
phase/4-analyser-planner
phase/5-nudge-agent
phase/6-web-dashboard
phase/7-report-agent
phase/8-polish
```

Each build phase lives on its own `phase/N-name` branch. When a phase is complete and tested, it is merged into `develop` via a Pull Request. `main` is only updated when `develop` is stable and all tests pass.

## Commit message format

```
<type>(<scope>): <short description>

Types: feat | fix | refactor | test | docs | chore | style
Scope: journal | library | analyser | planner | nudge | report | api | models | config

Examples:
feat(journal): add image upload support to JournalAgent
fix(analyser): correct rolling window calculation for domain coverage
test(library): add unit tests for LibraryAgent upsert logic
docs(prd): update API surface with new library endpoints
```

## Pull request checklist

- [ ] Branch is up to date with `develop`
- [ ] All tests pass (`uv run pytest`)
- [ ] No linting errors (`uv run ruff check .`)
- [ ] Type checks pass (`uv run mypy backend/`)
- [ ] New code has unit tests
- [ ] PR description explains what changed and why

## Local development setup

```bash
git clone https://github.com/YOUR_USERNAME/rooted-and-rising.git
cd rooted-and-rising
uv sync --extra dev
cp .env.example .env   # fill in your keys
uv run uvicorn backend.main:app --reload
```

## Running tests

```bash
uv run pytest                        # all tests
uv run pytest tests/unit/            # unit tests only
uv run pytest tests/unit/test_journal_agent.py  # single file
uv run pytest -v --tb=short          # verbose with short tracebacks
```
