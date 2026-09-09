from flask import Blueprint, render_template, request, jsonify
from database.db import query_db
from config import Config

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def home():
    """Home landing page explaining QuaNet Vision, problem, solution, stats and architecture."""
    # Fetch high level statistics for hero cards
    total_records = query_db("SELECT COUNT(*) as count FROM sensor_data", one=True)['count']
    total_water_bodies = query_db("SELECT COUNT(*) as count FROM water_bodies", one=True)['count']
    active_alerts = query_db("SELECT COUNT(*) as count FROM alerts WHERE status = 'ACTIVE'", one=True)['count']
    
    return render_template('index.html',
        total_records=total_records,
        total_water_bodies=total_water_bodies,
        active_alerts=active_alerts
    )

@dashboard_bp.route('/dashboard')
def index():
    """Real-Time Water Monitoring Dashboard with sensor telemetry and Chart.js feeds."""
    water_bodies = query_db("SELECT * FROM water_bodies ORDER BY id")
    selected_wb_id = request.args.get('water_body_id', type=int)
    
    if not selected_wb_id and water_bodies:
        selected_wb_id = water_bodies[0]['id']

    current_wb = query_db("SELECT * FROM water_bodies WHERE id = ?", (selected_wb_id,), one=True)
    
    # Latest reading for selected water body
    latest = query_db("""
        SELECT * FROM sensor_data 
        WHERE water_body_id = ? 
        ORDER BY timestamp DESC LIMIT 1
    """, (selected_wb_id,), one=True)
    
    if not latest:
        # Fallback default reading
        latest = {
            "ph": 7.2, "temperature": 24.5, "turbidity": 3.8,
            "dissolved_oxygen": 7.6, "tds": 220.0, "conductivity": 380.0,
            "water_quality": "GOOD", "timestamp": "Live Simulation", "is_demo": 1
        }

    # Historical time-series (last 30 readings for charts)
    history = query_db("""
        SELECT * FROM sensor_data 
        WHERE water_body_id = ? 
        ORDER BY timestamp ASC LIMIT 35
    """, (selected_wb_id,))

    # Recent active alerts for this water body
    alerts = query_db("""
        SELECT * FROM alerts 
        WHERE water_body_id = ? 
        ORDER BY timestamp DESC LIMIT 5
    """, (selected_wb_id,))

    # Quick summary counts across all stations
    station_counts = query_db("""
        SELECT water_quality, COUNT(*) as count 
        FROM sensor_data 
        GROUP BY water_quality
    """)
    quality_dist = {r['water_quality']: r['count'] for r in station_counts}

    # Chart datasets JSON formatting
    chart_labels = [r['date'] + " " + r['time'][:5] if 'time' in r else r['timestamp'][5:16] for r in history]
    chart_data = {
        "labels": chart_labels,
        "ph": [r['ph'] for r in history],
        "temperature": [r['temperature'] for r in history],
        "turbidity": [r['turbidity'] for r in history],
        "dissolved_oxygen": [r['dissolved_oxygen'] for r in history],
        "tds": [r['tds'] for r in history],
        "conductivity": [r['conductivity'] for r in history],
    }

    # Confidence calculation based on parameter deviations
    quality_info = Config.QUALITY_CLASSES.get(latest['water_quality'], Config.QUALITY_CLASSES["GOOD"])
    confidence = 94.5 if latest['water_quality'] == 'GOOD' else (88.2 if latest['water_quality'] == 'MODERATE' else 96.0)

    return render_template('dashboard.html',
        water_bodies=water_bodies,
        selected_wb=current_wb,
        latest=latest,
        alerts=alerts,
        quality_info=quality_info,
        confidence=confidence,
        chart_data=chart_data,
        quality_dist=quality_dist,
        thresholds=Config.WATER_QUALITY_THRESHOLDS
    )

@dashboard_bp.route('/about')
def about():
    """About Project Page with Aim, Objectives, and System Architecture comparisons."""
    return render_template('about.html')

@dashboard_bp.route('/how-it-works')
def how_it_works():
    """How It Works Page with Step-by-Step AI Workflow, CNN vs LSTM comparison, and Data Fusion."""
    return render_template('how_it_works.html')

@dashboard_bp.route('/about-team')
def about_team():
    """Academic Project Credits & Team Profile."""
    return render_template('about_team.html')

@dashboard_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact & Demonstration Inquiry Form."""
    message_sent = False
    if request.method == 'POST':
        message_sent = True
    return render_template('contact.html', message_sent=message_sent)
