from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.scan import Scan

report_bp = Blueprint('report', __name__)


@report_bp.route('/', methods=['GET'])
@jwt_required()
def get_scan_history():
    user_id = int(get_jwt_identity())
    scans = Scan.query.filter_by(user_id=user_id).order_by(Scan.created_at.desc()).all()
    return jsonify({
        'scans': [scan.to_dict() for scan in scans],
        'total': len(scans)
    }), 200


@report_bp.route('/<int:scan_id>', methods=['GET'])
@jwt_required()
def get_scan_report(scan_id):
    user_id = int(get_jwt_identity())
    scan = Scan.query.filter_by(id=scan_id, user_id=user_id).first()

    if not scan:
        return jsonify({'error': 'Scan not found'}), 404

    return jsonify({'scan': scan.to_dict()}), 200


@report_bp.route('/<int:scan_id>', methods=['DELETE'])
@jwt_required()
def delete_scan(scan_id):
    user_id = int(get_jwt_identity())
    scan = Scan.query.filter_by(id=scan_id, user_id=user_id).first()

    if not scan:
        return jsonify({'error': 'Scan not found'}), 404

    from models.db import db
    db.session.delete(scan)
    db.session.commit()
    return jsonify({'message': 'Scan deleted successfully'}), 200


@report_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    user_id = int(get_jwt_identity())
    scans = Scan.query.filter_by(user_id=user_id).all()

    if not scans:
        return jsonify({
            'total_scans': 0,
            'avg_fake_percentage': 0,
            'risk_distribution': {},
            'file_type_distribution': {}
        }), 200

    total = len(scans)
    avg_fake = sum(s.fake_percentage for s in scans) / total

    risk_dist = {}
    type_dist = {}
    for s in scans:
        risk_dist[s.risk_level] = risk_dist.get(s.risk_level, 0) + 1
        type_dist[s.file_type] = type_dist.get(s.file_type, 0) + 1

    return jsonify({
        'total_scans': total,
        'avg_fake_percentage': round(avg_fake, 2),
        'risk_distribution': risk_dist,
        'file_type_distribution': type_dist
    }), 200
