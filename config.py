import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    BASE_DIR = BASE_DIR
    SECRET_KEY = os.environ.get('SECRET_KEY', 'quanet-vision-secret-key-2026-academic-ai')
    DATABASE = os.path.join(BASE_DIR, 'database', 'quanet.db')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    DATASET_DIR = os.path.join(BASE_DIR, 'dataset')
    MODELS_DIR = os.path.join(BASE_DIR, 'models')
    STATIC_DIR = os.path.join(BASE_DIR, 'static')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tif', 'tiff', 'webp'}
    ALLOWED_CSV_EXTENSIONS = {'csv'}

    # Demo Credentials
    DEMO_ADMIN_EMAIL = "admin@quanetvision.com"
    DEMO_ADMIN_PASSWORD = "admin123"

    # Water Quality Standards & Thresholds (CPCB / WHO Guidelines Reference)
    # Status Classes: 0: GOOD, 1: MODERATE, 2: POOR
    WATER_QUALITY_THRESHOLDS = {
        "ph": {
            "good_min": 6.5,
            "good_max": 8.5,
            "moderate_min": 6.0,
            "moderate_max": 9.0,
            "unit": "",
            "label": "pH Level",
            "description": "Measures water acidity/alkalinity. Ideal neutral range: 6.5 to 8.5."
        },
        "temperature": {
            "good_min": 15.0,
            "good_max": 28.0,
            "moderate_min": 10.0,
            "moderate_max": 34.0,
            "unit": "°C",
            "label": "Temperature",
            "description": "Affects chemical reaction rates and dissolved oxygen levels."
        },
        "turbidity": {
            "good_max": 5.0,
            "moderate_max": 15.0,
            "unit": "NTU",
            "label": "Turbidity",
            "description": "Water cloudiness from suspended solids. <5 NTU is clear, >15 NTU indicates high sediment."
        },
        "dissolved_oxygen": {
            "good_min": 6.5,
            "moderate_min": 4.0,
            "unit": "mg/L",
            "label": "Dissolved Oxygen (DO)",
            "description": "Essential for aquatic ecosystems. >6.5 mg/L indicates healthy aeration, <4.0 mg/L is hypoxic."
        },
        "tds": {
            "good_max": 300.0,
            "moderate_max": 600.0,
            "unit": "mg/L",
            "label": "Total Dissolved Solids (TDS)",
            "description": "Combined inorganic and organic minerals. <300 mg/L is clean, >600 mg/L indicates mineral contamination."
        },
        "conductivity": {
            "good_max": 500.0,
            "moderate_max": 1000.0,
            "unit": "µS/cm",
            "label": "Electrical Conductivity (EC)",
            "description": "Ability to conduct electrical current. Correlates directly with dissolved ionic minerals."
        }
    }

    # Water Quality Class Metadata
    QUALITY_CLASSES = {
        "GOOD": {
            "badge_class": "badge-success",
            "color": "#10b981",
            "icon": "✓",
            "recommendation": "Water quality parameters are within optimal ranges. Regular periodic monitoring is recommended.",
            "risk_level": "Low"
        },
        "MODERATE": {
            "badge_class": "badge-warning",
            "color": "#f59e0b",
            "icon": "!",
            "recommendation": "Water quality deterioration detected in specific parameters. Increase monitoring frequency and investigate potential upstream sources.",
            "risk_level": "Medium"
        },
        "POOR": {
            "badge_class": "badge-danger",
            "color": "#ef4444",
            "icon": "⚠",
            "recommendation": "Severe water quality impairment detected. Possible pollution spike. Immediate field inspection and laboratory confirmatory testing recommended.",
            "risk_level": "High"
        }
    }
