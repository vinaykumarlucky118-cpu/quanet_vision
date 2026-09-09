import os
import json
import datetime
from flask import Blueprint, request, jsonify
from database.db import query_db, execute_db
from models.fusion import fusion_engine
from config import Config

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/sensor-data', methods=['GET'])
def get_sensor_data():
    """Returns recent sensor readings."""
    wb_id = request.args.get('water_body_id', type=int)
    limit = min(request.args.get('limit', 50, type=int), 200)

    where_sql = "WHERE water_body_id = ?" if wb_id else ""
    params = (wb_id, limit) if wb_id else (limit,)

    records = query_db(f"""
        SELECT sd.*, wb.name as water_body_name
        FROM sensor_data sd
        LEFT JOIN water_bodies wb ON sd.water_body_id = wb.id
        {where_sql}
        ORDER BY sd.timestamp DESC
        LIMIT ?
    """, params)

    return jsonify({
        "status": "success",
        "count": len(records),
        "data": records
    })

@api_bp.route('/predict', methods=['POST'])
def predict_api():
    """REST API for single and multimodal water quality prediction."""
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"status": "error", "message": "Invalid JSON body provided."}), 400

    try:
        model_choice = data.get('model_choice', 'CNN_LSTM_FUSION')
        result = fusion_engine.predict(data, image_path=data.get('image_path'), model_choice=model_choice)
        return jsonify({"status": "success", "result": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@api_bp.route('/iot-ingest', methods=['POST'])
def iot_ingest():
    """
    IoT Sensor Node Telemetry Ingestion Endpoint.
    Designed for future hardware connectivity (ESP32, Arduino, Raspberry Pi).
    """
    payload = request.get_json(force=True, silent=True)
    if not payload:
        return jsonify({"status": "error", "message": "Expected JSON payload from IoT device."}), 400

    try:
        wb_id = payload.get('water_body_id', 1)
        ph = float(payload['ph'])
        temp = float(payload.get('temperature', payload.get('temp', 25.0)))
        turbidity = float(payload['turbidity'])
        do = float(payload.get('dissolved_oxygen', payload.get('do', 7.0)))
        tds = float(payload['tds'])
        ec = float(payload.get('conductivity', payload.get('ec', tds * 1.6)))

        # Evaluate quality class
        is_poor = (do < 4.0 or turbidity > 15.0 or ph < 6.0 or ph > 9.0 or tds > 600.0)
        is_mod = (do < 6.0 or turbidity > 5.0 or ph < 6.5 or ph > 8.5 or tds > 300.0)
        quality = "POOR" if is_poor else ("MODERATE" if is_mod else "GOOD")

        now = datetime.datetime.now()
        d_str = now.strftime("%Y-%m-%d")
        t_str = now.strftime("%H:%M:%S")
        ts_str = now.strftime("%Y-%m-%d %H:%M:%S")

        node_id = payload.get('device_id', f'ESP32-Node-{wb_id}')

        record_id = execute_db("""
            INSERT INTO sensor_data (
                water_body_id, date, time, timestamp, ph, temperature,
                turbidity, dissolved_oxygen, tds, conductivity, water_quality, is_demo, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            wb_id, d_str, t_str, ts_str, ph, temp, turbidity, do, tds, ec,
            quality, 0, f"Live Telemetry ({node_id})"
        ))

        # Check for alert trigger
        alert_created = False
        if quality == "POOR":
            execute_db("""
                INSERT INTO alerts (timestamp, water_body_id, severity, parameter, value, threshold_exceeded, message, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ts_str, wb_id, "CRITICAL", "Live IoT Ingestion Anomaly", turbidity,
                "Exceeded Environmental Safe Limit",
                f"Severe water quality degradation detected in real-time from device {node_id}.",
                "ACTIVE"
            ))
            alert_created = True

        return jsonify({
            "status": "success",
            "message": "Telemetry received and recorded successfully.",
            "record_id": record_id,
            "evaluated_quality": quality,
            "alert_triggered": alert_created,
            "timestamp": ts_str
        }), 201

    except KeyError as ke:
        return jsonify({"status": "error", "message": f"Missing required telemetry parameter: {str(ke)}"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@api_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """Returns active environmental alerts."""
    alerts = query_db("SELECT * FROM alerts WHERE status = 'ACTIVE' ORDER BY timestamp DESC LIMIT 20")
    return jsonify({"status": "success", "count": len(alerts), "alerts": alerts})

@api_bp.route('/model-metrics', methods=['GET'])
def get_metrics():
    """Returns model benchmark evaluation metrics."""
    metrics_path = os.path.join(Config.MODELS_DIR, 'evaluation_metrics.json')
    if os.path.exists(metrics_path):
        with open(metrics_path, 'r') as f:
            return jsonify(json.load(f))
    return jsonify({"status": "error", "message": "Model evaluation metrics not yet generated."}), 404
