"""
ClinicAI — Flask Application Factory
=====================================
Creates and configures the Flask app with all blueprints, extensions,
Socket.IO, and the Redis event listener.
"""
from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO

load_dotenv()
os.environ["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("clinic_ai.app")

# ── App Factory ───────────────────────────────────────────────────────────────

def create_app() -> tuple[Flask, SocketIO]:
    app = Flask(__name__)

    # ── CORS ──────────────────────────────────────────────────────────────────
    CORS(app, resources={r"/*": {"origins": "*"}})

    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = app.make_response("")
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add("Access-Control-Allow-Headers", "Authorization, Content-Type, Accept, Origin, X-Requested-With")
            response.headers.add("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
            return response

    @app.after_request
    def add_cors_headers(response):
        response.headers.set("Access-Control-Allow-Origin", "*")
        response.headers.set("Access-Control-Allow-Headers", "Authorization, Content-Type, Accept, Origin, X-Requested-With")
        response.headers.set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        return response

    @app.errorhandler(Exception)
    def handle_global_error(e):
        logger.error(f"Global unhandled exception: {e}", exc_info=True)
        response = jsonify({"error": "Service Error", "detail": str(e)})
        response.status_code = 500
        return response


    # ── SocketIO ──────────────────────────────────────────────────────────────
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

    # Register socket events (chat, real-time events, etc.)
    from sockets import register_socket_events
    register_socket_events(socketio)

    # ── Database ──────────────────────────────────────────────────────────────
    db_user = os.getenv("DB_USER",     "root")
    db_pass = os.getenv("DB_PASSWORD", "")
    db_host = os.getenv("DB_HOST",     "localhost")
    db_port = os.getenv("DB_PORT",     "3306")
    db_name = os.getenv("DB_NAME",     "mediagents_db")

    app.config["SQLALCHEMY_DATABASE_URI"]        = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"]                     = os.getenv("SECRET_KEY", "dev-secret-key")

    from database import db
    db.init_app(app)
    with app.app_context():
        db.create_all()
        # Ensure latest schema columns exist (create_all doesn't update existing tables)
        from sqlalchemy import text
        try:
            db.session.execute(text("ALTER TABLE patient_vitals ADD COLUMN glucose DECIMAL(5,2) AFTER rr"))
            db.session.commit()
            logger.info("Added missing 'glucose' column")
        except Exception:
            db.session.rollback()
        try:
            db.session.execute(text("ALTER TABLE patient_vitals ADD COLUMN news2_score INT DEFAULT 0 AFTER glucose"))
            db.session.commit()
            logger.info("Added missing 'news2_score' column")
        except Exception:
            db.session.rollback()
        # Payment columns for appointments
        for col_sql in [
            "ALTER TABLE appointments ADD COLUMN payment_status VARCHAR(20) DEFAULT 'pending'",
            "ALTER TABLE appointments ADD COLUMN payment_amount DECIMAL(10,2) DEFAULT 500.00",
            "ALTER TABLE appointments ADD COLUMN payment_txn_id VARCHAR(100)",
            "ALTER TABLE appointments ADD COLUMN payment_method VARCHAR(30) DEFAULT 'UPI'",
            "ALTER TABLE appointments ADD COLUMN paid_at DATETIME",
        ]:
            try:
                db.session.execute(text(col_sql))
                db.session.commit()
            except Exception:
                db.session.rollback()
        logger.info("✅ Database initialized and patched")

    # ── Blueprints ────────────────────────────────────────────────────────────
    from routes.auth_routes        import auth_bp
    from routes.triage_routes      import triage_bp
    from routes.patient_routes     import patient_bp
    from routes.clinical_routes    import clinical_bp
    from routes.admin_routes       import admin_bp
    from routes.portal_routes      import portal_bp
    from routes.appointment_routes import appointment_bp
    from routes.medication_routes  import medication_bp
    from routes.monitoring_routes  import monitoring_bp
    from routes.analytics_routes   import analytics_bp
    from routes.agent_routes       import agent_bp
    from routes.report_routes      import report_bp

    # Core API Routes
    app.register_blueprint(auth_bp,         url_prefix="/api/auth")
    app.register_blueprint(triage_bp,       url_prefix="/api/triage")
    app.register_blueprint(patient_bp,      url_prefix="/api/patients")
    app.register_blueprint(clinical_bp,     url_prefix="/api/clinical")
    app.register_blueprint(admin_bp,        url_prefix="/api/admin")
    app.register_blueprint(portal_bp,       url_prefix="/api/portal")
    app.register_blueprint(appointment_bp,  url_prefix="/api/appointments")
    app.register_blueprint(medication_bp,   url_prefix="/api/medications")
    # New: Monitoring, Analytics, and Agent proxy routes
    app.register_blueprint(monitoring_bp,   url_prefix="/api/monitoring")
    app.register_blueprint(analytics_bp,    url_prefix="/api/analytics")
    app.register_blueprint(agent_bp,        url_prefix="/api/agents")
    app.register_blueprint(report_bp,       url_prefix="/api/reports")

    logger.info("✅ All blueprints registered")

    # ── System Endpoints ──────────────────────────────────────────────────────

    @app.route("/api/health", methods=["GET"])
    def health_check():
        from database import db as _db
        try:
            _db.session.execute(_db.text("SELECT 1"))
            db_status = "connected"
        except Exception:
            db_status = "disconnected"
        return jsonify({
            "status"   : "healthy",
            "service"  : "ClinicAI Backend",
            "database" : db_status,
            "version"  : "3.0.1",
        }), 200

    @app.route("/api/routes", methods=["GET"])
    def list_routes():
        """Return all registered routes for API introspection."""
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                "path"   : str(rule),
                "methods": sorted([m for m in rule.methods if m not in ("HEAD", "OPTIONS")]),
            })
        return jsonify(sorted(routes, key=lambda r: r["path"])), 200

    # ── Redis Event Listener ──────────────────────────────────────────────────
    if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        from event_listener import start_redis_listener
        start_redis_listener(
            socketio,
            app,
            redis_host=os.getenv("REDIS_HOST", "localhost"),
            redis_port=int(os.getenv("REDIS_PORT", 6379)),
        )
        logger.info("✅ Redis event listener started")

    logger.info("🚀 ClinicAI Backend ready — http://localhost:5000")
    return app, socketio


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app, socketio = create_app()
    socketio.run(app, debug=True, port=5000)
