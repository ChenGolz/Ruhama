from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import List, Tuple

import cv2
import face_recognition
import numpy as np
from sklearn.cluster import DBSCAN

from .config import (
    CLUSTER_EPS,
    CLUSTER_MIN_SAMPLES,
    FACE_JITTERS,
    FRAME_SAMPLE_EVERY_SECONDS,
    MAX_IMAGE_DIMENSION,
)
from .models import ClusterResult, FaceItem, ProjectResult


def _resize_if_needed(image: np.ndarray) -> np.ndarray:
    h, w = image.shape[:2]
    max_dim = max(h, w)
    if max_dim <= MAX_IMAGE_DIMENSION:
        return image
    scale = MAX_IMAGE_DIMENSION / float(max_dim)
    new_w = int(w * scale)
    new_h = int(h * scale)
    return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)


def _rgb(image_bgr: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)


def process_image(image_path: Path, project_dir: Path) -> ProjectResult:
    image_bgr = cv2.imread(str(image_path))
    if image_bgr is None:
        raise ValueError(f"Could not read image: {image_path}")

    image_bgr = _resize_if_needed(image_bgr)
    rgb = _rgb(image_bgr)

    face_locations = face_recognition.face_locations(rgb, model="hog")
    encodings = face_recognition.face_encodings(rgb, face_locations, num_jitters=FACE_JITTERS)

    all_items: list[dict] = []

    frame_path = project_dir / "frames" / "frame_000000.jpg"
    cv2.imwrite(str(frame_path), image_bgr)

    for i, (loc, enc) in enumerate(zip(face_locations, encodings)):
        top, right, bottom, left = loc
        face_crop = image_bgr[top:bottom, left:right]
        if face_crop.size == 0:
            continue
        face_path = project_dir / "faces" / f"face_{i:06d}.jpg"
        cv2.imwrite(str(face_path), face_crop)

        all_items.append(
            {
                "encoding": enc,
                "timestamp_sec": 0.0,
                "frame_path": str(frame_path.relative_to(project_dir)),
                "face_path": str(face_path.relative_to(project_dir)),
                "bbox": [left, top, right, bottom],
            }
        )

    return _cluster_items(all_items, project_dir=project_dir, source_type="image", source_name=image_path.name)


def process_video(video_path: Path, project_dir: Path, sample_every_seconds: float = FRAME_SAMPLE_EVERY_SECONDS) -> ProjectResult:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    duration_sec = total_frames / fps if total_frames > 0 else 0
    step_frames = max(int(fps * sample_every_seconds), 1)

    frame_idx = 0
    saved_count = 0
    face_count = 0
    all_items: list[dict] = []

    while True:
        ret, frame_bgr = cap.read()
        if not ret:
            break

        if frame_idx % step_frames != 0:
            frame_idx += 1
            continue

        timestamp_sec = frame_idx / fps
        frame_bgr = _resize_if_needed(frame_bgr)
        rgb = _rgb(frame_bgr)

        frame_path = project_dir / "frames" / f"frame_{saved_count:06d}.jpg"
        cv2.imwrite(str(frame_path), frame_bgr)

        face_locations = face_recognition.face_locations(rgb, model="hog")
        encodings = face_recognition.face_encodings(rgb, face_locations, num_jitters=FACE_JITTERS)

        for loc, enc in zip(face_locations, encodings):
            top, right, bottom, left = loc
            face_crop = frame_bgr[top:bottom, left:right]
            if face_crop.size == 0:
                continue
            face_path = project_dir / "faces" / f"face_{face_count:06d}.jpg"
            cv2.imwrite(str(face_path), face_crop)

            all_items.append(
                {
                    "encoding": enc,
                    "timestamp_sec": round(timestamp_sec, 2),
                    "frame_path": str(frame_path.relative_to(project_dir)),
                    "face_path": str(face_path.relative_to(project_dir)),
                    "bbox": [left, top, right, bottom],
                }
            )
            face_count += 1

        saved_count += 1
        frame_idx += 1

        if duration_sec and timestamp_sec > duration_sec:
            break

    cap.release()
    return _cluster_items(all_items, project_dir=project_dir, source_type="video", source_name=video_path.name)


def _cluster_items(all_items: list[dict], project_dir: Path, source_type: str, source_name: str) -> ProjectResult:
    if not all_items:
        return ProjectResult(
            project_id=project_dir.name,
            source_type=source_type,
            source_name=source_name,
            clusters=[],
        )

    encodings = np.array([item["encoding"] for item in all_items])

    clustering = DBSCAN(eps=CLUSTER_EPS, min_samples=CLUSTER_MIN_SAMPLES, metric="euclidean")
    labels = clustering.fit_predict(encodings)

    grouped: dict[int, list[dict]] = defaultdict(list)

    unknown_index = 100000
    for item, label in zip(all_items, labels):
        if label == -1:
            grouped[unknown_index].append(item)
            unknown_index += 1
        else:
            grouped[int(label)].append(item)

    cluster_results: List[ClusterResult] = []

    for public_idx, (_, items) in enumerate(sorted(grouped.items(), key=lambda kv: len(kv[1]), reverse=True), start=1):
        face_items = [
            FaceItem(
                timestamp_sec=item["timestamp_sec"],
                frame_path=item["frame_path"],
                face_path=item["face_path"],
                bbox=item["bbox"],
            )
            for item in items
        ]
        cluster_results.append(
            ClusterResult(
                cluster_id=public_idx - 1,
                display_name=f"Person {public_idx}",
                manual_name="",
                count=len(items),
                items=face_items,
            )
        )

    return ProjectResult(
        project_id=project_dir.name,
        source_type=source_type,
        source_name=source_name,
        clusters=cluster_results,
    )
