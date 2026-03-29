# Kibbutz Face Archive — GitHub Pages Version

This is the **GitHub Pages** version of the project.

It runs entirely in the browser and is designed for:
- uploaded images
- uploaded local video files

It does **not** run Python, FastAPI, OpenCV, or server-side YouTube downloading.

## What works on GitHub Pages

- Browser-based face detection
- Drawing face boxes on images and sampled video frames
- Cropping detected face thumbnails
- Downloading results as JSON

## What does not work on GitHub Pages

- Python backend
- OpenCV / server-side processing
- Uploading to a server
- Direct YouTube downloading from a pasted YouTube URL

For YouTube videos, download the video to your computer first, then upload the video file in the page.

## Files to use

Replace or add these files in the root of your repo:

- `index.html`
- `assets/app.js`
- `assets/styles.css`
- `.nojekyll`
- `README.md`

## How to publish on GitHub Pages

1. Push these files to your GitHub repo.
2. In GitHub, open **Settings → Pages**.
3. Under **Build and deployment**, choose:
   - **Source:** Deploy from a branch
   - **Branch:** `main` (or `master`)
   - **Folder:** `/ (root)`
4. Save.
5. Wait a minute or two.
6. GitHub will give you a URL like:

```text
https://YOUR-USERNAME.github.io/YOUR-REPO/
```

## Practical notes

- Processing happens in the browser, so large videos can be slow.
- This version samples video every few seconds instead of analyzing every frame.
- Nothing is uploaded to your server by this app.

## Main limitation

This version detects faces, but it does **not** automatically identify real people.
