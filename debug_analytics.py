from app import create_app
from flask import json
import traceback

app, socketio = create_app()

with app.app_context():
    try:
        from routes.analytics_routes import analytics_dashboard
        from flask import request
        
        # Simulate request
        with app.test_request_context('/api/analytics/dashboard'):
            response, status = analytics_dashboard()
            print(f"Status: {status}")
            print(f"Data: {response.get_data(as_text=True)}")
    except Exception as e:
        print(f"TEST FAILED: {e}")
        traceback.print_exc()
