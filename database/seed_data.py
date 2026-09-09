import os
import random
import datetime
import pandas as pd
import numpy as np
from database.db import get_db_connection, init_db
from config import Config

def generate_synthetic_water_data(num_records=1200):
    """
    Generates realistic, scientifically grounded multi-parameter water quality data.
    Models natural diurnal cycles and realistic pollution anomaly events.
    """
    water_bodies = [
        {"id": 1, "name": "Blue Lake Reservoir", "location": "Highland Watershed, Zone 1", "lat": 12.9716, "lng": 77.5946, "basin": "Protected Freshwater", "desc": "Municipal drinking water intake reservoir under regular environmental monitoring."},
        {"id": 2, "name": "Bellandur Urban Basin", "location": "Metropolitan South Outflow", "lat": 12.9352, "lng": 77.6698, "basin": "Urban Wetland", "desc": "Eutrophic urban water body prone to periodic industrial runoff and surfactant accumulation."},
        {"id": 3, "name": "Ganges Basin Station 4", "location": "Riverine Reach Delta", "lat": 25.3176, "lng": 82.9739, "basin": "River System", "desc": "High sediment river station with fluctuating monsoon turbidity and organic load."},
        {"id": 4, "name": "Victoria North Reach", "location": "Lakefront Sector B", "lat": 0.3476, "lng": 32.5825, "basin": "Freshwater Lake", "desc": "Large shallow lake basin subject to seasonal agricultural run-off and algal blooms."}
    ]

    records = []
    base_time = datetime.datetime.now() - datetime.timedelta(days=45)

    for i in range(num_records):
        wb = random.choice(water_bodies)
        time_offset = base_time + datetime.timedelta(hours=i * 0.9 + random.uniform(0, 0.4))
        
        # Decide condition regime for realistic simulation: 65% Good, 23% Moderate, 12% Poor
        regime_rand = random.random()
        
        # Station baseline bias
        if wb["name"] == "Blue Lake Reservoir":
            p_good, p_mod = 0.85, 0.12
        elif wb["name"] == "Bellandur Urban Basin":
            p_good, p_mod = 0.30, 0.40
        elif wb["name"] == "Ganges Basin Station 4":
            p_good, p_mod = 0.60, 0.25
        else:
            p_good, p_mod = 0.70, 0.20

        rand_val = random.random()
        if rand_val < p_good:
            # GOOD condition
            ph = round(random.uniform(6.9, 7.9) + 0.2 * np.sin(i / 12.0), 2)
            temp = round(random.uniform(20.0, 26.0) + 1.5 * np.sin(i / 24.0), 1)
            turbidity = round(random.uniform(1.2, 4.8), 2)
            do = round(random.uniform(6.8, 8.8) - 0.05 * (temp - 20), 2)
            tds = round(random.uniform(110.0, 280.0), 1)
            conductivity = round(tds * random.uniform(1.4, 1.8), 1)
            quality = "GOOD"
        elif rand_val < (p_good + p_mod):
            # MODERATE condition
            ph = round(random.choice([random.uniform(6.1, 6.4), random.uniform(8.4, 8.9)]), 2)
            temp = round(random.uniform(24.0, 31.0), 1)
            turbidity = round(random.uniform(5.5, 14.5), 2)
            do = round(random.uniform(4.2, 6.2), 2)
            tds = round(random.uniform(320.0, 580.0), 1)
            conductivity = round(tds * random.uniform(1.5, 1.9), 1)
            quality = "MODERATE"
        else:
            # POOR condition
            ph = round(random.choice([random.uniform(4.5, 5.9), random.uniform(9.1, 10.5)]), 2)
            temp = round(random.uniform(28.0, 35.0), 1)
            turbidity = round(random.uniform(15.5, 65.0), 2)
            do = round(random.uniform(1.2, 3.8), 2)
            tds = round(random.uniform(620.0, 1450.0), 1)
            conductivity = round(tds * random.uniform(1.7, 2.2), 1)
            quality = "POOR"

        records.append({
            "water_body_id": wb["id"],
            "water_body_name": wb["name"],
            "date": time_offset.strftime("%Y-%m-%d"),
            "time": time_offset.strftime("%H:%M:%S"),
            "timestamp": time_offset.strftime("%Y-%m-%d %H:%M:%S"),
            "ph": ph,
            "temperature": temp,
            "turbidity": turbidity,
            "dissolved_oxygen": do,
            "tds": tds,
            "conductivity": conductivity,
            "water_quality": quality,
            "is_demo": 1,
            "source": f"Simulated IoT Telemetry Node {wb['id']}"
        })

    return water_bodies, records

def seed_database():
    """Initializes and seeds database with water bodies, sensor data, alerts, and sample satellite records."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    water_bodies, records = generate_synthetic_water_data(1200)

    # Insert water bodies
    for wb in water_bodies:
        cursor.execute("""
            INSERT OR IGNORE INTO water_bodies (id, name, location, latitude, longitude, basin_type, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (wb["id"], wb["name"], wb["location"], wb["lat"], wb["lng"], wb["basin"], wb["desc"]))

    # Clear previous demo sensor data
    cursor.execute("DELETE FROM sensor_data WHERE is_demo = 1")
    cursor.execute("DELETE FROM alerts")

    # Insert sensor records
    for r in records:
        cursor.execute("""
            INSERT INTO sensor_data (
                water_body_id, date, time, timestamp, ph, temperature,
                turbidity, dissolved_oxygen, tds, conductivity, water_quality, is_demo, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            r["water_body_id"], r["date"], r["time"], r["timestamp"],
            r["ph"], r["temperature"], r["turbidity"], r["dissolved_oxygen"],
            r["tds"], r["conductivity"], r["water_quality"], r["is_demo"], r["source"]
        ))

    # Generate alerts based on threshold violations from recent records
    recent_records = sorted(records, key=lambda x: x["timestamp"], reverse=True)[:100]
    for r in recent_records:
        if r["water_quality"] == "POOR":
            if r["dissolved_oxygen"] < 4.0:
                cursor.execute("""
                    INSERT INTO alerts (timestamp, water_body_id, severity, parameter, value, threshold_exceeded, message, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    r["timestamp"], r["water_body_id"], "CRITICAL", "Dissolved Oxygen",
                    r["dissolved_oxygen"], "< 4.0 mg/L (Critical Hypoxia)",
                    f"Critically low Dissolved Oxygen ({r['dissolved_oxygen']} mg/L) detected at {r['water_body_name']}. Aquatic fauna risk.",
                    "ACTIVE"
                ))
            if r["turbidity"] > 15.0:
                cursor.execute("""
                    INSERT INTO alerts (timestamp, water_body_id, severity, parameter, value, threshold_exceeded, message, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    r["timestamp"], r["water_body_id"], "CRITICAL", "Turbidity",
                    r["turbidity"], "> 15.0 NTU (Suspended Particulate Spike)",
                    f"High turbidity ({r['turbidity']} NTU) detected at {r['water_body_name']}. Possible runoff sediment surge.",
                    "ACTIVE"
                ))
            if r["ph"] < 6.0 or r["ph"] > 9.0:
                cursor.execute("""
                    INSERT INTO alerts (timestamp, water_body_id, severity, parameter, value, threshold_exceeded, message, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    r["timestamp"], r["water_body_id"], "CRITICAL", "pH Level",
                    r["ph"], "< 6.0 or > 9.0 (pH Violation)",
                    f"Anomalous pH level ({r['ph']}) recorded at {r['water_body_name']}. Exceeds environmental safe range.",
                    "ACTIVE"
                ))
        elif r["water_quality"] == "MODERATE" and random.random() < 0.25:
            cursor.execute("""
                INSERT INTO alerts (timestamp, water_body_id, severity, parameter, value, threshold_exceeded, message, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                r["timestamp"], r["water_body_id"], "WARNING", "TDS / Conductivity",
                r["tds"], "> 300 mg/L (Elevated Minerals)",
                f"Elevated Total Dissolved Solids ({r['tds']} mg/L) detected at {r['water_body_name']}. Parameter trending upward.",
                "RESOLVED" if random.random() < 0.5 else "ACTIVE"
            ))

    # Also seed initial sample predictions
    cursor.execute("DELETE FROM predictions")
    sample_preds = [
        (datetime.datetime.now() - datetime.timedelta(hours=2), 1, 7.3, 24.5, 2.8, 7.8, 185.0, 310.0, None, "GOOD", 94.2, "CNN_LSTM_FUSION", "Low", "Optimal water quality parameters. Routine monitoring."),
        (datetime.datetime.now() - datetime.timedelta(hours=5), 2, 8.7, 28.2, 12.4, 4.8, 480.0, 820.0, None, "MODERATE", 87.5, "LSTM", "Medium", "Elevated turbidity and TDS detected. Increase sampling frequency."),
        (datetime.datetime.now() - datetime.timedelta(hours=8), 2, 5.4, 31.0, 38.5, 2.1, 890.0, 1540.0, None, "POOR", 96.1, "CNN_LSTM_FUSION", "High", "Critical hypoxia and high particulate contamination. Immediate field inspection required.")
    ]
    for sp in sample_preds:
        cursor.execute("""
            INSERT INTO predictions (
                timestamp, water_body_id, ph, temperature, turbidity, dissolved_oxygen,
                tds, conductivity, image_path, prediction, confidence, model_name, risk_level, recommendation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sp[0].strftime("%Y-%m-%d %H:%M:%S"), sp[1], sp[2], sp[3], sp[4], sp[5],
            sp[6], sp[7], sp[8], sp[9], sp[10], sp[11], sp[12], sp[13]
        ))

    conn.commit()
    conn.close()

    # Save dataset to CSV
    os.makedirs(Config.DATASET_DIR, exist_ok=True)
    csv_path = os.path.join(Config.DATASET_DIR, 'water_quality.csv')
    df = pd.DataFrame(records)
    export_df = df[["date", "time", "ph", "temperature", "turbidity", "dissolved_oxygen", "tds", "conductivity", "water_quality"]]
    export_df.to_csv(csv_path, index=False)
    print(f"[Seed] Successfully seeded SQLite database with {len(records)} sensor records.")
    print(f"[Seed] Exported dataset to {csv_path}")

if __name__ == '__main__':
    seed_database()
