import cv2
import numpy as np
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
from services.face_extractor import FaceExtractor


class DeepfakeVideoDetector:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self._build_model()
        self.face_extractor = FaceExtractor()
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def _build_model(self):
        """Build an EfficientNet-based binary classifier for deepfake detection."""
        model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.DEFAULT)
        # Replace classifier for binary classification (real vs fake)
        num_features = model.classifier[1].in_features
        model.classifier = nn.Sequential(
            nn.Dropout(p=0.2),
            nn.Linear(num_features, 256),
            nn.ReLU(),
            nn.Dropout(p=0.3),
            nn.Linear(256, 1),
            nn.Sigmoid()
        )
        model.to(self.device)
        model.eval()
        return model

    def _analyze_frame_quality(self, frame):
        """Analyze frame for deepfake artifacts."""
        scores = {}

        # Blurriness detection (Laplacian variance)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        scores['sharpness'] = min(laplacian_var / 500.0, 1.0)

        # Edge consistency analysis
        edges = cv2.Canny(gray, 100, 200)
        edge_density = np.sum(edges > 0) / edges.size
        scores['edge_consistency'] = edge_density

        # Color distribution analysis
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        h_std = np.std(hsv[:, :, 0])
        s_std = np.std(hsv[:, :, 1])
        scores['color_naturalness'] = min((h_std * s_std) / 2000.0, 1.0)

        # Noise analysis (high-frequency components)
        noise = cv2.subtract(frame, cv2.GaussianBlur(frame, (5, 5), 0))
        noise_level = np.mean(np.abs(noise.astype(float)))
        scores['noise_consistency'] = 1.0 - min(noise_level / 30.0, 1.0)

        # Texture analysis using Local Binary Pattern approximation
        kernel = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]])
        texture = cv2.filter2D(gray, -1, kernel)
        texture_score = np.std(texture) / 50.0
        scores['texture_regularity'] = min(texture_score, 1.0)

        return scores

    def _detect_temporal_anomalies(self, frame_scores):
        """Detect temporal inconsistencies across frames."""
        if len(frame_scores) < 2:
            return {'temporal_consistency': 0.8, 'flickering_score': 0.0}

        score_diffs = []
        for i in range(1, len(frame_scores)):
            diff = abs(frame_scores[i] - frame_scores[i - 1])
            score_diffs.append(diff)

        avg_diff = np.mean(score_diffs) if score_diffs else 0
        max_diff = np.max(score_diffs) if score_diffs else 0

        temporal_consistency = 1.0 - min(avg_diff * 2, 1.0)
        flickering_score = min(max_diff * 3, 1.0)

        return {
            'temporal_consistency': round(temporal_consistency, 4),
            'flickering_score': round(flickering_score, 4),
            'score_variance': round(float(np.var(frame_scores)), 4)
        }

    def analyze(self, video_path):
        """Full deepfake analysis on a video file."""
        faces, metadata = self.face_extractor.extract_faces_from_video(video_path, max_frames=10)

        if 'error' in metadata:
            return {
                'fake_percentage': 0,
                'real_percentage': 0,
                'risk_level': 'Unknown',
                'confidence_score': 0,
                'error': metadata['error']
            }

        if not faces:
            # No faces detected — analyze raw frames for artifacts
            return self._analyze_without_faces(video_path, metadata)

        # Run each face through the model
        frame_fake_scores = []
        frame_details = []

        with torch.no_grad():
            for i, face in enumerate(faces):
                face_rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
                tensor = self.transform(face_rgb).unsqueeze(0).to(self.device)
                prediction = self.model(tensor).item()
                frame_fake_scores.append(prediction)

                quality_scores = self._analyze_frame_quality(face)
                frame_details.append({
                    'face_index': i,
                    'fake_score': round(prediction, 4),
                    'quality_analysis': {k: round(v, 4) for k, v in quality_scores.items()}
                })

        # Aggregate results
        avg_fake_score = np.mean(frame_fake_scores)
        temporal = self._detect_temporal_anomalies(frame_fake_scores)

        # Weighted final score: model prediction + temporal + quality
        quality_avg = np.mean([
            np.mean([d['quality_analysis'].get('noise_consistency', 0.5) for d in frame_details]),
            np.mean([d['quality_analysis'].get('texture_regularity', 0.5) for d in frame_details]),
        ])

        # Combine signals
        final_fake_score = (
            0.5 * avg_fake_score +
            0.2 * (1.0 - temporal['temporal_consistency']) +
            0.15 * temporal['flickering_score'] +
            0.15 * (1.0 - quality_avg)
        )
        final_fake_score = max(0.0, min(1.0, final_fake_score))

        fake_pct = round(final_fake_score * 100, 2)
        real_pct = round((1 - final_fake_score) * 100, 2)

        if fake_pct >= 75:
            risk = 'Critical'
        elif fake_pct >= 50:
            risk = 'High'
        elif fake_pct >= 25:
            risk = 'Medium'
        else:
            risk = 'Low'

        return {
            'fake_percentage': fake_pct,
            'real_percentage': real_pct,
            'risk_level': risk,
            'confidence_score': round(min(len(faces) / 10, 1.0) * 100, 2),
            'metadata': metadata,
            'temporal_analysis': temporal,
            'frame_analysis': frame_details,
            'faces_analyzed': len(faces),
            'analysis_summary': {
                'model_score': round(avg_fake_score * 100, 2),
                'temporal_score': round((1.0 - temporal['temporal_consistency']) * 100, 2),
                'quality_score': round((1.0 - quality_avg) * 100, 2)
            }
        }

    def _analyze_without_faces(self, video_path, metadata):
        """Analyze video when no faces are detected."""
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        num_samples = min(8, total_frames)
        sample_interval = max(1, total_frames // num_samples)

        quality_scores = []
        for i in range(num_samples):
            frame_pos = i * sample_interval
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
            ret, frame = cap.read()
            if not ret:
                break
            scores = self._analyze_frame_quality(frame)
            avg = np.mean(list(scores.values()))
            quality_scores.append(avg)

        cap.release()

        if not quality_scores:
            return {
                'fake_percentage': 0,
                'real_percentage': 100,
                'risk_level': 'Unknown',
                'confidence_score': 10,
                'metadata': metadata,
                'note': 'No faces detected and insufficient frames for analysis'
            }

        anomaly_score = 1.0 - np.mean(quality_scores)
        fake_pct = round(anomaly_score * 100, 2)
        real_pct = round((1.0 - anomaly_score) * 100, 2)

        risk = 'Low'
        if fake_pct >= 75: risk = 'Critical'
        elif fake_pct >= 50: risk = 'High'
        elif fake_pct >= 25: risk = 'Medium'

        return {
            'fake_percentage': fake_pct,
            'real_percentage': real_pct,
            'risk_level': risk,
            'confidence_score': 40.0,
            'metadata': metadata,
            'note': 'No faces detected — analysis based on frame quality artifacts only',
            'analysis_summary': {
                'quality_anomaly_score': round(anomaly_score * 100, 2)
            }
        }
