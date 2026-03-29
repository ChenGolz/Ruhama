from pathlib import Path
import subprocess


def download_youtube_video(url: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    out_template = str(output_dir / "%(title).80s-%(id)s.%(ext)s")

    cmd = [
        "yt-dlp",
        "-f",
        "mp4/bestvideo+bestaudio/best",
        "-o",
        out_template,
        url,
    ]
    subprocess.run(cmd, check=True)

    videos = sorted(output_dir.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not videos:
        raise RuntimeError("yt-dlp completed but no file was downloaded.")
    return videos[0]
