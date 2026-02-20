from ultralytics import YOLO

model = YOLO("yolov8n.pt")

results = model.train(
    data="data.yaml",
    epochs=20,
    batch=8,
    imgsz=640,
    device="cpu",
    workers=4,            # faster loading
    project="runs",       # explicit folder
    name="traffic_signs"  # experiment name
)

print("Saved to:", results.save_dir)

model.val()
