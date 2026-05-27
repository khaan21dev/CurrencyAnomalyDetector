# Currency Trade Anomaly Detection Pipeline

A real-time currency exchange rate monitoring and anomaly detection pipeline inspired by MiFID II and Market Abuse Regulation (MAR) requirements. The system fetches live PLN/EUR, PLN/USD, and PLN/GBP exchange rates every 10 minutes, applies statistical anomaly detection rules, stores all data in Azure SQL, and fires automated email alerts via Azure Logic Apps when suspicious movements are detected. Built with Python, Docker, Terraform, Prometheus, and Grafana — fully containerised and deployable on Azure.

---

## Architecture

```
frankfurter.app (Free Exchange Rate API)
        ↓
Python Pipeline (Docker Container)
Fetches rates every 10 minutes
        ↓
Azure SQL Database
Stores rates and anomalies
        ↓
Anomaly Detection Engine
3 rules inspired by MiFID II, MAR, AML
        ↓
Anomaly Detected?
Yes → Azure Logic Apps → Email Alert
        ↓
Prometheus scrapes pipeline metrics
        ↓
Grafana Dashboard
Live rates, anomaly history, pipeline health
```

---

## Anomaly Detection Rules

### Rule 1 — Rate Velocity Breach (MiFID II)
Flags when a currency pair moves more than **1.5% in a single 10-minute window**. MEDIUM severity between 1.5% and 3%, HIGH severity above 3%. MiFID II requires real-time surveillance of unusual price movements that could indicate market manipulation.

### Rule 2 — Psychological Level Crossing (MAR)
Flags when a rate crosses key psychological levels — 4.10, 4.15, 4.20, 4.25, 4.30, 4.35, 4.40. Under Market Abuse Regulation, sudden crossings of key price levels can indicate coordinated trading activity.

### Rule 3 — Structuring Detection (AML)
Flags when a rate sits just below a round number threshold. Anti-Money Laundering regulations specifically target structuring behavior — artificially keeping values just below round number thresholds to avoid detection systems.

---

## Tech Stack

| Technology | Role |
|---|---|
| Python | Core pipeline — data ingestion, transformation, anomaly detection |
| Docker | Containerised application |
| Docker Compose | Local orchestration of pipeline, Prometheus, and Grafana |
| Terraform | Infrastructure as Code — provisions all Azure resources |
| Azure SQL Database | Stores exchange rates and detected anomalies |
| Azure Container Registry | Stores Docker images for production deployment |
| Azure Logic Apps | Automated email alerts on anomaly detection |
| Prometheus | Pipeline health monitoring — fetch count, duration, anomaly count |
| Grafana | Live dashboard — exchange rates, anomaly metrics, pipeline health |

---

## Azure Infrastructure (Terraform)

All Azure resources are provisioned with a single `terraform apply`:

- Resource Group — RG-CurrencyAnomalyDetector
- Azure SQL Server — North Europe
- Azure SQL Database — Basic tier
- Azure Container Registry — Basic tier
- Firewall rules — allow pipeline access to SQL

---

## Project Structure

```
currency-anomaly-detector/
├── pipeline/
│   ├── app.py              # Main pipeline engine
│   ├── detector.py         # Anomaly detection rules
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Container definition
├── terraform/
│   ├── main.tf             # Azure infrastructure
│   ├── variables.tf        # Configurable variables
│   └── outputs.tf          # Post-deployment outputs
├── grafana/
│   └── prometheus.yml      # Prometheus scrape config
├── docker-compose.yml      # Local stack orchestration
├── .env.example            # Environment variable template
└── README.md
```

---

## How to Run Locally

**Prerequisites:** Docker Desktop, Terraform, Azure CLI, Azure account

**Step 1 — Clone the repo**
```bash
git clone https://github.com/khaan21dev/CurrencyAnomalyDetector.git
cd CurrencyAnomalyDetector
```

**Step 2 — Provision Azure infrastructure**
```bash
cd terraform
terraform init
terraform apply -var='sql_admin_password=YourPassword123!' -var='logic_app_url=your-logic-app-url'
```

**Step 3 — Configure environment variables**
```bash
cp .env.example .env
```
Fill in `.env` with your real values from Terraform output.

**Step 4 — Start the pipeline**
```bash
docker-compose up --build
```

**Step 5 — Access the stack**

| Service | URL |
|---|---|
| Pipeline metrics | http://localhost:8000 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |

Grafana login: admin / admin

---

## Email Alerts

When an anomaly is detected the pipeline sends an HTTP POST to Azure Logic Apps which triggers an automated email containing the currency pair affected, current rate, rule triggered, severity level, and timestamp.

---

## Regulatory References

- **MiFID II** — Markets in Financial Instruments Directive II — requires real-time surveillance of trading activity
- **MAR** — Market Abuse Regulation — mandates detection of unusual price movements
- **AML** — Anti-Money Laundering — targets structuring behavior in financial transactions
- **EMIR** — European Market Infrastructure Regulation — trade reporting and monitoring requirements

---

## Screenshots

All screenshots can be found at SCREENSHOTS folder
