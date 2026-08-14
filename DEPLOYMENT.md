# BactoAI Deployment Guide

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLINIC USER                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Browser (Chrome/Firefox)                                │   │
│  │  - Login with credentials                                │   │
│  │  1 Upload .fna genome file                               │   │
│  │  - Enter sample ID and notes                             │   │
│  │  - View prediction results                               │   │
│  │  - View submission history                               │   │
│  └─────────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTPS
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BACTOAI SERVER                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Flask App (app.py)                                      │   │
│  │  - Authentication (session-based)                        │   │
│  │  - File upload & prediction                              │   │
│  │  - Submission history                                    │   │
│  │  - Audit logging                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│  ┌────────────────────┐   │   ┌────────────────────────────┐   │
│  │  SQLite Database   │◄──┘   │  Model Weights (files)     │   │
│  │  - users           │       │  - models_v4/*.joblib      │   │
│  │  - submissions     │       │  - transformers_v4/*.joblib │   │
│  │  - audit_log       │       │  - models/*.json           │   │
│  └────────────────────┘       └────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Option 1: Local Server (Quick Start)

### Prerequisites
- Python 3.9+
- pip

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/Savville/BactoAI.git
cd BactoAI

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize database
flask init-db

# 5. Create your first user
flask create-user
# Enter username, password, and clinic name

# 6. Run the app
flask run --host=0.0.0.0 --port=5000
```

Now open `http://localhost:5000` in your browser.

### For Network Access (other computers in same network):
```bash
# Find your IP address
# Windows: ipconfig | findstr IPv4
# Linux/Mac: ifconfig | grep inet

# Run with host=0.0.0.0 to allow network access
flask run --host=0.0.0.0 --port=5000

# Other computers access via: http://YOUR_IP:5000
```

---

## Option 2: Docker Deployment

### Build and Run Locally

```bash
# Build image
docker build -t bactoai .

# Run container
docker run -d \
  --name bactoai \
  -p 8080:8080 \
  -v bactoai-data:/app/data \
  -e BACTOAI_SECRET=your-secret-key-here \
  bactoai

# Create user
docker exec -it bactoai flask create-user
```

### Deploy to Cloud with Docker

#### Google Cloud Run (Recommended - Free Tier Eligible)

```bash
# 1. Install gcloud CLI and authenticate
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# 2. Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/bactoai

# 3. Deploy to Cloud Run
gcloud run deploy bactoai \
  --image gcr.io/YOUR_PROJECT_ID/bactoai \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --timeout 300

# 4. Set environment variables
gcloud run services update bactoai \
  --set-env-vars BACTOAI_SECRET=your-secret-key-here
```

#### AWS (ECS/Fargate)

```bash
# 1. Create ECR repository
aws ecr create-repository --repository-name bactoai

# 2. Build and push
aws ecr get-login-password | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com
docker build -t bactoai .
docker tag bactoai:latest ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/bactoai:latest
docker push ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/bactoai:latest

# 3. Create ECS cluster and service (see AWS docs for full setup)
```

---

## Option 3: Platform-as-a-Service (PaaS)

### Render.com (Simplest - Free Tier)

1. Connect GitHub repository on render.com
2. Create new Web Service:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Environment: `BACTOAI_SECRET=your-secret-key`
3. Add persistent disk for database (Settings > Disks)
4. Deploy

### Railway.app

1. Connect GitHub repo
2. Set environment variables:
   - `BACTOAI_SECRET=your-secret-key`
3. Deploy

### Fly.io

```bash
# Install flyctl
flyctl auth login

# Launch app
flyctl launch

# Set secrets
flyctl secrets set BACTOAI_SECRET=your-secret-key

# Deploy
flyctl deploy
```

---

## Production Checklist

- [ ] Change `BACTOAI_SECRET` to a long random string
- [ ] Use HTTPS (handled by most cloud platforms)
- [ ] Set up regular database backups
- [ ] Configure proper CORS if using separate frontend
- [ ] Add rate limiting (Flask-Limiter)
- [ ] Set up monitoring/alerting
- [ ] Add health check endpoint (`/health` already exists)
- [ ] Configure proper logging

---

## Database Schema

### users
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| username | TEXT UNIQUE | Login name |
| password_hash | TEXT | PBKDF2 hashed |
| clinic_name | TEXT | User's facility |
| created_at | TIMESTAMP | Registration date |
| is_active | INTEGER | Soft delete flag |

### submissions
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| user_id | INTEGER FK | Who submitted |
| sample_id | TEXT | User-provided ID |
| filename | TEXT | Original filename |
| genome_size | INTEGER | File size in bytes |
| meropenem_label | TEXT | RESISTANT/SUSCEPTIBLE |
| meropenem_prob REAL | Probability 0-1 |
| meropenem_confidence | TEXT | HIGH/MEDIUM/LOW |
| ciprofloxacin_label | TEXT | (same pattern) |
| cefotaxime_label | TEXT | (same pattern) |
| submitted_at | TIMESTAMP | When submitted |
| notes | TEXT | Optional notes |

### audit_log
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| user_id | INTEGER FK | Who did it |
| action | TEXT | login/logout/predict |
| details | TEXT | Extra info |
| ip_address | TEXT | Source IP |
| created_at | TIMESTAMP | When |

---

## Next Phases

### Phase 1: Basic Hosting (Week 1-2)
- Deploy to Render/Railway/Fly.io
- Test with clinic staff
- Gather feedback

### Phase 2: Multi-tenancy (Week 3-4)
- Add role-based access (admin/viewer)
- Admin dashboard for all submissions
- Export results as CSV/PDF

### Phase 3: Integration (Week 5-6)
- REST API for lab instrument integration
- HL7/FHIR compatibility for hospital systems
- Bulk upload support

### Phase 4: Monitoring & Retraining (Week 7+)
- Track prediction accuracy vs lab results
- Flag uncertain predictions for manual review
- Continuous model improvement cycle

---

## Troubleshooting

### Database locked errors
SQLite works best for <100 concurrent users. For higher load:
- Switch to PostgreSQL (change DB_PATH to connection string)
- Or use Docker with volume mount for persistence

### Model files too large for GitHub
- Use Git LFS for .joblib files
- Or download from Google Drive on first run
- Or build Docker image with models included

### Port already in use
```bash
# Find process using port 5000
# Windows: netstat -ano | findstr :5000
# Linux: lsof -i :5000

# Kill or use different port
flask run --port=8080
```
