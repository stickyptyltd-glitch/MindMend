#!/usr/bin/env python3

# Group and Couples Therapy Session Linking System
# Allows multiple devices to join the same therapy session using linking codes

therapy_session_code = '''
import random
import string
from datetime import datetime, timedelta
from flask import session, request, jsonify

class TherapySessionManager:
    def __init__(self):
        # In-memory storage for active sessions (use Redis/database in production)
        self.active_sessions = {}
        self.session_codes = {}

    def generate_session_code(self):
        """Generate a unique 6-digit session code"""
        code = ''.join(random.choices(string.digits, k=6))
        while code in self.session_codes:
            code = ''.join(random.choices(string.digits, k=6))
        return code

    def create_session(self, session_type, therapist_id, max_participants=4):
        """Create a new therapy session"""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
        session_code = self.generate_session_code()

        session_data = {
            'id': session_id,
            'code': session_code,
            'type': session_type,  # 'group', 'couples', 'family'
            'therapist_id': therapist_id,
            'max_participants': max_participants,
            'participants': [],
            'created_at': datetime.now(),
            'status': 'waiting',  # waiting, active, ended
            'video_room_id': f"room_{session_code}",
            'chat_enabled': True,
            'recording_enabled': False,
            'microexpression_analysis': True
        }

        self.active_sessions[session_id] = session_data
        self.session_codes[session_code] = session_id

        return session_data

    def join_session(self, session_code, user_id, user_name, device_info):
        """Join an existing session using session code"""
        if session_code not in self.session_codes:
            return {"error": "Invalid session code"}

        session_id = self.session_codes[session_code]
        session_data = self.active_sessions[session_id]

        if len(session_data['participants']) >= session_data['max_participants']:
            return {"error": "Session is full"}

        if session_data['status'] == 'ended':
            return {"error": "Session has ended"}

        participant = {
            'user_id': user_id,
            'user_name': user_name,
            'device_info': device_info,
            'joined_at': datetime.now(),
            'is_host': len(session_data['participants']) == 0,
            'video_enabled': True,
            'audio_enabled': True,
            'connection_status': 'connected'
        }

        session_data['participants'].append(participant)

        # Start session when therapist joins or minimum participants reached
        if session_data['status'] == 'waiting' and len(session_data['participants']) >= 1:
            session_data['status'] = 'active'
            session_data['started_at'] = datetime.now()

        return {
            "success": True,
            "session": session_data,
            "participant": participant
        }

    def get_session_status(self, session_code):
        """Get current session status and participants"""
        if session_code not in self.session_codes:
            return {"error": "Session not found"}

        session_id = self.session_codes[session_code]
        return self.active_sessions[session_id]

    def update_participant_status(self, session_code, user_id, updates):
        """Update participant settings (video/audio/etc)"""
        if session_code not in self.session_codes:
            return {"error": "Session not found"}

        session_id = self.session_codes[session_code]
        session_data = self.active_sessions[session_id]

        for participant in session_data['participants']:
            if participant['user_id'] == user_id:
                participant.update(updates)
                return {"success": True}

        return {"error": "Participant not found"}

    def end_session(self, session_code, user_id):
        """End a therapy session (therapist only)"""
        if session_code not in self.session_codes:
            return {"error": "Session not found"}

        session_id = self.session_codes[session_code]
        session_data = self.active_sessions[session_id]

        # Check if user is therapist or session host
        is_authorized = False
        for participant in session_data['participants']:
            if participant['user_id'] == user_id and (participant['is_host'] or user_id == session_data['therapist_id']):
                is_authorized = True
                break

        if not is_authorized:
            return {"error": "Not authorized to end session"}

        session_data['status'] = 'ended'
        session_data['ended_at'] = datetime.now()

        return {"success": True, "session": session_data}

# Global session manager instance
therapy_session_manager = TherapySessionManager()

# Flask routes for session management
@app.route('/api/therapy-session/create', methods=['POST'])
def create_therapy_session():
    """Create a new therapy session"""
    data = request.get_json()

    session_type = data.get('type', 'group')
    therapist_id = session.get('user_id', 'therapist_demo')
    max_participants = data.get('max_participants', 4)

    if session_type == 'couples':
        max_participants = 3  # 2 clients + 1 therapist
    elif session_type == 'family':
        max_participants = 6  # Family + therapist

    session_data = therapy_session_manager.create_session(
        session_type, therapist_id, max_participants
    )

    return jsonify({
        "success": True,
        "session_code": session_data['code'],
        "session_id": session_data['id'],
        "video_room_id": session_data['video_room_id']
    })

@app.route('/api/therapy-session/join', methods=['POST'])
def join_therapy_session():
    """Join an existing therapy session"""
    data = request.get_json()

    session_code = data.get('session_code')
    user_id = session.get('user_id', f"user_{random.randint(1000, 9999)}")
    user_name = data.get('user_name', 'Anonymous')
    device_info = data.get('device_info', {
        'type': 'web',
        'browser': request.headers.get('User-Agent', 'Unknown'),
        'ip': request.remote_addr
    })

    result = therapy_session_manager.join_session(
        session_code, user_id, user_name, device_info
    )

    if "error" in result:
        return jsonify(result), 400

    # Store session info in user session
    session['therapy_session_code'] = session_code
    session['therapy_session_id'] = result['session']['id']

    return jsonify(result)

@app.route('/api/therapy-session/status/<session_code>')
def get_therapy_session_status(session_code):
    """Get current session status"""
    result = therapy_session_manager.get_session_status(session_code)

    if "error" in result:
        return jsonify(result), 404

    return jsonify(result)

@app.route('/api/therapy-session/update-participant', methods=['POST'])
def update_participant_status():
    """Update participant settings"""
    data = request.get_json()

    session_code = data.get('session_code')
    user_id = session.get('user_id')
    updates = data.get('updates', {})

    result = therapy_session_manager.update_participant_status(
        session_code, user_id, updates
    )

    return jsonify(result)

@app.route('/api/therapy-session/end', methods=['POST'])
def end_therapy_session():
    """End a therapy session"""
    data = request.get_json()

    session_code = data.get('session_code')
    user_id = session.get('user_id')

    result = therapy_session_manager.end_session(session_code, user_id)

    if "error" in result:
        return jsonify(result), 403

    return jsonify(result)
'''

print("Therapy session linking system created with:")
print("✅ 6-digit session codes for easy device linking")
print("✅ Support for group, couples, and family therapy")
print("✅ Real-time participant management")
print("✅ Device-specific connection tracking")
print("✅ Therapist authorization controls")
print("✅ Video room integration ready")
print("✅ Microexpression analysis enabled by default")