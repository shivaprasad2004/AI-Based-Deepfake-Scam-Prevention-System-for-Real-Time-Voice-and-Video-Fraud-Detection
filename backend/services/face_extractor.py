import cv2
import numpy as np
from PIL import Image
import os


class FaceExtractor:
    def __init__(self):
        # Use OpenCV's built-in Haar cascade for face detection
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

    def extract_faces_from_frame(self, frame, target_size=(224, 224)):
        """Extract faces from a single frame."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        face_images = []
        face_locations = []

        for (x, y, w, h) in faces:
            # Add padding around face
            padding = int(0.2 * max(w, h))
            x1 = max(0, x - padding)
            y1 = max(0, y - padding)
            x2 = min(frame.shape[1], x + w + padding)
            y2 = min(frame.shape[0], y + h + padding)

            face_img = frame[y1:y2, x1:x2]
            face_img = cv2.resize(face_img, target_size)
            face_images.append(face_img)
            face_locations.append({'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h)})

        return face_images, face_locations

    def extract_faces_from_video(self, video_path, max_frames=30, sample_interval=None):
        """Extract faces from video frames at regular intervals."""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return [], {'error': 'Could not open video file'}

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = total_frames / fps if fps > 0 else 0

        if sample_interval is None:
            sample_interval = max(1, total_frames // max_frames)

        all_faces = []
        frame_analyses = []
        num_samples = min(max_frames, total_frames)

        for i in range(num_samples):
            frame_idx = i * sample_interval
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if not ret:
                break

            faces, locations = self.extract_faces_from_frame(frame)
            for face in faces:
                all_faces.append(face)
            frame_analyses.append({
                'frame_index': frame_idx,
                'timestamp': frame_idx / fps if fps > 0 else 0,
                'faces_detected': len(faces),
                'face_locations': locations
            })

        cap.release()

        metadata = {
            'total_frames': total_frames,
            'fps': fps,
            'width': width,
            'height': height,
            'duration': round(duration, 2),
            'resolution': f'{width}x{height}',
            'frames_analyzed': len(frame_analyses),
            'total_faces_extracted': len(all_faces),
            'frame_analyses': frame_analyses
        }

        return all_faces, metadata

    def get_video_metadata(self, video_path):
        """Get basic video metadata without extracting faces."""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {}

        metadata = {
            'total_frames': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'duration': round(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) / max(cap.get(cv2.CAP_PROP_FPS), 1), 2),
            'resolution': f'{int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}'
        }
        cap.release()
        return metadata
