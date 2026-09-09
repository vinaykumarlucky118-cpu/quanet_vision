import os
from flask import Blueprint, render_template, request, jsonify, flash
from werkzeug.utils import secure_filename
from models.fusion import fusion_engine
from database.db import query_db, execute_db
from config import Config

satellite_bp = Blueprint('satellite', __name__)

@satellite_bp.route('/satellite', methods=['GET', 'POST'])
def index():
    """Satellite Analysis Studio for CNN feature extraction and water condition diagnosis."""
    water_bodies = query_db("SELECT id, name, location FROM water_bodies ORDER BY id")
    analysis_result = None
    analyzed_image_url = None

    # Curate sample satellite images
    samples = [
        {"name": "Clear Oligotrophic Water", "filename": "good_sat_001.jpg", "category": "GOOD", "desc": "Low turbidity, high blue optical reflectance, minimal chlorophyll absorption."},
        {"name": "Suspended Sediment Plume", "filename": "moderate_sat_001.jpg", "category": "MODERATE", "desc": "Moderate turbidity with inorganic suspended sediment transport."},
        {"name": "Algal Bloom & Eutrophication", "filename": "poor_sat_001.jpg", "category": "POOR", "desc": "High green reflectance, high NDWI algae risk proxy, critical organic load."}
    ]

    if request.method == 'POST':
        wb_id = request.form.get('water_body_id', type=int)
        sample_choice = request.form.get('sample_image')
        uploaded_file = request.files.get('satellite_image')
        
        target_path = None
        web_image_url = None

        if uploaded_file and uploaded_file.filename != '':
            filename = secure_filename(uploaded_file.filename)
            ext = filename.rsplit('.', 1)[-1].lower()
            if ext in Config.ALLOWED_IMAGE_EXTENSIONS:
                os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
                target_path = os.path.join(Config.UPLOAD_FOLDER, filename)
                uploaded_file.save(target_path)
                web_image_url = f"/uploads/{filename}"
        elif sample_choice:
            # Find sample image in dataset
            cat = "good" if "good" in sample_choice else ("moderate" if "moderate" in sample_choice else "poor")
            sample_path = os.path.join(Config.DATASET_DIR, 'satellite_images', cat, sample_choice)
            if os.path.exists(sample_path):
                target_path = sample_path
                web_image_url = f"/dataset-img/{cat}/{sample_choice}"

        if target_path and os.path.exists(target_path):
            result = fusion_engine.extract_satellite_features(target_path)
            if result:
                analysis_result = result
                analyzed_image_url = web_image_url
                
                # Save to database
                execute_db("""
                    INSERT INTO satellite_records (
                        water_body_id, image_filename, title, turbidity_index,
                        algae_risk_index, detected_condition, confidence, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    wb_id, os.path.basename(target_path),
                    "Satellite Spatial Analysis",
                    result['metrics']['turbidity_optical_index'],
                    result['metrics']['algal_ndwi_proxy'],
                    result['predicted_condition'],
                    result['confidence'],
                    f"Mean B:{result['metrics']['mean_blue']}, G:{result['metrics']['mean_green']}, R:{result['metrics']['mean_red']}"
                ))

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                "status": "success",
                "result": analysis_result,
                "image_url": analyzed_image_url
            })

    # Recent satellite records
    recent_records = query_db("""
        SELECT sr.*, wb.name as water_body_name 
        FROM satellite_records sr 
        LEFT JOIN water_bodies wb ON sr.water_body_id = wb.id 
        ORDER BY sr.timestamp DESC LIMIT 6
    """)

    return render_template('satellite.html',
        water_bodies=water_bodies,
        samples=samples,
        result=analysis_result,
        image_url=analyzed_image_url,
        recent_records=recent_records,
        quality_classes=Config.QUALITY_CLASSES
    )
