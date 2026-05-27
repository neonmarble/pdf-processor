# How to Run `pymupdf-compress.py` on Windows with `uv`

## Overview

This project uses [`uv`](https://github.com/astral-sh/uv) — a fast Python package manager — to manage dependencies and run scripts. The setup below lets you run `pymupdf-compress.py` on Windows (and Linux/macOS) without manually installing Python or PyMuPDF.

---

## Prerequisites

| Requirement | Install |
|-------------|---------|
| `uv` | `winget install uv` or `powershell -c "irm https://astral.sh/uv/install.ps1 \| iex"` |
| Python | Built-in via `uv` (no system Python needed) |
| Ghostscript (optional, for `gs-compress.py`) | [https://ghostscript.com](https://ghostscript.com) |

> uv manages Python versions, dependencies, and virtual environments automatically.

---

## Setup Options

Choose one of the following approaches. **Option A** is recommended for this project; **Option B** is useful for quick ad-hoc changes.

### Option A: Project-Based Setup (Recommended)

```powershell
# Clone the repo
git clone <repo-url>
cd pdf-processor

# Sync dependencies declared in pyproject.toml into a local .venv
uv sync
```

`uv sync` reads `pyproject.toml`, creates a `.venv/`, and installs all declared packages. No global Python pollution.

### Option B: Inline Script Metadata (PEP 723)

For single scripts without a `pyproject.toml`, add dependencies directly to the script:

```powershell
uv add --script pymupdf-compress.py pymupdf
```

This inserts a metadata block at the top of the script:

```python
# /// script
# dependencies = [
#   "pymupdf",
# ]
# ///
```

Now the script is self-contained — `uv run pymupdf-compress.py` resolves dependencies automatically on any machine.

### Option C: Ad-hoc (Temporary Dependency)

Pass dependencies on the command line without modifying anything:

```powershell
uv run --with pymupdf pymupdf-compress.py --help
```

`--with` adds a temporary dependency for that single run. Nothing is installed persistently.

---

## Running the Script

### Using the Entry Point (Option A)

If `pyproject.toml` defines a `[project.scripts]` entry point, you can omit the `.py` extension:

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

### Using the Script Filename (Options B and C)

```powershell
# Runs pymupdf-compress.py with inline metadata (Option B)
uv run pymupdf-compress.py --help

# Runs with a temporary dependency (Option C)
uv run --with pymupdf pymupdf-compress.py --help
```

---

## What `uv run` Does

1. **Detects `pyproject.toml`** in the current directory (or inline metadata in the script).
2. **Finds or creates a `.venv`** with the declared Python interpreter and dependencies.
3. **Runs the script** with that `.venv`'s environment active.

No `pip install`, no activating venvs, no system Python pollution.

> **`uv run` vs. `uv tool run`:** `uv run` is project-aware — it reads your `pyproject.toml` and `.venv`. `uv tool run` (aliased as `uvx`) is ephemeral — it downloads a tool in a temporary environment and cleans up after. Use `uv run` for your own scripts; use `uv tool run` for external tools like PyInstaller.

---

## Python Version Management

uv can install and manage Python versions for you:

```powershell
# Install a specific Python version
uv python install 3.12

# Use a specific version for a run
uv run --python 3.12 pymupdf-compress.py

# Pin a version in pyproject.toml
# Add this under [project]:
# requires-python = ">=3.9"
```

If no system Python is available, uv fetches the latest compatible version automatically.

---

## Project Structure After Setup

```
pdf-processor/
├── .venv/                  # uv-managed virtual environment (auto-created)
│   └── lib/python*/site-packages/
│       └── pymupdf/        # Installed automatically by uv sync
├── pyproject.toml          # Declares dependencies + entry points
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

The entry point is defined in `pyproject.toml`:

```toml
[project.scripts]
pymupdf-compress = "pymupdf_compress:main"
```

---

## Key uv Commands

| Command | Purpose |
|---------|---------|
| `uv run script.py` | Run a script with auto-managed dependencies |
| `uv run --with pkg script.py` | Run a script with a temporary dependency |
| `uv run --python 3.12 script.py` | Run with a specific Python version |
| `uv add --script script.py pkg` | Add dependency to script's inline metadata (PEP 723) |
| `uv sync` | Install all dependencies declared in `pyproject.toml` |
| `uv python install 3.12` | Install a specific Python version |
| `uv tool run --with pkg tool ...` | Run a tool in an ephemeral isolated environment |
| `uvx` | Shorthand alias for `uv tool run` |

---

## Uninstalling / Cleaning Up

```powershell
# Remove the virtual environment
Remove-Item -Recurse -Force .venv

# Remove generated output
Remove-Item -Recurse -Force compressed

# Remove inline metadata from a script
# Delete the # /// script ... # /// block from the top of the file
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `uv: command not found` | Install uv: `winget install uv` or rerun the install script |
| `pymupdf-compress: command not found` | Run from the directory containing `pyproject.toml`, or use the `.py` filename |
| `FileNotFoundError: Ghostscript` | Install Ghostscript and ensure `gswin64c` is on PATH, or use `-g gs` on Linux |
| Dependency not found during run | Pass it explicitly: `uv run --with <package> pymupdf-compress.py` |
| Wrong Python version | Use `uv python install 3.12` then `uv run --python 3.12 pymupdf-compress.py` |
| Stale `.venv` after adding dependencies | Run `uv sync` to recreate the environment from `pyproject.toml` |
| `uv run` installs unexpected version | Check `[project] requires-python` in `pyproject.toml` to constrain versions |

---

## Key Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | Declares dependencies, Python version constraints, and entry points |
| `.venv/` | uv-managed virtual environment (auto-created, auto-ignored) |
| `pymupdf-compress.py` | Main script — no shebang change needed; `uv run` handles Python resolution |
| `.gitignore` | Already ignores `.venv/`, `build/`, `dist/`, and `__pycache__/` |

---

## Why uv Over Traditional Workflows?

| Traditional | uv Approach |
|-------------|-------------|
| `python -m venv .venv` | Automatic environment management |
| `.venv\Scripts\activate` | No activation needed |
| `pip install pymupdf` | `uv sync` or `uv run --with pymupdf` |
| `python script.py` | `uv run pymupdf-compress` |
| Manual Python install | `uv python install 3.12` |
| Version conflicts across projects | Each project gets its own `.venv` automatically |
