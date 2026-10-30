"""
Humanize all deliverable markdown files using the humanizer skill rules.
Removes em dashes and AI-isms, makes writing sound more natural.
"""
import re, os, sys
sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# =====================================================================
# AI-ism replacement map (Tier 1 + Tier 2 from humanizer skill)
# =====================================================================
AI_REPLACE = {
    # Tier 1 — always replace
    r'\bdelve\b': 'look into',
    r'\bleverage\b': 'use',
    r'\bparadigm\b': 'approach',
    r'\brobust\b': 'strong',
    r'\bcomprehensive\b': 'thorough',
    r'\bcutting.edge\b': 'latest',
    r'\bpivotal\b': 'key',
    r'\bunderscores\b': 'shows',
    r'\bmeticulous\b': 'careful',
    r'\bseamless\b': 'smooth',
    r'\butilize\b': 'use',
    r'\bgame.changer\b': None,
    r'\btestament.*?to\b': 'evidence of',
    r'\bembark\b': 'start',
    r'\bbeacon\b': None,
    r'\btapestry\b': None,
    r'\brealm\b': 'field',
    r'\bwatershed\b': 'key',
    r'\bdeep.dive\b': 'look at',
    r'\bunpack\b': 'explain',
    r'\bharness\b': 'use',
    r'\bnavigate\b': 'work through',
    r'\bfoster\b': 'build',
    r'\belevate\b': 'improve',
    r'\bunleash\b': 'enable',
    r'\bstreamline\b': 'simplify',
    r'\bempower\b': 'enable',
    r'\bbolster\b': 'support',
    r'\bspearhead\b': 'lead',
    r'\bcatalyze\b': 'trigger',
    r'\breimagine\b': 'rethink',
    r'\bgalvanize\b': 'rally',
    r'\baugment\b': 'expand',
    r'\bcultivate\b': 'build',
    r'\billuminate\b': 'clarify',
    r'\bjuxtapose\b': 'compare',
    r'\btransformative\b': 'major',
    r'\bcornerstone\b': 'foundation',
    r'\bparamount\b': 'most important',
    r'\bpoised\b': 'ready',
    r'\burgeoning\b': 'growing',
    r'\bnascent\b': 'new',
    r'\bquintessential\b': 'typical',
    r'\boverarching\b': 'main',
    r'\bsignificant\b': 'important',
    r'\binnovative\b': 'new',
    r'\beffective\b': 'works well',
    r'\bdynamic\b': 'active',
    r'\bscalable\b': 'expandable',
    r'\bcompelling\b': 'strong',
    r'\bunprecedented\b': 'new',
    r'\bexceptional\b': 'outstanding',
    r'\bremarkable\b': 'notable',
    r'\bsophisticated\b': 'complex',
    r'\binstrumental\b': 'key',
    r'\binterplay\b': 'relationship',
    r'\bfeatures\b': 'has',
    r'\bboasts\b': 'has',
    r'\bcommence\b': 'start',
    r'\bascertain\b': 'confirm',
    r'\bendeavor\b': 'effort',
    r'\bkeen\b': 'interested',
    # Tier 2 — flag when 2+ per paragraph
    r'\bharness\b': 'use',
    r'\bnavigate\b': 'work through',
    r'\bfoster\b': 'build',
    r'\belevate\b': 'improve',
    r'\bunleash\b': 'enable',
    r'\bstreamline\b': 'simplify',
    r'\bempower\b': 'enable',
    r'\bbolster\b': 'support',
    r'\bspearhead\b': 'lead',
    r'\bcatalyze\b': 'trigger',
    r'\breimagine\b': 'rethink',
    r'\bgalvanize\b': 'rally',
    r'\baugment\b': 'expand',
    r'\bcultivate\b': 'build',
    r'\billuminate\b': 'clarify',
    r'\bjuxtapose\b': 'compare',
    r'\btransformative\b': 'major',
    r'\bcornerstone\b': 'foundation',
    r'\bparamount\b': 'most important',
    r'\bpoised\b': 'ready',
    r'\burgeoning\b': 'growing',
    r'\bnascent\b': 'new',
    r'\bquintessential\b': 'typical',
    r'\boverarching\b': 'main',
}

# Hollow intensifiers to remove
INTENSIFIERS = [
    r'\bgenuine\s+',
    r'\breal\s+(improvement|advantage|difference)',
    r'\btruly\s+',
    r'\bquite\s+frankly\s+',
    r"\bto\s+be\s+honest\s+",
    r"\blet's\s+be\s+clear\s+",
    r"\bit's\s+worth\s+noting\s+that\s+",
    r'\bit\s+is\s+important\s+to\s+note\s+that\s+',
    r'\bin\s+terms\s+of\s+',
    r'\bthe\s+reality\s+is\s+that\s+',
    r'\bperhaps\s+',
    r'\bcould\s+potentially\s+',
    r"\bto\s+be\s+clear\s+",
    r'\bnearly\s+',
    r'\balmost\s+entirely\s+',
    r"\bit\s+is\s+crucial\s+to\s+",
    r"\bit\s+is\s+essential\s+to\s+",
]

# Transition phrases to remove or rewrite
TRANSITIONS = {
    r'\bMoreover\b': 'Also',
    r'\bFurthermore\b': 'Also',
    r'\bAdditionally\b': 'Also',
    r'\bNotably\b': '',
    r'\bIn\s+conclusion\b': '',
    r'\bTo\s+summarize\b': '',
    r'\bWhen\s+it\s+comes\s+to\b': '',
    r'\bAt\s+the\s+end\s+of\s+the\s+day\b': '',
    r'\bThat\s+said\b': 'But',
}

# Chatbot artifacts
CHATBOT = [
    r'Great\s+question!\s*',
    r"Let's\s+dive\s+in!\s*",
    r"I\s+hope\s+this\s+helps!\s*",
    r"Let's\s+explore\s*",
    r"Let's\s+break\s+this\s+down\s*",
    r"You're\s+absolutely\s+right!\s*",
    r"That's\s+a\s+really\s+insightful\s+observation.\s*",
    r"You're\s+asking\s+about\s+.*?\.\s*",
    r"To\s+answer\s+your\s+question.*?\.\s*",
    r'Breaking\s+this\s+down\s*',
    r'Step\s+\d+\s*:',
    r"As\s+of\s+my\s+last\s+update\s*",
    r"I don't\s+have\s+access\s+to\s+real-time\s+data\s*",
    r'Interestingly\s*,',
    r'Surprisingly\s*,',
    r'Without\s+a\s+doubt\s*',
    r'the\s+real\s+question\s+is\s*',
    r'at\s+its\s+core\s*',
    r'make\s+no\s+mistake\s*',
    r"Here's\s+the\s+thing",
    r"Here's\s+what\s+you\s+need\s+to\s+know",
    r"In\s+today's\s+\w+\s+",
    r"In\s+an\s+era\s+where",
    r"It's\s+worth\s+mentioning\s+that\s+",
    r"Of\s+course,",
]

# Filler / hedging
FILLER = [
    r'\bIt\s+is\s+important\s+to\s+note\s+that\s+',
    r'\bIn\s+terms\s+of\s+',
    r'\bThe\s+reality\s+is\s+that\s+',
    r'\bAs\s+mentioned\s+earlier\s*,',
    r'\bAs\s+discussed\s+above\s*,',
]


def humanize(text):
    if not text or not isinstance(text, str):
        return text

    # Fix em dashes first
    text = re.sub(r'\s+—\s+', ', ', text)
    text = re.sub(r' ([—–]) ', ' (', text)
    text = re.sub(r' ([—–])$', ')', text)

    # AI-isms
    for pat, rep in AI_REPLACE.items():
        if rep is None:
            text = re.sub(pat, '', text, flags=re.I)
        else:
            text = re.sub(pat, rep, text, flags=re.I)

    # Intensifiers
    for pat in INTENSIFIERS:
        text = re.sub(pat, '', text, flags=re.I)

    # Transitions
    for pat, rep in TRANSITIONS.items():
        text = re.sub(pat, rep, text, flags=re.I)

    # Chatbot artifacts
    for pat in CHATBOT:
        text = re.sub(pat, '', text, flags=re.I)

    # Filler
    for pat in FILLER:
        text = re.sub(pat, '', text, flags=re.I)

    # Fix "It's not X - it's Y" pattern
    text = re.sub(r"It's not (\w+) -- it's (\w+)", r'It is \2, not \1', text)
    text = re.sub(r"It's not (\w+) - it's (\w+)", r'It is \2, not \1', text)

    # Remove empty paragraphs
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)

    return text.strip()


def process_file(filepath):
    """Process a single markdown file. Returns (changed_count, new_content)."""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        original = f.read()

    # Don't modify code blocks
    parts = []
    in_code = False
    current = []
    for line in original.split('\n'):
        if line.startswith('```'):
            if in_code:
                parts.append(('code', '\n'.join(current)))
                current = []
            else:
                current = [line]
            in_code = not in_code
        elif in_code:
            current.append(line)
        else:
            if current:
                parts.append(('text', '\n'.join(current)))
                current = []
    if current:
        parts.append(('text', '\n'.join(current)))

    new_parts = []
    changes = 0
    for ptype, text in parts:
        if ptype == 'code':
            new_parts.append(text)
        else:
            orig_text = text
            processed = humanize(text)
            if processed != orig_text:
                changes += 1
            new_parts.append(processed)

    new_content = '\n'.join(new_parts)

    # Count changes
    orig_em = original.count('\u2014')
    new_em = new_content.count('\u2014')
    orig_ai = sum(len(re.findall(p, original, re.I)) for p in AI_REPLACE)
    new_ai = sum(len(re.findall(p, new_content, re.I)) for p in AI_REPLACE)

    return changes, orig_em, new_em, orig_ai, new_ai, new_content


def main():
    print("=" * 60)
    print("  HUMANIZING BACTOAI DOCUMENTS")
    print("=" * 60)

    # Find all markdown files in deliverables and project root
    md_files = []
    skip_dirs = {'.git', '.venv', '.venv-wsl', 'node_modules', 'bactoai/.git', '__pycache__', '.claude'}
    for root, dirs, fnames in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for f in fnames:
            if f.endswith('.md') and not f.startswith('.'):
                md_files.append(os.path.join(root, f))

    total_changes = 0
    total_em_before = 0
    total_em_after = 0
    total_ai_before = 0
    total_ai_after = 0

    for fp in sorted(md_files):
        try:
            rel = os.path.relpath(fp, PROJECT_ROOT)
            changed, em_b, em_a, ai_b, ai_a, _ = process_file(fp)
            total_changes += changed
            total_em_before += em_b
            total_em_after += em_a
            total_ai_before += ai_b
            total_ai_after += ai_a

            if changed > 0 or em_b != em_a or ai_b != ai_a:
                delta_em = em_b - em_a
                delta_ai = ai_b - ai_a
                print('  [%+d em, %+d AI] %s' % (delta_em, delta_ai, rel))

                # Write back
                with open(fp, 'w', encoding='utf-8') as f:
                    _, _, _, _, _, new_content = process_file(fp)
                    f.write(new_content)
        except Exception as e:
            print('  ERROR %s: %s' % (os.path.relpath(fp, PROJECT_ROOT), e))

    print()
    print('Summary:')
    print('  Em dashes: %d -> %d (%d removed)' % (total_em_before, total_em_after, total_em_before - total_em_after))
    print('  AI-isms:   %d -> %d (%d removed)' % (total_ai_before, total_ai_after, total_ai_before - total_ai_after))
    print('  Files changed: %d' % total_changes)


if __name__ == '__main__':
    main()
