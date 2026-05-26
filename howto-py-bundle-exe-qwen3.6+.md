# How to Bundle a Python Script as a Standalone `.exe` on Windows

## Prerequisites

- **Python 3.9+** installed
- **uv** installed: `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`

---

## Step-by-Step

### 1. Create a Virtual Environment

```powershell
uv venv .venv
```

### 2. Activate the Environment

```powershell
.venv\Scripts\activate
```

### 3. Install Dependencies

```powershell
uv pip install <your-package> pyinstaller
```

Replace `<your-package>` with the script's dependency (e.g. `pymupdf`).

### 4. Build the Executable

```powershell
pyinstaller --onefile --name <script-name> <script-name>.py
```

**Key flags:**
| Flag | Purpose |
|------|---------|
| `--onefile` | Bundles everything into a single `.exe` |
| `--name` | Sets output filename (without extension) |
| `--console` | Keeps terminal window (default, for CLI output) |

### 5. Verify the Build

```powershell
dist\<script-name>.exe --help
```

The executable will be at: `dist\<script-name>.exe`

---

## Troubleshooting

### PyInstaller can't find the package

Add hidden import:
```powershell
pyinstaller --onefile --name <script-name> --hidden-import <your-package> <script-name>.py
```

### Missing binary/data files

If runtime errors occur about missing `.so`/`.dll` files:
```powershell
pyinstaller --onefile --name <script-name> --collect-all <your-package> <script-name>.py
```

### Clean rebuild

```powershell
Remove-Item -Recurse -Force build, dist, <script-name>.spec
pyinstaller --onefile --name <script-name> <script-name>.py
```

---

## Optional: Reusable Build Script

Save as `build.bat` for one-command builds:

```bat
@echo off
call .venv\Scripts\activate.bat
uv pip install <your-package> pyinstaller
pyinstaller --onefile --name <script-name> <script-name>.py
echo.
echo Build complete: dist\<script-name>.exe
pause
```

---

## Notes

- The resulting `.exe` is self-contained — no Python or pip required on target machines
- First run may be slow as PyInstaller extracts to `%TEMP%`; subsequent runs are faster
- File size depends on dependencies; packages with C extensions (like PyMuPDF) produce larger binaries (~50-100 MB)
