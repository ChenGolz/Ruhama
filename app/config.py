from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

FRAME_SAMPLE_EVERY_SECONDS = 2.0
FACE_JITTERS = 1
CLUSTER_EPS = 0.45
CLUSTER_MIN_SAMPLES = 2
MAX_IMAGE_DIMENSION = 1600

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
