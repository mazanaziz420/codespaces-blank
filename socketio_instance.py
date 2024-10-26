from flask_socketio import SocketIO

socketio = SocketIO(cors_allowed_origins="*")

@socketio.on('connect', namespace='/notifications')
def handle_connect():
    print("Client connected")

@socketio.on('disconnect', namespace='/notifications')
def handle_disconnect():
    print("Client disconnected")