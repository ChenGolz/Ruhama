# Kibbutz Face Archive (Local YouTube-Friendly Version)

This patch updates the original local project so it is easier to use for a YouTube-heavy workflow.

## What changed

- Better wording for **paste a YouTube link and process**
- Each detected face can show a **direct link back to the original YouTube video at that timestamp**
- Adds simple launch scripts:
  - `run_local.command` for macOS/Linux
  - `run_local.bat` for Windows

## Important boundary

This remains a **human-review archive tool**:
- detects faces
- groups anonymous appearances
- lets people manually review

It does **not** automatically identify real people.

## How timestamp links work

When the source was a YouTube URL, each appearance gets a link like:

```text
https://www.youtube.com/watch?v=VIDEO_ID&t=75s
```

So reviewers can click directly to the moment the person appeared.

## Files in this patch

Replace or add these files in your original repo:

- `app/models.py`
- `app/main.py`
- `app/templates/index.html`
- `app/templates/project.html`
- `README.md`
- `run_local.command`
- `run_local.bat`

## Fastest way to run locally

### macOS / Linux
```bash
chmod +x run_local.command
./run_local.command
```

### Windows
Double-click:

```text
run_local.bat
```

Or from terminal:

```powershell
run_local.bat
```

Then open:

```text
http://127.0.0.1:8000
```

## Manual run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```
