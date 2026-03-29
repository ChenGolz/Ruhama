# Kibbutz Face Archive (Safe Version)

A free, local-first project for **face detection, anonymous clustering, and human review** from:
- uploaded videos
- uploaded images
- YouTube links

This project **does not automatically identify real people**. Instead, it:
1. detects faces
2. groups likely appearances of the same person as **Person 1 / Person 2 / ...**
3. lets a human review and manually assign names in the browser

That makes it suitable for historical archive work where community members recognize people from footage.

## What it does

- Accepts **video**, **image**, or **YouTube URL**
- Extracts frames from video every N seconds
- Detects faces
- Creates embeddings for each face
- Clusters repeated appearances into anonymous groups
- Generates a simple review UI
- Lets you rename groups manually, for example:
  - `Person 1` → `David`
  - `Person 2` → `Miriam`

## Important boundary

This repo is built for **human-in-the-loop archival review**.
It does **not** try to identify real people automatically.

## Tech stack

- Python 3.10+
- FastAPI
- OpenCV
- face_recognition
- scikit-learn
- yt-dlp
- Jinja2

## Quick start

### 1. Clone
```bash
git clone https://github.com/YOUR-USERNAME/kibbutz-face-archive-safe.git
cd kibbutz-face-archive-safe
```

### 2. Create virtual environment
```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install ffmpeg

You need `ffmpeg` available on your machine.

- Ubuntu/Debian:
```bash
sudo apt update && sudo apt install ffmpeg
```

- macOS (Homebrew):
```bash
brew install ffmpeg
```

- Windows:
Install ffmpeg and add it to PATH.

### 4. Install Python dependencies
```bash
pip install -r requirements.txt
```

## Notes about `face_recognition`

`face_recognition` is convenient, but on some systems it can be harder to install because it depends on `dlib`.

If install fails:
- try Python 3.10 or 3.11
- make sure build tools are installed
- or swap in another embedding backend later

For a first local prototype, this is still one of the simplest choices.

## Run the app

```bash
uvicorn app.main:app --reload
```

Open:
```text
http://127.0.0.1:8000
```

## Project structure

```text
kibbutz-face-archive-safe/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── storage.py
│   ├── youtube.py
│   ├── pipeline.py
│   ├── templates/
│   │   ├── index.html
│   │   └── project.html
│   └── static/
├── data/
├── requirements.txt
└── README.md
```

## Workflow

### Upload image
- detects faces in one image
- clusters all found faces (usually one cluster per person)

### Upload video
- extracts frames every `sample_every_seconds`
- detects faces in each frame
- groups repeated appearances

### Submit YouTube URL
- downloads the video locally with `yt-dlp`
- processes it the same way as uploaded video

## Output

For each project, the app saves:
- `results.json`
- cropped face thumbnails
- extracted frames
- source file
- manual labels

## Results JSON example

```json
{
  "project_id": "abc123",
  "source_type": "video",
  "clusters": [
    {
      "cluster_id": 0,
      "display_name": "Person 1",
      "manual_name": "",
      "count": 12,
      "items": [
        {
          "timestamp_sec": 14.0,
          "frame_path": "frames/frame_000014.jpg",
          "face_path": "faces/face_000021.jpg",
          "bbox": [120, 40, 260, 180]
        }
      ]
    }
  ]
}
```

## Tuning

In `app/config.py` you can change:
- frame sampling rate
- face clustering threshold
- minimum cluster size

## GitHub tips

1. Create a new empty repo on GitHub
2. Copy these files into it
3. Then run:

```bash
git init
git add .
git commit -m "Initial commit: safe face archive MVP"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/kibbutz-face-archive-safe.git
git push -u origin main
```

## Next useful upgrades

- better review UI
- Hebrew interface
- export CSV
- SQLite database
- background job queue
- duplicate video detection
- stronger clustering and merge/split controls
- family/admin access controls

## Safety-minded use case

Good fit:
- archival footage review
- historical video organization
- helping community members recognize people manually
- finding timestamps where the same unknown person appears

Not included:
- automatic identity matching against named people
- surveillance-style search by real identity
