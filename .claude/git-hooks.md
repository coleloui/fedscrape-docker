# Pre-commit Hooks

Husky + lint-staged, configured at the **repo root** (`package.json`, not
inside `fedscrape-ui/`) so a single hook covers both the Python backend
and the frontend in one commit. Adapted from pineframe's root
`package.json` lint-staged block — same tool, npm instead of pnpm, no
`postinstall` chain since Python deps aren't npm-managed here.

## One-time setup

```sh
npm install   # runs the "prepare": "husky" script, wires up .husky/
```

Python-side hooks (`ruff check --fix`) require `ruff` to be on `PATH` —
i.e. your Python virtualenv with the `dev` extra installed
(`pip install -e ".[dev]"` or the `uv` equivalent) needs to be **active in
the shell you run `git commit` from**. There's no PATH-detection or
graceful-skip built into the hook — if `ruff` isn't found, the commit
fails outright rather than silently skipping the Python check.

## What runs on commit

`.husky/pre-commit` runs `npx lint-staged`, which only touches files that
are actually staged, matched against these globs:

| Glob | Command |
|---|---|
| `fedscrape-ui/src/**/*.{js,jsx,ts,tsx}` | `prettier --write`, then `eslint --fix` |
| `fedscrape-ui/**/*.{json,css,md}` | `prettier --write` |
| `fedscrape-ui/src/**/*.{ts,tsx}` | `tsc -b` (no-emit typecheck — fails the commit on type errors, doesn't modify files) |
| `*.py` (repo root) | `ruff check --fix` |

Prettier/eslint fixes are applied and re-staged automatically before the
commit completes — you'll see the fixed version in the commit, not the
version you originally staged. If `tsc -b` fails, the commit is blocked
entirely (it can't auto-fix a type error).

## Why Pyright isn't wired into the hook

Only `ruff` runs pre-commit for Python, deliberately. Pyright in strict
mode currently reports ~555 findings across the codebase, but the large
majority are cascading "unknown type" noise from `pytest`/`pytest-asyncio`
fixtures that don't ship type stubs — not real bugs. Wiring strict Pyright
into the commit-blocking hook right now would make every commit touching
`tests/` fail on pre-existing noise, not on anything the commit
introduced. Pyright findings are being addressed incrementally when
touching specific files, not in a bulk pass or via the hook. Don't add
Pyright to `lint-staged` without discussing it first — this was a
deliberate scoping decision, not an oversight.

## Skipping the hook

`git commit --no-verify` bypasses it entirely. Reach for this only for a
genuine emergency (e.g. the hook itself is broken) — not as a way to land
a commit with known lint failures. If the hook is wrong or too strict for
a legitimate case, fix the hook/config instead of routinely bypassing it.
