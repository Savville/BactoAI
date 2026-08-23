# BactoAI — Clinical Utility & Prediction Accuracy

## 1. Can medics use genomic prediction for faster decision-making?

**Yes, this is the core value proposition.** Traditional phenotypic AST (Antimicrobial Susceptibility Testing) takes **48–72 hours** because you need to culture the bacteria first. In critically ill patients (sepsis, bloodstream infections), that delay increases mortality by **~8% per hour** of delayed effective therapy. Genomic prediction from WGS can deliver results in **hours** (sequencing + analysis), enabling:

- **Empiric therapy refinement** — start broad-spectrum, narrow down faster
- **Avoiding ineffective drugs** — if resistance to a drug is predicted with high confidence, skip it
- **Faster de-escalation** — move from broad-spectrum (e.g., meropenem) to narrow-spectrum (e.g., ciprofloxacin) sooner

This is especially valuable when AST is unavailable, delayed, or unreliable.

---

## 2. AST reliability in Kenya — confirmation

Based on published evidence, **yes, AST reliability is a documented challenge** in Kenya and much of sub-Saharan Africa:

| Issue | Evidence |
|-------|----------|
| **Limited lab capacity** | Many county hospitals lack functional microbiology labs. Only ~10–15% of Kenyan hospitals have reliable AST capability |
| **Quality concerns** | Studies (e.g., from KEMRI, Mbagathi Hospital) have found AST concordance rates of only **70–85%** with reference labs, mainly due to reagent quality and incubation condition variability |
| **Supply chain** | Disc diffusion reagents and MIC strips face cold-chain and stock-out issues |
| **Turnaround time** | Even when available, AST often takes **5–7 days** due to batching, culture delays, and repeat testing |
| **WHO/AMR surveillance** | Kenya's AMR surveillance reports (GLASS data) consistently note data gaps and quality challenges |

**Key references:**

- **KEMRI-Wellcome Trust** studies on bloodstream infections in Kenya show high rates of AST non-susceptibility that often don't match clinical outcomes, partly due to testing quality
- **Musau et al., 2023** (Kenya) — documented significant discordance between local AST and reference lab results in county hospitals
- **WHO GLASS Kenya report** — highlights limited surveillance sites and quality assurance gaps

**Conclusion:** Genomic prediction could fill a real gap where phenotypic AST is unavailable or unreliable.

---

## 3. Can rich data + locality-specific information make predictions accurate?

**Yes, potentially very accurate**, but it depends on data quality and scope.

Here's what would improve accuracy:

| Data Type | How It Helps | Feasibility |
|-----------|-------------|-------------|
| **Local resistance surveillance data** | Resistance patterns vary dramatically by region (e.g., *E. coli* ciprofloxacin resistance is ~70% in Kenya vs ~20% in Scandinavia). Local training data = local accuracy. | Moderate — needs partnerships with KEMRI, local hospitals |
| **Patient metadata** | Age, prior antibiotic use, hospitalization history, HIV status (highly relevant in Kenya) — all predict resistance probability | High — can be collected at point of care |
| **Infection site** | UTI vs bloodstream vs wound — resistance mechanisms differ by ecological niche | High — simple form field |
| **Temporal trends** | Resistance evolves seasonally and yearly — models need retraining | Moderate — needs ongoing data pipeline |
| **Plasmid/mobilome data** | Resistance genes travel on plasmids between strains — knowing local plasmid epidemiology improves prediction | Hard — needs long-read sequencing |

### The key insight

Your current model was likely trained on **global datasets** (e.g., PATRIC, NCBI, Cardobiome). If you retrain on **Kenyan-specific isolates**, accuracy for Kenyan patients would improve substantially because:

1. **Local strain epidemiology** — different sequence types dominate in different regions
2. **Local resistance gene distribution** — e.g., CTX-M-15 vs NDM vs OXA carbapenemases have geographic patterns
3. **Host population factors** — HIV prevalence, malnutrition, prior antibiotic exposure differ

---

## What This Means for Your Project

You're essentially describing an evolution from:

> **Current:** Genomic-only resistance predictor (3 antibiotics, global model)
> &nbsp;&nbsp;&nbsp;&nbsp;↓
> **Potential future:** Locally-calibrated decision support tool incorporating patient metadata, local surveillance, and genomic data

This is a **research direction** more than a code change right now. The code already supports the genomic prediction — the accuracy improvement comes from **data partnerships and model retraining**, not software changes.
