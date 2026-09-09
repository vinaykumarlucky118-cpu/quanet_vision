import os
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from training.data_preprocessing import load_and_preprocess_sensor_data
from config import Config

def train_baselines():
    """Trains Logistic Regression and Random Forest baseline classifiers."""
    X_train, X_test, y_train, y_test, _, _ = load_and_preprocess_sensor_data()
    
    save_dir = os.path.join(Config.MODELS_DIR, 'baseline_models')
    os.makedirs(save_dir, exist_ok=True)
    
    # 1. Logistic Regression
    lr = LogisticRegression(max_iter=1000, random_state=42)
    lr.fit(X_train, y_train)
    lr_pred = lr.predict(X_test)
    
    lr_metrics = {
        'accuracy': round(float(accuracy_score(y_test, lr_pred) * 100), 2),
        'precision': round(float(precision_score(y_test, lr_pred, average='weighted', zero_division=0) * 100), 2),
        'recall': round(float(recall_score(y_test, lr_pred, average='weighted', zero_division=0) * 100), 2),
        'f1_score': round(float(f1_score(y_test, lr_pred, average='weighted', zero_division=0) * 100), 2),
    }
    joblib.dump(lr, os.path.join(save_dir, 'logistic_regression.joblib'))
    
    # 2. Random Forest
    rf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    rf.fit(X_train, y_train)
    rf_pred = rf.predict(X_test)
    
    rf_metrics = {
        'accuracy': round(float(accuracy_score(y_test, rf_pred) * 100), 2),
        'precision': round(float(precision_score(y_test, rf_pred, average='weighted', zero_division=0) * 100), 2),
        'recall': round(float(recall_score(y_test, rf_pred, average='weighted', zero_division=0) * 100), 2),
        'f1_score': round(float(f1_score(y_test, rf_pred, average='weighted', zero_division=0) * 100), 2),
    }
    joblib.dump(rf, os.path.join(save_dir, 'random_forest.joblib'))
    
    print(f"[Baseline] Logistic Regression -> Acc: {lr_metrics['accuracy']}%, F1: {lr_metrics['f1_score']}%")
    print(f"[Baseline] Random Forest -> Acc: {rf_metrics['accuracy']}%, F1: {rf_metrics['f1_score']}%")
    
    return lr_metrics, rf_metrics

if __name__ == '__main__':
    train_baselines()
