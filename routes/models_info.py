import os
import json
from flask import Blueprint, render_template
from config import Config

models_info_bp = Blueprint('models_info', __name__)

@models_info_bp.route('/models')
def index():
    """AI Models Architecture, Deep Learning Specifications, and Dynamic Benchmarks."""
    metrics_path = os.path.join(Config.MODELS_DIR, 'evaluation_metrics.json')
    eval_data = None
    
    if os.path.exists(metrics_path):
        try:
            with open(metrics_path, 'r') as f:
                eval_data = json.load(f)
        except Exception:
            eval_data = None

    # Load baseline/lstm/cnn metrics directly if present
    lstm_info = {}
    lstm_meta_path = os.path.join(Config.MODELS_DIR, 'lstm_model', 'lstm_metrics.json')
    if os.path.exists(lstm_meta_path):
        with open(lstm_meta_path, 'r') as f:
            lstm_info = json.load(f)

    cnn_info = {}
    cnn_meta_path = os.path.join(Config.MODELS_DIR, 'cnn_model', 'cnn_metrics.json')
    if os.path.exists(cnn_meta_path):
        with open(cnn_meta_path, 'r') as f:
            cnn_info = json.load(f)

    return render_template('models.html',
        eval_data=eval_data,
        lstm_info=lstm_info,
        cnn_info=cnn_info
    )
