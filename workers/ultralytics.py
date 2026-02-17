# ai_worker.py

from ultralytics import YOLO

_model = None

def _get_model(model_path):
    global _model
    if _model is None:
        _model = YOLO(model_path)
    return _model


def run_inference(frame, model_path, threshold):
    model = _get_model(model_path)

    results = model.track(frame, persist=True, verbose=False)
    result = results[0]

    detections = []

    if result.boxes is None:
        return detections

    for box in result.boxes:
        conf = float(box.conf.item())
        if conf < threshold:
            continue

        cls = int(box.cls.item())
        x1, y1, x2, y2 = box.xyxy[0].tolist()

        track_id = None
        if hasattr(box, "id") and box.id is not None:
            track_id = int(box.id.item())

        detections.append({
            "track_id": track_id,
            "class_id": cls,
            "confidence": conf,
            "u": (x1 + x2) / 2.0,
            "v": (y1 + y2) / 2.0,
            "bbox": [x1, y1, x2, y2]
        })

    return detections
