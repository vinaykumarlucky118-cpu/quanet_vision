import unittest
from models.fusion import fusion_engine

class TestPredictionEngine(unittest.TestCase):
    def test_good_water_quality_prediction(self):
        sensor_input = {
            'ph': 7.4,
            'temperature': 22.0,
            'turbidity': 2.1,
            'dissolved_oxygen': 7.8,
            'tds': 180.0,
            'conductivity': 290.0
        }
        result = fusion_engine.predict(sensor_input, model_choice="RANDOM_FOREST")
        self.assertIn("prediction", result)
        self.assertEqual(result["prediction"], "GOOD")
        self.assertGreater(result["confidence"], 50.0)
        self.assertIn("recommendation", result)

    def test_poor_water_quality_prediction(self):
        sensor_input = {
            'ph': 5.0, # highly acidic
            'temperature': 33.0,
            'turbidity': 45.0, # high turbidity
            'dissolved_oxygen': 1.8, # severe hypoxia
            'tds': 950.0,
            'conductivity': 1800.0
        }
        result = fusion_engine.predict(sensor_input, model_choice="RANDOM_FOREST")
        self.assertIn("prediction", result)
        self.assertEqual(result["prediction"], "POOR")
        self.assertIn("Critical", [v["status"] for v in result["parameter_risks"].values()])

    def test_invalid_sensor_inputs(self):
        invalid_input = {'ph': 'invalid_string', 'turbidity': 'abc'}
        with self.assertRaises(ValueError):
            fusion_engine.predict(invalid_input)

if __name__ == '__main__':
    unittest.main()
