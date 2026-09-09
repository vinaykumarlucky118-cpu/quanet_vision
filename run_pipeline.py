import sys
import os

# Add venv site-packages and app root to path
app_dir = os.path.dirname(os.path.abspath(__file__))
venv_site = os.path.join(app_dir, '.venv', 'Lib', 'site-packages')
if venv_site not in sys.path:
    sys.path.insert(0, venv_site)
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

print("Starting QuaNet Vision Training & Data Seeding Pipeline...")

from database.seed_data import seed_database
print("1. Seeding Database & Creating Datasets...")
seed_database()

from training.train_baseline import train_baselines
print("2. Training Baseline Models (Logistic Regression & Random Forest)...")
train_baselines()

from training.train_lstm import train_lstm_model
print("3. Training LSTM Time-Series Sensor Model...")
train_lstm_model(epochs=15)

from training.train_cnn import train_cnn_model
print("4. Training Satellite CNN Feature Extraction Model...")
train_cnn_model(epochs=10)

from training.evaluate import run_comprehensive_evaluation
print("5. Running Comprehensive Multimodal Evaluation...")
run_comprehensive_evaluation()

print("Pipeline finished successfully!")
