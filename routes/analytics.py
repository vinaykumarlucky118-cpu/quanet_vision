import numpy as np
import pandas as pd
from flask import Blueprint, render_template, request, jsonify
from database.db import query_db
from config import Config

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics')
def index():
    """Advanced Environmental Water Analytics Studio."""
    wb_id = request.args.get('water_body_id', type=int)
    water_bodies = query_db("SELECT id, name FROM water_bodies ORDER BY id")

    where_sql = "WHERE water_body_id = ?" if wb_id else ""
    params = (wb_id,) if wb_id else ()

    records = query_db(f"""
        SELECT ph, temperature, turbidity, dissolved_oxygen, tds, conductivity, water_quality, timestamp
        FROM sensor_data
        {where_sql}
        ORDER BY timestamp ASC
    """, params)

    if not records:
        return render_template('analytics.html', water_bodies=water_bodies, selected_wb=wb_id, has_data=False)

    df = pd.DataFrame(records)
    feature_cols = ['ph', 'temperature', 'turbidity', 'dissolved_oxygen', 'tds', 'conductivity']

    # 1. Statistical summary metrics
    stats = {}
    for col in feature_cols:
        vals = df[col].dropna()
        stats[col] = {
            'min': round(float(vals.min()), 2),
            'max': round(float(vals.max()), 2),
            'mean': round(float(vals.mean()), 2),
            'std': round(float(vals.std()), 2),
            'median': round(float(vals.median()), 2)
        }

    # 2. Quality distribution
    counts = df['water_quality'].value_counts().to_dict()
    total = len(df)
    quality_dist = {
        'GOOD': {'count': counts.get('GOOD', 0), 'pct': round((counts.get('GOOD', 0) / total) * 100, 1)},
        'MODERATE': {'count': counts.get('MODERATE', 0), 'pct': round((counts.get('MODERATE', 0) / total) * 100, 1)},
        'POOR': {'count': counts.get('POOR', 0), 'pct': round((counts.get('POOR', 0) / total) * 100, 1)},
    }

    # 3. Parameter Pearson Correlation Matrix
    corr_matrix = df[feature_cols].corr().round(3).to_dict()
    corr_labels = ['pH', 'Temperature', 'Turbidity', 'DO', 'TDS', 'Conductivity']
    corr_matrix_list = []
    for r_col in feature_cols:
        row = []
        for c_col in feature_cols:
            row.append(round(float(corr_matrix[r_col][c_col]), 2))
        corr_matrix_list.append(row)

    # 4. Trend timeline samples (subsample up to 50 for smooth charts)
    step = max(1, len(df) // 40)
    sub_df = df.iloc[::step]
    trend_data = {
        'timestamps': [str(t)[5:16] for t in sub_df['timestamp']],
        'ph': sub_df['ph'].tolist(),
        'turbidity': sub_df['turbidity'].tolist(),
        'dissolved_oxygen': sub_df['dissolved_oxygen'].tolist(),
        'tds': sub_df['tds'].tolist()
    }

    return render_template('analytics.html',
        water_bodies=water_bodies,
        selected_wb=wb_id,
        has_data=True,
        stats=stats,
        quality_dist=quality_dist,
        corr_labels=corr_labels,
        corr_matrix=corr_matrix_list,
        trend_data=trend_data,
        total_samples=total
    )
