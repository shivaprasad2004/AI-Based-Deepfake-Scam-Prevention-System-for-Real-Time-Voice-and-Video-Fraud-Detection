from models.db import db
from datetime import datetime
import json


class Scan(db.Model):
    __tablename__ = 'scans'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)  # 'video' or 'audio'
    source_type = db.Column(db.String(20), nullable=False)  # 'local', 'url', 'drive'
    file_size = db.Column(db.Integer)
    duration = db.Column(db.Float)
    resolution = db.Column(db.String(20))

    # Detection results
    fake_percentage = db.Column(db.Float, nullable=False)
    real_percentage = db.Column(db.Float, nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)  # Low, Medium, High, Critical
    confidence_score = db.Column(db.Float)

    # Detailed analysis stored as JSON
    detailed_report = db.Column(db.Text)

    status = db.Column(db.String(20), default='processing')  # processing, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_report(self, report_dict):
        self.detailed_report = json.dumps(report_dict)

    def get_report(self):
        if self.detailed_report:
            return json.loads(self.detailed_report)
        return {}

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'file_type': self.file_type,
            'source_type': self.source_type,
            'file_size': self.file_size,
            'duration': self.duration,
            'resolution': self.resolution,
            'fake_percentage': self.fake_percentage,
            'real_percentage': self.real_percentage,
            'risk_level': self.risk_level,
            'confidence_score': self.confidence_score,
            'detailed_report': self.get_report(),
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
