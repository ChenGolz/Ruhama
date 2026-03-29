import {
  FaceDetector,
  FilesetResolver
} from "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.22/+esm";

const MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite";
const WASM_URL = "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.22/wasm";

const fileInput = document.getElementById("fileInput");
const processBtn = document.getElementById("processBtn");
const clearBtn = document.getElementById("clearBtn");
const sampleStepInput = document.getElementById("sampleStep");
const minConfidenceInput = document.getElementById("minConfidence");
const imagePreview = document.getElementById("imagePreview");
const videoPreview = document.getElementById("videoPreview");
const overlayCanvas = document.getElementById("overlayCanvas");
const emptyPreview = document.getElementById("emptyPreview");
const statusBox = document.getElementById("statusBox");
const progressBar = document.getElementById("progressBar");
const summary = document.getElementById("summary");
const resultsGrid = document.getElementById("resultsGrid");
const downloadJsonBtn = document.getElementById("downloadJsonBtn");

let faceDetector = null;
let currentFile = null;
let currentObjectUrl = null;
let latestResults = null;

function setStatus(text) {
  statusBox.textContent = text;
}

function resetUI() {
  imagePreview.classList.add("hidden");
  videoPreview.classList.add("hidden");
  overlayCanvas.classList.add("hidden");
  emptyPreview.classList.remove("hidden");
  resultsGrid.innerHTML = "";
  summary.innerHTML = "";
  progressBar.value = 0;
  downloadJsonBtn.disabled = true;
  latestResults = null;
  clearCanvas();
}

function clearCanvas() {
  const ctx = overlayCanvas.getContext("2d");
  ctx.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
}

function revokeObjectUrl() {
  if (currentObjectUrl) {
    URL.revokeObjectURL(currentObjectUrl);
    currentObjectUrl = null;
  }
}

function downloadBlob(filename, blob) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

async function initDetector() {
  setStatus("Loading MediaPipe face detector in your browser...");
  const vision = await FilesetResolver.forVisionTasks(WASM_URL);
  faceDetector = await FaceDetector.createFromOptions(vision, {
    baseOptions: {
      modelAssetPath: MODEL_URL,
      delegate: "GPU"
    },
    runningMode: "IMAGE",
    minDetectionConfidence: Number(minConfidenceInput.value),
    minSuppressionThreshold: 0.3
  });
  setStatus("Ready. Choose an image or a local video file.");
}

function setPreviewSource(file) {
  revokeObjectUrl();
  currentObjectUrl = URL.createObjectURL(file);
  const isImage = file.type.startsWith("image/");
  emptyPreview.classList.add("hidden");

  if (isImage) {
    imagePreview.src = currentObjectUrl;
    imagePreview.classList.remove("hidden");
    videoPreview.classList.add("hidden");
  } else {
    videoPreview.src = currentObjectUrl;
    videoPreview.classList.remove("hidden");
    imagePreview.classList.add("hidden");
  }
}

function syncOverlayToElement(el) {
  const rect = el.getBoundingClientRect();
  overlayCanvas.width = el.videoWidth || el.naturalWidth || el.clientWidth;
  overlayCanvas.height = el.videoHeight || el.naturalHeight || el.clientHeight;
  overlayCanvas.style.width = `${rect.width}px`;
  overlayCanvas.style.height = `${rect.height}px`;
  overlayCanvas.classList.remove("hidden");
}

function drawDetections(detections, width, height) {
  overlayCanvas.width = width;
  overlayCanvas.height = height;
  overlayCanvas.classList.remove("hidden");
  const ctx = overlayCanvas.getContext("2d");
  ctx.clearRect(0, 0, width, height);
  ctx.lineWidth = 3;
  ctx.strokeStyle = "#00c853";
  ctx.fillStyle = "#00c853";
  ctx.font = "14px Arial";

  detections.forEach((det, i) => {
    const box = det.boundingBox;
    ctx.strokeRect(box.originX, box.originY, box.width, box.height);
    const label = `Face ${i + 1}`;
    const y = Math.max(16, box.originY - 8);
    ctx.fillText(label, box.originX, y);
  });
}

function cropFaceToDataUrl(sourceEl, bbox) {
  const sx = Math.max(0, Math.floor(bbox.originX));
  const sy = Math.max(0, Math.floor(bbox.originY));
  const sw = Math.max(1, Math.floor(bbox.width));
  const sh = Math.max(1, Math.floor(bbox.height));
  const canvas = document.createElement("canvas");
  canvas.width = sw;
  canvas.height = sh;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(sourceEl, sx, sy, sw, sh, 0, 0, sw, sh);
  return canvas.toDataURL("image/jpeg", 0.9);
}

function renderFaceCards(items) {
  resultsGrid.innerHTML = "";
  if (!items.length) {
    resultsGrid.innerHTML = `<p>No faces found.</p>`;
    return;
  }

  items.forEach((item, idx) => {
    const card = document.createElement("div");
    card.className = "face-card";
    card.innerHTML = `
      <img src="${item.face_data_url}" alt="Detected face ${idx + 1}">
      <div class="face-meta">
        <div><strong>Face ${idx + 1}</strong></div>
        <div>${item.timestamp_sec != null ? `Time: ${item.timestamp_sec.toFixed(2)}s` : "Image"}</div>
        <div>Confidence: ${(item.score * 100).toFixed(1)}%</div>
        <div>Box: x=${Math.round(item.bbox.x)}, y=${Math.round(item.bbox.y)}, w=${Math.round(item.bbox.width)}, h=${Math.round(item.bbox.height)}</div>
      </div>
    `;
    resultsGrid.appendChild(card);
  });
}

async function ensureImageLoaded(img) {
  if (img.complete && img.naturalWidth) return;
  await new Promise((resolve, reject) => {
    img.onload = () => resolve();
    img.onerror = reject;
  });
}

async function ensureVideoReady(video) {
  if (video.readyState >= 2) return;
  await new Promise((resolve, reject) => {
    video.onloadeddata = () => resolve();
    video.onerror = reject;
  });
}

async function processImage() {
  await faceDetector.setOptions({
    runningMode: "IMAGE",
    minDetectionConfidence: Number(minConfidenceInput.value),
  });

  await ensureImageLoaded(imagePreview);
  syncOverlayToElement(imagePreview);
  setStatus("Running face detection on image...");
  const result = faceDetector.detect(imagePreview);
  const detections = result.detections || [];
  drawDetections(detections, imagePreview.naturalWidth, imagePreview.naturalHeight);

  const items = detections.map((det) => ({
    timestamp_sec: null,
    score: det.categories?.[0]?.score ?? 0,
    bbox: {
      x: det.boundingBox.originX,
      y: det.boundingBox.originY,
      width: det.boundingBox.width,
      height: det.boundingBox.height
    },
    face_data_url: cropFaceToDataUrl(imagePreview, det.boundingBox)
  }));

  latestResults = {
    source_name: currentFile.name,
    source_type: "image",
    processed_at: new Date().toISOString(),
    face_count: items.length,
    items
  };

  summary.innerHTML = `<strong>${items.length}</strong> face(s) found in the image.`;
  renderFaceCards(items);
  downloadJsonBtn.disabled = false;
  setStatus("Done.");
}

async function seekVideo(video, time) {
  return new Promise((resolve) => {
    const handler = () => {
      video.removeEventListener("seeked", handler);
      resolve();
    };
    video.addEventListener("seeked", handler);
    video.currentTime = Math.min(time, Math.max(0, video.duration || 0));
  });
}

async function processVideo() {
  await faceDetector.setOptions({
    runningMode: "VIDEO",
    minDetectionConfidence: Number(minConfidenceInput.value),
  });

  await ensureVideoReady(videoPreview);
  videoPreview.pause();
  syncOverlayToElement(videoPreview);
  setStatus("Processing video locally in your browser...");

  const duration = videoPreview.duration || 0;
  const step = Math.max(0.25, Number(sampleStepInput.value) || 2);
  const sampledItems = [];
  let frameCounter = 0;
  const totalSteps = Math.max(1, Math.ceil(duration / step));

  for (let t = 0; t <= duration; t += step) {
    await seekVideo(videoPreview, t);
    const timeMs = performance.now();
    const result = faceDetector.detectForVideo(videoPreview, timeMs);
    const detections = result.detections || [];

    detections.forEach((det) => {
      sampledItems.push({
        timestamp_sec: t,
        score: det.categories?.[0]?.score ?? 0,
        bbox: {
          x: det.boundingBox.originX,
          y: det.boundingBox.originY,
          width: det.boundingBox.width,
          height: det.boundingBox.height
        },
        face_data_url: cropFaceToDataUrl(videoPreview, det.boundingBox)
      });
    });

    if (detections.length) {
      drawDetections(
        detections,
        videoPreview.videoWidth,
        videoPreview.videoHeight
      );
    }

    frameCounter += 1;
    progressBar.value = Math.min(1, frameCounter / totalSteps);
    setStatus(`Processed ${frameCounter} / ${totalSteps} sampled frame(s)...`);
    await new Promise((r) => setTimeout(r, 0));
  }

  latestResults = {
    source_name: currentFile.name,
    source_type: "video",
    processed_at: new Date().toISOString(),
    sample_every_seconds: step,
    face_count: sampledItems.length,
    items: sampledItems
  };

  summary.innerHTML = `
    <strong>${sampledItems.length}</strong> face detection(s) found across sampled video frames.<br>
    Sample interval: <strong>${step}s</strong>.
  `;
  renderFaceCards(sampledItems);
  downloadJsonBtn.disabled = false;
  setStatus("Done. This GitHub Pages version detects faces, but does not cluster or auto-identify people.");
}

fileInput.addEventListener("change", () => {
  const file = fileInput.files?.[0] || null;
  currentFile = file;
  resetUI();
  if (!file) {
    processBtn.disabled = true;
    setStatus(faceDetector ? "Ready. Choose an image or a local video file." : "Loading detector...");
    return;
  }
  setPreviewSource(file);
  processBtn.disabled = !faceDetector;
  setStatus(`Selected: ${file.name}`);
});

processBtn.addEventListener("click", async () => {
  if (!faceDetector || !currentFile) return;
  processBtn.disabled = true;
  try {
    if (currentFile.type.startsWith("image/")) {
      await processImage();
    } else if (currentFile.type.startsWith("video/")) {
      await processVideo();
    } else {
      setStatus("Unsupported file type.");
    }
  } catch (err) {
    console.error(err);
    setStatus(`Failed: ${err.message || err}`);
  } finally {
    processBtn.disabled = false;
  }
});

clearBtn.addEventListener("click", () => {
  fileInput.value = "";
  currentFile = null;
  revokeObjectUrl();
  resetUI();
  processBtn.disabled = true;
  setStatus(faceDetector ? "Ready. Choose an image or a local video file." : "Loading detector...");
});

downloadJsonBtn.addEventListener("click", () => {
  if (!latestResults) return;
  const blob = new Blob([JSON.stringify(latestResults, null, 2)], { type: "application/json" });
  downloadBlob("face-detections.json", blob);
});

resetUI();
initDetector().catch((err) => {
  console.error(err);
  setStatus(`Could not load detector: ${err.message || err}`);
});
