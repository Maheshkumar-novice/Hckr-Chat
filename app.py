from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from datetime import datetime

from config import Config
from database import db

app = Flask(__name__)
app.config.from_object(Config)

socketio = SocketIO(app, cors_allowed_origins="*")

active_users = {}
typing_users = set()
@app.route('/hckr_chat_')
def hckr_chat_index():
    return render_template('chat.html')

@socketio.on('hckr_chat_connect')
def hckr_chat_handle_connect():
    print(f"Client connected: {request.sid}")

@socketio.on('hckr_chat_disconnect')
def hckr_chat_handle_disconnect():
    if request.sid in active_users:
        user_data = active_users[request.sid]
        emit('hckr_chat_user_left', {'username': user_data['username']}, broadcast=True)
        typing_users.discard(request.sid)
        emit('hckr_chat_typing_update', {'typing_users': list(typing_users)}, broadcast=True)
        del active_users[request.sid]
    print(f"Client disconnected: {request.sid}")

@socketio.on('hckr_chat_join')
def hckr_chat_handle_join(data):
    username = data.get('username')
    
    if not username:
        emit('hckr_chat_error', {'message': 'Username required'})
        return
    
    active_users[request.sid] = {'username': username}
    
    messages = db.execute("""
        SELECT username, message, timestamp 
        FROM messages 
        ORDER BY timestamp DESC 
        LIMIT 50
    """)
    
    emit('hckr_chat_load_messages', {
        'messages': [dict(msg) for msg in reversed(messages)]
    })
    
    emit('hckr_chat_user_joined', {'username': username}, broadcast=True)
    
    users = [user['username'] for user in active_users.values()]
    emit('hckr_chat_user_list', {'users': users}, broadcast=True)

@socketio.on('hckr_chat_message')
def hckr_chat_handle_message(data):
    if request.sid not in active_users:
        emit('hckr_chat_error', {'message': 'Not connected'})
        return
    
    user_data = active_users[request.sid]
    username = user_data['username']
    message = data.get('message', '').strip()
    
    if not message:
        return
    
    if len(message) > Config.MAX_MESSAGE_LENGTH:
        emit('hckr_chat_error', {'message': f'Message too long (max {Config.MAX_MESSAGE_LENGTH} characters)'})
        return
    
    if message.startswith('/'):
        hckr_chat_handle_command(message, username)
        return
    
    db.execute("""
        INSERT INTO messages (username, message, timestamp) 
        VALUES (?, ?, ?)
    """, (username, message, datetime.now()))
    
    emit('hckr_chat_message', {
        'username': username,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }, broadcast=True)

def hckr_chat_handle_command(message, username):
    parts = message[1:].split(' ', 1)
    command = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ''
    
    if command == 'help':
        emit('hckr_chat_system_message', {
            'message': 'Available commands: /help, /users, /nick <new_name>, /me <action>'
        })
    
    elif command == 'users':
        users = [user['username'] for user in active_users.values()]
        emit('hckr_chat_system_message', {
            'message': f'Users online: {", ".join(users)}'
        })
    
    elif command == 'nick':
        if args:
            old_username = username
            new_username = args.strip()
            active_users[request.sid]['username'] = new_username
            emit('hckr_chat_nick_change', {
                'old_nick': old_username,
                'new_nick': new_username
            }, broadcast=True)
        else:
            emit('hckr_chat_system_message', {'message': 'Usage: /nick <new_name>'})
    
    elif command == 'me':
        if args:
            db.execute("""
                INSERT INTO messages (username, message, timestamp) 
                VALUES (?, ?, ?)
            """, (username, f"* {args}", datetime.now()))
            
            emit('hckr_chat_message', {
                'username': username,
                'message': args,
                'timestamp': datetime.now().isoformat(),
                'type': 'action'
            }, broadcast=True)
        else:
            emit('hckr_chat_system_message', {'message': 'Usage: /me <action>'})
    
    else:
        emit('hckr_chat_system_message', {'message': f'Unknown command: /{command}'})

@socketio.on('hckr_chat_typing')
def hckr_chat_handle_typing(data):
    if request.sid not in active_users:
        return
    
    is_typing = data.get('typing', False)
    username = active_users[request.sid]['username']
    
    if is_typing:
        typing_users.add(request.sid)
    else:
        typing_users.discard(request.sid)
    
    typing_usernames = [active_users[sid]['username'] for sid in typing_users if sid in active_users]
    emit('hckr_chat_typing_update', {'typing_users': typing_usernames}, broadcast=True)

if __name__ == '__main__':
    socketio.run(
        app, 
        host=Config.HOST, 
        port=Config.PORT, 
        debug=Config.DEBUG,
        allow_unsafe_werkzeug=True
    )