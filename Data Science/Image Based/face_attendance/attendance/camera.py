import os
import cv2
import numpy as np
import face_recognition
from datetime import datetime
from uuid import uuid4
from .models import StudentData, Attendance

TRAINING_PATH = "static/Training images"

class VideoCamera:
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.encodeListKnown = []
        self.classNames = []
        self.load_known_faces()

    def __del__(self):
        self.video.release()

    def load_known_faces(self):
        self.encodeListKnown = []
        self.classNames = []
        
        try:
            # Fetch all students from database
            students = StudentData.objects.all()
            
            for student in students:
                # Check if image path exists
                if student.image and os.path.exists(student.image):
                    try:
                        img = cv2.imread(student.image)
                        if img is not None:
                            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                            encs = face_recognition.face_encodings(img)
                            if encs:
                                self.encodeListKnown.append(encs[0])
                                # Use the exact name from the database
                                self.classNames.append(student.name)
                    except Exception as e:
                        print(f"Error loading face for {student.name}: {e}")
        except Exception as e:
            print(f"Database error in load_known_faces: {e}")

    def get_frame(self, mode='none'):
        success, image = self.video.read()
        if not success:
            return None

        if mode == 'recognize' and self.encodeListKnown:
            imgS = cv2.resize(image, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
            facesCurFrame = face_recognition.face_locations(imgS)
            encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

            for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                faceDis = face_recognition.face_distance(self.encodeListKnown, encodeFace)
                if len(faceDis) > 0:
                    matchIndex = np.argmin(faceDis)
                    if faceDis[matchIndex] < 0.50:
                        name = self.classNames[matchIndex].upper()
                        # Mark attendance in background-ish via local logic
                        self.mark_attendance_internal(name)
                    else:
                        name = 'UNKNOWN'
                else:
                    name = 'UNKNOWN'

                y1, x2, y2, x1 = [v * 4 for v in faceLoc]
                color = (0, 255, 0) if name != 'UNKNOWN' else (0, 0, 255)
                cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
                cv2.putText(image, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 2)

        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

    def mark_attendance_internal(self, name):
        try:
            now = datetime.now()
            today = now.date()
            
            # Find the student by name
            student = StudentData.objects.filter(name__iexact=name).first()
            if not student:
                print(f"Student {name} not found in database")
                return
            
            # Check if student already has a record for today
            exists = Attendance.objects.filter(
                student=student, 
                date=today
            ).exists()
            
            if exists:
                # Already marked for today - do nothing
                print(f"Attendance already marked for {name} today")
            else:
                # Create a new record - first time seen today
                Attendance.objects.create(student=student, date=today, time=now.time())
                print(f"✓ Attendance MARKED for {name} at {now.time().strftime('%I:%M:%S %p')}")
        except Exception as e:
            print(f"Error in internal mark: {e}")

global_camera = None

def get_camera():
    global global_camera
    if global_camera is None:
        global_camera = VideoCamera()
    return global_camera
