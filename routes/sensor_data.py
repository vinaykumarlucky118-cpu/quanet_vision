import os
import io
import csv
import random
import datetime
import pandas as pd
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, jsonify
from werkzeug.utils import secure_filename
from database.db import query_db, execute_db, get_db
from config import Config

sensor_data_bp = Blueprint('sensor_data', __name__)

@sensor_data_bp.route('/sensor-data')
def index():
    """Searchable, filterable, and paginated sensor readings table."""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    
    # Filter parameters
    search = request.args.get('search', '').strip()
    status = request.args.get('status', '').strip()
    wb_id = request.args.get('water_body_id', type=int)
    
    where_clauses = []
    params = []

    if search:
        where_clauses.append("(sd.date LIKE ? OR sd.time LIKE ? OR wb.name LIKE ?)")
        search_param = f"%{search}%"
        params.extend([search_param, search_param, search_param])
        
    if status and status in ['GOOD', 'MODERATE', 'POOR']:
        where_clauses.append("sd.water_quality = ?")
        params.append(status)

    if wb_id:
        where_clauses.append("sd.water_body_id = ?")
        params.append(wb_id)

    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    # Count total matching rows
    count_sql = f"""
        SELECT COUNT(*) as count 
        FROM sensor_data sd 
        LEFT JOIN water_bodies wb ON sd.water_body_id = wb.id 
        {where_sql}
    """
    total_records = query_db(count_sql, tuple(params), one=True)['count']
    total_pages = max(1, (total_records + per_page - 1) // per_page)

    # Fetch paginated rows
    query_sql = f"""
        SELECT sd.*, wb.name as water_body_name 
        FROM sensor_data sd 
        LEFT JOIN water_bodies wb ON sd.water_body_id = wb.id 
        {where_sql}
        ORDER BY sd.timestamp DESC 
        LIMIT ? OFFSET ?
    """
    query_params = list(params) + [per_page, offset]
    records = query_db(query_sql, tuple(query_params))

    water_bodies = query_db("SELECT id, name FROM water_bodies ORDER BY id")

    return render_template('sensor_data.html',
        records=records,
        page=page,
        total_pages=total_pages,
        total_records=total_records,
        search=search,
        status=status,
        selected_wb=wb_id,
        water_bodies=water_bodies,
        quality_classes=Config.QUALITY_CLASSES
    )

@sensor_data_bp.route('/sensor-data/sample-template')
def sample_template():
    """Generates and downloads a clean sample CSV template for user uploads."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["date", "time", "ph", "temperature", "turbidity", "dissolved_oxygen", "tds", "conductivity", "water_quality"])
    
    now = datetime.datetime.now()
    writer.writerow([now.strftime("%Y-%m-%d"), "08:00:00", "7.35", "23.5", "2.8", "7.8", "190.0", "310.0", "GOOD"])
    writer.writerow([now.strftime("%Y-%m-%d"), "09:00:00", "8.65", "27.0", "8.4", "5.2", "420.0", "690.0", "MODERATE"])
    writer.writerow([now.strftime("%Y-%m-%d"), "10:00:00", "5.20", "31.5", "38.0", "2.1", "880.0", "1520.0", "POOR"])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=quanet_sample_template.csv"}
    )

@sensor_data_bp.route('/sensor-data/simulate-packet', methods=['POST'])
def simulate_packet():
    """Simulates injection of a new real-time IoT packet during live demonstration."""
    wb_id = request.form.get('water_body_id', 1, type=int)
    quality_mode = request.form.get('quality_mode', 'RANDOM')

    if quality_mode == 'GOOD':
        ph = round(random.uniform(7.1, 7.8), 2)
        temp = round(random.uniform(22.0, 26.0), 1)
        turb = round(random.uniform(1.8, 3.8), 2)
        do = round(random.uniform(7.2, 8.5), 2)
        tds = round(random.uniform(150.0, 240.0), 1)
        ec = round(tds * 1.5, 1)
        quality = "GOOD"
    elif quality_mode == 'POOR':
        ph = round(random.choice([5.2, 9.4]), 2)
        temp = round(random.uniform(30.0, 34.0), 1)
        turb = round(random.uniform(25.0, 55.0), 2)
        do = round(random.uniform(1.8, 3.2), 2)
        tds = round(random.uniform(750.0, 1100.0), 1)
        ec = round(tds * 1.8, 1)
        quality = "POOR"
    else: # Moderate or Random
        ph = round(random.uniform(6.2, 8.8), 2)
        temp = round(random.uniform(25.0, 29.0), 1)
        turb = round(random.uniform(6.0, 12.0), 2)
        do = round(random.uniform(4.5, 6.0), 2)
        tds = round(random.uniform(340.0, 520.0), 1)
        ec = round(tds * 1.6, 1)
        quality = "MODERATE"

    now = datetime.datetime.now()
    d_str = now.strftime("%Y-%m-%d")
    t_str = now.strftime("%H:%M:%S")
    ts_str = now.strftime("%Y-%m-%d %H:%M:%S")

    rec_id = execute_db("""
        INSERT INTO sensor_data (
            water_body_id, date, time, timestamp, ph, temperature,
            turbidity, dissolved_oxygen, tds, conductivity, water_quality, is_demo, source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        wb_id, d_str, t_str, ts_str, ph, temp, turb, do, tds, ec, quality, 1, "Simulated IoT Sensor Node"
    ))

    if quality == 'POOR':
        execute_db("""
            INSERT INTO alerts (timestamp, water_body_id, severity, parameter, value, threshold_exceeded, message, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ts_str, wb_id, "CRITICAL", "Live Injected Anomaly", turb,
            "Critical Safe Threshold Breach",
            f"Live anomalous reading recorded: Turbidity {turb} NTU, DO {do} mg/L, pH {ph}.",
            "ACTIVE"
        ))

    flash(f"Simulated live telemetry packet recorded (#{rec_id}) with status: {quality} (Turbidity: {turb} NTU, DO: {do} mg/L)!", "success")
    return redirect(url_for('dashboard.index', water_body_id=wb_id))

@sensor_data_bp.route('/sensor-data/upload-csv', methods=['POST'])
def upload_csv():
    """Uploads and validates a user CSV dataset, importing records into the database."""
    if 'csv_file' not in request.files:
        flash("No file part provided in upload request.", "danger")
        return redirect(url_for('sensor_data.index'))

    file = request.files['csv_file']
    if file.filename == '':
        flash("No CSV file selected for upload.", "warning")
        return redirect(url_for('sensor_data.index'))

    if not file.filename.lower().endswith('.csv'):
        flash("Invalid file format. Please upload a standard comma-separated .csv file.", "danger")
        return redirect(url_for('sensor_data.index'))

    wb_id = request.form.get('water_body_id', 1, type=int)

    try:
        df = pd.read_csv(file)
        df.columns = [str(c).strip().lower().replace(' ', '_') for c in df.columns]

        col_aliases = {
            'ph': 'ph',
            'temp': 'temperature', 'temperature': 'temperature',
            'turbidity': 'turbidity', 'turb': 'turbidity',
            'do': 'dissolved_oxygen', 'dissolved_oxygen': 'dissolved_oxygen', 'dissolvedoxygen': 'dissolved_oxygen',
            'tds': 'tds',
            'ec': 'conductivity', 'conductivity': 'conductivity', 'elect_cond': 'conductivity'
        }

        standardized_df = pd.DataFrame()
        missing_required = []
        
        for std_col, orig_key in [('ph', 'ph'), ('temperature', 'temperature'), ('turbidity', 'turbidity'),
                                  ('dissolved_oxygen', 'dissolved_oxygen'), ('tds', 'tds'), ('conductivity', 'conductivity')]:
            found = False
            for c in df.columns:
                if col_aliases.get(c) == std_col:
                    standardized_df[std_col] = pd.to_numeric(df[c], errors='coerce')
                    found = True
                    break
            if not found:
                missing_required.append(std_col)

        if missing_required:
            flash(f"CSV Validation Error: Missing required columns: {', '.join(missing_required)}. Expected: ph, temperature, turbidity, dissolved_oxygen, tds, conductivity.", "danger")
            return redirect(url_for('sensor_data.index'))

        now = datetime.datetime.now()
        dates = df['date'] if 'date' in df.columns else [now.strftime("%Y-%m-%d")] * len(df)
        times = df['time'] if 'time' in df.columns else [now.strftime("%H:%M:%S")] * len(df)
        
        imported_count = 0
        conn = get_db()
        cursor = conn.cursor()

        for idx, row in standardized_df.iterrows():
            if pd.isna(row['ph']) or pd.isna(row['turbidity']):
                continue

            row_ph = float(row['ph'])
            row_temp = float(row['temperature'])
            row_turb = float(row['turbidity'])
            row_do = float(row['dissolved_oxygen'])
            row_tds = float(row['tds'])
            row_ec = float(row['conductivity'])

            is_poor = (row_do < 4.0 or row_turb > 15.0 or row_ph < 6.0 or row_ph > 9.0 or row_tds > 600.0)
            is_mod = (row_do < 6.0 or row_turb > 5.0 or row_ph < 6.5 or row_ph > 8.5 or row_tds > 300.0)
            
            if 'water_quality' in df.columns and pd.notna(df['water_quality'].iloc[idx]):
                quality = str(df['water_quality'].iloc[idx]).strip().upper()
                if quality not in ['GOOD', 'MODERATE', 'POOR']:
                    quality = 'POOR' if is_poor else ('MODERATE' if is_mod else 'GOOD')
            else:
                quality = 'POOR' if is_poor else ('MODERATE' if is_mod else 'GOOD')

            d_str = str(dates.iloc[idx])[:10]
            t_str = str(times.iloc[idx])[:8]
            ts_str = f"{d_str} {t_str}"

            cursor.execute("""
                INSERT INTO sensor_data (
                    water_body_id, date, time, timestamp, ph, temperature,
                    turbidity, dissolved_oxygen, tds, conductivity, water_quality, is_demo, source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                wb_id, d_str, t_str, ts_str,
                row_ph, row_temp, row_turb, row_do, row_tds, row_ec,
                quality, 0, "User Uploaded CSV"
            ))

            if quality == 'POOR':
                cursor.execute("""
                    INSERT INTO alerts (timestamp, water_body_id, severity, parameter, value, threshold_exceeded, message, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    ts_str, wb_id, "CRITICAL", "Multi-parameter Anomaly", row_turb,
                    "Imported Threshold Violation",
                    f"Water quality deterioration imported from CSV at station ID {wb_id}. (Turbidity: {row_turb} NTU, DO: {row_do} mg/L).",
                    "ACTIVE"
                ))

            imported_count += 1

        conn.commit()
        flash(f"Successfully validated and imported {imported_count} sensor telemetry rows from '{file.filename}'!", "success")

    except Exception as e:
        flash(f"Failed to parse CSV file: {str(e)}", "danger")

    return redirect(url_for('sensor_data.index'))

@sensor_data_bp.route('/sensor-data/export-csv')
def export_csv():
    """Exports sensor data as a downloadable CSV."""
    records = query_db("""
        SELECT sd.date, sd.time, sd.ph, sd.temperature, sd.turbidity,
               sd.dissolved_oxygen, sd.tds, sd.conductivity, sd.water_quality,
               wb.name as water_body_name, sd.source
        FROM sensor_data sd
        LEFT JOIN water_bodies wb ON sd.water_body_id = wb.id
        ORDER BY sd.timestamp DESC
    """)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["date", "time", "ph", "temperature", "turbidity", "dissolved_oxygen", "tds", "conductivity", "water_quality", "station_name", "source"])

    for r in records:
        writer.writerow([
            r['date'], r['time'], r['ph'], r['temperature'], r['turbidity'],
            r['dissolved_oxygen'], r['tds'], r['conductivity'], r['water_quality'],
            r['water_body_name'], r['source']
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=quanet_sensor_telemetry_export.csv"}
    )
