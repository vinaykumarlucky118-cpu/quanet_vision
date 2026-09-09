import sys
import os

# Automatically add venv site-packages and app root to path if running via base Python
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
venv_site = os.path.join(BASE_DIR, '.venv', 'Lib', 'site-packages')
if venv_site not in sys.path and os.path.exists(venv_site):
    sys.path.insert(0, venv_site)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask, render_template, send_from_directory, g
from config import Config
from database.db import close_db, init_db, query_db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure required runtime folders exist
    os.makedirs(app.config.get('UPLOAD_FOLDER', os.path.join(Config.BASE_DIR, 'uploads')), exist_ok=True)
    os.makedirs(app.config.get('DATASET_DIR', os.path.join(Config.BASE_DIR, 'dataset')), exist_ok=True)
    os.makedirs(app.config.get('MODELS_DIR', os.path.join(Config.BASE_DIR, 'models')), exist_ok=True)
    os.makedirs(os.path.join(Config.BASE_DIR, 'database'), exist_ok=True)

    # Jinja globals
    app.jinja_env.globals.update(max=max, min=min)

    # Database teardown handler
    app.teardown_appcontext(close_db)

    # Context processors for global template variables
    @app.context_processor
    def inject_global_data():
        active_alert_count = 0
        try:
            row = query_db("SELECT COUNT(*) as count FROM alerts WHERE status = 'ACTIVE'", one=True)
            if row:
                active_alert_count = row['count']
        except Exception:
            pass
        return {
            'active_alert_count': active_alert_count,
            'current_user': getattr(g, 'user', None)
        }

    # Static file routes for uploads and dataset sample imagery
    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    @app.route('/dataset-img/<category>/<filename>')
    def dataset_image(category, filename):
        cat_dir = os.path.join(app.config['DATASET_DIR'], 'satellite_images', category)
        return send_from_directory(cat_dir, filename)

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.prediction import prediction_bp
    from routes.satellite import satellite_bp
    from routes.sensor_data import sensor_data_bp
    from routes.analytics import analytics_bp
    from routes.alerts import alerts_bp
    from routes.reports import reports_bp
    from routes.models_info import models_info_bp
    from routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(prediction_bp)
    app.register_blueprint(satellite_bp)
    app.register_blueprint(sensor_data_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(alerts_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(models_info_bp)
    app.register_blueprint(api_bp)

    # Friendly Custom Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    @app.errorhandler(413)
    def request_entity_too_large(e):
        return render_template('500.html', error_message="File upload is too large. Maximum allowed size is 16 MB."), 413

    return app

if __name__ == '__main__':
    if not os.path.exists(Config.DATABASE):
        init_db()
        from database.seed_data import seed_database
        seed_database()

    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    print(f"\n=======================================================")
    print(f"  QuaNet Vision: Deep Learning Water Quality Prediction")
    print(f"  Running locally on: http://127.0.0.1:{port}")
    print(f"  Demo Credentials: {Config.DEMO_ADMIN_EMAIL} / {Config.DEMO_ADMIN_PASSWORD}")
    print(f"=======================================================\n", flush=True)
    app.run(host='0.0.0.0', port=port, debug=False)
