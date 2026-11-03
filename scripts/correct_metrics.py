"""
Update the revised letter and technical summary with corrected metrics.
Fixes:
1. Ciprofloxacin AUC: 0.879 -> 0.9559
2. BV-BRC reclassified from "external validation" to "in-corpus benchmark"
3. Meropenem confirmed at 0.9871
4. Cefotaxime v3 notes added
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

def update_file(path, replacements):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    original = content
    for old, new in replacements:
        content = content.replace(old, new)
    changes = sum(1 for a, b in replacements if a in original and b not in original or a in original and a != b)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return content != original, len(content)

# Letter corrections
letter_path = 'deliverables/Revised_Letter_to_NPHL.md'
letter_replacements = [
    # Fix ciprofloxacin AUC
    ('ROC-AUC 0.879 (95% CI [0.820, 0.938])', 'ROC-AUC 0.9559 (95% CI [0.920, 0.992])'),
    # Fix BV-BRC description
    ('On an independent BV-BRC dataset of 500 E. coli genomes, cefotaxime prediction achieved ROC-AUC 0.933, sensitivity 82.8%, specificity 95.2%.',
     'On an in-corpus BV-BRC holdout benchmark of 500 E. coli genomes (same source as training data, not an independent external dataset), cefotaxime prediction at optimized threshold t=0.20 achieved ROC-AUC 0.933, sensitivity 82.8%, specificity 95.2%. Prospective external validation will be performed on fresh NPHL clinical isolates.'),
    # Fix any remaining 0.952 references for meropenem
    ('ROC-AUC 0.952', 'ROC-AUC 0.987'),
]
letter_changed, letter_size = update_file(letter_path, letter_replacements)
print(f'Letter: {"UPDATED" if letter_changed else "no changes"} ({letter_size} bytes)')

# Summary corrections
summary_path = 'deliverables/NPHL_Technical_Summary.md'
summary_replacements = [
    # Fix ciprofloxacin AUC in table
    ('| Ciprofloxacin | 140 | 94.1% | [87.8%, 97.3%] | 94.4% | [88.0%, 97.5%] | 94.1% | 94.4% | 5.9% (4/68) | 5.6% (4/72) | 0.879 | [0.820, 0.938] |',
     '| Ciprofloxacin | 140 | 94.1% | [87.8%, 97.3%] | 94.4% | [88.0%, 97.5%] | 94.1% | 94.4% | 5.9% (4/68) | 5.6% (4/72) | 0.9559 | [0.920, 0.992] |'),
    # Fix BV-BRC description
    ('These results come from retrospective analysis of public data, including external validation on an independent BV-BRC cohort of 500 E. coli genomes (AUC 0.933).',
     'These results come from retrospective analysis of public data. An in-corpus BV-BRC holdout benchmark (500 E. coli genomes, same source as training data) showed ROC-AUC 0.933 at threshold t=0.20. This is NOT an independent external validation — prospective validation will occur at NPHL on fresh clinical isolates.'),
    # Add note about cefotaxime v3
    ('| Cefotaxime (v4 external, 500 genomes, t=0.20) | 500 | 82.8% | [77.6%, 87.0%] | 95.2% | [91.8%, 97.2%] | 94.5% | 84.7% | 17.2% (43/250) | 4.8% (12/250) | 0.9333 | [0.917, 0.949] |',
     '| Cefotaxime v3 (NCBI holdout) | 145 | N/A* | — | N/A* | — | N/A | N/A | N/A | N/A | 0.8721 | — |\n| Cefotaxime BV-BRC benchmark (in-corpus) | 500 | 82.8% | [77.6%, 87.0%] | 95.2% | [91.8%, 97.2%] | 94.5% | 84.7% | 17.2% (43/250) | 4.8% (12/250) | 0.933 | [0.917, 0.949] |'),
]
summary_changed, summary_size = update_file(summary_path, summary_replacements)
print(f'Summary: {"UPDATED" if summary_changed else "no changes"} ({summary_size} bytes)')

# Verify
print()
print('Verification:')
with open(letter_path) as f:
    l = f.read()
print(f'  Letter has 0.9559: {"0.9559" in l}')
print(f'  Letter has "in-corpus": {"in-corpus" in l}')
print(f'  Letter has no "0.879": {"0.879" not in l}')
with open(summary_path) as f:
    s = f.read()
print(f'  Summary has 0.9559: {"0.9559" in s}')
print(f'  Summary has "in-corpus": {"in-corpus" in s}')
print(f'  Summary has no "0.879": {"0.879" not in s}')
