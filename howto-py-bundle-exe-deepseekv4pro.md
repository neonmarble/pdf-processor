# How to Bundle a Python Script as a Standalone `.exe` on Windows

## Prerequisites

Install **uv** (no system Python required):

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Or via winget:

```powershell
winget install uv
```

> uv manages Python versions, dependencies, and virtual environments automatically.

---

## Setup Options

Choose one of the following approaches. **Option A (inline script metadata)** is recommended for single scripts; **Option B (pyproject.toml)** is better for multi-file projects.

### Option A: Inline Script Metadata (Recommended for Single Scripts)

Add PEP 723 dependencies directly to your script:

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

### Option B: Project-Based Setup (Recommended for Multi-File Projects)

```powershell
# Clone or create the project directory
git clone <repo-url>
cd pdf-processor

# Sync dependencies declared in pyproject.toml into a local .venv
uv sync
```

`uv sync` reads `pyproject.toml`, creates a `.venv/`, and installs all declared packages. The project structure after setup:

```
pdf-processor/
├── .venv/                  # uv-managed virtual environment (auto-created)
│   └── lib/python*/site-packages/pymupdf/
├── pyproject.toml          # Declares dependencies and entry points
├── pymupdf-compress.py     # The script
└── gs-compress.py          # Ghostscript variant (optional)
```

### Option C: Ad-hoc (No Script Modification)

```powershell
uv tool run --with pyinstaller --with pymupdf pyinstaller --onefile --name pymupdf-compress pymupdf-compress.py
```

Specifies dependencies on the command line without touching the script file.

---

## Verify the Script Runs

Before bundling, confirm the script works:

```powershell
# Standard usage
uv run pymupdf-compress.py

# Custom output directory
uv run pymupdf-compress.py -o my-output

# Aggressive compression mode
uv run pymupdf-compress.py -m aggressive

# Dry run (preview only)
uv run pymupdf-compress.py --dry-run
```

> If `pyproject.toml` defines a `[project.scripts]` entry point, you can omit the `.py` extension:
>
> ```toml
> [project.scripts]
> pymupdf-compress = "pymupdf_compress:main"
> ```
>
> Then: `uv run pymupdf-compress -o my-output`

---

## Build the Standalone Executable

`uv tool run` creates an ephemeral environment that is **isolated from your project** — the script's dependencies must be included via `--with` so PyInstaller can discover them during import analysis.

### Using `uv tool run` (Ephemeral — No Global Install)

```powershell
uv tool run --with pyinstaller --with pymupdf pyinstaller --onefile --name pymupdf-compress pymupdf-compress.py
```

`uvx` is a shorthand alias for `uv tool run`:

```powershell
uvx --with pyinstaller --with pymupdf pyinstaller --onefile --name pymupdf-compress pymupdf-compress.py
```

**What happens:**
- PyInstaller runs in a temporary isolated environment
- `--with pymupdf` makes your script's dependencies available to PyInstaller's import analysis
- No manual venv creation or activation needed
- PyInstaller is downloaded and cleaned up automatically
- Dependencies are cached globally, so repeated builds are fast

### Alternative: Build via `uv run` (Project-Aware)

If you are using **Option B** (project with `pyproject.toml` and `uv sync`), `uv run` respects the project's `.venv` and you don't need to list script dependencies again:

```powershell
uv run --with pyinstaller pyinstaller --onefile --name pymupdf-compress pymupdf-compress.py
```

### Output

The executable is placed at:

```
dist\pymupdf-compress.exe
```

Verify the build:

```powershell
dist\pymupdf-compress.exe --help
```

---

## PyInstaller Flags

| Flag | Purpose |
|------|---------|
| `--onefile` / `-F` | Bundles everything into a single `.exe` (easier distribution, slower startup) |
| `--onedir` / `-D` | One-folder bundle (default; faster startup, more files to distribute) |
| `--name` | Sets the output filename (without extension) |
| `--console` | Keeps terminal window (default, required for CLI scripts) |
| `--windowed` / `-w` | Suppresses terminal window (GUI applications only) |
| `--hidden-import` | Include modules PyInstaller cannot auto-detect |
| `--collect-all` | Include all package data and binaries (use when imports fail at runtime) |
| `--add-data` | Include extra non-Python files (format: `src;dest` on Windows) |

---

## Troubleshooting

### PyInstaller cannot find a package

Use `--hidden-import` for packages that import dynamically:

```powershell
uv tool run --with pyinstaller --with pymupdf pyinstaller --onefile --name pymupdf-compress --hidden-import pymupdf pymupdf-compress.py
```

### Missing binary or data files at runtime

Force PyInstaller to collect all package data:

```powershell
uv tool run --with pyinstaller --with pymupdf pyinstaller --onefile --name pymupdf-compress --collect-all pymupdf pymupdf-compress.py
```

### Clean rebuild

Delete build artifacts and rebuild from scratch:

```powershell
Remove-Item -Recurse -Force build, dist, pymupdf-compress.spec
uv tool run --with pyinstaller --with pymupdf pyinstaller --onefile --name pymupdf-compress pymupdf-compress.py
```

### Use a specific Python version

```powershell
uv tool run --with pyinstaller --with pymupdf --python 3.12 pyinstaller --onefile --name pymupdf-compress pymupdf-compress.py
```

### Pin PyInstaller to a version range

```powershell
uv tool run --with 'pyinstaller>=6.0' --with pymupdf pyinstaller --onefile --name pymupdf-compress pymupdf-compress.py
```

### `uv: command not found`

Install uv: `winget install uv` or rerun the install script.

### `pymupdf-compress: command not found`

Run `uv run` commands from the directory containing `pyproject.toml`, or use the script filename with `.py` extension.

### Ghostscript not found

Install Ghostscript from https://ghostscript.com and ensure `gswin64c` is on your `PATH`, or use `-g gs` on Linux.

---

## Optional: Build Script

Save as `build.bat` for one-command builds:

```bat
@echo off
uv tool run --with pyinstaller --with pymupdf pyinstaller --onefile --name pymupdf-compress pymupdf-compress.py
echo.
echo Build complete: dist\pymupdf-compress.exe
pause
```

---

## Cleaning Up

```powershell
# Remove virtual environment (project-based setups)
Remove-Item -Recurse -Force .venv

# Remove build artifacts
Remove-Item -Recurse -Force build, dist, *.spec

# Remove generated output
Remove-Item -Recurse -Force compressed
```

---

## Key uv Commands

| Command | Purpose |
|---------|---------|
| `uv run script.py` | Run script with auto-managed dependencies |
| `uv run --with pkg script.py` | Run script with a temporary dependency |
| `uv add --script script.py pkg` | Add dependency to script's inline metadata |
| `uv sync` | Install all dependencies declared in `pyproject.toml` |
| `uv tool run --with pkg tool ...` | Run a tool in an ephemeral isolated environment |
| `uv tool install tool` | Install a tool globally for repeated use |
| `uv python install 3.12` | Install a specific Python version |

---

## Notes

- **No system Python required**: uv fetches the right Python version automatically.
- **No manual venv management**: uv creates and manages environments under the hood.
- **Ephemeral isolation**: `uv tool run` creates a clean temp environment — script dependencies must be passed via `--with` for PyInstaller to find them.
- **Project-aware alternative**: Use `uv run --with pyinstaller pyinstaller ...` from within a project to inherit `.venv` dependencies automatically.
- **Self-contained exe**: The resulting `.exe` requires no Python or pip on target machines.
- **First-run overhead**: `--onefile` executables extract to `%TEMP%` on first launch; subsequent launches are faster.
- **Binary size**: Packages with C extensions (e.g., PyMuPDF) produce larger binaries (~50–100 MB).
- **Cross-platform scope**: Build on Windows for Windows; build on Linux for Linux.
- **Dependencies are globally cached**: Repeated builds are fast after the first run.
- **Ephemeral tools**: `uv tool run` downloads and cleans up tools automatically; no pollution.

---

## Why uv Over Traditional Workflows

| Traditional | uv Approach |
|-------------|-------------|
| `python -m venv .venv` | Automatic environment management |
| `.venv\Scripts\activate` | No activation needed |
| `pip install pyinstaller pymupdf` | `uv tool run --with pyinstaller` or `uv sync` |
| Manual dependency management | Locked, reproducible environments |
| Manual cleanup | Ephemeral environments auto-clean |
