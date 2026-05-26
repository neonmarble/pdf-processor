# Howto: Making `pymupdf-compress.py` Executable on Windows with `uv`

## Overview

This project uses [`uv`](https://github.com/astral-sh/uv) — a fast Python package manager — to manage dependencies and run scripts. The setup below lets you run `pymupdf-compress.py` on Windows (and Linux/macOS) without manually installing Python or PyMuPDF.

---

## Prerequisites

| Requirement | Install |
|-------------|---------|
| Python | Built-in via `uv` (no system Python needed) |
| `uv` | `winget install uv` or `irm https://astral.sh/uv/install.ps1 \| iex` |
| Ghostscript (optional, for `gs-compress.py`) | [https://ghostscript.com](https://ghostscript.com) |

---

## Setup (One-Time)

```powershell
# 1. Clone the repo
git clone <repo-url>
cd pdf-processor

# 2. Create pyproject.toml and sync dependencies
#    - A pyproject.toml will be created declaring pymupdf
#    - uv creates a .venv/ and installs pymupdf into it
uv sync
```

> **Note:** `uv sync` reads `pyproject.toml` and builds a local `.venv` with exactly the dependencies declared. No global Python pollution.

---

## Running the Script

```powershell
# Standard usage (all PDFs in current dir → compressed/)
uv run pymupdf-compress

# Custom output directory
uv run pymupdf-compress -o my-output

# Aggressive compression (subsets fonts, re-compresses images)
uv run pymupdf-compress -m aggressive

# Dry run (preview only)
uv run pymupdf-compress --dry-run

# Combine options
uv run pymupdf-compress -o out -m aggressive -e 50
```

---

## What `uv run` Does

1. **Detects `pyproject.toml`** in the current directory.
2. **Finds or creates a `.venv`** with the declared Python interpreter and dependencies.
3. **Runs the script** (`pymupdf-compress.py`) with that `.venv`'s environment active.

No `pip install`, no activating venvs, no system Python pollution.

---

## Project Structure After Setup

```
pdf-processor/
├── .venv/                  # uv-managed virtual environment (auto-created)
│   └── lib/python*/site-packages/
│       └── pymupdf/        # Installed automatically by uv sync
├── pyproject.toml          # Declares dependencies + entry points (created once)
├── pymupdf-compress.py     # The script
└── gs-compress.py          # Ghostscript variant (separate dependency)
```

---

## Adding the Script as a Command

With `pyproject.toml` configured, `uv sync` also registers `pymupdf-compress` as a **project script**. This means:

```powershell
uv run pymupdf-compress -o out
```

acts exactly like a native executable named `pymupdf-compress`.

---

## Uninstalling / Cleaning Up

```powershell
# Remove the virtual environment
Remove-Item -Recurse -Force .venv

# Remove generated output
Remove-Item -Recurse -Force compressed
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `uv: command not found` | Install `uv` first: `winget install uv` |
| `pymupdf-compress: command not found` | Run inside the repo dir where `pyproject.toml` exists |
| `FileNotFoundError: Ghostscript` | Install Ghostscript and ensure `gswin64c` is on PATH, or use `-g gs` on Linux |

---

## Key Files

- **`pyproject.toml`** — Created once; declares `pymupdf` dependency and the `pymupdf-compress` entry point.
- **`.gitignore`** — Already ignores `.venv/`, `build/`, `dist/`, and `__pycache__/`.
- **`pymupdf-compress.py`** — No shebang change needed; `uv run` handles Python resolution automatically on Windows.
