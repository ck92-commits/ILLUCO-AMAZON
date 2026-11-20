"""Turn analysis/negative_keywords.csv + the audit's pause list into a copy-paste sheet for the
Amazon Advertising console (one block per campaign / ad group / match type)."""
import csv, collections
rows = list(csv.DictReader(open('analysis/negative_keywords.csv', encoding='utf-8')))
SHORT = {'VIC-M-SP-Dental Mirror Branded and Product KW': 'BRAND-KW',
         'VIC-BOF | SP | Dental Mirror HEAD 1x 2x 3x | SP Exact Target + Prod Exp + Brand Exp': 'HEADS-KW',
         'VIC-M- SP | Dental Mirror Category | Dental Mirror | All Single Multipack': 'CATEGORY',
         'VIC-SP-AUTO-DTMR-1PK-ALL': 'AUTO-1PK', 'VIC-SP-AUTO-MRHD-5PK-ALL': 'AUTO-HEADS',
         'SP-Dermatoscope-KWs-All': 'DERM'}
ORDER = ['BRAND-KW', 'HEADS-KW', 'CATEGORY', 'AUTO-1PK', 'AUTO-HEADS', 'DERM']
LABEL = {'negative exact': 'Negative exact', 'negative phrase': 'Negative phrase',
         'negative product target (ASIN)': 'Negative products (ASIN)'}
PAUSES = [
    ('BRAND-KW', 'dental', 'Phrase', '$191 spend, 2 orders ($235); 92% of its spend went to handpieces, loupes, drills, materials'),
    ('BRAND-KW', 'dental tools home use', 'Broad', '$168 spend, 2 orders ($350); consumer intent'),
    ('BRAND-KW', 'dental hygienist must haves', 'Exact', '$16 spend, 0 orders; gift-list search'),
    ('HEADS-KW', 'dental mirror', 'Broad', '$8.55 spend, 0 orders (the converting "dental mirror" PHRASE keyword stays on)'),
    ('DERM', 'dermatoscope otoscopes & ophthalmoscopes', 'Broad', 'Off-target keyword, 0 orders'),
    ('DERM', 'dermatoscope iphone', 'any', 'Phone-attachment search; ILLUCO units are handheld'),
    ('DERM', 'smartphone dermatoscope', 'any', 'Phone-attachment search'),
    ('DERM', 'dermatoscope for smart phone', 'any', 'Phone-attachment search'),
    ('DERM', 'dermatoscope attachment for iphone', 'any', 'Phone-attachment search'),
]
groups = collections.OrderedDict()
camp_full, ag_full = {}, {}
for r in rows:
    c = SHORT[r['campaign']]
    camp_full[c] = r['campaign']; ag_full[c] = r['ad_group']
    groups.setdefault((c, r['match_type']), []).append(r)

out = []
w = out.append
w('# Apply today: negative keywords and pauses (Sponsored Products)')
w('')
w('Advertising console > Campaign manager. No budget changes. About 15 minutes.')
w('Source: `analysis/ppc_audit.md` (search terms Sep 17 - Nov 20, 2026). Tick each box as you go.')
w('')
w('## 1. Pause these keywords')
w('')
w('Campaign > ad group > **Targeting** tab > find the keyword > switch it off.')
w('')
w('| Done | Campaign | Keyword | Match | Why |')
w('|---|---|---|---|---|')
for c, kw, mt, why in PAUSES:
    w(f'| [ ] | {c} | {kw} | {mt} | {why} |')
w('')
w('Not a pause, so not applied here: cutting the DERM "dermatoscope" exact bid from $2.31 to about $1.27 (your call).')
w('')
w('## 2. Add negative keywords and negative products')
w('')
w('Campaign > ad group > **Negative targeting** tab > **Add negative keywords** > pick the match type > paste the block (one per line) > Add > Save. For ASINs use **Add negative products**.')
w('If an ad group does not offer negative keywords (the CATEGORY ad group is a category target), add only its negative products and skip its keyword blocks.')
w('')
for c in ORDER:
    w(f'### {c}')
    w('')
    w(f'Campaign: `{camp_full[c]}`  ')
    w(f'Ad group: `{ag_full[c]}`')
    w('')
    for mt in ['negative exact', 'negative phrase', 'negative product target (ASIN)']:
        rs = groups.get((c, mt))
        if not rs:
            continue
        spent = sum(float(x['spend_to_date'] or 0) for x in rs)
        w(f'- [ ] **{LABEL[mt]}** ({len(rs)}; ${spent:,.2f} spent on these with 0 orders)')
        w('')
        w('```')
        for x in rs:
            w(x['keyword'])
        w('```')
        w('')
total = len(rows); spent = sum(float(x['spend_to_date'] or 0) for x in rows)
w('## 3. Check after 7 days')
w('')
w('- Search term report: none of the negated terms should appear again in these ad groups.')
w('- "dental mirror" orders should keep coming through CATEGORY (where it converts at 23% ACoS).')
w('- If brand sales ("illuco ...") drop, a negative is too broad: tell me which ad group.')
w('')
w(f'Totals: {total} negatives ({sum(1 for x in rows if x["match_type"]=="negative exact")} exact, '
  f'{sum(1 for x in rows if x["match_type"]=="negative phrase")} phrase, '
  f'{sum(1 for x in rows if "ASIN" in x["match_type"])} ASIN) and {len(PAUSES)} pauses. '
  f'Negated terms spent ${spent:,.2f} with 0 orders; with the 3 BRAND-KW pauses the audit estimates $639 (28%) less spend for $585 of sales at risk.')
open('analysis/APPLY_negatives_and_pauses.md', 'w').write('\n'.join(out) + '\n')
print('written', total, 'negatives', len(PAUSES), 'pauses')
