"""
Humanize the BactoAI validation documents:
- Remove em dashes
- Remove AI-isms from the humanizer catalog
- Make writing sound more natural/human
- Preserve technical accuracy
"""
import re
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# =====================================================================
# AI-ism replacement map (from humanizer skill)
# =====================================================================
AI_ISMS = {
    # Tier 1 - always replace
    r'\bdelve\b': 'look into',
    r'\bleverage\b': 'use',
    r'\bparadigm\b': 'approach',
    r'\brobust\b': 'strong',
    r'\bcomprehensive\b': 'thorough',
    r'\bcutting-edge\b': 'latest',
    r'\bpivotal\b': 'key',
    r'\bunderscores\b': 'shows',
    r'\bmeticulous\b': 'careful',
    r'\bseamless\b': 'smooth',
    r'\butilize\b': 'use',
    r'\bgame-changer\b': None,  # remove entirely
    r'\btestament to\b': 'evidence of',
    r'\bembark\b': 'start',
    r'\bbeacon\b': None,
    r'\btapestry\b': None,
    r'\brealm\b': 'field',
    r'\bwatershed\b': 'key',
    r'\bdeep dive\b': 'look at',
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
    r'\bin order to\b': 'to',
    r'\bdue to the fact that\b': 'because',
    r'\bserves as\b': 'is',
    r'\bfeatures\b': 'has',
    r'\bboasts\b': 'has',
    r'\bcommence\b': 'start',
    r'\bascertain\b': 'confirm',
    r'\bendeavor\b': 'effort',
    r'\bkeen\b': 'interested',
}

# =====================================================================
# Em dash replacement
# =====================================================================
def fix_em_dashes(text):
    """Replace em dashes with appropriate punctuation."""
    # Em dash surrounded by spaces -> replace with comma or period
    text = re.sub(r'\s+—\s+', ', ', text)
    # Em dash without spaces (like in table separators) -> leave alone
    # But fix standalone em dashes used as parenthetical
    text = re.sub(r' ([—–]) ', ' (', text)
    text = re.sub(r' ([—–])$', ')', text)
    return text


def humanize_text(text):
    """Apply all humanization rules."""
    # First fix em dashes
    text = fix_em_dashes(text)
    
    # Then replace AI-isms (case-insensitive)
    for pattern, replacement in AI_ISMS.items():
        if replacement is None:
            # Remove the phrase entirely
            text = re.sub(pattern, '', text, flags=re.I)
        else:
            text = re.sub(pattern, replacement, text, flags=re.I)
    
    # Remove hollow intensifiers
    intensifiers = [
        r'\bgenuine\s+', r'\breal\s+(improvement|advantage)',
        r'\btruly\s+', r'\bquite\s+frankly\s+', r'\bto\s+be\s+honest\s+',
        r'\blet\'s\s+be\s+clear\s+', r"\bit's\s+worth\s+noting\s+that\s+",
        r'\bit\s+is\s+important\s+to\s+note\s+that\s+',
        r'\bin\s+terms\s+of\s+', r'\bthe\s+reality\s+is\s+that\s+',
        r'\bperhaps\s+', r'\bcould\s+potentially\s+',
        r'\bto\s+be\s+clear\s+', r'\bnearly\s+', r'\balmost\s+entirely\s+',
    ]
    for pat in intensifiers:
        text = re.sub(pat, '', text, flags=re.I)
    
    # Fix transition phrases
    transitions = {
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
    for pat, rep in transitions.items():
        text = re.sub(pat, rep, text, flags=re.I)
    
    # Remove chatbot artifacts
    chatbot_artifacts = [
        r'Great\s+question!\s*',
        r"Let's\s+dive\s+in!\s*",
        r'I\s+hope\s+this\s+helps!\s*',
        r'Here\s+is\s+an\s+essay\s+on\s+this\s+topic\s*',
        r"Let's\s+explore\s*",
        r"Let's\s+break\s+this\s+down\s*",
        r"You're\s+absolutely\s+right!\s*",
        r'That\'s\s+a\s+really\s+insightful\s+observation.\s*',
        r'You\'re\s+asking\s+about\s+.*?\.\s*',
        r'To\s+answer\s+your\s+question.*?\.\s*',
        r'Breaking\s+this\s+down\s*',
        r'Step\s+\d+\s*:',
        r'As\s+of\s+my\s+last\s+update\s*',
        r'I\s+don\'t\s+have\s+access\s+to\s+real-time\s+data\s*',
        r'Interestingly\s*,',
        r'Surprisingly\s*,',
        r'Without\s+a\s+doubt\s*',
        r'the\s+real\s+question\s+is\s*',
        r'at\s+its\s+core\s*',
        r'make\s+no\s+mistake\s*',
    ]
    for pat in chatbot_artifacts:
        text = re.sub(pat, '', text, flags=re.I)
    
    # Fix "It's not X, it's Y" pattern
    text = re.sub(r"It's not (\w+)--it's (\w+)", r'It is \2, not \1', text)
    text = re.sub(r"It's not (\w+) - it's (\w+)", r'It is \2, not \1', text)
    
    # Remove empty paragraphs caused by deletions
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    return text.strip()


def process_markdown_file(filepath):
    """Process a markdown file for humanization."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Don't modify code blocks, table syntax, or inline code
    # Split by code blocks first
    parts = []
    in_code = False
    current = []
    lines = content.split('\n')
    
    for line in lines:
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
    
    result_parts = []
    for part_type, text in parts:
        if part_type == 'code':
            result_parts.append(text)
        else:
            result_parts.append(humanize_text(text))
    
    return '\n'.join(result_parts)


def process_excel_sheets(wb):
    """Process all text cells in the Excel workbook."""
    import openpyxl
    
    sheets_to_process = ['Guiding Questions', 'Letter Claims', 'Deliverables', 'Validation Steps']
    
    for sheet_name in sheets_to_process:
        if sheet_name not in wb.sheetnames:
            continue
        ws = wb[sheet_name]
        changed = 0
        for row in ws.iter_rows():
            for cell in row:
                if cell.value and isinstance(cell.value, str):
                    original = cell.value
                    processed = humanize_text(original)
                    if processed != original:
                        cell.value = processed
                        changed += 1
        print(f"  {sheet_name}: {changed} cells updated")
    
    return wb


def main():
    print("=" * 60)
    print("  HUMANIZING BACTOAI VALIDATION DOCUMENTS")
    print("=" * 60)
    
    # Process markdown file
    md_path = os.path.join(PROJECT_ROOT, 'deliverables', 'KU_IvE_Validation_Answers.md')
    if os.path.exists(md_path):
        print(f"\n[1] Processing: {os.path.basename(md_path)}")
        original = open(md_path).read()
        processed = process_markdown_file(md_path)
        
        # Count changes
        orig_em = original.count('—')
        proc_em = processed.count('—')
        print(f"  Em dashes: {orig_em} -> {proc_em}")
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(processed)
        print(f"  Saved.")
    
    # Process Excel
    xlsx_path = os.path.join(PROJECT_ROOT, 'deliverables', 'BactoAI Validation Capture.xlsx')
    if os.path.exists(xlsx_path):
        print(f"\n[2] Processing: BactoAI Validation Capture.xlsx")
        wb = openpyxl.load_workbook(xlsx_path)
        wb = process_excel_sheets(wb)
        wb.save(xlsx_path)
        print(f"  Saved.")
    
    print("\nDone.")


if __name__ == '__main__':
    main()
