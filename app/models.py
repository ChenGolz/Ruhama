from pydantic import BaseModel, Field
from typing import List, Optional


class FaceItem(BaseModel):
    timestamp_sec: float
    frame_path: str
    face_path: str
    bbox: List[int]
    source_link: str = ""


class ClusterResult(BaseModel):
    cluster_id: int
    display_name: str
    manual_name: str = ""
    count: int
    items: List[FaceItem] = Field(default_factory=list)


class ProjectResult(BaseModel):
    project_id: str
    source_type: str
    source_name: str
    source_url: Optional[str] = None
    clusters: List[ClusterResult] = Field(default_factory=list)
