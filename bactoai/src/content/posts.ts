export type Post = {
  slug: string;
  title: string;
  excerpt: string;
  category: "Research" | "Clinical" | "Public Health" | "Product";
  date: string;
  readTime: string;
  gradient: string;
};

export const posts: Post[] = [
  {
    slug: "why-genomic-amr-prediction",
    title: "Why genomic AMR prediction is the diagnostic upgrade hospitals actually need",
    excerpt:
      "Culture-based testing was designed for a world with fewer resistant strains. Here's what changes when the genome, not the culture plate, becomes the primary signal.",
    category: "Clinical",
    date: "May 8, 2026",
    readTime: "6 min read",
    gradient: "from-primary to-primary",
  },
  {
    slug: "validating-meropenem-model",
    title: "How we validated our Meropenem model to 0.952 ROC-AUC",
    excerpt:
      "A behind-the-scenes look at the training set, holdout strategy, and confidence-calibration work that produced BactoAI's flagship prediction model.",
    category: "Research",
    date: "April 22, 2026",
    readTime: "9 min read",
    gradient: "from-primary to-primary",
  },
  {
    slug: "amr-in-lmic-hospitals",
    title: "AMR in LMIC hospitals: what the surveillance data isn't telling you",
    excerpt:
      "A short field note from our pilot deployments across East African hospitals — and why local genomic surveillance changes the risk picture entirely.",
    category: "Public Health",
    date: "April 3, 2026",
    readTime: "5 min read",
    gradient: "from-primary to-primary",
  },
  {
    slug: "bactoai-api-launch",
    title: "Announcing the BactoAI API: predictions in your LIMS",
    excerpt:
      "Our REST API lets hospital LIMS systems submit isolates and receive resistance predictions directly. Here's the design and how to get access.",
    category: "Product",
    date: "March 19, 2026",
    readTime: "4 min read",
    gradient: "from-primary to-primary",
  },
  {
    slug: "confidence-scores-clinical",
    title: "Confidence scores that a clinician can actually reason about",
    excerpt:
      "Model uncertainty is easy to compute and hard to communicate. We share the calibration and visualization choices behind BactoAI's confidence bars.",
    category: "Clinical",
    date: "March 2, 2026",
    readTime: "7 min read",
    gradient: "from-primary to-primary",
  },
  {
    slug: "who-priority-pathogens",
    title: "Mapping the WHO priority pathogens list to our roadmap",
    excerpt:
      "How the WHO priority pathogens list shapes the antibiotics we support next — and where LMIC-specific resistance patterns diverge from global rankings.",
    category: "Public Health",
    date: "February 14, 2026",
    readTime: "8 min read",
    gradient: "from-primary to-primary",
  },
];
