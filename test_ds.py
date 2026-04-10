import traceback
from app import create_app
from database import db
from sqlalchemy import text
app, _ = create_app()
app.app_context().push()
from routes.clinical_routes import get_decision_support

try:
    with app.test_request_context():
        res = get_decision_support('3d3da520-1692-4af2-9b2e-ac72a4e6ae1e')
        import json
        print("RESULT:")
        print(res.get_data(as_text=True))
except Exception as e:
    print("ERROR OCCURRED:")
    traceback.print_exc()
