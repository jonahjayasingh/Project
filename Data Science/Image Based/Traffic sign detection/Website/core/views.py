import os
import cv2
import json
import uuid
import asyncio
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ultralytics import YOLO
import numpy as np
import base64

# Load YOLO models
MODEL_PATHS = [
    os.path.join(settings.BASE_DIR, 'model', 'best.pt'),
]

models = []
for path in MODEL_PATHS:
    if os.path.exists(path):
        models.append(YOLO(path))
    else:
        print(f"Warning: Model not found at {path}")

# If no custom models found, use default
if not models:
    models.append(YOLO('yolov8s.pt'))


@csrf_exempt
def predict_frame(request):
    """
    Receive a frame via POST (base64 encoded), 
    process it with YOLO using OpenCV, 
    and return detection data and optionally the annotated image.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    try:
        data = json.loads(request.body)
        image_data = data.get('image', '')
        if not image_data:
            return JsonResponse({'error': 'No image data'}, status=400)

        # Decode base64 image
        format, imgstr = image_data.split(';base64,')
        img_bytes = base64.b64decode(imgstr)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return JsonResponse({'error': 'Invalid image'}, status=400)

        # Run YOLO inference
        detections = []
        annotated_img = img.copy()
        
        for m in models:
            results = m(img, conf=0.25, imgsz=320, verbose=False, iou=0.45)
            res = results[0]
            # Clean labels
            res.names = {k: v.replace('_', ' ') for k, v in res.names.items()}
            annotated_img = res.plot(img=annotated_img)
            
            for box in res.boxes:
                cls_id = int(box.cls[0])
                label = res.names[cls_id]
                conf = float(box.conf[0])
                detections.append({
                    'label': label,
                    'conf': round(conf, 2)
                })

        # Encode annotated image back to base64
        _, buffer = cv2.imencode('.jpg', annotated_img)
        encoded_img = base64.b64encode(buffer).decode('utf-8')

        return JsonResponse({
            'detections': detections,
            'image': f'data:image/jpeg;base64,{encoded_img}'
        })
    except Exception as e:
        print(f"Error in predict_frame: {e}")
        return JsonResponse({'error': str(e)}, status=500)


def home(request):

    return render(request, 'core/home.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'core/register.html', {'form': form})

@login_required
def predict_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image_file = request.FILES['image']
        
        # Save image temporarily
        temp_name = f"{uuid.uuid4()}_{image_file.name}"
        temp_path = os.path.join(settings.MEDIA_ROOT, 'temp', temp_name)
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        
        with open(temp_path, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)
        
        # Run YOLO with all models
        detections = []
        original_img = cv2.imread(temp_path)
        display_img = original_img.copy()
        
        # Prepare crops directory
        crop_base_dir = os.path.join(settings.MEDIA_ROOT, 'crops')
        os.makedirs(crop_base_dir, exist_ok=True)
        
        crop_dir_name = f"crops_{uuid.uuid4().hex[:8]}"
        crop_dir = os.path.join(crop_base_dir, crop_dir_name)
        os.makedirs(crop_dir, exist_ok=True)

        
        for m in models:
            results = m(temp_path)
            res = results[0]
            # Modify labels for visual plot
            res.names = {k: v.replace('_', ' ') for k, v in res.names.items()}
            display_img = res.plot(img=display_img)
            
            # Detect classes and crop
            for i, box in enumerate(res.boxes):
                cls_id = int(box.cls[0])
                label = res.names[cls_id]
                conf = float(box.conf[0])
                
                # Get coordinates for cropping
                xyxy = box.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = map(int, xyxy)
                
                # Crop and save
                crop = original_img[y1:y2, x1:x2]
                crop_name = f"crop_{i}_{uuid.uuid4().hex[:4]}.jpg"
                crop_path = os.path.join(crop_dir, crop_name)
                cv2.imwrite(crop_path, crop)
                
                detections.append({
                    'label': label, 
                    'conf': round(conf, 2),
                    'crop_url': os.path.join(settings.MEDIA_URL, 'crops', crop_dir_name, crop_name)
                })
        
        # Save merged annotated image
        result_dir = os.path.join(settings.MEDIA_ROOT, 'results')
        os.makedirs(result_dir, exist_ok=True)
        result_name = f"result_{temp_name}"
        result_path = os.path.join(result_dir, result_name)
        
        cv2.imwrite(result_path, display_img)

        return render(request, 'core/predict_image.html', {
            'original_image': os.path.join(settings.MEDIA_URL, 'temp', temp_name),
            'result_image': os.path.join(settings.MEDIA_URL, 'results', result_name),
            'detections': detections
        })
        
    return render(request, 'core/predict_image.html')

@login_required
def predict_video_page(request):
    return render(request, 'core/predict_video.html')


