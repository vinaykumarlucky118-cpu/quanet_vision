import os
import json
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
from models.fusion import fusion_engine
from database.db import query_db, execute_db
from config import Config

prediction_bp = Blueprint('prediction', __name__)

@prediction_bp.route('/prediction', methods=['GET', 'POST'])
def index():
    """Water Quality Prediction Page supporting Single Sensor and Multimodal Satellite Fusion."""
    water_bodies = query_db("SELECT id, name, location FROM water_bodies ORDER BY id")
    prediction_result = None

    # Sample presets for quick academic demo
    presets = {
        "good": {"ph": 7.4, "temperature": 23.5, "turbidity": 2.4, "dissolved_oxygen": 7.8, "tds": 180.0, "conductivity": 290.0, "label": "Protected Freshwater (Clean)"},
        "moderate": {"ph": 8.6, "temperature": 27.5, "turbidity": 8.9, "dissolved_oxygen": 5.1, "tds": 410.0, "conductivity": 680.0, "label": "Agricultural Runoff (Moderate Sediment)"},
        "poor": {"ph": 5.2, "temperature": 31.0, "turbidity": 34.5, "dissolved_oxygen": 2.1, "tds": 920.0, "conductivity": 1650.0, "label": "Industrial Effluent / Severe Hypoxia (Poor)"}
    }

    if request.method == 'POST':
        try:
            wb_id = request.form.get('water_body_id', type=int)
            model_choice = request.form.get('model_choice', 'CNN_LSTM_FUSION')
            
            sensor_input = {
                'ph': float(request.form.get('ph', 7.0)),
                'temperature': float(request.form.get('temperature', 25.0)),
                'turbidity': float(request.form.get('turbidity', 4.0)),
                'dissolved_oxygen': float(request.form.get('dissolved_oxygen', 7.0)),
                'tds': float(request.form.get('tds', 200.0)),
                'conductivity': float(request.form.get('conductivity', 350.0))
            }

            # Handle optional satellite image upload
            image_path = None
            uploaded_file = request.files.get('satellite_image')
            
            if uploaded_file and uploaded_file.filename != '':
                filename = secure_filename(uploaded_file.filename)
                ext = filename.rsplit('.', 1)[-1].lower()
                if ext in Config.ALLOWED_IMAGE_EXTENSIONS:
                    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
                    save_path = os.path.join(Config.UPLOAD_FOLDER, filename)
                    uploaded_file.save(save_path)
                    image_path = save_path
            
            # Execute prediction
            result = fusion_engine.predict(sensor_input, image_path=image_path, model_choice=model_choice)
            
            # Store in database
            pred_id = execute_db("""
                INSERT INTO predictions (
                    water_body_id, ph, temperature, turbidity, dissolved_oxygen,
                    tds, conductivity, image_path, prediction, confidence,
                    model_name, risk_level, recommendation, features_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                wb_id, sensor_input['ph'], sensor_input['temperature'],
                sensor_input['turbidity'], sensor_input['dissolved_oxygen'],
                sensor_input['tds'], sensor_input['conductivity'],
                image_path, result['prediction'], result['confidence'],
                result['model_name'], result['risk_level'],
                result['recommendation'], json.dumps(result['parameter_risks'])
            ))

            prediction_result = result
            prediction_result['id'] = pred_id

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"status": "success", "data": prediction_result})

        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"status": "error", "message": str(e)}), 400
            flash(f"Prediction Error: {str(e)}", "danger")

    # Recent predictions history
    recent_predictions = query_db("""
        SELECT p.*, wb.name as water_body_name 
        FROM predictions p 
        LEFT JOIN water_bodies wb ON p.water_body_id = wb.id 
        ORDER BY p.timestamp DESC LIMIT 6
    """)

    return render_template('prediction.html',
        water_bodies=water_bodies,
        presets=presets,
        result=prediction_result,
        recent_predictions=recent_predictions,
        quality_classes=Config.QUALITY_CLASSES
    )
