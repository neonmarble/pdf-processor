# How to Bundle a Python Script as a Standalone `.exe` on Windows

## Prerequisites

- **uv** installed: `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`

> uv manages Python versions, dependencies, and virtual environments automatically — no manual Python or venv setup required.

---

## Quick Start (Recommended)

### Build the Executable

```powershell
uv tool run --with pyinstaller pyinstaller --onefile --name pymupdf-compress pymupdf-compress.py
```

**What this does:**
- Runs PyInstaller in an ephemeral (temporary) isolated environment
- No manual venv creation or activation needed
- PyInstaller is downloaded and cleaned up automatically
- Your script's dependencies are handled separately (see below)

### Verify the Build

```powershell
dist\pymupdf-compress.exe --help
```

The executable will be at: `dist\pymupdf-compress.exe`

---

## Complete Workflow

### Option 1: Script with Inline Metadata (Best Practice)

Add PEP 723 inline dependency metadata to your script:

```powershell
uv add --script pymupdf-compress.py pymupdf
```

This adds a block at the top of your script:

```python
# /// script
# dependencies = [
#   "pymupdf",
# ]
# ///
```

Then build:

```powershell
uv tool run --with pyinstaller pyinstaller --onefile --name pymupdf-compress pymupdf-compress.py
```

**Benefits:**
- Dependencies are declared in the script itself
- `uv run pymupdf-compress.py` works anywhere with automatic dependency resolution
- Reproducible across machines

### Option 2: Ad-hoc Dependencies

If you don't want to modify the script:

```powershell
uv tool run --with pyinstaller --with pymupdf pyinstaller --onefile --name pymupdf-compress pymupdf-compress.py
```

Or use the `--with` flag at runtime:

```powershell
uv run --with pymupdf pymupdf-compress.py --help
```

### Option 3: Project-Based Workflow

For larger projects with multiple scripts:

```powershell
# Initialize a project
uv init pdf-processor
cd pdf-processor

# Add dependencies
uv add pymupdf

# Build the executable
uv tool run --with pyinstaller pyinstaller --onefile --name pymupdf-compress pymupdf-compress.py
```

---

## Key uv Commands

| Command | Purpose |
|---------|---------|
| `uv run script.py` | Run script with auto-managed dependencies |
| `uv run --with pkg script.py` | Run script with temporary dependency |
| `uv add --script script.py pkg` | Add dependency to script's inline metadata |
| `uv tool run pyinstaller ...` | Run PyInstaller in ephemeral environment |
| `uv tool run --with pyinstaller pyinstaller ...` | Run PyInstaller without installing it globally |
| `uv tool install pyinstaller` | Install PyInstaller globally for repeated use |
| `uv python install 3.12` | Install a specific Python version |

---

## PyInstaller Flags

| Flag | Purpose |
|------|---------|
| `--onefile` | Bundles everything into a single `.exe` |
| `--name` | Sets output filename (without extension) |
| `--console` | Keeps terminal window (default, for CLI output) |
| `--hidden-import` | Include modules PyInstaller can't detect |
| `--collect-all` | Include all package data/files |

---

## Troubleshooting

### PyInstaller can't find the package

```powershell
uv tool run --with pyinstaller pyinstaller --onefile --name pymupdf-compress --hidden-import pymupdf pymupdf-compress.py
```

### Missing binary/data files at runtime

```powershell
uv tool run --with pyinstaller pyinstaller --onefile --name pymupdf-compress --collect-all pymupdf pymupdf-compress.py
```

### Clean rebuild

```powershell
Remove-Item -Recurse -Force build, dist, pymupdf-compress.spec
uv tool run --with pyinstaller pyinstaller --onefile --name pymupdf-compress pymupdf-compress.py
```

### Use a specific Python version

```powershell
uv tool run --with pyinstaller --python 3.12 pyinstaller --onefile --name pymupdf-compress pymupdf-compress.py
```

### Pin PyInstaller version

```powershell
uv tool run --with 'pyinstaller>=6.0' pyinstaller --onefile --name pymupdf-compress pymupdf-compress.py
```

---

## Optional: Reusable Build Script

Save as `build.bat` for one-command builds:

```bat
@echo off
uv tool run --with pyinstaller pyinstaller --onefile --name pymupdf-compress pymupdf-compress.py
echo.
echo Build complete: dist\pymupdf-compress.exe
pause
```

---

## Notes

- **No manual venv management**: uv creates isolated environments automatically
- **Ephemeral tool environments**: `uv tool run` downloads and cleans up tools automatically
- **Global cache**: Dependencies are cached globally, so repeated builds are fast
- **Self-contained exe**: The resulting `.exe` requires no Python or pip on target machines
- **First run overhead**: PyInstaller extracts to `%TEMP%` on first run; subsequent runs are faster
- **Binary size**: Packages with C extensions (like PyMuPDF) produce larger binaries (~50-100 MB)
- **Cross-platform**: Build on Windows for Windows; build on Linux for Linux

---

## Why uv Over Traditional Workflows?

| Traditional | uv Approach |
|-------------|-------------|
| `python -m venv .venv` | Automatic environment management |
| `.venv\Scripts\activate` | No activation needed |
| `pip install pyinstaller pymupdf` | `uv tool run --with pyinstaller` |
| `pyinstaller ...` | Same command, better isolation |
| Manual cleanup | Ephemeral environments auto-clean |
| Version conflicts | Locked, reproducible environments |
