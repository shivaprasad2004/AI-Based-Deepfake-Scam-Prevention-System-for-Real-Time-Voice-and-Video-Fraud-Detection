from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.db import db
from models.scan import Scan
from services.file_handler import FileHandler
from services.video_detector import DeepfakeVideoDetector
from services.audio_detector import DeepfakeAudioDetector
from services.url_analyzer import URLAnalyzer

upload_bp = Blueprint('upload', __name__)

video_detector = None
audio_detector = None


def get_video_detector():
    global video_detector
    if video_detector is None:
        video_detector = DeepfakeVideoDetector()
    return video_detector


def get_audio_detector():
    global audio_detector
    if audio_detector is None:
        audio_detector = DeepfakeAudioDetector()
    return audio_detector


def _process_and_save(file_info, user_id, source_type):
    """Run detection and save results to database."""
    file_type = file_info['file_type']
    file_path = file_info['path']

    try:
        if file_type == 'video':
            result = get_video_detector().analyze(file_path)
        elif file_type == 'audio':
            result = get_audio_detector().analyze(file_path)
        else:
            FileHandler.cleanup_file(file_path)
            return {'error': 'Unsupported file type'}, 400

        if 'error' in result:
            FileHandler.cleanup_file(file_path)
            return {'error': result['error']}, 400

        scan = Scan(
            user_id=user_id,
            filename=file_info['original_name'],
            file_type=file_type,
            source_type=source_type,
            file_size=file_info.get('file_size'),
            duration=result.get('metadata', {}).get('duration'),
            resolution=result.get('metadata', {}).get('resolution'),
            fake_percentage=result['fake_percentage'],
            real_percentage=result['real_percentage'],
            risk_level=result['risk_level'],
            confidence_score=result.get('confidence_score', 0),
            status='completed'
        )
        scan.set_report(result)
        db.session.add(scan)
        db.session.commit()

        FileHandler.cleanup_file(file_path)

        return {
            'message': 'Analysis completed',
            'scan': scan.to_dict()
        }, 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        FileHandler.cleanup_file(file_path)
        return {'error': f'Analysis failed: {str(e) or repr(e)}'}, 500


@upload_bp.route('/local', methods=['POST'])
@jwt_required()
def upload_local():
    user_id = int(get_jwt_identity())

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file_info, error = FileHandler.save_uploaded_file(request.files['file'])
    if error:
        return jsonify({'error': error}), 400

    result, status = _process_and_save(file_info, user_id, 'local')
    return jsonify(result), status


@upload_bp.route('/url', methods=['POST'])
@jwt_required()
def upload_url():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data or not data.get('url'):
        return jsonify({'error': 'URL is required'}), 400

    file_info, error = FileHandler.download_from_url(data['url'])
    if error:
        return jsonify({'error': error}), 400

    result, status = _process_and_save(file_info, user_id, 'url')
    return jsonify(result), status


@upload_bp.route('/analyze-link', methods=['POST'])
@jwt_required()
def analyze_link():
    """Analyze a URL to determine if it's fake or legitimate."""
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data or not data.get('url'):
        return jsonify({'error': 'URL is required'}), 400

    url = data['url'].strip()
    result = URLAnalyzer.analyze(url)

    if 'error' in result:
        return jsonify({'error': result['error']}), 400

    scan = Scan(
        user_id=user_id,
        filename=result.get('hostname', url[:100]),
        file_type='link',
        source_type='link',
        fake_percentage=result['fake_percentage'],
        real_percentage=result['real_percentage'],
        risk_level=result['risk_level'],
        confidence_score=result.get('confidence_score', 0),
        status='completed'
    )
    scan.set_report(result)
    db.session.add(scan)
    db.session.commit()

    return jsonify({
        'message': 'Link analysis completed',
        'scan': scan.to_dict()
    }), 200


@upload_bp.route('/drive', methods=['POST'])
@jwt_required()
def upload_drive():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data or not data.get('url'):
        return jsonify({'error': 'Google Drive URL is required'}), 400

    file_info, error = FileHandler.download_from_drive(data['url'])
    if error:
        return jsonify({'error': error}), 400

    result, status = _process_and_save(file_info, user_id, 'drive')
    return jsonify(result), status
