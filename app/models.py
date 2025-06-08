from app import db
from datetime import datetime

class Record(db.Model):
    __tablename__ = 'records'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'score': self.score,
            'timestamp': self.timestamp.isoformat()
        }
    
    def __repr__(self):
        return f'<Record {self.name}: {self.score}>'
