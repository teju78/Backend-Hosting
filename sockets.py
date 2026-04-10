import requests
import os
from flask_socketio import emit
from flask import current_app
from database import db
from models.chat import ChatMessage

def register_socket_events(socketio):
    @socketio.on('connect')
    def handle_connect():
        print("✅ Client connected to WebSocket")

    @socketio.on('disconnect')
    def handle_disconnect():
        print("❌ Client disconnected")

    @socketio.on('chat_message')
    def handle_chat_message(data):
        """
        Proxies chat messages from Frontend to Agent 08 (Chat Assistant).
        """
        patient_id = data.get('patient_id', 'anonymous')
        message = data.get('message', '')
        
        print(f"💬 Chat from {patient_id}: {message}")
        
        try:
            # Forward to Agent 08
            agent_url = os.getenv('AGENT_08_URL', 'http://127.0.0.1:8008')
            print(f"📡 Forwarding to Agent 08 at {agent_url}")
            resp = requests.post(f"{agent_url}/chat", json={
                "patient_id": patient_id,
                "message": message
            })
            
            # Save User Message with explicit context
            with current_app.app_context():
                try:
                    user_msg = ChatMessage(patient_id=patient_id, role='user', content=message)
                    db.session.add(user_msg)
                    db.session.commit()
                    print(f"💾 User message saved to DB for {patient_id}")
                except Exception as db_err:
                    print(f"❌ DB Error (User Message): {db_err}")
                    db.session.rollback()

            if resp.status_code == 200:
                result = resp.json()
                assistant_text = result.get("response_text", "I'm processing that...")
                intent = result.get("intent", "general")

                # Save Assistant Message with explicit context
                with current_app.app_context():
                    try:
                        assistant_msg = ChatMessage(
                            patient_id=patient_id, 
                            role='assistant', 
                            content=assistant_text,
                            intent=intent
                        )
                        db.session.add(assistant_msg)
                        db.session.commit()
                        print(f"💾 Assistant message saved to DB for {patient_id}")
                    except Exception as db_err:
                        print(f"❌ DB Error (Assistant Message): {db_err}")
                        db.session.rollback()

                # Send back to Frontend
                emit('chat_response', {
                    "role": "assistant",
                    "content": assistant_text,
                    "intent": intent,
                    "escalation_required": result.get("escalation_required", False)
                })
            else:
                emit('chat_response', {"role": "assistant", "content": "I'm having trouble connecting to my knowledge base."})
                
        except Exception as e:
            print(f"❌ Chat Proxy Error: {e}")
            emit('chat_response', {"role": "assistant", "content": "My communication modules are temporarily offline."})
