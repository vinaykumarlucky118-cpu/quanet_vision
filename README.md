# QuaNet Vision: Deep Learning for Intelligent Water Quality Prediction
### Subtitle: A Hybrid IoT–Satellite Deep Learning System

---

## 🌊 Project Description

> **QuaNet Vision is a hybrid IoT–satellite deep learning platform designed for intelligent water quality monitoring and prediction. The system combines water-quality sensor data and satellite imagery to obtain complementary temporal and spatial information. LSTM is used to analyze sequential sensor data, while CNN is used to extract features from satellite images. These features can be fused to generate an intelligent water-quality prediction. The results are presented through an interactive web dashboard containing sensor values, trends, analytics, alerts and reports. The platform is designed as an academic prototype and can later be extended with real-time IoT devices and satellite data services.**

---

## 🚀 Key Highlights & Capabilities

* **Hybrid Multimodal Deep Learning**:
  * **Temporal LSTM Network**: Analyzes in-situ multi-parameter sequential time-series sensor telemetry (pH, Temperature, Turbidity, Dissolved Oxygen, TDS, Conductivity).
  * **Spatial CNN Vision Model**: Processes satellite imagery tiles ($128\times 128\times 3$) to extract chlorophyll absorption, algal blooms, and surface sediment plumes.
  * **Late Data Fusion Layer**: Combines 32-dimensional spatial and temporal representations for high-confidence water quality classification (GOOD ✓, MODERATE !, POOR ⚠).
* **Authentic Empirical Benchmarking**: Evaluated against classical Machine Learning baselines (Logistic Regression & Random Forest) with authentic, computed Accuracy, Precision, Recall, F1-Score, and Confusion Matrices.
* **Real-Time Web Monitoring Dashboard**: Central water status badge, 6 live parameter telemetry cards with reference safe limits, and 5 interactive Chart.js time-series charts.
* **Multimodal Prediction Studio**: Interactive web form with one-click academic presets, custom parameter sliders, optional satellite image upload, parameter risk breakdowns, and safety recommendations.
* **Satellite Analysis Studio**: Tile upload and curated reference image gallery with automated NDWI algal proxy and turbidity optical index feature extraction.
* **Sensor Telemetry Data Management**: Searchable, filterable, sortable, and paginated table with CSV dataset import (with column validation) and one-click CSV export.
* **Advanced Environmental Analytics**: Parameter distribution metrics ($\mu, \sigma$, min, max), doughnut quality breakdown, and Pearson correlation matrix heatmap ($r$).
* **Automated Alert & Anomaly Engine**: Real-time threshold violation triggers with CRITICAL, WARNING, and RESOLVED status feeds.
* **Compliance & Assessment Reports**: Live report builder with one-click **PDF Report Generation** (powered by ReportLab) and CSV summary export.
* **Future Hardware-Ready REST API**: Dedicated endpoint (`POST /api/iot-ingest`) ready for direct field connection with ESP32, Arduino, or Raspberry Pi sensor nodes.

---

## 📁 Project Architecture & Folder Structure

```
quanet_vision/
├── app.py                      # Flask Application Factory & Server Entrypoint
├── config.py                   # System Configuration, Water Standards & Thresholds
├── requirements.txt            # Python Dependencies Specification
├── run_pipeline.py             # Data Seeding & Model Training Orchestrator
├── run_tests.py                # Automated Unit & Integration Test Runner
├── README.md                   # Complete Documentation & Windows Setup Guide
│
├── database/
│   ├── db.py                   # SQLite Connection & Helper Operations
│   ├── schema.sql              # Database Tables (users, sensor_data, predictions, alerts, etc.)
│   ├── seed_data.py            # Multi-Station Synthetic Telemetry & Alert Generator
│   └── quanet.db               # Populated SQLite Database
│
├── dataset/
│   ├── water_quality.csv       # Multi-parameter Water Quality Dataset
│   └── satellite_images/       # Satellite Image Tiles (good, moderate, poor condition)
│
├── models/
│   ├── preprocessing/          # Scalers & Label Encoders (StandardScaler)
│   ├── baseline_models/        # Logistic Regression & Random Forest Models
│   ├── lstm_model/             # Trained LSTM Weights & Parameters
│   ├── cnn_model/              # Trained CNN Weights & Architecture
│   ├── fusion.py               # Hybrid Inference & Recommendation Engine
│   └── evaluation_metrics.json # Authentically Evaluated Performance Metrics & Confusion Matrices
│
├── training/
│   ├── data_preprocessing.py   # Dataset Ingestion & Feature Normalization
│   ├── train_baseline.py       # Baseline Models Trainer
│   ├── train_lstm.py           # Temporal Time-Series LSTM Trainer
│   ├── train_cnn.py            # Satellite Computer Vision CNN Trainer
│   └── evaluate.py             # Empirical Holdout Evaluation Script
│
├── routes/
│   ├── auth.py                 # Demo Sign-In & Session Handling
│   ├── dashboard.py            # Dashboard & Informational Views
│   ├── prediction.py           # Single & Multimodal Prediction Forms
│   ├── satellite.py            # Satellite Image Upload & CNN Feature Studio
│   ├── sensor_data.py          # Data Tables, Pagination & CSV Upload/Export
│   ├── analytics.py            # Statistical Distribution & Pearson Heatmap
│   ├── alerts.py               # Anomaly Feed & Alert Resolution
│   ├── reports.py              # Report Preview & PDF Generation
│   ├── models_info.py          # Architecture Specifications & Dynamic Tables
│   └── api.py                  # JSON REST API & Hardware Ingestion Endpoints
│
├── templates/
│   ├── base.html               # Master Layout with Navigation, Sticky Header & Footer
│   ├── index.html              # Home Page (Hero, Stats, Problem/Solution)
│   ├── about.html              # Project Aim, Objectives & Architecture Schematics
│   ├── how_it_works.html       # 8-Stage Pipeline, CNN vs LSTM Comparison
│   ├── dashboard.html          # Water Monitoring Dashboard & 5 Time-Series Charts
│   ├── prediction.html         # Prediction Form with Presets & Risk Breakdown
│   ├── satellite.html          # Satellite Analysis Studio
│   ├── sensor_data.html        # Telemetry Table, Pagination & CSV Import
│   ├── analytics.html          # Environmental Analytics & Correlation Matrix
│   ├── alerts.html             # Anomaly Alerts Feed
│   ├── reports.html            # Report Builder & PDF Preview
│   ├── models.html             # Model Architectures & Confusion Matrices
│   ├── about_team.html         # Student & Institutional Project Credits
│   ├── contact.html            # Inquiries & Demo Contact Form
│   ├── login.html              # Demo Authentication Screen
│   ├── 404.html                # Not Found Error Page
│   └── 500.html                # Application Notice Error Page
│
├── static/
│   ├── css/
│   │   └── style.css           # Modern Environmental Deep-Navy Theme
│   └── js/
│       ├── main.js             # Mobile Navigation & Alert Auto-Dismissal
│       ├── dashboard.js        # 5 Chart.js Time-Series Visualizers
│       ├── prediction.js       # Dynamic AJAX Predictions & Loading Spinners
│       ├── satellite.js        # Image Preview & Sample Tile Handlers
│       └── charts.js           # Analytics Doughnut & Trajectory Renderers
│
└── tests/
    ├── test_data.py            # Dataset Schema & Preprocessing Tests
    ├── test_prediction.py      # Inference Engine & Physics Logic Tests
    └── test_api.py             # Route HTTP 200 & REST API Unit Tests
```

---

## 🛠️ Step-by-Step Installation & Execution Guide (Windows)

### 1. Prerequisites
* Python 3.11 or higher installed on your system.

### 2. Navigate to Project Directory
```powershell
cd c:\Users\vinay\OneDrive\Desktop\quanet_vision
```

### 3. Create & Activate Virtual Environment
```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 4. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 5. Seed Database & Train AI Models (Optional - Already Bundled)
To re-seed the SQLite database with 1200+ sensor records and retrain the CNN, LSTM, and Baseline models:
```powershell
python run_pipeline.py
```

### 6. Run Automated Test Suite
Verify that all 12 test suites (API, Data, Prediction, Reports) pass:
```powershell
python run_tests.py
```

### 7. Launch the QuaNet Vision Web Server
```powershell
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🔑 Default Local Demo Credentials

| Role | Email | Password |
| :--- | :--- | :--- |
| **Administrator / Evaluator** | `admin@quanetvision.com` | `admin123` |

*(Note: Used for local demonstration and session testing).*

---

## 📡 IoT Hardware Connection & REST API Documentation

### Ingestion Endpoint: `POST /api/iot-ingest`
To connect physical ESP32 / Arduino sensor rigs transmitting over Wi-Fi/GSM, send a JSON payload:

```bash
curl -X POST http://127.0.0.1:5000/api/iot-ingest \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "ESP32-STATION-01",
    "water_body_id": 1,
    "ph": 7.35,
    "temperature": 24.2,
    "turbidity": 3.1,
    "dissolved_oxygen": 7.6,
    "tds": 195.0,
    "conductivity": 310.0
  }'
```

**Response (201 Created):**
```json
{
  "status": "success",
  "message": "Telemetry received and recorded successfully.",
  "record_id": 1201,
  "evaluated_quality": "GOOD",
  "alert_triggered": false,
  "timestamp": "2026-09-02 11:30:00"
}
```

---

## 📊 Water Quality Reference Standards

| Parameter | Optimal (GOOD ✓) | Moderate Alert (MODERATE !) | Severe Risk (POOR ⚠) | Unit |
| :--- | :--- | :--- | :--- | :--- |
| **pH Level** | 6.5 – 8.5 | 6.0 – 6.5 or 8.5 – 9.0 | &lt; 6.0 or &gt; 9.0 | — |
| **Temperature** | 15.0 – 28.0 | 10.0 – 15.0 or 28.0 – 34.0 | &lt; 10.0 or &gt; 34.0 | °C |
| **Turbidity** | &le; 5.0 | 5.0 – 15.0 | &gt; 15.0 | NTU |
| **Dissolved Oxygen** | &ge; 6.5 | 4.0 – 6.5 | &lt; 4.0 (Hypoxic) | mg/L |
| **Total Dissolved Solids** | &le; 300.0 | 300.0 – 600.0 | &gt; 600.0 | mg/L |
| **Conductivity** | &le; 500.0 | 500.0 – 1000.0 | &gt; 1000.0 | µS/cm |

---

## 🎓 Academic Demonstration Flow

1. **Home (`/`)**: Explain the core motivation, limitations of manual sampling, and the 4-pillar IoT + Satellite deep learning solution.
2. **About & How It Works (`/about`, `/how-it-works`)**: Present the 8-step pipeline, compare CNN (spatial vision) vs LSTM (temporal sequences), and review the data fusion diagram.
3. **Monitoring Dashboard (`/dashboard`)**: Switch between stations (Blue Lake Reservoir, Bellandur Urban Basin, Ganges Basin), examine the 6 live parameter cards, and review the 5 Chart.js time-series charts.
4. **Prediction Studio (`/prediction`)**: Test one-click demo presets (Clean Reservoir, Agricultural Runoff, Industrial Effluent) or upload a custom satellite tile to witness multimodal fusion and safety advisories.
5. **Satellite Analysis (`/satellite`)**: Select reference satellite tiles or upload a custom optical image to inspect extracted NDWI algae proxies, turbidity optical ratios, and CNN classification.
6. **Sensor Telemetry Data (`/sensor-data`)**: Search and filter records, export the dataset as CSV, or test importing custom CSV datasets with instant column validation.
7. **Analytics (`/analytics`)**: Inspect statistical summary distributions ($\mu, \sigma$) and the Pearson parameter cross-correlation heatmap ($r$).
8. **Reports (`/reports`)**: Preview the formal water quality compliance document and generate a downloadable **PDF Report** with one click.
9. **Model Information (`/models`)**: Review the empirical benchmark comparison table and confusion matrices dynamically computed on the holdout test partition.

---

## ⚖️ Academic Research Disclaimer
*QuaNet Vision is an academic research demonstration and prototyping platform. All predictions and anomaly warnings are generated by machine learning and deep learning models and do not substitute certified regulatory water quality laboratory compliance testing.*
