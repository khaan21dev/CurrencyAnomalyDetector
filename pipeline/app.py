import requests
import schedule
import time
import pymssql
import os
from datetime import datetime
from detector import analyze_rate
from prometheus_client import start_http_server, Counter, Gauge, Histogram
from dotenv import load_dotenv

load_dotenv()

# Prometheus metrics
FETCH_COUNTER = Counter('pipeline_fetches_total', 'Total number of API fetches')
ANOMALY_COUNTER = Counter('anomalies_detected_total', 'Total anomalies detected')
FETCH_DURATION = Histogram('pipeline_fetch_duration_seconds', 'Time spent fetching rates')
CURRENT_RATE = Gauge('current_rate', 'Current exchange rate', ['pair'])

# Database connection
def get_db_connection():
    return pymssql.connect(
        server=os.getenv('DB_SERVER'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        tds_version='7.4'
    )


# Create tables if they don't exist
def setup_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='rates' AND xtype='U')
        CREATE TABLE rates (
            id INT IDENTITY(1,1) PRIMARY KEY,
            timestamp DATETIME,
            pair VARCHAR(10),
            rate FLOAT,
            change_percent FLOAT
        )
    ''')
    
    cursor.execute('''
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='anomalies' AND xtype='U')
        CREATE TABLE anomalies (
            id INT IDENTITY(1,1) PRIMARY KEY,
            timestamp DATETIME,
            pair VARCHAR(10),
            rate FLOAT,
            rule_triggered VARCHAR(100),
            severity VARCHAR(20)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database setup complete")

# Fetch rates from free API
def fetch_rates():
    with FETCH_DURATION.time():
        try:
            response = requests.get(
                'https://api.frankfurter.app/latest',
                params={'from': 'PLN', 'to': 'EUR,USD,GBP'}
            )
            data = response.json()
            FETCH_COUNTER.inc()
            return data['rates']
        except Exception as e:
            print(f"Error fetching rates: {e}")
            return None

# Save rate to database
def save_rate(pair, rate, change_percent):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO rates (timestamp, pair, rate, change_percent) VALUES (%s, %s, %s, %s)',
        (datetime.utcnow(), pair, rate, change_percent)
    )
    conn.commit()
    conn.close()


# Save anomaly to database
def save_anomaly(pair, rate, rule, severity):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO anomalies (timestamp, pair, rate, rule_triggered, severity) VALUES (%s, %s, %s, %s, %s)',
        (datetime.utcnow(), pair, rate, rule, severity)
    )
    conn.commit()
    conn.close()
    ANOMALY_COUNTER.inc()


# Get previous rate from database
def get_previous_rate(pair):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT TOP 1 rate FROM rates WHERE pair = %s ORDER BY timestamp DESC',
            (pair,)
        )
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
    except:
        return None

# Main pipeline function
def run_pipeline():
    print(f"Pipeline running at {datetime.utcnow()}")
    
    rates = fetch_rates()
    if not rates:
        return
    
    for currency, rate in rates.items():
        pair = f"PLN/{currency}"
        previous_rate = get_previous_rate(pair)
        
        # Calculate change percentage
        change_percent = 0
        if previous_rate:
            change_percent = ((rate - previous_rate) / previous_rate) * 100
        
        # Update Prometheus gauge
        CURRENT_RATE.labels(pair=pair).set(rate)
        
        # Save rate to database
        save_rate(pair, rate, change_percent)
        print(f"{pair}: {rate} (change: {change_percent:.4f}%)")
        
        # Run anomaly detection
        anomaly = analyze_rate(pair, rate, change_percent, previous_rate)
        if anomaly:
            save_anomaly(pair, rate, anomaly['rule'], anomaly['severity'])
            print(f"ANOMALY DETECTED: {pair} - {anomaly['rule']} - {anomaly['severity']}")
            
            # Trigger Logic App alert
            logic_app_url = os.getenv('LOGIC_APP_URL')
            if logic_app_url:
                try:
                    requests.post(logic_app_url, json={
                        'pair': pair,
                        'rate': rate,
                        'rule': anomaly['rule'],
                        'severity': anomaly['severity'],
                        'timestamp': str(datetime.utcnow())
                    })
                    print("Alert sent to Logic App")
                except Exception as e:
                    print(f"Failed to send alert: {e}")

if __name__ == '__main__':
    print("Starting Currency Anomaly Detection Pipeline")
    
    # Start Prometheus metrics server
    start_http_server(8000)
    print("Prometheus metrics available at port 8000")
    
    # Setup database tables
    setup_database()
    
    # Run pipeline immediately on start
    run_pipeline()
    
    # Schedule pipeline every 10 minutes
    schedule.every(10).minutes.do(run_pipeline)
    
    print("Pipeline scheduled every 10 minutes")
    
    while True:
        schedule.run_pending()
        time.sleep(1)
