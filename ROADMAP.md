# BactoAI, Technical & Business Roadmap

**Date:** 2026-10-04
**Goal:** Transform BactoAI from prototype to revenue-generating business
**Current State:** Flask web app, 3 antibiotic predictions, Supabase DB, API with auth, deployed on Render, merging into main website (in progress)

---

## Part 1: Technical Advancements

### Phase 1: Stability & Performance (2-4 weeks)

| Task                                    | Why                                                      | Effort |
| --------------------------------------- | -------------------------------------------------------- | ------ |
| Docker containerize the app             | Eliminates Render cold starts, easier local dev          | Medium |
| Add Celery + Redis for async processing | Bulk uploads won't timeout, queue genomes for prediction | Medium |
| Cache frequently-accessed genomes       | Same genome submitted twice = instant result             | Low    |
| Add Prometheus + Grafana metrics        | Monitor prediction latency, error rates, model drift     | Medium |
| Set up automated backup of Supabase     | Data loss protection                                     | Low    |
| Add Sentry for error tracking           | See production errors in real-time                       | Low    |

---

### Phase 2: ML Improvements (1-3 months)

| Task                        | Why                                                    | Effort          |
| --------------------------- | ------------------------------------------------------ | --------------- |
| Add more antibiotics        | Tazobactam, colistin, amikacin increase clinical value | Medium          |
| Add more species            | Pseudomonas, Enterococcus expand use cases             | Medium          |
| Retrain models quarterly    | New NCBI data improves accuracy over time              | Low (automated) |
| Add species-aware modeling  | Different models per species = better accuracy         | Medium          |
| Implement active learning   | Feedback loop from lab results retrains model          | High            |
| Calibrate confidence scores | Better uncertainty estimates = more trust              | Medium          |

---

### Phase 3: Integration Features (1-2 months)

| Task                      | Why                                         | Effort |
| ------------------------- | ------------------------------------------- | ------ |
| HL7/FHIR interface        | Connect to hospital lab information systems | High   |
| Batch processing workflow | Upload 100 genomes, get report back         | Medium |
| PDF report generation     | Professional results for clinicians         | Low    |
| Email/SMS notification    | "Your results are ready"                    | Low    |
| REST API documentation    | Swagger/OpenAPI spec for developers         | Low    |
| Webhook support           | Push results to external systems            | Medium |

---

### Phase 4: Advanced (3-6 months)

| Task                          | Why                                   | Effort |
| ----------------------------- | ------------------------------------- | ------ |
| Multi-tenant SaaS             | Each hospital gets isolated data      | High   |
| Role-based access control     | Lab tech vs admin vs researcher views | Medium |
| Geospatial heatmap            | Show resistance trends by region      | Medium |
| Predictive outbreak detection | Flag unusual resistance patterns      | High   |
| Mobile app (React Native)     | Field use in clinics without laptops  | High   |

---

---

## Part 2: Ground Activities & Partnerships

### MOUs & Institutional Agreements

| Organization                                                  | Purpose                                                                     | Status                      | Value                                              |
| ------------------------------------------------------------- | --------------------------------------------------------------------------- | --------------------------- | -------------------------------------------------- |
| **ASM (American Society for Microbiology)**             | Technical endorsement, conference visibility, credibility in clinical micro | In progress, MOU drafting | High, global microbiology authority              |
| **Kenya Ministry of Health**                            | National guideline integration, pilot sites in public hospitals             | Early outreach              | High, government adoption = massive scale        |
| **Africa CDC**                                          | Continental AMR surveillance program, funding alignment                     | Researching                 | High, continental reach, grant pipeline          |
| **WHO Global AMR Observatory**                          | Data contribution, methodological alignment                                 | Long-term                   | High, WHO backing validates the product          |
| **Local teaching hospitals** (KEMRI, Moi Referral, KNH) | Clinical validation, training programs, real-world testing                  | Outreach phase              | High, peer-reviewed evidence + free case studies |

---

### What an ASM MOU Looks Like

**Possible terms:**

- ASM endorses BactoAI as a decision-support tool (not a diagnostic replacement)
- Co-branded webinars or workshops at ASM Conferences
- BactoAI featured in ASM's member resources or Continuing Medical Education (CME)
- Discounted access for ASM members
- Joint publication on accuracy/validation study

**Why it matters:**

- Instant credibility in clinical microbiology circles
- Access to 35,000+ infectious disease professionals
- Potential pathway into hospital lab workflows
- Publishable validation data co-branded with a recognized society

---

### Antimicrobial Resistance Partnerships

| Partner Type                        | Example                                       | What You Offer                                          | What You Gain                                         |
| ----------------------------------- | --------------------------------------------- | ------------------------------------------------------- | ----------------------------------------------------- |
| **AMR surveillance networks** | GLASS (WHO), NRSN (Kenya)                     | Genomic resistance data, trend visualizations           | Legitimacy, data-sharing agreements, policy influence |
| **Diagnostic labs**           | reference labs in East Africa                 | Free/ discounted tool access                            | Real-world validation data, feedback loop             |
| **Pharma companies**          | GSK, Johnson & Johnson AMR divisions          | Targeted resistance landscape data                      | Sponsorship, research grants                          |
| **Academic institutions**     | University of Nairobi, KEMRI-Wellcome         | Student training, co-supervised theses, research papers | Talent pipeline, publication credits                  |
| **NGOs**                      | Wellcome Trust, Gates Foundation AMR programs | Surveillance dashboards for underserved regions         | Grant funding, field deployment                       |

---

### Ground-Level Activities (Ongoing)

| Activity                          | Frequency              | Owner          | Notes                                               |
| --------------------------------- | ---------------------- | -------------- | --------------------------------------------------- |
| MOU negotiations (ASM, Kenya MoH) | Weekly                 | Founder        | Legal review required before signing                |
| Hospital pilot visits             | Bi-weekly              | Founder + team | Nairobi, Mombasa, Kisumu target cities              |
| Conference attendance             | Quarterly              | Founder        | Kenya Medical Laboratory Congress, AST meetings     |
| Data-sharing agreements           | Ongoing                | Team           | With partner labs for model retraining              |
| Training workshops for lab techs  | Monthly                | Founder        | Build community, collect feedback, demonstrate tool |
| Grant applications                | As opportunities arise | Founder        | WHO, Gates, EU Horizon, USAID                       |

---

## Part 5: Go-to-Market Strategy

### Target Markets (Priority Order)

1. **Private clinics in East Africa**, First target (Kenya pitch deck ready)
2. **Reference laboratories**, Already do AST, need faster results
3. **Research institutions**, Need batch analysis, publishing data
4. **Veterinary clinics**, Similar resistance patterns, less regulation
5. **Pharmaceutical companies**, Drug development, clinical trials

---

### Sales Channels

| Channel      | Approach                                                  | Cost   |
| ------------ | --------------------------------------------------------- | ------ |
| Direct sales | Visit clinics in Nairobi, Mombasa, Kisumu                 | Low    |
| Partnerships | Lab equipment distributors, reagent suppliers             | Low    |
| Conferences  | Kenya Medical Laboratory Congress, AST workshops          | Medium |
| Online       | SEO, Google Ads targeting "antibiotic resistance testing" | Medium |
| Grants       | WHO, Gates Foundation, Africa CDC funding                 | Free   |

---

### Initial Customer Acquisition

**Month 1-2:**

- Offer free pilot to 5-10 clinics
- Collect feedback and case studies
- Build referral program ($50 credit per referral)

**Month 3-4:**

- Launch paid tiers
- Target 20 paying customers
- Publish accuracy validation paper

**Month 5-6:**

- Expand to 50+ customers
- Apply for health tech grants
- Explore partnerships with diagnostic companies

---

## Part 6: Immediate Next Steps

### This Week

- [ ] **Fix prediction 500 error**, Run `migrations/supabase_setup.sql` on the Flask backend's Supabase project (see `PREDICTION_PIPELINE_FIX.md`)
- [ ] Verify `/health` returns `database_ok: true`
- [ ] Create pricing page and billing setup (Stripe)
- [ ] Draft pilot agreement for first 5 clinics
- [ ] Advance ASM MOU negotiations, legal review of draft terms

### This Month

- [ ] Add 1-2 more antibiotics
- [ ] Reach out to 10 clinics in Nairobi
- [ ] Apply for 2-3 relevant grants

### This Quarter

- [ ] 20 paying customers
- [ ] Published validation study
- [ ] HL7/FHIR integration MVP
- [ ] Grant funding secured

---

## Summary

| Dimension    | Action                                             | Impact                |
| ------------ | -------------------------------------------------- | --------------------- |
| Tech         | Docker, async processing, monitoring               | Production-ready      |
| ML           | More antibiotics, species models, active learning  | Competitive advantage |
| Business     | SaaS subscription starting at $99/month            | Recurring revenue     |
| Sales        | Direct clinic outreach in Kenya                    | First customers       |
| Partnerships | ASM MOU, AMR org alliances, government pilot sites | Credibility + scale   |

---

*This roadmap is based on the current BactoAI codebase, the Kenya pitch deck, and standard health-tech startup patterns. Adjust timelines based on available resources.*
