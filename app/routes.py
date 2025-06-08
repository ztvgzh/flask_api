from flask import Blueprint, request, jsonify
from app import db
from app.models import Record

api_bp = Blueprint('api', __name__)

@api_bp.route('/ping', methods=['GET'])
def ping():
    """Health check endpoint"""
    return jsonify({"status": "ok"})

@api_bp.route('/submit', methods=['POST'])
def submit():
    """Submit new record"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        name = data.get('name')
        score = data.get('score')
        
        if not name or score is None:
            return jsonify({"error": "Name and score are required"}), 400
        
        if not isinstance(score, int):
            return jsonify({"error": "Score must be an integer"}), 400
        
        # Create new record
        record = Record(name=name, score=score)
        db.session.add(record)
        db.session.commit()
        
        return jsonify({
            "message": "Record created successfully",
            "record": record.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@api_bp.route('/results', methods=['GET'])
def results():
    """Get all records"""
    try:
        records = Record.query.all()
        return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
