
from flask_socketio import emit
from app_factory import socketio
from models.video_analyzer import VideoAnalyzer
from models.biometric_integrator import BiometricIntegrator
from models.database import db, VideoAnalysis, BiometricData
import json
import logging
from datetime import datetime

video_analyzer = VideoAnalyzer()
biometric_integrator = BiometricIntegrator()

@socketio.on('video_frame')
def handle_video_frame(data):
    try:
        frame_data = data.get('frame_data')
        session_id = data.get('session_id')
        if not frame_data:
            emit('error', {'message': 'No frame data provided'})
            return
        analysis = video_analyzer.analyze_frame(frame_data)
        if analysis.get('confidence', 0) > 0.7:
            video_analysis = VideoAnalysis(
                session_id=session_id if session_id else None,
                emotions_detected=json.dumps(analysis.get('emotions', {})),
                microexpressions=json.dumps(analysis.get('microexpressions', {})),
                confidence_score=analysis.get('confidence', 0),
                frame_timestamp=data.get('timestamp', 0)
            )
            db.session.add(video_analysis)
            db.session.commit()
        emit('video_analysis', {
            'session_id': session_id,
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logging.error(f"Error processing video frame: {e}")
        emit('error', {'message': 'Error processing video frame'})

@socketio.on('biometric_update')
def handle_biometric_update(data):
    try:
        if not data:
            emit('error', {'message': 'No biometric data provided'})
            return
        analysis = biometric_integrator.analyze_real_time(data)
        if analysis.get('store_data', False):
            biometric_entry = BiometricData(
                heart_rate=data.get('heart_rate'),
                stress_level=data.get('stress_level'),
                hrv_score=data.get('hrv_score'),
                raw_data=json.dumps(data)
            )
            db.session.add(biometric_entry)
            db.session.commit()
        emit('biometric_analysis', {
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logging.error(f"Error processing biometric data: {e}")
        emit('error', {'message': 'Error processing biometric data'})
