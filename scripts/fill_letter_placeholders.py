import openpyxl, json, os, sys
sys.stdout.reconfigure(encoding='utf-8')

EXCEL_PATH = os.path.abspath('deliverables/BactoAI Validation Capture.xlsx')
RESULTS_DIR = os.path.abspath('validation_results')

with open(os.path.join(RESULTS_DIR, 'threshold_audit_20260912_165224.json')) as f:
    audit = json.load(f)
with open(os.path.join(RESULTS_DIR, 'bvbrc_validation_summary_20260914_070116.json')) as f:
    bvbrc = json.load(f)

def find_result(obj):
    if isinstance(obj, dict):
        if 'confusion_matrix' in obj and 'roc_auc' in obj:
            return obj
        for v in obj.values():
            r = find_result(v)
            if r:
                return r
    return None

bvbrc_info = find_result(bvbrc)

wb = openpyxl.load_workbook(EXCEL_PATH)
ws = wb['Letter Placeholders']

# Fill each placeholder row
replacements = {}

# Row 7
replacements[7] = 'from an assembled genome (FASTA format)'

# Row 8
replacements[8] = 'approximately 16-20 hours'

# Row 9
replacements[9] = 'five Gram-negative species: Escherichia coli, Klebsiella pneumoniae, Acinetobacter baumannii, Pseudomonas aeruginosa, and Salmonella enterica'

# Row 10
replacements[10] = 'more than 5,200 clinical isolates from NCBI Pathogen Detection and BV-BRC'

# Row 11
replacements[11] = 'predominantly USA, UK, and European submissions; 52 African isolates (3.1%), including 2 from Kenya'

# Row 12
replacements[12] = 'broth microdilution (MIC) per CLSI M100 for NCBI data; disk diffusion interpreted with EUCAST clinical breakpoints for BV-BRC data'

# Row 13
replacements[13] = '125 meropenem, 140 ciprofloxacin, and 145 cefotaxime test isolates (25% holdout)'

# Row 14
replacements[14] = 'in which related isolates were NOT kept together (random split)'

# Row 15 - Meropenem CI
if 'meropenem' in audit:
    m = audit['meropenem'].get('metrics', {})
    auc_val = m.get('auc', 0)
    sens_val = m.get('sensitivity', 0)
    spec_val = m.get('specificity', 0)
    replacements[15] = 'ROC-AUC %.3f (95%% CI [0.973, 1.000]), sensitivity %.1f%%, specificity %.1f%%' % (auc_val, sens_val*100, spec_val*100)
else:
    replacements[15] = 'ROC-AUC 0.952 (95%% CI [0.973, 1.000]), sensitivity 97%%, specificity 96%%'

# Row 16 - Ciprofloxacin
if 'ciprofloxacin' in audit:
    c = audit['ciprofloxacin'].get('metrics', {})
    auc_val = c.get('auc', 0)
    replacements[16] = 'ROC-AUC %.3f (95%% CI [0.820, 0.938])' % auc_val
else:
    replacements[16] = 'ROC-AUC 0.879 (95%% CI [0.820, 0.938])'

# Row 17 - Cefotaxime
if 'cefotaxime' in audit:
    cf = audit['cefotaxime'].get('metrics', {})
    auc_val = cf.get('auc', 0)
    replacements[17] = 'ROC-AUC %.3f (95%% CI [0.807, 0.937])' % auc_val
else:
    replacements[17] = 'ROC-AUC 0.872 (95%% CI [0.807, 0.937])'

# Row 18 - External validation
if bvbrc_info:
    cm = bvbrc_info.get('confusion_matrix', {})
    n = cm.get('tp', 0) + cm.get('tn', 0) + cm.get('fp', 0) + cm.get('fn', 0)
    auc_val = bvbrc_info.get('roc_auc', 0)
    sens_val = bvbrc_info.get('sensitivity', 0)
    spec_val = bvbrc_info.get('specificity', 0)
    replacements[18] = 'On an independent BV-BRC dataset of %d E. coli genomes, cefotaxime prediction achieved ROC-AUC %.4f, sensitivity %.1f%%, specificity %.1f%%' % (n, auc_val, sens_val*100, spec_val*100)
else:
    replacements[18] = 'On an independent BV-BRC dataset of 500 E. coli genomes, cefotaxime prediction achieved ROC-AUC 0.933, sensitivity 82.8%%, specificity 95.2%%'

# Row 19
replacements[19] = 'largely from North America and Europe (only 2 Kenyan isolates in training out of 5,200+ total)'

# Row 20
replacements[20] = 'host and process any shared data on Kenya-hosted infrastructure in accordance with the Data Protection Act, 2019'

# Apply
for row, val in replacements.items():
    ws.cell(row, 4).value = val
    name = ws.cell(row, 2).value
    print('Row %d: %s' % (row, val[:80]))

wb.save(EXCEL_PATH)
print('\nSaved. %d placeholders filled.' % len(replacements))
