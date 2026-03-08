import numpy as np
import librosa
import subprocess
import tempfile
import os


def _get_ffmpeg_path():
    try:
        from imageio_ffmpeg import get_ffmpeg_exe
        return get_ffmpeg_exe()
    except ImportError:
        return 'ffmpeg'


def _load_audio_with_ffmpeg(audio_path, sr=16000):
    """Load any audio/video file by converting to wav via ffmpeg first."""
    ext = os.path.splitext(audio_path)[1].lower()
    # Try librosa directly for simple formats
    if ext in ('.wav', '.flac'):
        return librosa.load(audio_path, sr=sr)

    # Convert to wav using ffmpeg for all other formats
    ffmpeg = _get_ffmpeg_path()
    tmp_wav = tempfile.mktemp(suffix='.wav')
    try:
        cmd = [
            ffmpeg, '-y', '-i', audio_path,
            '-ar', str(sr), '-ac', '1', '-f', 'wav',
            '-loglevel', 'error',
            tmp_wav
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            raise RuntimeError(f'ffmpeg conversion failed: {result.stderr.strip()}')
        y, sr_out = librosa.load(tmp_wav, sr=sr)
        return y, sr_out
    finally:
        if os.path.exists(tmp_wav):
            os.remove(tmp_wav)


class DeepfakeAudioDetector:
    def __init__(self):
        self.sample_rate = 16000
        self.n_mfcc = 20
        self.n_mels = 128

    def _extract_features(self, audio_path):
        """Extract audio features for deepfake detection."""
        y, sr = _load_audio_with_ffmpeg(audio_path, sr=self.sample_rate)
        duration = librosa.get_duration(y=y, sr=sr)

        features = {}

        # MFCC features
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=self.n_mfcc)
        features['mfcc_mean'] = np.mean(mfccs, axis=1).tolist()
        features['mfcc_std'] = np.std(mfccs, axis=1).tolist()

        # Spectral features
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        features['spectral_centroid_mean'] = float(np.mean(spectral_centroid))
        features['spectral_centroid_std'] = float(np.std(spectral_centroid))

        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        features['spectral_rolloff_mean'] = float(np.mean(spectral_rolloff))

        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
        features['spectral_bandwidth_mean'] = float(np.mean(spectral_bandwidth))

        # Zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(y)[0]
        features['zcr_mean'] = float(np.mean(zcr))
        features['zcr_std'] = float(np.std(zcr))

        # Chroma features
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        features['chroma_mean'] = float(np.mean(chroma))
        features['chroma_std'] = float(np.std(chroma))

        # RMS energy
        rms = librosa.feature.rms(y=y)[0]
        features['rms_mean'] = float(np.mean(rms))
        features['rms_std'] = float(np.std(rms))

        # Mel spectrogram statistics
        mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=self.n_mels)
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
        features['mel_spec_mean'] = float(np.mean(mel_spec_db))
        features['mel_spec_std'] = float(np.std(mel_spec_db))

        # Pitch features
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        pitch_values = pitches[magnitudes > np.median(magnitudes)]
        if len(pitch_values) > 0:
            features['pitch_mean'] = float(np.mean(pitch_values))
            features['pitch_std'] = float(np.std(pitch_values))
            features['pitch_range'] = float(np.ptp(pitch_values))
        else:
            features['pitch_mean'] = 0.0
            features['pitch_std'] = 0.0
            features['pitch_range'] = 0.0

        metadata = {
            'duration': round(duration, 2),
            'sample_rate': sr,
            'total_samples': len(y),
        }

        return features, metadata

    def _compute_anomaly_scores(self, features):
        """Compute anomaly scores based on feature analysis."""
        scores = {}

        # Spectral consistency — synthetic audio often has unusual spectral properties
        sc_std = features.get('spectral_centroid_std', 0)
        scores['spectral_consistency'] = 1.0 - min(sc_std / 2000.0, 1.0)

        # Pitch naturalness — deepfake audio may have limited pitch variation
        pitch_std = features.get('pitch_std', 0)
        pitch_range = features.get('pitch_range', 0)
        if pitch_std < 20:
            scores['pitch_naturalness'] = 0.3  # Very uniform pitch = suspicious
        elif pitch_std > 200:
            scores['pitch_naturalness'] = 0.4  # Too variable = suspicious
        else:
            scores['pitch_naturalness'] = 0.8

        # Energy consistency
        rms_std = features.get('rms_std', 0)
        rms_mean = features.get('rms_mean', 0.01)
        energy_variation = rms_std / max(rms_mean, 0.001)
        if energy_variation < 0.1:
            scores['energy_naturalness'] = 0.3  # Too consistent
        elif energy_variation > 2.0:
            scores['energy_naturalness'] = 0.4  # Too variable
        else:
            scores['energy_naturalness'] = 0.85

        # MFCC analysis — deepfakes often show unusual MFCC distributions
        mfcc_std_values = features.get('mfcc_std', [])
        if mfcc_std_values:
            avg_mfcc_std = np.mean(mfcc_std_values)
            if avg_mfcc_std < 5:
                scores['mfcc_naturalness'] = 0.3
            elif avg_mfcc_std > 30:
                scores['mfcc_naturalness'] = 0.5
            else:
                scores['mfcc_naturalness'] = 0.8
        else:
            scores['mfcc_naturalness'] = 0.5

        # Zero crossing rate analysis
        zcr_mean = features.get('zcr_mean', 0)
        if zcr_mean < 0.02 or zcr_mean > 0.2:
            scores['zcr_naturalness'] = 0.4
        else:
            scores['zcr_naturalness'] = 0.8

        # Mel spectrogram smoothness
        mel_std = features.get('mel_spec_std', 0)
        if mel_std < 5:
            scores['mel_naturalness'] = 0.3  # Too smooth
        elif mel_std > 25:
            scores['mel_naturalness'] = 0.5
        else:
            scores['mel_naturalness'] = 0.8

        return scores

    def _segment_analysis(self, audio_path, segment_duration=3.0):
        """Analyze audio in segments to detect inconsistencies."""
        y, sr = _load_audio_with_ffmpeg(audio_path, sr=self.sample_rate)
        total_duration = librosa.get_duration(y=y, sr=sr)
        segment_samples = int(segment_duration * sr)

        segment_scores = []
        for start in range(0, len(y), segment_samples):
            end = min(start + segment_samples, len(y))
            segment = y[start:end]

            if len(segment) < sr:  # Skip segments shorter than 1 second
                continue

            mfccs = librosa.feature.mfcc(y=segment, sr=sr, n_mfcc=13)
            zcr = librosa.feature.zero_crossing_rate(segment)[0]
            rms = librosa.feature.rms(y=segment)[0]

            segment_scores.append({
                'start_time': round(start / sr, 2),
                'end_time': round(end / sr, 2),
                'mfcc_mean': float(np.mean(mfccs)),
                'zcr_mean': float(np.mean(zcr)),
                'rms_mean': float(np.mean(rms))
            })

        # Detect inconsistencies between segments
        if len(segment_scores) > 1:
            mfcc_values = [s['mfcc_mean'] for s in segment_scores]
            consistency_score = 1.0 - min(np.std(mfcc_values) / 10.0, 1.0)
        else:
            consistency_score = 0.5

        return segment_scores, round(consistency_score, 4)

    def analyze(self, audio_path):
        """Full deepfake analysis on an audio file."""
        try:
            features, metadata = self._extract_features(audio_path)
        except Exception as e:
            return {
                'fake_percentage': 0,
                'real_percentage': 0,
                'risk_level': 'Unknown',
                'confidence_score': 0,
                'error': str(e) or repr(e)
            }

        anomaly_scores = self._compute_anomaly_scores(features)
        segment_analysis, segment_consistency = self._segment_analysis(audio_path)

        # Weighted combination of anomaly scores
        weights = {
            'spectral_consistency': 0.15,
            'pitch_naturalness': 0.2,
            'energy_naturalness': 0.15,
            'mfcc_naturalness': 0.2,
            'zcr_naturalness': 0.1,
            'mel_naturalness': 0.1,
        }

        # Naturalness = how real it sounds (higher = more real)
        naturalness = sum(anomaly_scores.get(k, 0.5) * w for k, w in weights.items())
        # Factor in segment consistency
        naturalness = 0.85 * naturalness + 0.15 * segment_consistency

        fake_score = 1.0 - naturalness
        fake_pct = round(fake_score * 100, 2)
        real_pct = round(naturalness * 100, 2)

        if fake_pct >= 75:
            risk = 'Critical'
        elif fake_pct >= 50:
            risk = 'High'
        elif fake_pct >= 25:
            risk = 'Medium'
        else:
            risk = 'Low'

        confidence = min(metadata['duration'] / 10.0, 1.0) * 100

        return {
            'fake_percentage': fake_pct,
            'real_percentage': real_pct,
            'risk_level': risk,
            'confidence_score': round(confidence, 2),
            'metadata': metadata,
            'feature_analysis': {k: round(v, 4) for k, v in anomaly_scores.items()},
            'segment_analysis': segment_analysis,
            'segment_consistency': segment_consistency,
            'analysis_summary': {
                'spectral_score': round(anomaly_scores.get('spectral_consistency', 0.5) * 100, 2),
                'pitch_score': round(anomaly_scores.get('pitch_naturalness', 0.5) * 100, 2),
                'mfcc_score': round(anomaly_scores.get('mfcc_naturalness', 0.5) * 100, 2),
                'energy_score': round(anomaly_scores.get('energy_naturalness', 0.5) * 100, 2),
                'overall_naturalness': round(naturalness * 100, 2)
            }
        }
