# BactoAI - Team Continuation Guide

## Project Overview

BactoAI is an AI-powered antibiotic resistance prediction system. It analyzes bacterial genome sequences (.fna files) and predicts whether the bacteria is resistant or susceptible to three antibiotics: Meropenem, Ciprofloxacin, and Cefotaxime.

## Current State

- **Model**: v4 Deep Ensemble (5 models per antibiotic, uncertainty-aware)
- **Web App**: Flask-based with login, file upload, prediction, and history tracking
- **Database**: SQLite (logs all users, submissions, and audit trail)
- **Deployment**: Ready for local network or cloud hosting

## Repository Setup

### Two Remotes

```bash
# Check remotes
git remote -v

# origin = your personal repo (Savville/BactoAI)
# bactoai-eng = team repo (bactoai-eng/BACTOAI)

# Push to both
git push origin main
git push bactoai-eng main
```

### Clone (for new team members)

```bash
git clone https://github.com/bactoai-eng/BACTOAI.git
cd BactoAI
```

---

## Local Development

### Prerequisites
- Python 3.9 or higher
- pip

### Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Mac/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Initialize Database

```bash
python -c "from app import init_db; init_db()"
```

### Create First User

```bash
python -c "
from app import get_db, hash_password
import sqlite3
db = sqlite3.connect('data/bactoai.db')
db.execute('INSERT INTO users (username, password_hash, clinic_name) VALUES (?, ?, ?)',
    ('admin', hash_password('YOUR_PASSWORD'), 'Lab Name'))
db.commit()
db.close()
print('User created')
"
```

### Run Locally

```bash
python app.py
```

Open browser: `http://localhost:5000`

---

## Network Access (Clinic/Lab)

To allow other computers on the same network to access the app:

### Step 1: Find Your IP Address

**Windows:**
```bash
ipconfig | findstr IPv4
```

**Mac/Linux:**
```bash
ifconfig | grep inet
```

Look for something like `192.168.x.x` or `10.x.x.x`.

### Step 2: Run with Network Access

```bash
python app.py
```

The app runs on `0.0.0.0:5000` by default, meaning it accepts connections from any network interface.

### Step 3: Share the URL

Give other users: `http://YOUR_IP:5000`

Example: `http://192.168.1.42:5000`

### Firewall (if blocked)

**Windows:**
1. Open Windows Defender Firewall
2. Click "Allow an app through firewall"
3. Add Python or port 5000

Or run as Administrator.

---

## Cloud Deployment (Render.com - Free Tier)

Render provides free hosting with a public URL. This is the easiest way to make the app accessible from anywhere (not just local network).

### Prerequisites
- GitHub account
- Render account (render.com) - free tier available

### Step 1: Connect Repository

1. Go to render.com → Sign up / Log in
2. Click **New +** → **Web Service**
3. Connect GitHub account
4. Select repository: `bactoai-eng/BACTOAI`
5. Choose branch: `main`

### Step 2: Configure Service

| Setting | Value |
|---------|-------|
| Name | `bactoai` |
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:app` |
| Instance Type | Free (or Sticky for better performance) |

### Step 3: Add Environment Variables

In Render dashboard → Environment → Add:

| Key | Value |
|-----|-------|
| `BACTOAI_SECRET` | Generate a random string (e.g., `python -c "import secrets; print(secrets.token_hex(32))"`) |

### Step 4: Add Persistent Disk (Important!)

SQLite needs persistent storage:

1. In Render dashboard → Disks → Add Disk
2. Name: `bactoai-data`
3. Mount Path: `/app/data`
4. Size: 1 GB (free tier)

### Step 5: Deploy

Click **Create Web Service**. Render will:
1. Install dependencies
2. Start the app
3. Provide a URL: `https://bactoai.onrender.com`

### Step 6: Create First User (After Deploy)

```bash
# Open Render Shell (in dashboard → Shell tab)
python -c "
from app import init_db, get_db, hash_password
init_db()
import sqlite3
db = sqlite3.connect('data/bactoai.db')
db.execute('INSERT INTO users (username, password_hash, clinic_name) VALUES (?, ?, ?)',
    ('admin', hash_password('SECURE_PASSWORD'), 'Central Lab'))
db.commit()
db.close()
print('Admin user created')
"
```

---

## Cloud Deployment (Docker - Alternative)

If you prefer Docker or need more control:

### Build Image

```bash
docker build -t bactoai .
```

### Run Locally with Docker

```bash
docker run -d \
  --name bactoai \
  -p 8080:8080 \
  -v bactoai-data:/app/data \
  -e BACTOAI_SECRET=your-secret-key \
  bactoai
```

### Deploy to Google Cloud Run

```bash
# Install gcloud CLI first
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Build and push
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/bactoai

# Deploy
gcloud run deploy bactoai \
  --image gcr.io/YOUR_PROJECT_ID/bactoai \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi
```

---

## Project Structure

```
BACTOAI/
├── app.py                          # Flask application (auth, API, database)
├── bactoai_pipeline.py             # ML pipeline (feature extraction, training)
├── requirements.txt                # Python dependencies
├── Procfile                        # Render/Railway deployment config
├── Dockerfile                      # Docker deployment
├── .gitignore / .dockerignore      # Exclusion rules
├── DEPLOYMENT.md                   # Detailed deployment guide
├── README.md                       # Project overview
│
├── templates/
│   ├── index.html                  # Main page (upload + results)
│   ├── auth_base.html              # Base template for auth pages
│   ├── login.html                  # Login page
│   ├── register.html               # Registration page
│   └── history.html                # Submission history table
│
├── static/
│   └── style.css                   # All styles
│
├── scripts/
│   └── ncbi_bigquery.py            # BigQuery data enrichment
│
└── data/
    ├── models_v4/                  # Trained models (15 .joblib files)
    ├── transformers_v4/            # Feature transformers (6 files)
    ├── models/                     # Legacy v3 models
    ├── transformers/               # Legacy v3 transformers
    ├── bigquery_output/            # Enrichment results
    └── bactoai.db                  # SQLite database (created on init)
```

---

## Database Reference

### Tables

**users**
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| username | TEXT UNIQUE | Login name |
| password_hash | TEXT | PBKDF2 hashed password |
| clinic_name | TEXT | User's facility name |
| created_at | TIMESTAMP | Registration date |
| is_active | INTEGER | Soft delete flag (1=active) |

**submissions**
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| user_id | INTEGER FK | References users.id |
| sample_id | TEXT | User-provided sample identifier |
| filename | TEXT | Original uploaded filename |
| genome_size | INTEGER | File size in bytes |
| meropenem_label | TEXT | RESISTANT/SUSCEPTIBLE |
| meropenem_prob REAL | Probability (0-1) |
| meropenem_confidence | TEXT | HIGH/MEDIUM/LOW |
| ciprofloxacin_label | TEXT | Same pattern |
| cefotaxime_label | TEXT | Same pattern |
| submitted_at | TIMESTAMP | When prediction was made |
| notes | TEXT | Optional user notes |

**audit_log**
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| user_id | INTEGER FK | Who performed the action |
| action | TEXT | login/logout/predict |
| details | TEXT | Additional info |
| ip_address | TEXT | Source IP address |
| created_at | TIMESTAMP | When action occurred |

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/login` | No | Login page |
| POST | `/login` | No | Submit credentials |
| GET | `/register` | No | Registration page |
| POST | `/register` | No | Create account |
| GET | `/logout` | Yes | Clear session |
| GET | `/` | Yes | Main prediction page |
| POST | `/predict` | Yes | Upload genome, get predictions |
| GET | `/history` | Yes | View submission history |
| GET | `/history/json` | Yes | JSON API for history |
| GET | `/validate` | Yes | Run model validation |
| GET | `/health` | No | Health check (models + DB) |

---

## Prediction API Usage

### Upload and Predict

```bash
curl -X POST -F "file=@genome.fna" \
     -F "sample_id=PAT-001" \
     -F "notes=Blood culture, patient fever" \
     -b "session=YOUR_SESSION_COOKIE" \
     https://your-app.onrender.com/predict
```

### Response Format

```json
{
  "filename": "genome.fna",
  "results": [
    {
      "antibiotic": "Meropenem",
      "probability": 0.8234,
      "lower_bound": 0.7123,
      "upper_bound": 0.9345,
      "label": "RESISTANT",
      "status": "resistant",
      "confidence": "HIGH",
      "recommendation": "Likely resistant. Consider an alternative antibiotic.",
      "adaptive_threshold": 0.55
    },
    {
      "antibiotic": "Ciprofloxacin",
      "probability": 0.1234,
      "lower_bound": 0.0456,
      "upper_bound": 0.2012,
      "label": "SUSCEPTIBLE",
      "status": "susceptible",
      "confidence": "HIGH",
      "recommendation": "Likely susceptible based on the current model ensemble.",
      "adaptive_threshold": 0.52
    }
  ]
}
```

---

## Key Files Explained

### `app.py` - Main Application
- Handles user authentication (login/register/logout)
- Serves web pages
- Processes file uploads
- Runs predictions
- Logs everything to SQLite

### `bactoai_pipeline.py` - ML Pipeline
- Feature extraction from genomes (k-mers + gene signatures)
- Model training with deep ensembles
- Conformal prediction
- Uncertainty quantification

### `templates/index.html` - Frontend
- Drag-and-drop file upload
- Sample ID and notes fields
- Results display with probabilities and confidence intervals
- Navigation to history page

---

## Common Tasks

### Add a New User

```bash
# Using Flask CLI
flask create-user

# Or directly in Python
python -c "
from app import get_db, hash_password
import sqlite3
db = sqlite3.connect('data/bactoai.db')
db.execute('INSERT INTO users (username, password_hash, clinic_name) VALUES (?, ?, ?)',
    ('newuser', hash_password('password123'), 'Clinic Name'))
db.commit()
db.close()
"
```

### Backup Database

```bash
# SQLite backup (just copy the file)
copy data\bactoai.db data\bactoai_backup.db

# Or export to SQL
.venv\Scripts\sqlite3.exe data\bactoai.db .dump > backup.sql
```

### View All Submissions

```bash
python -c "
import sqlite3
db = sqlite3.connect('data/bactoai.db')
db.row_factory = sqlite3.Row
rows = db.execute('SELECT * FROM submissions ORDER BY submitted_at DESC LIMIT 10').fetchall()
for r in rows:
    print(dict(r))
"
```

### Retrain Models (New Data)

1. Add new metadata CSV to `data/`
2. Add new genome files to `data/genomes/`
3. Run:
```bash
python bactoai_pipeline_v4.py --train --antibiotic meropenem
python bactoai_pipeline_v4.py --train --antibiotic ciprofloxacin
python bactoai_pipeline_v4.py --train --antibiotic cefotaxime
```

---

## Model Performance

| Antibiotic | Accuracy | ROC-AUC | Training Samples |
|------------|----------|---------|------------------|
| Meropenem | 89.5% | 0.942 | 124 |
| Ciprofloxacin | 81.8% | 0.877 | 143 |
| Cefotaxime | 78.6% | 0.872 | 145 |

*Metrics from v4 ensemble (5 seeds, 25% holdout)*

---

## Security Notes

1. **Change default passwords** - Never use default credentials in production
2. **Use HTTPS** - Render provides this by default
3. **Secret Key** - Set `BACTOAI_SECRET` environment variable to a long random string
4. **Database** - Keep `data/bactoai.db` backed up regularly
5. **File Uploads** - App only accepts `.fna`, `.fasta`, `.gz` files

---

## Troubleshooting

### Port Already in Use
```bash
# Windows: find process on port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Or change port in app.py
app.run(host="0.0.0.0", port=8080)
```

### Database Locked (SQLite)
SQLite allows one writer at a time. For high concurrency:
- Switch to PostgreSQL
- Or use WAL mode (already enabled in app.py)

### Model Loading Errors
Ensure all files are present:
- `data/models_v4/model_{antibiotic}_model{0-4}.joblib` (15 files)
- `data/transformers_v4/vectorizer_{antibiotic}.joblib` (3 files)
- `data/transformers_v4/selector_{antibiotic}.joblib` (3 files)

### sklearn Version Warnings
Models were trained with sklearn 1.7.2, current is 1.8.0.
Warnings are non-critical. To eliminate:
```bash
pip install scikit-learn==1.7.2
```
Or retrain models with current version.

---

## Next Development Priorities

1. **Deploy to Render** - Get a public URL for clinics
2. **Add results export** - PDF reports, CSV download
3. **Admin dashboard** - View all users and submissions
4. **Bulk upload** - Multiple genomes at once
5. **Retraining pipeline** - Feedback loop from lab results
6. **PostgreSQL** - For production scale

---

## Contact & Resources

- **Team Repo**: https://github.com/bactoai-eng/BACToai-eng/BACTOAI
- **Render Dashboard**: https://dashboard.render.com
- **Flask Docs**: https://flask.palletsprojects.com
- **scikit-learn**: https://scikit-learn.org
