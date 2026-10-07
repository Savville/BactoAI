import samwelPhoto from "@/assets/samwel-elegwa.png.asset.json";
import sheilaPhoto from "@/assets/sheila-okwisa.png.asset.json";
import williamPhoto from "@/assets/william-otieno.jpg.asset.json";
import sylviaPhoto from "@/assets/sylvia-jane-nyambura.jpg.asset.json";
import thomasPhoto from "@/assets/thomas-bonuke.jpg.asset.json";

type Member = {
  name: string;
  role: string;
  bio: string;
  extended: string;
  focus: string[];
  photo?: string;
};

const team: Member[] = [
  {
    name: "Samwel Elegwa",
    role: "Founder & CEO",
    photo: samwelPhoto.url,
    bio: "Biotechnology researcher at Kenyatta University with hands-on analytical experience from a Kenya Bureau of Standards attachment in gravimetry, titrimetry, spectroscopy, and related laboratory methods. An alumnus of the NextGen Antimicrobial Stewards Initiative and 2nd-place finisher at Kenyatta University's Research in Science bootcamp, where BactoAI was first pitched.",
    extended:
      "Leads BactoAI's vision, scientific direction, and strategic growth — representing the company with hospitals, universities, funders, and antimicrobial stewardship networks across East Africa.",
    focus: ["Vision & strategy", "Scientific direction", "Strategic growth"],
  },
  {
    name: "Sheila Okwisa",
    role: "Chief Technology Officer",
    photo: sheilaPhoto.url,
    bio: "Software engineer responsible for BactoAI's technology infrastructure and product development.",
    extended:
      "Leads the engineering architecture, cloud systems, and development workflows that transform BactoAI's scientific models and data pipelines into reliable, scalable software products.",
    focus: ["Technology & engineering", "Cloud infrastructure", "Product development"],
  },
  {
    name: "William Otieno",
    role: "Machine Learning Engineer",
    photo: williamPhoto.url,
    bio: "Electrical engineer specialising in applied machine learning and predictive analytics.",
    extended:
      "Leads the development, training, evaluation, and optimisation of BactoAI's machine-learning systems, working closely with the wider team to translate scientific and clinical requirements into reliable predictive tools.",
    focus: ["Machine learning", "Model evaluation", "Predictive analytics"],
  },
  {
    name: "Sylvia Jane Nyambura",
    role: "Chief Operating Officer",
    photo: sylviaPhoto.url,
    bio: "Leads BactoAI's day-to-day operations, pilot coordination, project execution, and organisational systems.",
    extended:
      "Connects the scientific, engineering, and partnership functions to ensure that projects move efficiently from development to real-world implementation.",
    focus: ["Operations", "Pilot coordination", "Project execution"],
  },
  {
    name: "Thomas Raphael Bonuke",
    role: "Partnerships & Grants Lead",
    photo: thomasPhoto.url,
    bio: "Kenyatta University biotechnologist with laboratory training in molecular biology, virology and bacteriology at the National Veterinary Reference Laboratory. Led grants and partnerships for the Future Researchers Poster Summit.",
    extended:
      "Leads BactoAI's grant applications and builds partnerships with funders, hospitals and research institutions.",
    focus: ["Grant writing", "Funder engagement", "Institutional partnerships"],
  },
];

const advisors = [
  {
    name: "Dr George Orinda",
    role: "Scientific Advisor",
    tags: ["Microbiology", "AMR", "Clinical validation"],
  },
  {
    name: "Dr. Thomas Musyoka, PhD",
    role: "Bioinformatics Advisor",
    tags: ["Computational biology", "ML", "Genomics"],
  },
  {
    name: "Kenyatta Innovation Centre",
    role: "Innovation Partner",
    tags: ["Commercialization", "Incubation", "Mentorship"],
  },
];

function initials(n: string) {
  return n
    .split(" ")
    .map((s) => s[0])
    .slice(0, 2)
    .join("");
}

export function Team() {
  return (
    <section id="team" className="py-24 md:py-32 bg-card/40">
      <div className="mx-auto max-w-7xl px-6">
        <div className="max-w-3xl">
          <div className="text-sm font-semibold text-primary uppercase tracking-widest">Team</div>
          <h2 className="mt-4 text-4xl md:text-5xl font-bold tracking-tight text-foreground">
            Scientists, engineers, and clinicians — building precision AMR diagnostics.
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Different expertise. One system. One company. BactoAI is a multidisciplinary team
            building one AMR intelligence platform — the product, models, and technology belong to
            the company, and each of us leads a defined part of it.
          </p>
        </div>

        <div
          className="mt-14 rounded-3xl border border-dashed border-border/70 bg-card/30 h-64 md:h-80 flex items-center justify-center"
          aria-hidden="true"
        >
          <span className="text-xs uppercase tracking-widest text-muted-foreground">
            Team photo coming soon
          </span>
        </div>

        <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {team.map((m) => (
            <div
              key={m.name}
              className="rounded-2xl border border-border bg-background p-6 shadow-soft hover:shadow-elegant transition"
            >
              <div className="flex items-center gap-4">
                {m.photo ? (
                  <img
                    src={m.photo}
                    alt={`${m.name}, ${m.role} at BactoAI`}
                    loading="lazy"
                    className="w-20 h-20 rounded-full object-cover object-top border border-border"
                  />
                ) : (
                  <div className="w-20 h-20 rounded-full bg-gradient-hero text-white flex items-center justify-center font-bold text-xl">
                    {initials(m.name)}
                  </div>
                )}
                <div>
                  <div className="font-semibold text-foreground">{m.name}</div>
                  <div className="text-xs text-primary font-medium">{m.role}</div>
                </div>
              </div>
              <p className="mt-4 text-sm text-muted-foreground leading-relaxed">{m.bio}</p>
              <p className="mt-3 text-sm text-muted-foreground leading-relaxed">{m.extended}</p>
              <div className="mt-4 flex flex-wrap gap-2">
                {m.focus.map((f) => (
                  <span
                    key={f}
                    className="text-[11px] rounded-full bg-muted px-2.5 py-1 text-muted-foreground"
                  >
                    {f}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-20">
          <h3 className="text-2xl font-bold text-foreground">Advisors & Partners</h3>
          <div className="mt-8 grid gap-6 md:grid-cols-3">
            {advisors.map((a) => (
              <div key={a.name} className="rounded-2xl border border-border bg-background p-6">
                <div className="font-semibold text-foreground">{a.name}</div>
                <div className="text-xs text-primary font-medium">{a.role}</div>
                <div className="mt-4 flex flex-wrap gap-2">
                  {a.tags.map((t) => (
                    <span
                      key={t}
                      className="text-[11px] rounded-full bg-muted px-2.5 py-1 text-muted-foreground"
                    >
                      {t}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
