import unittest
import json
from app import create_app

class TestFlaskEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_routes_status_code_200(self):
        routes = [
            '/',
            '/about',
            '/how-it-works',
            '/dashboard',
            '/prediction',
            '/satellite',
            '/sensor-data',
            '/analytics',
            '/alerts',
            '/reports',
            '/models',
            '/about-team',
            '/contact',
            '/login'
        ]
        for route in routes:
            response = self.client.get(route)
            self.assertEqual(response.status_code, 200, f"Route '{route}' returned {response.status_code} instead of 200.")

    def test_sensor_data_export_csv(self):
        response = self.client.get('/sensor-data/export-csv')
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/csv', response.headers.get('Content-Type', ''))

    def test_reports_export_pdf(self):
        response = self.client.get('/reports/pdf?water_body_id=1')
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/pdf', response.headers.get('Content-Type', ''))

    def test_api_sensor_data(self):
        response = self.client.get('/api/sensor-data')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data.get('status'), 'success')
        self.assertIsInstance(data.get('data'), list)

    def test_api_predict(self):
        payload = {
            "ph": 7.3,
            "temperature": 24.0,
            "turbidity": 2.5,
            "dissolved_oxygen": 7.5,
            "tds": 200.0,
            "conductivity": 350.0
        }
        response = self.client.post('/api/predict', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data.get('status'), 'success')
        self.assertIn('prediction', data.get('result', {}))

    def test_api_iot_ingest(self):
        payload = {
            "device_id": "TEST-ESP32-NODE-01",
            "water_body_id": 1,
            "ph": 7.2,
            "temp": 24.5,
            "turbidity": 3.1,
            "do": 7.4,
            "tds": 210.0,
            "conductivity": 340.0
        }
        response = self.client.post('/api/iot-ingest', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data.get('status'), 'success')
        self.assertIn('record_id', data)

if __name__ == '__main__':
    unittest.main()
