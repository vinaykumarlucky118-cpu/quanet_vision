from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from database.db import query_db, execute_db

alerts_bp = Blueprint('alerts', __name__)

@alerts_bp.route('/alerts')
def index():
    """Water Quality Anomaly and Environmental Alert Feed."""
    severity = request.args.get('severity', '').strip()
    status = request.args.get('status', 'ACTIVE').strip()
    wb_id = request.args.get('water_body_id', type=int)

    where_clauses = []
    params = []

    if status and status != 'ALL':
        where_clauses.append("a.status = ?")
        params.append(status)

    if severity:
        where_clauses.append("a.severity = ?")
        params.append(severity)

    if wb_id:
        where_clauses.append("a.water_body_id = ?")
        params.append(wb_id)

    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    alerts = query_db(f"""
        SELECT a.*, wb.name as water_body_name, wb.location as water_body_location
        FROM alerts a
        LEFT JOIN water_bodies wb ON a.water_body_id = wb.id
        {where_sql}
        ORDER BY a.timestamp DESC
    """, tuple(params))

    # Alert summary metrics
    crit_count = query_db("SELECT COUNT(*) as count FROM alerts WHERE severity = 'CRITICAL' AND status = 'ACTIVE'", one=True)['count']
    warn_count = query_db("SELECT COUNT(*) as count FROM alerts WHERE severity = 'WARNING' AND status = 'ACTIVE'", one=True)['count']
    resolved_count = query_db("SELECT COUNT(*) as count FROM alerts WHERE status = 'RESOLVED'", one=True)['count']

    water_bodies = query_db("SELECT id, name FROM water_bodies ORDER BY id")

    return render_template('alerts.html',
        alerts=alerts,
        crit_count=crit_count,
        warn_count=warn_count,
        resolved_count=resolved_count,
        selected_severity=severity,
        selected_status=status,
        selected_wb=wb_id,
        water_bodies=water_bodies
    )

@alerts_bp.route('/alerts/resolve/<int:alert_id>', methods=['POST'])
def resolve(alert_id):
    """Marks an alert as resolved."""
    execute_db("UPDATE alerts SET status = 'RESOLVED' WHERE id = ?", (alert_id,))
    flash(f"Alert #{alert_id} has been marked as RESOLVED.", "success")
    return redirect(url_for('alerts.index'))

@alerts_bp.route('/alerts/dismiss/<int:alert_id>', methods=['POST'])
def dismiss(alert_id):
    """Dismisses an alert."""
    execute_db("UPDATE alerts SET status = 'DISMISSED' WHERE id = ?", (alert_id,))
    flash(f"Alert #{alert_id} has been DISMISSED.", "info")
    return redirect(url_for('alerts.index'))
