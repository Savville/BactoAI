# BactoAI — Deployment, Infrastructure & Hosting Guide

## Context
BactoAI is live on Render and Vercel but the user has questions about infrastructure: what the warnings mean, whether they need a larger backend, what VPS is, how PostgreSQL fits in, and how hosting + domain names work. This document explains all these concepts clearly.

---

## 1. The sklearn Warnings — What Do They Mean?

The warnings you see:
```
InconsistentVersionWarning: Trying to unpickle estimator DecisionTreeClassifier 
from version 1.7.2 when using version 1.8.0
```

**This is NOT an error. Your app is working fine.** Here's what it means:

| Aspect | Explanation |
|--------|-------------|
| **What happened** | Your ML models were trained and saved using scikit-learn 1.7.2, but Render installed 1.8.0 |
| **Is it breaking?** | No — the models still load and predictions still work |
| **Should you worry?** | Minor — predictions might be 0.1–0.5% less optimal than with the exact version |
| **Do you need bigger servers?** | **No** — this has nothing to do with server size or memory |

**Fix (optional):** Pin scikit-learn to 1.7.2 in `requirements-ml.txt` to eliminate warnings:
```
scikit-learn==1.7.2
```

---

## 2. Do You Need a Database (PostgreSQL)?

### Current Situation
BactoAI currently uses **SQLite** — a file-based database stored on the server's filesystem.

### The Problem with SQLite on Render
Render has an **ephemeral filesystem** — meaning:
- Every time Render redeploys or restarts your service, the SQLite database is **wiped clean**
- All user accounts, submission history, and feedback data are **lost**
- That's why the admin user must be recreated on every startup (we coded a workaround)

### PostgreSQL — The Solution
**PostgreSQL** (not a "language" — it's a database *system*) is a proper server-based database that:

| Feature | SQLite (current) | PostgreSQL (recommended) |
|---------|------------------|--------------------------|
| **Data persistence** | ❌ Lost on redeploy | ✅ Permanent, survives restarts |
| **Concurrent users** | ⚠️ Struggles with many | ✅ Handles hundreds/thousands |
| **Data safety** | ❌ Single file, easy to corrupt | ✅ Enterprise-grade reliability |
| **Backups** | Manual | Automated |
| **Where it runs** | Same server as app | Separate managed service |

### What You Store in PostgreSQL
- **User accounts** (usernames, passwords, roles)
- **Submission history** (every genome analyzed)
- **Feedback data** (lab-confirmed results for model improvement)
- **API keys**
- **Audit logs**

### What About the Genome Files (.fna files)?
Genome files should NOT go in the database. Instead:
- Store them in **cloud object storage** (AWS S3, Google Cloud Storage, or Cloudflare R2)
- Database stores only the **file path/metadata**, not the file itself

### Recommendation
**Yes, you should migrate to PostgreSQL** — especially if:
- You want user data to persist across deploys
- Multiple users will use the app simultaneously
- You're collecting feedback data for model retraining

---

## 3. What is VPS? How Does It Relate to Render?

### Definitions

| Term | What It Is | Analogy |
|------|-----------|---------|
| **Render** | Platform-as-a-Service (PaaS) — you push code, they run it | Like renting a furnished apartment — everything is managed for you |
| **VPS** (Virtual Private Server) | A virtual machine in the cloud where you control everything | Like renting an empty house — you bring your own furniture, plumbing, electricity |
| **Cloud Hosting** (AWS, GCP, Azure) | The underlying infrastructure that powers everything | The land the house is built on |

### Render vs VPS — Comparison

| Aspect | Render (PaaS) | VPS (e.g., DigitalOcean, Linode, Hetzner) |
|--------|--------------|------------------------------------------|
| **Setup complexity** | Easy — push code, it runs | Harder — you configure everything |
| **Control** | Limited — Render decides the environment | Full — you install OS, software, everything |
| **Scaling** | Automatic (mostly) | Manual — you resize the server |
| **Cost** | Higher per unit of power | Cheaper for same resources |
| **Maintenance** | Render handles server security patches | YOU handle all security, updates |
| **Persistence** | Ephemeral filesystem (data lost on redeploy) | Permanent filesystem (your disk, your rules) |
| **Database** | Add-on service or external | Install PostgreSQL yourself on same/different server |
| **Custom software** | Limited to what Render supports | Install anything you want |
| **SSH access** | ❌ No | ✅ Full root access |

### Can VPS Replace Render?
**Yes, absolutely.** A VPS can do everything Render does, plus more. But you trade convenience for control.

### What Moving to VPS Would Mean for BactoAI

| Task | On Render | On VPS |
|------|-----------|--------|
| Deploy app | `git push` | You configure Gunicorn + Nginx yourself |
| PostgreSQL | Add-on or external | You install and manage it |
| Environment variables | Dashboard | You edit config files |
| SSL/HTTPS | Automatic | You configure Let's Encrypt yourself |
| Monitoring | Built-in | You set up your own |
| Backups | Built-in | You script them yourself |
| Updates | Render handles OS patches | **You** must patch the OS monthly |

### Typical VPS Providers
| Provider | Starting Price | Good For |
|----------|---------------|----------|
| **DigitalOcean** | $4–6/month | Beginners, good docs |
| **Linode** (Akamai) | $5/month | Reliable, simple |
| **Hetzner** | ~€3–5/month | Best price/performance in Europe |
| **AWS Lightsail** | $3.50/month | AWS ecosystem |
| **Vultr** | $2.50/month | Budget option |

### Recommendation for BactoAI
**Stay on Render for now** unless:
- You need persistent storage without paying for Render add-ons
- You want full control over the environment
- You're comfortable with Linux system administration
- You need to run custom background workers or cron jobs

If you outgrow Render, a **$6–12/month VPS from DigitalOcean or Hetzner** with PostgreSQL installed locally would serve you well.

---

## 4. How Do Hosting and Domain Names Relate to VPS?

### The Relationship

```
Domain Name (bactoai.com)
        │
        ▼
    DNS (Domain Name System)
        │
        ▼
    Server IP Address (e.g., 167.99.123.45)
        │
        ▼
    Your VPS / Render / Hosting Server
        │
        ▼
    Flask App (listening on port 5000/8000)
```

### Step-by-Step Explanation

| Component | What It Does | Analogy |
|-----------|-------------|---------|
| **Domain Name** | Human-readable address (bactoai.com) | Your business name |
| **DNS** | Translates domain → IP address | Phone book |
| **IP Address** | Server's numeric address (167.99.123.45) | Phone number |
| **Server (VPS)** | The computer running your app | Your office |
| **Web Server (Nginx)** | Receives HTTP requests, forwards to Flask | Receptionist |
| **Flask App** | Your Python application | You, doing the work |

### How They Connect

1. **Buy a domain** (e.g., from Namecheap, Google Domains, Cloudflare) — ~$10–15/year
2. **Point DNS** to your server's IP address (Render gives you a URL; VPS gives you an IP)
3. **Server receives requests** on port 80 (HTTP) or 443 (HTTPS)
4. **Nginx/Reverse proxy** forwards to your Flask app
5. **Flask processes** the request and returns the response

### On Render
- Render gives you a free URL: `bactoai.onrender.com`
- You can add a custom domain (bactoai.com) in Render dashboard
- Render handles DNS configuration guides + free SSL

### On VPS
- You get an IP address from the VPS provider
- You manually configure DNS to point your domain to that IP
- You install and configure Nginx as a reverse proxy
- You set up Let's Encrypt for free SSL certificates

### Cost Breakdown
| Item | Cost |
|------|------|
| Domain name (.com) | $10–15/year |
| VPS server | $4–12/month |
| SSL certificate | Free (Let's Encrypt) |
| DNS hosting | Free (Cloudflare) |
| **Total for self-hosted** | **~$50–150/year** |
| **Render (hobby tier)** | **$7/month + domain** |

---

## 5. Summary — Where BactoAI Stands

| Component | Current Setup | Recommendation |
|-----------|--------------|----------------|
| **Hosting** | Render (PaaS) | ✅ Good for now — stay here |
| **Database** | SQLite (ephemeral) | ⚠️ Migrate to PostgreSQL when you need persistence |
| **File storage** | Local filesystem | Consider cloud storage later |
| **Domain** | bactoai.onrender.com | Buy custom domain when ready for production |
| **VPS** | Not using | Not needed yet — Render handles it |
| **Warnings** | sklearn version mismatch | Pin version when convenient — not urgent |

### When to Consider Moving to VPS
- You need persistent storage without paying for Render add-ons
- You want to run background workers (Celery) for long-running predictions
- You need custom system libraries or GPU access
- You're comfortable managing a Linux server
- Cost optimization becomes important at scale

### Immediate Next Steps
1. **Don't worry about the warnings** — they're harmless
2. **Add PostgreSQL** on Render when you need data persistence
3. **Stay on Render** until you outgrow it
4. **Buy a domain** (bactoai.com or similar) when you're ready to go public
5. **Learn Linux basics** if you eventually want to move to VPS
