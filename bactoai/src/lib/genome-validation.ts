// Shared, browser-safe validation + parsing helpers for genome uploads.
export const MAX_GENOME_BYTES = 25 * 1024 * 1024;
export const GENOME_EXTENSIONS = [
  ".fasta",
  ".fa",
  ".fna",
  ".fastq",
  ".fq",
  ".fasta.gz",
  ".fa.gz",
  ".fna.gz",
  ".fastq.gz",
  ".fq.gz",
];

export const ORGANISMS = [
  "Klebsiella pneumoniae",
  "Escherichia coli",
  "Staphylococcus aureus",
  "Pseudomonas aeruginosa",
  "Acinetobacter baumannii",
  "Enterococcus faecium",
  "Salmonella enterica",
  "Mycobacterium tuberculosis",
  "Other",
] as const;

export const SPECIMENS = [
  "Blood culture",
  "Urine culture",
  "Wound swab",
  "Sputum / respiratory",
  "Cerebrospinal fluid",
  "Stool",
  "Environmental",
  "Other",
] as const;

export type SequenceStats = {
  format: "FASTA" | "FASTQ";
  records: number;
  totalBases: number;
  gcPercent: number;
  nPercent: number;
  longestRecord: number;
  n50: number;
  headers: string[];
  excerpt: string;
};

export function validateGenomeFile(file: File | null): string | null {
  if (!file) return "Choose a genome file to analyze.";
  const n = file.name.toLowerCase();
  if (!GENOME_EXTENSIONS.some((e) => n.endsWith(e)))
    return "Unsupported file type. Use .fasta, .fa, .fna, .fastq or .fq (optionally .gz).";
  if (file.size === 0) return "This file is empty.";
  if (file.size > MAX_GENOME_BYTES)
    return `File is ${(file.size / 1048576).toFixed(1)} MB — the limit is 25 MB.`;
  return null;
}

async function readText(file: File): Promise<string> {
  if (file.name.toLowerCase().endsWith(".gz")) {
    const stream = file.stream().pipeThrough(new DecompressionStream("gzip"));
    return await new Response(stream).text();
  }
  return await file.text();
}

/** Parses the file in the browser. Throws an Error with a user-friendly message. */
export async function parseGenome(file: File): Promise<SequenceStats> {
  let text: string;
  try {
    text = await readText(file);
  } catch {
    throw new Error("We couldn't read this file. If it's gzipped, check it isn't corrupted.");
  }
  const trimmed = text.trimStart();
  const first = trimmed.charAt(0);
  if (first !== ">" && first !== "@")
    throw new Error(
      "This doesn't look like FASTA or FASTQ — the file should start with '>' or '@'.",
    );
  const format = first === ">" ? "FASTA" : "FASTQ";
  const lines = trimmed.split(/\r?\n/);
  const lengths: number[] = [];
  const headers: string[] = [];
  let gc = 0,
    nCount = 0,
    total = 0,
    excerpt = "",
    cur = 0;
  const addSeq = (seq: string) => {
    const s = seq.trim().toUpperCase();
    for (let i = 0; i < s.length; i++) {
      const c = s.charCodeAt(i);
      if (c === 71 || c === 67) gc++;
      else if (c === 78) nCount++;
    }
    total += s.length;
    cur += s.length;
    if (excerpt.length < 4000) excerpt += s.slice(0, 4000 - excerpt.length);
  };
  if (format === "FASTA") {
    for (const line of lines) {
      if (line.startsWith(">")) {
        if (headers.length) lengths.push(cur);
        cur = 0;
        if (headers.length < 8) headers.push(line.slice(1, 120));
      } else if (line) addSeq(line);
    }
    lengths.push(cur);
  } else {
    for (let i = 0; i + 1 < lines.length; i += 4) {
      if (!lines[i].startsWith("@"))
        throw new Error("Malformed FASTQ: record headers must start with '@'.");
      if (headers.length < 8) headers.push(lines[i].slice(1, 120));
      cur = 0;
      addSeq(lines[i + 1]);
      lengths.push(cur);
    }
  }
  if (total < 100)
    throw new Error("The file contains too little sequence to analyze (under 100 bases).");
  if (/[^ACGTNRYKMSWBDHV]/i.test(excerpt))
    throw new Error("Sequence contains characters that aren't valid nucleotide codes.");
  const sorted = [...lengths].sort((a, b) => b - a);
  let acc = 0,
    n50 = 0;
  for (const l of sorted) {
    acc += l;
    if (acc >= total / 2) {
      n50 = l;
      break;
    }
  }
  return {
    format,
    records: lengths.length,
    totalBases: total,
    gcPercent: Math.round((gc / total) * 1000) / 10,
    nPercent: Math.round((nCount / total) * 1000) / 10,
    longestRecord: sorted[0] ?? 0,
    n50,
    headers,
    excerpt,
  };
}
