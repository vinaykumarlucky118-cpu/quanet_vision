import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from config import Config

def load_and_preprocess_sensor_data(csv_path=None):
    """Loads and preprocesses water quality sensor data."""
    if csv_path is None:
        csv_path = os.path.join(Config.DATASET_DIR, 'water_quality.csv')
    
    if not os.path.exists(csv_path):
        from database.seed_data import seed_database
        seed_database()
        
    df = pd.read_csv(csv_path)
    
    # Feature columns
    feature_cols = ['ph', 'temperature', 'turbidity', 'dissolved_oxygen', 'tds', 'conductivity']
    target_col = 'water_quality'
    
    # Drop NaNs if any
    df = df.dropna(subset=feature_cols + [target_col])
    
    X = df[feature_cols].values
    y_raw = df[target_col].values
    
    # Standardize label encoding: 0: GOOD, 1: MODERATE, 2: POOR
    label_map = {'GOOD': 0, 'MODERATE': 1, 'POOR': 2}
    y = np.array([label_map.get(str(val).upper(), 1) for val in y_raw])
    
    # Train test split (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    
    # Scaler
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Save artifacts
    save_dir = os.path.join(Config.MODELS_DIR, 'preprocessing')
    os.makedirs(save_dir, exist_ok=True)
    
    joblib.dump(scaler, os.path.join(save_dir, 'scaler.joblib'))
    
    feature_meta = {
        'feature_cols': feature_cols,
        'label_map': label_map,
        'reverse_label_map': {0: 'GOOD', 1: 'MODERATE', 2: 'POOR'},
        'n_samples': len(df),
        'train_samples': len(X_train),
        'test_samples': len(X_test)
    }
    with open(os.path.join(save_dir, 'feature_metadata.json'), 'w') as f:
        json.dump(feature_meta, f, indent=4)
        
    return X_train_scaled, X_test_scaled, y_train, y_test, scaler, feature_cols

def create_sequences(X, y, seq_length=8):
    """Creates sliding window time-series sequences for LSTM training."""
    xs, ys = [], []
    for i in range(len(X) - seq_length):
        xs.append(X[i:(i + seq_length)])
        ys.append(y[i + seq_length])
    return np.array(xs), np.array(ys)

if __name__ == '__main__':
    load_and_preprocess_sensor_data()
    print("[Preprocess] Tabular data preprocessing completed successfully.")
