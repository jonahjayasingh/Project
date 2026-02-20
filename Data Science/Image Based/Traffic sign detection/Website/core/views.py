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
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaRelay
import av

# Load YOLO models
MODEL_PATHS = [
    '/Volumes/CrucialX9/Project/runs/detect/indian-traffic-sign4/weights/best.pt',
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


relay = MediaRelay()


pcs = set()

class VideoTransformTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self, track):
        super().__init__()
        self.track = track
        self.frame_count = 0

    async def recv(self):
        try:
            frame = await self.track.recv()
            self.frame_count += 1
            
            # Skip fewer frames (process every 2nd frame) to improve detection chance
            if self.frame_count % 2 != 0:
                return frame

            # Convert to numpy array
            img = frame.to_ndarray(format="bgr24")
            
            # Use a slightly higher imgsz for better accuracy (416 is a good compromise)
            # Increase confidence sensitivity to 0.25
            annotated_img = img.copy()
            for m in models:
                results = m(img, conf=0.25, imgsz=416, verbose=False, iou=0.45)
                res = results[0]
                # Clean labels on the fly
                res.names = {k: v.replace('_', ' ') for k, v in res.names.items()}
                annotated_img = res.plot(img=annotated_img)
            
            # Rebuild frame
            new_frame = av.VideoFrame.from_ndarray(annotated_img, format="bgr24")
            new_frame.pts = frame.pts
            new_frame.time_base = frame.time_base
            
            return new_frame
        except Exception as e:
            print(f"Error in VideoTransformTrack: {e}")
            return None

        except Exception as e:
            print(f"Error in VideoTransformTrack: {e}")
            return None


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

@csrf_exempt
async def rtc_offer(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)
        
    print("Received RTC offer")
    try:
        params = json.loads(request.body)
        offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

        pc = RTCPeerConnection()
        pcs.add(pc)

        @pc.on("iceconnectionstatechange")
        async def on_iceconnectionstatechange():
            print(f"ICE Connection State: {pc.iceConnectionState}")
            if pc.iceConnectionState == "failed" or pc.iceConnectionState == "closed":
                await pc.close()
                pcs.discard(pc)

        # Use an event to wait for the track
        track_event = asyncio.Event()

        @pc.on("track")
        def on_track(track):
            print(f"Track received: {track.kind}")
            if track.kind == "video":
                pc.addTrack(VideoTransformTrack(relay.subscribe(track)))
                track_event.set()

        await pc.setRemoteDescription(offer)
        
        # Wait up to 5 seconds for the track to be identified
        try:
            await asyncio.wait_for(track_event.wait(), timeout=5.0)
        except asyncio.TimeoutError:
            print("Timeout waiting for track event")

        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)

        return JsonResponse({
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type
        })
    except Exception as e:
        print(f"Error in rtc_offer: {e}")
        return JsonResponse({"error": str(e)}, status=500)


