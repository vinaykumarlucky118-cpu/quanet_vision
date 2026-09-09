import unittest
import os
import pandas as pd
import numpy as np
from config import Config
from training.data_preprocessing import load_and_preprocess_sensor_data

class TestDataPreprocessing(unittest.TestCase):
    def setUp(self):
        self.csv_path = os.path.join(Config.DATASET_DIR, 'water_quality.csv')

    def test_csv_dataset_exists(self):
        self.assertTrue(os.path.exists(self.csv_path), "Dataset water_quality.csv should exist.")

    def test_csv_dataset_columns(self):
        df = pd.read_csv(self.csv_path)
        required_cols = ['ph', 'temperature', 'turbidity', 'dissolved_oxygen', 'tds', 'conductivity', 'water_quality']
        for col in required_cols:
            self.assertIn(col, df.columns, f"Required column '{col}' missing from dataset.")

    def test_data_preprocessing_pipeline(self):
        X_train, X_test, y_train, y_test, scaler, feature_cols = load_and_preprocess_sensor_data()
        self.assertGreater(len(X_train), 0)
        self.assertGreater(len(X_test), 0)
        self.assertEqual(len(feature_cols), 6)
        self.assertEqual(X_train.shape[1], 6)
        # Check target labels are in {0, 1, 2}
        self.assertTrue(set(np.unique(y_train)).issubset({0, 1, 2}))

if __name__ == '__main__':
    unittest.main()
