from __future__ import annotations

import shutil
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import ALLOWED_IMAGE_EXTENSIONS, ALLOWED_VIDEO_EXTENSIONS, DATA_DIR
from .pipeline import process_image, process_video
from .storage import list_projects, load_json, new_project_dir, save_json
from .youtube import download_youtube_video

app = FastAPI(title="Kibbutz Face Archive (Safe Version)")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

app.mount("/data", StaticFiles(directory=str(DATA_DIR)), name="data")


def _suffix(filename: str) -> str:
    return Path(filename).suffix.lower()


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    projects = list_projects()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "projects": projects,
        },
    )


@app.post("/upload", response_class=HTMLResponse)
async def upload_file(request: Request, file: UploadFile = File(...)):
    suffix = _suffix(file.filename or "")
    project_dir = new_project_dir("upload")

    if suffix not in ALLOWED_IMAGE_EXTENSIONS | ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    upload_path = project_dir / "uploads" / (file.filename or "uploaded_file")
    with upload_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    if suffix in ALLOWED_IMAGE_EXTENSIONS:
        result = process_image(upload_path, project_dir)
    else:
        result = process_video(upload_path, project_dir)

    save_json(project_dir / "results.json", result.model_dump())
    return RedirectResponse(url=f"/project/{project_dir.name}", status_code=303)


@app.post("/youtube", response_class=HTMLResponse)
async def youtube_submit(request: Request, youtube_url: str = Form(...)):
    project_dir = new_project_dir("youtube")
    try:
        video_path = download_youtube_video(youtube_url, project_dir / "uploads")
        result = process_video(video_path, project_dir)
        save_json(project_dir / "results.json", result.model_dump())
        return RedirectResponse(url=f"/project/{project_dir.name}", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to download or process YouTube video: {e}")


@app.get("/project/{project_id}", response_class=HTMLResponse)
def project_page(request: Request, project_id: str):
    project_dir = DATA_DIR / project_id
    results_path = project_dir / "results.json"

    if not results_path.exists():
        raise HTTPException(status_code=404, detail="Project not found.")

    results = load_json(results_path)
    return templates.TemplateResponse(
        "project.html",
        {
            "request": request,
            "project": results,
            "project_id": project_id,
        },
    )


@app.post("/project/{project_id}/rename")
async def rename_cluster(
    project_id: str,
    cluster_id: int = Form(...),
    manual_name: str = Form(...),
):
    project_dir = DATA_DIR / project_id
    results_path = project_dir / "results.json"
    if not results_path.exists():
        raise HTTPException(status_code=404, detail="Project not found.")

    results = load_json(results_path)
    found = False
    for cluster in results.get("clusters", []):
        if int(cluster["cluster_id"]) == cluster_id:
            cluster["manual_name"] = manual_name.strip()
            found = True
            break

    if not found:
        raise HTTPException(status_code=404, detail="Cluster not found.")

    save_json(results_path, results)
    return RedirectResponse(url=f"/project/{project_id}", status_code=303)
