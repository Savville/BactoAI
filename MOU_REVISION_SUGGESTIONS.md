# Suggested Amendments to BactoAI x OHAC-Kenya MOU (v2)

This document outlines suggested redlines, additions, and deletions for the [BactoAI x OHAC-Kenya MOU (v2) (1).pdf](file:///c:/Users/User/Documents/RESEARCH/Bacto_AI/BactoAI%20x%20OHAC-Kenya%20MOU%20(v2)%20(1).pdf). The objective is to protect BactoAI from operational overload, prevent legal and technical lock-in, and secure reciprocal value.

---

## 1. Section 4: Gram-Negative Isolate Data

### Issue
The current draft states that OHAC-Kenya will provide data "to the extent it holds them." This creates a risk where BactoAI expends pipeline and engineering resources while OHAC delivers an underpowered or incomplete dataset.

### Proposed Edit
Add a minimum data threshold condition before BactoAI initiates pipeline freezing and tool configuration.

### Suggested Draft Text
> **4.1 Data Availability Threshold:**  
> OHAC-Kenya will confirm the availability of a minimum viable dataset (defined as at least 30 resistant and 30 susceptible isolates with verified AST metadata for *Klebsiella pneumoniae*) prior to BactoAI executing the model freeze and pipeline setup. If the available isolate count falls below this threshold, the parties will agree in writing on a revised scope or timeline before technical work starts.

---

## 2. Section 5: External Validation Protocol

### Issue 1: Offline Inference Alternative (Item 2)
Allowing OHAC-Kenya to run BactoAI's offline inference tool locally means BactoAI never inspects or receives the genomic data. BactoAI would also bear the cost of packaging, deploying, and debugging custom offline software on third-party machines.

### Proposed Edit
Remove the local inference alternative from the primary validation phase.

### Suggested Draft Text
> **5.2 Blind Run Procedure:**  
> The default validation route will be used: OHAC-Kenya provides de-identified sequence files (raw FASTQ or assemblies) to BactoAI; BactoAI executes inference and returns predictions; OHAC-Kenya unblinds and scores the outputs. Any deployment of offline tools to third-party infrastructure remains outside the scope of this validation and requires a separate technical agreement.

---

### Issue 2: Publication of Unfavourable Findings (Item 5)
Section 5 states: *"A short joint report covering all results, including poor ones. Neither party suppresses or reframes unfavourable findings."*  
In low-resource clinical settings, phenotypic discordance, disk diffusion variance, or breakpoint discrepancies often produce false errors. BactoAI must have the right to investigate technical discrepancies rather than accepting raw mismatch figures as final proof of algorithmic failure.

### Proposed Edit
Add an AST discordance and QC review step prior to finalizing the report.

### Suggested Draft Text
> **5.5 Quality Review and Reporting:**  
> A joint validation report will detail all evaluated metrics. In the event of discordant results (very major or major errors), the parties will conduct a technical review to examine AST methodology, quality control logs, coverage depth, and breakpoint editions before finalizing the report. Contextual notes regarding phenotypic quality or sequencing depth will be included alongside raw metrics.

---

## 3. Section 6: Data Ownership, Access, and Restrictions

### Issue 1: Mandatory 30-Day Deletion
Requiring BactoAI to permanently delete genomes within 30 days destroys reproducibility. BactoAI cannot audit past runs or compare future model improvements against this cohort.

### Proposed Edit
Permit BactoAI to retain an archived, de-identified copy for algorithm benchmarking and reproducibility verification.

### Suggested Draft Text
> **6.5 Data Retention and Archival:**  
> BactoAI will cease active processing of the validation dataset within 30 days of issuing the final validation report. BactoAI may retain an encrypted, de-identified archive of the sequence data solely for scientific reproducibility, error auditing, and comparative benchmarking of future model iterations. BactoAI will not use the archived data for commercial distribution.

---

### Issue 2: Future Training Rights (No Retraining Rule)
Currently, Section 6 strictly bars model training and states that any training addendum promises no equity or revenue share. BactoAI provides free validation and technical work; having a path to integrate local Kenyan data into model retraining is critical.

### Proposed Edit
Insert a right of first negotiation for post-validation model retraining.

### Suggested Draft Text
> **6.9 Option for Retraining Use:**  
> Following successful delivery of the validation report, OHAC-Kenya grants BactoAI a right of first negotiation to incorporate de-identified genomic sequences into future model training sets. Terms of academic attribution, co-authorship on resulting methodology papers, and partner credits will be established in a brief addendum.

---

## 4. Section 7 & Section 10: Community Outreach and Contributions

### Issue: Unfunded Operational and Agency Labour
Section 7 and Section 10 commit BactoAI to:
1. Graphic design and writing support for AMR infographics and social posts.
2. Field survey data collection.
3. Dedicated bioinformatics training sessions for OHAC mentors and advocates.
4. Rigid response timelines (confirming speakers within 7 days of 14-day notice).

These obligations divert startup engineering resources into unpaid marketing and teaching support.

### Proposed Edit
Remove agency-style commitments (design, field collection, bioinformatics courses) and replace rigid speaker timelines with reasonable efforts.

### Suggested Draft Text
> **7.1 Webinar Participation:**  
> BactoAI will make reasonable efforts to provide a technical speaker on genomics and AI diagnostics for OHAC-Kenya webinars, subject to team availability and at least 14 days written notice.  
>  
> **7.3 Collaborative Content:**  
> The parties may jointly review and co-brand public awareness content on AMR stewardship where mutually agreed. Each party remains responsible for its own content production and design.  
>  
> **7.4 Community Surveys:**  
> OHAC-Kenya leads and conducts all community surveys, including data collection and regulatory compliance. BactoAI's role is limited to advising on survey question design and reviewing high-level aggregated trends upon request.

*(Note: In Section 10 table, delete "Bioinformatics training sessions for OHAC-Kenya mentors and advocates" and "AMR content, design and writing support".)*

---

## 5. Section 9: Funding and Resources

### Issue: Asymmetric Funder Support
Section 9 notes that OHAC-Kenya may ask BactoAI for support letters for its sponsorship and board applications, but BactoAI's upside is limited to potential lab introductions.

### Proposed Edit
Add reciprocal letters of support for BactoAI grant applications and innovation competitions.

### Suggested Draft Text
> **9.4 Mutual Grant and Innovation Support:**  
> Where eligible, OHAC-Kenya will provide letters of collaboration or institutional endorsements to support BactoAI in applications for research grants, innovation accelerators, and non-dilutive funding calls related to East African AMR diagnostics.

---

## 6. Section 11: Milestones and Governance

### Issue: Unrealistic 8-Week Timeline
Section 11 sets an 8-week schedule starting from MOU signing. Given that Section 6 requires third-party ethics approvals and co-owner consents from partner hospitals or universities, external bureaucratic delays could stall the timeline before data even arrives.

### Proposed Edit
Anchor milestones to the date clean data is received, rather than MOU signing.

### Suggested Draft Text
> **11.1 Milestone Schedule:**  
> The validation timeline will run according to operational milestones triggered by data delivery:  
> - Phase 1 (Data Inventory & Ownership Consents): Within 3 weeks of MOU execution.  
> - Phase 2 (Data Transfer & Quality Gate): Within 1 week of executed Data-Use Annex and ethics clearances.  
> - Phase 3 (Blind Validation Run): 3 weeks from receipt of verified sequence data.  
> - Phase 4 (Discordance Review & Joint Report): 2 weeks following completion of predictions.  
> - Phase 5 (Review Gate): Joint discussion on publication and retraining options.

---

## 7. Section 12: Publications, IP, and Fast-Track Disclosures

### Issue 1: 30-Day Delay on Public Statements
A mandatory 30-day notice period before mentioning results or partnerships creates bottlenecks for grant deadlines, investor updates, and accelerator applications.

### Proposed Edit
Shorten the review window to 10 business days and add an explicit carve-out for pitch decks and grant proposals.

### Suggested Draft Text
> **12.2 Review Period and Investor Carve-Out:**  
> Manuscripts and formal public press releases using the other party's name will be shared at least 10 business days prior to submission. In addition, either party may include high-level summary metrics and cite the formal partnership in non-public pitch decks, grant applications, and investor progress reports without requiring prior written approval, provided no raw data or confidential details are disclosed.

---

### Issue 2: Intellectual Property Ring-Fencing
Section 12 mentions background IP, but does not explicitly protect algorithmic enhancements made during the project.

### Proposed Edit
Clarify that all model updates, software improvements, and feature engineering stay exclusively with BactoAI.

### Suggested Draft Text
> **12.6 Improvements and Derived Algorithms:**  
> All algorithms, pipeline code, model weights, diagnostic architectures, and technical improvements developed by BactoAI before, during, or as an outcome of this collaboration remain the sole and exclusive intellectual property of BactoAI.

---

## 8. Section 14: Legal Enforceability and Preconditions

### Issue: Asymmetric Binding Terms
Section 14 binds BactoAI to strict data handling, visibility, and confidentiality rules, but does not make OHAC-Kenya's data delivery obligations binding.

### Proposed Edit
Clarify that BactoAI's binding duties under Section 6 take effect only upon verified transfer of the dataset.

### Suggested Draft Text
> **14.3 Operative Binding Provisions:**  
> Sections 6, 8, 12, and 13 are legally binding on the parties. BactoAI's obligations under Section 6 become active only upon the actual receipt and acceptance of the isolate dataset described in Section 4.

---

## Summary Priority Matrix

| Priority | Section | Target Clause | Objective |
| :--- | :--- | :--- | :--- |
| **High** | Sec 6 | 30-day deletion rule | Allow retained de-identified archive for benchmarking |
| **High** | Sec 6 | Ban on model training | Secure first-negotiation right for post-validation training |
| **High** | Sec 7 & 10 | Training & design support | Cut bioinformatics training and design agency tasks |
| **High** | Sec 12 | IP ring-fencing | Protect all model updates and pipeline code as BactoAI IP |
| **Medium** | Sec 5 | Blind run alternative | Remove local offline tool deployment from initial phase |
| **Medium** | Sec 5 | Unfavourable findings | Add discordance review and QC inspection before reporting |
| **Medium** | Sec 11 | 8-week timeline | Anchor phases to data delivery instead of MOU signing |
| **Medium** | Sec 12 | 30-day approval SLA | Shorten to 10 days; add pitch deck and grant carve-out |
| **Low** | Sec 9 | Mutual grant support | Ensure OHAC provides partner letters for BactoAI funding bids |
