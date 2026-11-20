#!/usr/bin/env python3
"""ILLUCO Sponsored Products + Brand Analytics Search Query Performance (SQP) audit.

Reads the exports in data/account/ (read-only, never written) and writes:
  analysis/ppc_audit.md          audit report (tables first)
  analysis/negative_keywords.csv negatives to upload
  analysis/harvest_keywords.csv  search terms to add as Exact
  analysis/sqp_top_queries.csv   SQP top queries, ILLUCO purchase wins and relevant gaps

Run from the repo root:  python3 -I scripts/ppc_sqp_audit.py
Analysis only: nothing here raises a budget.
"""
from __future__ import annotations

import io
import math
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'account'
RAW = ROOT / 'data' / 'raw'
LISTINGS = ROOT / 'listings'
OUT = ROOT / 'analysis'

F_CAMPAIGN = DATA / 'CHECK-_ILLUCO_3.csv'
F_TERMS = DATA / 'CHECK-_ILLUCO_1.xlsx'
F_TARGETS = DATA / 'CHECK-_ILLUCO_2.xlsx'
F_SQP = {'2026-Q3': DATA / 'SQP_Brand_Quarter_2026_09_30.csv',
         '2026-09': DATA / 'SQP_Brand_Month_2026_09_30.csv',
         '2026-10': DATA / 'SQP_Brand_Month_2026_10_31.csv'}
F_BUSINESS = DATA / 'BusinessReport-11-20-26.csv'
F_RETURNS = DATA / '293310020777.csv'
F_COMPETITORS = RAW / 'competitor_search.json'
F_LISTING_UPDATES = LISTINGS / 'Existing_Listings_Update_Sheet.xlsx'

# Waste / harvest rules from the brief
WASTE_MIN_CLICKS = 8
WASTE_MIN_SPEND = 8.0
HARVEST_MIN_ORDERS = 2
HARVEST_ACOS_FLOOR = 0.30           # "... below the account average (or < 30%)"

# Campaign short codes used in tables (full names are kept in the CSVs)
CAMP = {
    'VIC-M-SP-Dental Mirror Branded and Product KW':
        ('BRAND-KW', 'Manual keywords: brand + generic (illuco, dental, dental mirror, dental tools home use)'),
    'VIC-BOF | SP | Dental Mirror HEAD 1x 2x 3x | SP Exact Target + Prod Exp + Brand Exp':
        ('HEADS-KW', 'Manual keywords for replacement heads; spend is almost all "dental mirror" phrase'),
    'VIC-M- SP | Dental Mirror Category | Dental Mirror | All Single Multipack':
        ('CATEGORY', 'Manual category target category="Dental Mirrors" (singles + multipacks)'),
    'VIC-SP-AUTO-DTMR-1PK-ALL': ('AUTO-1PK', 'Auto: single mirror with handle'),
    'VIC-SP-AUTO-MRHD-5PK-ALL': ('AUTO-HEADS', 'Auto: replacement heads 5-pack'),
    'VIC-SP-AUTO-DTMR-5PK-AB': ('AUTO-5PK', 'Auto: 5-pack with handles'),
    'VIC-SP Auto Dental Mirror Substitutes and Close Match': ('AUTO-LEGACY', 'Auto: legacy substitutes/close match'),
    'SP-Dermatoscope-KWs-All': ('DERM', 'Manual keywords: dermatoscopes'),
}
MIRROR_SINGLE_CAMPS = {'CATEGORY', 'AUTO-1PK'}          # sell mostly the $19.99-31.90 single
MIRROR_PRO_CAMPS = {'BRAND-KW', 'HEADS-KW', 'AUTO-HEADS', 'AUTO-5PK', 'AUTO-LEGACY'}

# ---------------------------------------------------------------- text classes
RX_BRAND = re.compile(r'illuc|ulluc|iluco|\bidm\b|\bids-?\d{3,4}\b')
RX_ASIN = re.compile(r'^b0[0-9a-z]{8}$')
RX_MIRROR = re.compile(r'mirr|miror|espejo|reflector')
RX_DERM = re.compile(r'derm')
RX_MOUTH_CTX = re.compile(r'mirr|miror|espejo|\bteeth\b|\btooth\b|\bmouth\b')
RX_LIGHT = re.compile(r'\b(lights?|lighted|lighting|light[- ]?up|led|rechargeable|illuminated)\b')
CONSUMER_RULES = [
    ('LED / lighted / rechargeable', None),    # needs mirror/teeth context, see classify_term
    ('Home use', re.compile(r'\bhome\b')),
    ('Kids / child / classroom', re.compile(r'\b(kids?|child|children|classroom|toddler|toy|costume)\b')),
    ('Disposable / plastic', re.compile(r'\b(disposable|plastic)\b')),
    ('Pick sets / plaque / tartar / cleaning', re.compile(r'\b(picks?|plaque|tartar|cleaning|cleaner|scraper|floss|whitening)\b')),
    ('Hand / makeup / telescoping / car inspection', re.compile(r'hand ?held mirror|\bhand mirror|makeup|make-up|telescop|mechanic|automotive|\bcar\b')),
]
RX_RHODIUM = re.compile(r'rhod|rodio|rhoid|\bradio\b')
RX_PHONE = re.compile(r'iphone|smart ?phone|cell ?phone|\bphone\b')
RX_DERM_DEVICE = re.compile(r'derm[a-z]*scop|dermlite|dermalite|lampara de wood|luz de wood|\bwoods? lamp')
RX_COMP_BRAND = re.compile(r'zirc|hu.?friedy|dermlite|dermalite|iboolo|iboloo|american eagle|surgimac|osung|medesy|'
                           r'purevac|henry schein|artman|\bjmu\b|ceonam|pofozo')
RX_SPANISH = re.compile(r'espejo|odontolog|lupas|dermatoscopio|ultrasonido|camara|turbina|material de|lámina|motor de|'
                        r'floruro|accesorios|bucal|dentales|lampara|luz de|[^\x00-\x7f]{2,}')
CONSUMER_CLASSES = [c for c, _ in CONSUMER_RULES] + ['ASIN: low-price / LED competitor']
IRRELEVANT_CLASSES = ['Rhodium (competing coating)', 'Off-category: non-mirror dental / generic',
                      'Off-category: not a dermatoscope', 'Phone-attachment dermatoscope']


def clean_term(t: str) -> str:
    # "light weight" and "without light" are not LED modifiers (they describe a plain professional mirror)
    return re.sub(r'light ?weight|without (a )?light', '', t)


# ---------------------------------------------------------------- IO helpers
def read_text(p: Path) -> str:
    b = p.read_bytes()
    try:
        return b.decode('utf-8-sig')
    except UnicodeDecodeError:
        return b.decode('cp1252')


def read_csv_any(p: Path, header_token: str | None = None) -> tuple[pd.DataFrame, str | None]:
    """CSV with optional metadata line(s) before the header row."""
    lines = read_text(p).splitlines()
    start, meta = 0, None
    if header_token:
        for i, line in enumerate(lines):
            if line.lstrip('"').startswith(header_token):
                start = i
                break
        meta = '\n'.join(lines[:start]) or None
    return pd.read_csv(io.StringIO('\n'.join(lines[start:]))), meta


def money(v) -> float:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return 0.0
    s = str(v).replace('$', '').replace(',', '').strip()
    return float(s) if s else 0.0


def div(a, b):
    return a / b if b else float('nan')


# ---------------------------------------------------------------- formatting
def fm(x, d=2):
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return '-'
    return f'${x:,.{d}f}'


def fp(x, d=1):
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return '-'
    return f'{x * 100:.{d}f}%'


def fsp(x, d=2):
    """SQP share fields are already percentages (0.60 means 0.60%)."""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return '-'
    return f'{x:.{d}f}%'


def fi(x):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return '-'
    return f'{int(round(x)):,}'


def md_table(rows: list[list], header: list[str], align: str | None = None) -> str:
    align = align or 'l' * len(header)
    out = ['| ' + ' | '.join(header) + ' |',
           '|' + '|'.join('---:' if a == 'r' else '---' for a in align) + '|']
    for r in rows:
        out.append('| ' + ' | '.join(str(c).replace('|', '\\|') for c in r) + ' |')
    return '\n'.join(out)


# ---------------------------------------------------------------- load
def load_campaigns() -> pd.DataFrame:
    df, _ = read_csv_any(F_CAMPAIGN)
    df.columns = [c.strip() for c in df.columns]
    for c in ['Budget Amount', 'Spend', '7 Day Total Sales']:
        df[c] = df[c].map(money)
    df['Start'] = pd.to_datetime(df['Start Date'], format='%b %d, %Y')
    df['End'] = pd.to_datetime(df['End Date'], format='%b %d, %Y')
    df['code'] = df['Campaign Name'].map(lambda n: CAMP[n][0])
    df['impr'] = df['Impressions'].astype(float)
    df['clicks'] = df['Clicks'].astype(float)
    df['orders'] = df['7 Day Total Orders (#)'].astype(float)
    df['spend'] = df['Spend']
    df['sales'] = df['7 Day Total Sales']
    # sanity check against the exported ACOS
    rep = df['Total Advertising Cost of Sales (ACOS)'].astype(str).str.rstrip('%').astype(float) / 100
    calc = (df['spend'] / df['sales']).where(df['sales'] > 0, 0.0)
    assert (rep - calc).abs().max() < 0.001, 'campaign ACOS mismatch'
    return df


def load_terms() -> pd.DataFrame:
    st = pd.read_excel(F_TERMS)
    st.columns = [c.strip() for c in st.columns]
    st = st.rename(columns={'Customer Search Term': 'term', 'Campaign Name': 'campaign', 'Ad Group Name': 'ad_group',
                            'Impressions': 'impr', 'Clicks': 'clicks', 'Spend': 'spend', '7 Day Total Sales': 'sales',
                            '7 Day Total Orders (#)': 'orders', '7 Day Total Units (#)': 'units',
                            '7 Day Advertised SKU Sales': 'adv_sales', '7 Day Other SKU Sales': 'other_sales',
                            'Match Type': 'match', 'Targeting': 'target'})
    st['term'] = st['term'].astype(str).str.strip().str.lower()
    st['code'] = st['campaign'].map(lambda n: CAMP[n][0])
    return st


def load_targets() -> pd.DataFrame:
    tg = pd.read_excel(F_TARGETS)
    tg.columns = [c.strip() for c in tg.columns]
    tg = tg.rename(columns={'Campaign Name': 'campaign', 'Ad Group Name': 'ad_group', 'Targeting': 'target',
                            'Match Type': 'match', 'Impressions': 'impr', 'Clicks': 'clicks', 'Spend': 'spend',
                            '7 Day Total Sales': 'sales', '7 Day Total Orders (#)': 'orders',
                            'Top-of-search Impression Share': 'tos_is', 'Cost Per Click (CPC)': 'cpc'})
    tg['code'] = tg['campaign'].map(lambda n: CAMP[n][0])
    return tg


def load_sqp(period: str) -> tuple[pd.DataFrame, str]:
    df, meta = read_csv_any(F_SQP[period], header_token='Search Query')
    df = df.rename(columns={
        'Search Query': 'query', 'Search Query Score': 'score', 'Search Query Volume': 'volume',
        'Impressions: Total Count': 'impr_total', 'Impressions: Brand Count': 'impr_brand',
        'Impressions: Brand Share %': 'impr_share', 'Clicks: Total Count': 'clicks_total',
        'Clicks: Brand Count': 'clicks_brand', 'Clicks: Brand Share %': 'click_share',
        'Cart Adds: Total Count': 'carts_total', 'Cart Adds: Brand Count': 'carts_brand',
        'Cart Adds: Brand Share %': 'cart_share', 'Purchases: Total Count': 'purch_total',
        'Purchases: Brand Count': 'purch_brand', 'Purchases: Brand Share %': 'purch_share',
        'Purchases: Purchase Rate %': 'purch_rate', 'Purchases: Price (Median)': 'mkt_purch_price',
        'Clicks: Brand Price (Median)': 'brand_click_price', 'Reporting Date': 'reporting_date'})
    df['query'] = df['query'].astype(str).str.strip().str.lower()
    df['period'] = period
    df['vol_rank'] = df['volume'].rank(ascending=False, method='first').astype(int)
    return df, (meta or '').strip()


def load_business() -> pd.DataFrame:
    df, _ = read_csv_any(F_BUSINESS)
    for c in ['Ordered Product Sales']:
        df[c] = df[c].map(money)
    for c in ['Sessions - Total', 'Units Ordered', 'Total Order Items', 'Page Views - Total']:
        df[c] = df[c].astype(str).str.replace(',', '').astype(float)

    def fam(t):
        t = t.lower()
        if 'dermatoscope' in t:
            return 'dermatoscope'
        if 'photo mirror' in t:
            return 'photo'
        if 'head only' in t:
            return 'heads'
        if '5-pack) with handles' in t:
            return '5-pack kit'
        if t.startswith('1 dental mirror'):
            return 'single'
        return 'other (headlight, Hansderma brushes)'
    df['family'] = df['Title'].map(fam)
    return df


def load_competitor_asins() -> dict:
    import json
    out = {}
    if F_COMPETITORS.exists():
        for x in json.loads(read_text(F_COMPETITORS)):
            out[x['asin'].lower()] = x
    return out


def load_listing_copy() -> dict:
    """Proposed copy (title, highlight, bullets, description, backend) per mirror family, read-only."""
    copy = {}
    if not F_LISTING_UPDATES.exists():
        return copy
    import openpyxl
    wb = openpyxl.load_workbook(F_LISTING_UPDATES, read_only=True, data_only=True)
    rows = list(wb['Listing Updates'].iter_rows(values_only=True))
    h = {k: i for i, k in enumerate(rows[0])}
    fam_map = {'5-Pack with Handles': '5-pack kit', 'Replacement Heads 5-Pack': 'heads', 'Single Mirror with Handle': 'single'}
    cols = ['NEW title (<75 chars)', 'NEW Item Highlight', 'NEW Bullet 1', 'NEW Bullet 2', 'NEW Bullet 3', 'NEW Bullet 4',
            'NEW Bullet 5', 'NEW Description', 'NEW Generic Keywords (backend)']
    for r in rows[1:]:
        fam = fam_map.get(r[h['Family']])
        if fam:
            copy.setdefault(fam, []).append(' '.join(str(r[h[c]] or '') for c in cols))
    return {k: ' '.join(v).lower() for k, v in copy.items()}


# ---------------------------------------------------------------- classification
def classify_term(term: str, code: str, own_asins: set, comp: dict) -> str:
    t = clean_term(term)
    if RX_BRAND.search(t):
        return 'Brand / ILLUCO model'
    if RX_ASIN.match(t):
        if t in own_asins:
            return 'ASIN: own listing'
        c = comp.get(t)
        if c:
            title = (c.get('title') or '').lower()
            price = money(c.get('price')) if c.get('price') else None
            if re.search(r'\b(led|light|rechargeable|disposable)\b|100 ?pcs', title) or (price is not None and price < 10):
                return 'ASIN: low-price / LED competitor'
        return 'ASIN: other competitor'
    if code == 'DERM':
        if not RX_DERM.search(t):
            return 'Off-category: not a dermatoscope'
        if RX_PHONE.search(t):
            return 'Phone-attachment dermatoscope'
        return 'Relevant dermatoscope term'
    if RX_LIGHT.search(t) and RX_MOUTH_CTX.search(t):
        return 'LED / lighted / rechargeable'
    for name, rx in CONSUMER_RULES[1:]:
        if rx.search(t):
            return name
    if RX_RHODIUM.search(t):
        return 'Rhodium (competing coating)'
    if not RX_MIRROR.search(t):
        return 'Off-category: non-mirror dental / generic'
    return 'Relevant mirror term'


def harvest_family(term: str, aov: float) -> str:
    if RX_DERM.search(term) or re.search(r'\bids-?\d', term):
        return 'dermatoscope'
    if re.search(r'photo|occlusal|buccal|lingual', term):
        return 'photo'
    if re.search(r'\bheads?\b|replacement|refill', term):
        return 'heads'
    if aov and aov < 45:
        return 'single'
    return '5-pack kit'


def sqp_relevance(q: str) -> str:
    if RX_BRAND.search(q):
        return 'Brand (ILLUCO)'
    if RX_DERM_DEVICE.search(q):
        return 'Dermatoscope'
    if re.search(r'dermat', q):
        return 'Dermatology: adjacent (magnifiers, tools)'
    if re.search(r'hand ?held mirror|\bhand mirror|patient mirror|head mirror|head miror|doctor mirror', q):
        return 'Off-category'
    mirror = re.search(r'mirr|miror|espejo', q)
    dental_ctx = re.search(r'dental|dentist|mouth|tooth|teeth|oral|odont|bucal|intraoral|zirc|hu.?friedy|espejo', q)
    if mirror and dental_ctx:
        if re.search(r'photo|occlusal|buccal|lingual', q):
            return 'Photo mirror'
        if RX_LIGHT.search(q) or re.search(r'\b(disposable|plastic|kids?|children|classroom|home)\b', q):
            return 'Mirror: consumer (LED/disposable/kids/home)'
        if RX_RHODIUM.search(q):
            return 'Mirror: rhodium (competing coating)'
        if re.search(r'\bheads?\b|replacement|refill', q):
            return 'Mirror heads'
        if re.search(r'\bteeth\b|\btooth\b', q):
            return 'Mirror: consumer-leaning (teeth)'
        return 'Mirror: core'
    return 'Off-category'


STOP = {'for', 'with', 'de', 'the', 'a', 'and', 'of', 'to', 'in', 'x', 'un', 'una', 'para', 'con', 'los', 'las', 'el', 'la'}


def _tokens(s: str) -> list[str]:
    out = []
    for w in re.findall(r'[a-z0-9#]+', s.lower()):
        if w in STOP:
            continue
        if len(w) > 3 and w.endswith('s') and not w.endswith('ss'):
            w = w[:-1]
        out.append(w)
    return out


def covered(q: str, text: str) -> bool:
    if not text:
        return False
    vocab = set(_tokens(text))
    return all(w in vocab for w in _tokens(q))


# ---------------------------------------------------------------- main
def main() -> None:
    OUT.mkdir(exist_ok=True)
    camp = load_campaigns()
    st = load_terms()
    tg = load_targets()
    sqp = {p: load_sqp(p) for p in F_SQP}
    sqp_oct_vol = sqp['2026-10'][0].set_index('query').volume.to_dict()
    br = load_business()
    comp = load_competitor_asins()
    copy = load_listing_copy()
    own_asins = set(br['(Child) ASIN'].str.lower()) | set(br['(Parent) ASIN'].str.lower())
    fog_returns, n_returns, ret_window = 0, 0, 'n/a'
    if F_RETURNS.exists():                       # FBA customer returns (context for the anti-fog claim)
        ret, _ = read_csv_any(F_RETURNS)
        n_returns = len(ret)
        fog_returns = int(ret['customer-comments'].fillna('').str.contains(r'fog|stay dry', case=False).sum())
        rd = pd.to_datetime(ret['return-date'])
        ret_window = f'{rd.min():%b %Y} - {rd.max():%b %Y}'
    code_of = {n: v[0] for n, v in CAMP.items()}
    name_of = {v[0]: n for n, v in CAMP.items()}
    md: list[str] = []

    # ------------------------------------------------------------ windows
    c_start, c_end = camp['Start'].min(), camp['End'].max()
    st_start, st_end = st['Start Date'].min(), st['End Date'].max()
    tg_start, tg_end = tg['Start Date'].min(), tg['End Date'].max()
    c_days = (c_end - c_start).days + 1
    st_days = (st_end - st_start).days + 1
    single_day_rows = int((st['Start Date'] == st['End Date']).sum())

    def d(x):
        return x.strftime('%b %-d, %Y')

    # ------------------------------------------------------------ a. campaign summary
    camp = camp.sort_values('spend', ascending=False)
    tot = camp[['impr', 'clicks', 'spend', 'orders', 'sales']].sum()
    acct_acos = tot.spend / tot.sales
    st_tot = st[['impr', 'clicks', 'spend', 'orders', 'sales', 'adv_sales', 'other_sales']].sum()
    st_acos = st_tot.spend / st_tot.sales
    harvest_acos = max(min(acct_acos, st_acos), HARVEST_ACOS_FLOOR)   # stricter (lower) of the two account averages
    enabled_budget = camp.loc[camp.Status == 'ENABLED', 'Budget Amount'].sum()
    st_camp = st.groupby('code')[['spend', 'clicks', 'orders', 'sales']].sum()

    rows = []
    for _, r in camp.iterrows():
        days = (r.End - r.Start).days + 1
        st_spend = st_camp.spend.get(r.code, 0.0)
        live_days = (min(r.End, st_end) - st_start).days + 1      # paused campaigns: only their live days in the window
        status = r.Status + (f' (last day {d(r.End)})' if r.Status != 'ENABLED' else '')
        rows.append([f'**{r.code}**', status, fm(r['Budget Amount'], 0), fi(r.impr), fi(r.clicks), fp(div(r.clicks, r.impr), 2),
                     fm(r.spend), fm(div(r.spend, r.clicks)), fi(r.orders), fp(div(r.orders, r.clicks)), fm(r.sales),
                     fp(div(r.spend, r.sales)), f'{div(r.sales, r.spend):.2f}' if r.spend else '-',
                     fm(div(r.spend, days)), fm(st_spend / live_days) + f' ({fp(div(st_spend / live_days, r["Budget Amount"]), 0)})'])
    rows.append(['**Total**', f'{(camp.Status == "ENABLED").sum()} enabled / {(camp.Status != "ENABLED").sum()} paused',
                 fm(camp['Budget Amount'].sum(), 0) + f' ({fm(enabled_budget, 0)} enabled)', fi(tot.impr), fi(tot.clicks),
                 fp(div(tot.clicks, tot.impr), 2), fm(tot.spend), fm(div(tot.spend, tot.clicks)), fi(tot.orders),
                 fp(div(tot.orders, tot.clicks)), fm(tot.sales), fp(acct_acos), f'{div(tot.sales, tot.spend):.2f}',
                 fm(tot.spend / c_days), fm(st_tot.spend / st_days) + f' ({fp(div(st_tot.spend / st_days, enabled_budget), 0)})'])
    campaign_table = md_table(rows, ['Campaign', 'Status', 'Budget/day', 'Impr.', 'Clicks', 'CTR', 'Spend', 'CPC', 'Orders',
                                     'CVR', 'Sales', 'ACoS', 'ROAS', 'Avg spend/day (report window)',
                                     f'Avg spend/day {st_start:%b %-d}-{st_end:%b %-d} (% of budget)'],
                              'llrrrrrrrrrrrrr')

    # ------------------------------------------------------------ search term aggregates
    st['cls'] = [classify_term(t, c, own_asins, comp) for t, c in zip(st.term, st.code)]
    agg_cols = dict(impr=('impr', 'sum'), clicks=('clicks', 'sum'), spend=('spend', 'sum'), sales=('sales', 'sum'),
                    orders=('orders', 'sum'), units=('units', 'sum'), adv_sales=('adv_sales', 'sum'),
                    other_sales=('other_sales', 'sum'),
                    targets=('target', lambda s: '; '.join(sorted({str(x) for x in s}))),
                    matches=('match', lambda s: '; '.join(sorted({str(x) for x in s}))),
                    first=('Start Date', 'min'), last=('End Date', 'max'))
    by_cat = st.groupby(['campaign', 'ad_group', 'term'], as_index=False).agg(**agg_cols)
    by_cat['code'] = by_cat.campaign.map(code_of)
    by_cat['cls'] = [classify_term(t, c, own_asins, comp) for t, c in zip(by_cat.term, by_cat.code)]
    by_term = st.groupby('term', as_index=False).agg(
        impr=('impr', 'sum'), clicks=('clicks', 'sum'), spend=('spend', 'sum'), sales=('sales', 'sum'),
        orders=('orders', 'sum'), n_camps=('code', 'nunique'))
    term_orders = by_term.set_index('term').orders
    # orders per term per campaign, for "converts elsewhere"
    conv_where = (by_cat[by_cat.orders > 0].groupby('term')
                  .apply(lambda g: ', '.join(f'{c} ({int(o)})' for c, o in zip(g.code, g.orders)), include_groups=False))

    # ------------------------------------------------------------ brand / non-brand split
    def bucket(row):
        if row.cls == 'Brand / ILLUCO model':
            return 'Brand / ILLUCO model terms'
        if row.cls == 'ASIN: own listing':
            return 'Own product pages (ILLUCO ASINs)'
        if row.cls.startswith('ASIN'):
            return 'Competitor product pages (ASINs)'
        if row.code == 'DERM':
            return 'Non-brand keywords: dermatoscope'
        return 'Non-brand keywords: mirrors'
    st['bucket'] = st.apply(bucket, axis=1)
    bsplit = st.groupby('bucket')[['clicks', 'spend', 'orders', 'sales']].sum()
    order_b = ['Brand / ILLUCO model terms', 'Non-brand keywords: mirrors', 'Non-brand keywords: dermatoscope',
               'Own product pages (ILLUCO ASINs)', 'Competitor product pages (ASINs)']
    brand_rows = []
    for b in order_b:
        if b in bsplit.index:
            r = bsplit.loc[b]
            brand_rows.append([b, fi(r.clicks), fm(r.spend), fp(r.spend / st_tot.spend), fi(r.orders), fm(r.sales),
                               fp(r.sales / st_tot.sales), fp(div(r.spend, r.sales)), fp(div(r.orders, r.clicks))])
    nb = bsplit.drop(index=['Brand / ILLUCO model terms'], errors='ignore').sum()
    brand_rows.append(['**All except brand terms**', fi(nb.clicks), fm(nb.spend), fp(nb.spend / st_tot.spend), fi(nb.orders),
                       fm(nb.sales), fp(nb.sales / st_tot.sales), fp(div(nb.spend, nb.sales)), fp(div(nb.orders, nb.clicks))])
    brand_rows.append(['**Total (search-term report)**', fi(st_tot.clicks), fm(st_tot.spend), '100.0%', fi(st_tot.orders),
                       fm(st_tot.sales), '100.0%', fp(st_acos), fp(div(st_tot.orders, st_tot.clicks))])
    brand_table = md_table(brand_rows, ['Traffic type', 'Clicks', 'Spend', '% spend', 'Orders', 'Sales', '% sales', 'ACoS', 'CVR'],
                           'lrrrrrrrr')
    brand_b = bsplit.loc['Brand / ILLUCO model terms']
    # brand inside each campaign
    camp_brand = st.assign(is_brand=st.bucket.eq('Brand / ILLUCO model terms')).groupby(['code', 'is_brand'])[['spend', 'orders', 'sales']].sum()

    # ------------------------------------------------------------ b. wasted spend
    waste_mask = (by_cat.orders == 0) & ((by_cat.clicks >= WASTE_MIN_CLICKS) | (by_cat.spend >= WASTE_MIN_SPEND))
    w_cat = by_cat[waste_mask].copy().sort_values('spend', ascending=False)
    w_term_mask = (by_term.orders == 0) & ((by_term.clicks >= WASTE_MIN_CLICKS) | (by_term.spend >= WASTE_MIN_SPEND))
    w_term = by_term[w_term_mask].copy().sort_values('spend', ascending=False)
    w_union_spend = by_cat[waste_mask | (by_cat.term.isin(w_term.term) & (by_cat.orders == 0))].spend.sum()
    zero_order_spend = by_cat[by_cat.orders == 0].spend.sum()

    def waste_action(r) -> str:
        if r.cls in CONSUMER_CLASSES or r.cls in IRRELEVANT_CLASSES:
            return 'Negate (consumer / irrelevant)'
        if r.cls == 'ASIN: own listing':
            return 'Keep (own listing), watch'
        if r.cls.startswith('ASIN'):
            return 'Negative product target'
        if r.cls == 'Brand / ILLUCO model':
            return 'Keep (brand)'
        where = conv_where.get(r.term)
        if where:
            return f'Negative exact here; converts in {where}'
        return 'Relevant: keep, cut bid / watch (no orders anywhere yet)'
    w_cat['action'] = w_cat.apply(waste_action, axis=1)
    w_cat['orders_elsewhere'] = w_cat.term.map(lambda t: int(term_orders.get(t, 0)))
    waste_rows = [[i + 1, r.code, r.term, r.cls, fi(r.clicks), fm(r.spend), r.orders_elsewhere, r.action]
                  for i, (_, r) in enumerate(w_cat.head(25).iterrows())]
    waste_table = md_table(waste_rows, ['#', 'Campaign', 'Search term', 'Class', 'Clicks', 'Spend', 'Orders in other campaigns', 'Action'],
                           'rlllrrrl')
    w_term_rows = [[r.term, int(r.n_camps), fi(r.clicks), fm(r.spend)] for _, r in w_term.head(15).iterrows()]
    w_term_table = md_table(w_term_rows, ['Search term (all campaigns)', 'Campaigns', 'Clicks', 'Spend'], 'lrrr')
    w_action_sum = w_cat.groupby(w_cat.action.str.split(';').str[0].str.replace(r' \(.*', '', regex=True))['spend'].agg(['size', 'sum'])

    # ------------------------------------------------------------ c. leakage
    leak_rows = []
    leak_tot = {'consumer': [0, 0, 0, 0.0, 0, 0.0], 'irrelevant': [0, 0, 0, 0.0, 0, 0.0]}
    for group, classes in (('consumer', CONSUMER_CLASSES), ('irrelevant', IRRELEVANT_CLASSES)):
        for cls in classes:
            sub = by_cat[by_cat.cls == cls]
            if sub.empty:
                leak_rows.append([group.title(), cls, 0, 0, fm(0), '0.0%', 0, fm(0), '-', 'none in this window'])
                continue
            terms = sub.groupby('term')[['spend', 'orders']].sum().sort_values('spend', ascending=False)
            ex = ', '.join(f'"{t}" {fm(s)}' for t, s in terms.spend.head(4).items())
            camps = ', '.join(sub.groupby('code').spend.sum().sort_values(ascending=False).index[:3])
            leak_rows.append([group.title(), cls, sub.term.nunique(), fi(sub.clicks.sum()), fm(sub.spend.sum()),
                              fp(sub.spend.sum() / st_tot.spend), fi(sub.orders.sum()), fm(sub.sales.sum()), camps, ex])
            t = leak_tot[group]
            t[0] += sub.term.nunique(); t[1] += sub.clicks.sum(); t[3] += sub.spend.sum(); t[4] += sub.orders.sum(); t[5] += sub.sales.sum()
    for g in ('consumer', 'irrelevant'):
        t = leak_tot[g]
        leak_rows.append([f'**{g.title()} subtotal**', '', t[0], fi(t[1]), fm(t[3]), fp(t[3] / st_tot.spend), fi(t[4]), fm(t[5]),
                          fp(div(t[3], t[5])) + ' ACoS', ''])
    leak_all_spend = leak_tot['consumer'][3] + leak_tot['irrelevant'][3]
    leak_all_sales = leak_tot['consumer'][5] + leak_tot['irrelevant'][5]
    leak_all_orders = leak_tot['consumer'][4] + leak_tot['irrelevant'][4]
    leak_rows.append(['**Consumer + irrelevant**', '', '', '', fm(leak_all_spend), fp(leak_all_spend / st_tot.spend),
                      fi(leak_all_orders), fm(leak_all_sales), fp(div(leak_all_spend, leak_all_sales)) + ' ACoS', ''])
    # which keyword/target let the leakage in
    leak_src = (st[st.cls.isin(CONSUMER_CLASSES + IRRELEVANT_CLASSES)]
                .groupby(['code', 'target', 'match']).spend.sum().sort_values(ascending=False))
    leak_src_txt = '; '.join(f'{c} "{t}" ({m.lower() if m != "-" else "auto/category"}) {fm(v)} = {fp(v / leak_all_spend, 0)}'
                             for (c, t, m), v in leak_src.head(4).items())
    spanish = st[st.term.map(lambda x: bool(RX_SPANISH.search(x)))]
    spanish_stats = spanish[['clicks', 'spend', 'orders']].sum()
    leak_table = md_table(leak_rows, ['Group', 'Class', 'Terms', 'Clicks', 'Spend', '% of spend', 'Orders', 'Sales', 'Main campaigns', 'Examples (spend)'],
                          'llrrrrrrll')
    # theme checks (not exclusive): fog / teeth / rhodium by campaign
    def theme(rx):
        m = st[st.term.map(lambda x: bool(re.search(rx, clean_term(x))))]
        g = m.groupby('code')[['clicks', 'spend', 'orders', 'sales']].sum()
        return m[['clicks', 'spend', 'orders', 'sales']].sum(), g
    fog_tot, fog_by = theme(r'fog')
    teeth_tot, teeth_by = theme(r'\b(teeth|tooth)\b')

    # ------------------------------------------------------------ d. winners / harvest
    exact_kw = {(r.target.lower(), r.code) for r in tg.itertuples() if r.match == 'EXACT'}
    exact_terms = {t for t, _ in exact_kw}
    harvest = []
    seen = set()
    # 1) account-wide qualification
    for r in by_term.itertuples():
        if r.orders >= HARVEST_MIN_ORDERS and r.sales > 0 and r.spend / r.sales < harvest_acos and not RX_ASIN.match(r.term):
            sub = by_cat[by_cat.term == r.term].sort_values(['orders', 'sales'], ascending=False)
            src = sub.iloc[0]
            harvest.append(dict(term=r.term, basis='account-wide', src=src.campaign, src_code=src.code, orders=r.orders,
                                spend=r.spend, sales=r.sales, clicks=r.clicks,
                                all_camps='; '.join(f'{x.code}: {int(x.orders)} ord / {fm(x.spend)}' for x in sub.itertuples())))
            seen.add(r.term)
    # 2) qualifies inside one campaign/ad group only
    for r in by_cat.itertuples():
        if r.term in seen or RX_ASIN.match(r.term):
            continue
        if r.orders >= HARVEST_MIN_ORDERS and r.sales > 0 and r.spend / r.sales < harvest_acos:
            tt = by_term.set_index('term').loc[r.term]
            sub = by_cat[by_cat.term == r.term].sort_values(['orders', 'sales'], ascending=False)
            harvest.append(dict(term=r.term, basis=f'within {r.code} only', src=r.campaign, src_code=r.code, orders=r.orders,
                                spend=r.spend, sales=r.sales, clicks=r.clicks,
                                all_camps='; '.join(f'{x.code}: {int(x.orders)} ord / {fm(x.spend)}' for x in sub.itertuples()),
                                acct=(tt.orders, tt.spend, tt.sales)))
            seen.add(r.term)
    hv = pd.DataFrame(harvest)
    hv['acos'] = hv.spend / hv.sales
    hv['aov'] = hv.sales / hv.orders
    hv['family'] = [harvest_family(t, a) for t, a in zip(hv.term, hv.aov)]
    hv = hv.sort_values(['orders', 'acos'], ascending=[False, True])

    def harvest_note(r) -> str:
        bits = []
        if RX_BRAND.search(r.term):
            bits.append('Brand term: run as Exact in a brand ad group that serves all families; family shown is from order value')
        if isinstance(r.get('acct'), tuple):
            o, s, sa = r['acct']
            bits.append(f'Account-wide {int(o)} orders / {fm(s)} / ACoS {fp(div(s, sa))}: negative-exact it where it does not convert')
        if 'fog' in r.term:
            bits.append(f'Anti-fog claim: proposed listing copy drops "Fog-Resistant" and {fog_returns} return comments cite fogging/'
                        'water - harvest only if the claim stays')
        if r.term in exact_terms:
            served = tg[(tg.target.str.lower() == r.term) & (tg.match == 'EXACT')]
            q_vol = sqp_oct_vol.get(r.term)
            bits.append('Already an Exact keyword in ' + ', '.join(f'{x.code} ({fi(x.impr)} impr. in 90 days)' for x in served.itertuples())
                        + (f' although SQP shows {fi(q_vol)} searches in Oct' if q_vol else '')
                        + ': check it is enabled and bid at least as high as the broad/phrase versions')
        bits.append('Now captured by ' + r.all_camps)
        return '. '.join(bits)
    hv['notes'] = hv.apply(harvest_note, axis=1)
    near = by_term[(by_term.orders >= HARVEST_MIN_ORDERS) & (by_term.sales > 0) & ~by_term.term.isin(hv.term)
                   & ~by_term.term.str.match(RX_ASIN)].copy()
    near['acos'] = near.spend / near.sales
    near = near.sort_values('orders', ascending=False)
    asin_win = by_term[by_term.term.str.match(RX_ASIN) & (by_term.orders >= HARVEST_MIN_ORDERS)].copy()
    asin_win['acos'] = asin_win.spend / asin_win.sales
    asin_win['owner'] = asin_win.term.map(lambda a: 'ILLUCO' if a in own_asins else
                                          (comp[a].get('brand') + ' ' + str(comp[a].get('price')) if a in comp else 'unknown'))

    harvest_rows = [[r.term, r.src_code, r.basis, fi(r.orders), fm(r.spend), fm(r.sales), fp(r.acos), fm(r.aov), r.family,
                     'yes' if r.term in exact_terms else 'no'] for _, r in hv.iterrows()]
    harvest_table = md_table(harvest_rows, ['Search term', 'Main source', 'Qualifies', 'Orders', 'Spend', 'Sales', 'ACoS', 'AOV',
                                            'Suggested family', 'Already Exact?'], 'lllrrrrrll')

    # ------------------------------------------------------------ e. targeting report
    def match_group(r):
        if r.match in ('EXACT', 'PHRASE', 'BROAD'):
            return f'Keyword {r.match.lower()}'
        t = str(r.target)
        if t.startswith('category='):
            return 'Category target'
        if t.startswith('keyword-group='):
            return 'Keyword group (theme)'
        return f'Auto: {t}'
    tg['mgroup'] = tg.apply(match_group, axis=1)
    mg = tg.groupby('mgroup').agg(targets=('target', 'size'), impr=('impr', 'sum'), clicks=('clicks', 'sum'),
                                  spend=('spend', 'sum'), orders=('orders', 'sum'), sales=('sales', 'sum'))
    mg = mg.sort_values('spend', ascending=False)
    tg_tot = mg.sum()
    mg_rows = [[k, int(r.targets), fi(r.impr), fi(r.clicks), fp(div(r.clicks, r.impr), 2), fm(div(r.spend, r.clicks)), fm(r.spend),
                fi(r.orders), fm(r.sales), fp(div(r.spend, r.sales)), fp(div(r.orders, r.clicks))] for k, r in mg.iterrows()]
    mg_rows.append(['**Total**', int(tg_tot.targets), fi(tg_tot.impr), fi(tg_tot.clicks), fp(div(tg_tot.clicks, tg_tot.impr), 2),
                    fm(div(tg_tot.spend, tg_tot.clicks)), fm(tg_tot.spend), fi(tg_tot.orders), fm(tg_tot.sales),
                    fp(div(tg_tot.spend, tg_tot.sales)), fp(div(tg_tot.orders, tg_tot.clicks))])
    mg_table = md_table(mg_rows, ['Match type / target type', 'Targets', 'Impr.', 'Clicks', 'CTR', 'CPC', 'Spend', 'Orders', 'Sales',
                                  'ACoS', 'CVR'], 'lrrrrrrrrrr')
    # brand share of each target's sales in the search-term window
    tb = st.assign(is_brand=st.bucket.eq('Brand / ILLUCO model terms'))
    tb_sum = tb.groupby(['code', 'target', 'match']).agg(st_spend=('spend', 'sum'), st_sales=('sales', 'sum'), st_orders=('orders', 'sum'))
    tb_brand = tb[tb.is_brand].groupby(['code', 'target', 'match']).agg(b_spend=('spend', 'sum'), b_sales=('sales', 'sum'), b_orders=('orders', 'sum'))
    tb_all = tb_sum.join(tb_brand, how='left').fillna(0)

    paused_codes = set(camp.loc[camp.Status != 'ENABLED', 'code'])

    _de = tg[(tg.code == 'DERM') & (tg.target == 'dermatoscope') & (tg.match == 'EXACT')].iloc[0]
    derm_cap = div(_de.sales, _de.orders) * div(_de.orders, _de.clicks) * 0.30     # CPC for 30% ACoS at observed CVR

    def target_verdict(r, b):
        acos = div(r.spend, r.sales)
        if r.code in paused_codes:
            return 'Campaign paused'
        if RX_BRAND.search(str(r.target)):
            return 'Keep (brand)'
        if r.code == 'DERM':
            if re.search(r'otoscope|ophthalmoscope|phone', str(r.target)):
                return 'Pause (off-target keyword)'
            if r.target == 'dermatoscope' and r.match == 'EXACT':
                return f'Cut bid {fm(r.cpc)} -> <= {fm(derm_cap)}'
            if r.orders == 0:
                return f'Low data at DERM CVR; keep CPC <= {fm(derm_cap)}'
        if r.orders == 0 and r.spend >= WASTE_MIN_SPEND:
            return 'Pause / negate'
        if r.orders == 0:
            return 'Low data'
        if b is not None and b.st_sales > 0 and b.b_sales / b.st_sales >= 0.5:
            nb_acos = div(b.st_spend - b.b_spend, b.st_sales - b.b_sales)
            return f'Brand-driven: non-brand ACoS {fp(nb_acos)}; split brand out, cut bid'
        if acos <= harvest_acos:
            return 'Keep'
        if acos >= 0.5:
            return 'Cut bid / pause'
        return 'Tighten (negatives, lower bid)'
    tgt = tg[(tg.spend >= 5) | (tg.orders > 0)].sort_values('spend', ascending=False)
    tgt_rows = []
    for r in tgt.itertuples():
        key = (r.code, r.target, r.match)
        b = tb_all.loc[key] if key in tb_all.index else None
        brand_note = '-'
        if b is not None and b.st_sales > 0:
            brand_note = f'{fp(b.b_sales / b.st_sales, 0)} of {fm(b.st_sales, 0)}'
        elif b is not None:
            brand_note = 'no sales'
        tgt_rows.append([r.code, r.target, r.match, fp(r.tos_is, 2) if pd.notna(r.tos_is) else '-', fi(r.impr), fi(r.clicks),
                         fm(r.cpc), fm(r.spend), fi(r.orders), fm(r.sales), fp(div(r.spend, r.sales)), brand_note,
                         target_verdict(r, b)])
    tgt_table = md_table(tgt_rows, ['Campaign', 'Target', 'Match', 'Top-of-search IS', 'Impr.', 'Clicks', 'CPC', 'Spend', 'Orders',
                                    'Sales', 'ACoS', f'Brand-term share of sales ({st_start:%b %-d}-{st_end:%b %-d})', 'Verdict'],
                         'lllrrrrrrrrrl')
    zero_click_kw = tg[(tg.clicks == 0) & tg.match.isin(['EXACT', 'PHRASE', 'BROAD'])]

    # ------------------------------------------------------------ f. dermatoscope
    dc = camp[camp.code == 'DERM'].iloc[0]
    dt = tg[tg.code == 'DERM']
    d_exact = dt[(dt.target == 'dermatoscope') & (dt.match == 'EXACT')].iloc[0]
    d_st = st[st.code == 'DERM']
    d_st_spend = d_st.spend.sum()
    d_head = by_cat[(by_cat.code == 'DERM') & (by_cat.term == 'dermatoscope')].iloc[0]
    d_cvr = div(d_exact.orders, d_exact.clicks)
    d_aov = div(d_exact.sales, d_exact.orders)
    sqp_oct = sqp['2026-10'][0].set_index('query')
    sqp_q3 = sqp['2026-Q3'][0].set_index('query')
    sqp_sep = sqp['2026-09'][0].set_index('query')
    derm_br = br[br.family == 'dermatoscope'][['Sessions - Total', 'Units Ordered', 'Ordered Product Sales']].sum()
    d_off = by_cat[(by_cat.code == 'DERM') & by_cat.cls.isin(IRRELEVANT_CLASSES)]
    derm_kw_zero = dt[(dt.clicks == 0)]

    # ------------------------------------------------------------ negatives
    enabled_codes = set(camp.loc[camp.Status == 'ENABLED', 'code'])
    adg_of = by_cat.groupby('code').ad_group.first().to_dict()
    for code_, name_ in name_of.items():
        if code_ not in adg_of:
            adg_of[code_] = tg[tg.code == code_].ad_group.iloc[0]
    PHRASES = [
        # phrase, scope, reason
        ('with light', 'mirror_all', 'Consumer LED mirror modifier ("with light", not bare "light", so "dental mirror without light" '
                                     'and "light weight" stay open)'),
        ('light up', 'mirror_all', 'Consumer LED/light-up mirror modifier'),
        ('lighted', 'mirror_all', 'Consumer LED/light-up mirror modifier'),
        ('led', 'mirror_all', 'Consumer LED/light-up mirror modifier'),
        ('rechargeable', 'mirror_all', 'Consumer LED/light-up mirror modifier'),
        ('home', 'mirror_pro', 'Consumer home-use modifier (kept open in single-mirror campaigns: converted once there at low cost)'),
        ('kids', 'mirror_all', 'Consumer/kids modifier'),
        ('child', 'mirror_all', 'Consumer/kids modifier'),
        ('classroom', 'mirror_all', 'Education/kids modifier'),
        ('disposable', 'mirror_all', 'Disposable mirrors: wrong product and price tier'),
        ('plastic', 'mirror_all', 'Plastic mirrors: wrong product and price tier'),
        ('pick', 'mirror_all', 'Consumer mirror-and-pick sets'),
        ('plaque', 'mirror_all', 'Consumer plaque-removal tools'),
        ('tartar', 'mirror_all', 'Consumer tartar-removal tools'),
        ('cleaning', 'mirror_all', 'Consumer teeth-cleaning tools'),
        ('hand mirror', 'mirror_all', 'Hand/vanity mirrors, not mouth mirrors'),
        ('makeup', 'mirror_all', 'Makeup mirrors'),
        ('telescoping', 'mirror_all', 'Telescoping inspection mirrors (automotive/mechanic)'),
        ('mechanic', 'mirror_all', 'Automotive/mechanic inspection mirrors'),
        ('rhodium', 'mirror_all', 'Competing coating: ILLUCO is front-surface dielectric, not rhodium'),
        ('rodio', 'mirror_all', 'Spanish "rodio" = rhodium (competing coating)'),
        ('radio', 'mirror_data', '"radio dental mirrors" = rhodium/rodio variant'),
        ('rhoid', 'mirror_data', 'Rhodium misspelling'),
        ('automotive', 'mirror_all', 'Automotive inspection mirrors'),
        ('handpiece', 'mirror_data', 'Off-category dental equipment'),
        ('hand piece', 'mirror_data', 'Off-category dental equipment'),
        ('drill', 'mirror_data', 'Off-category dental equipment'),
        ('loupe', 'mirror_data', 'Off-category: magnification loupes'),
        ('loupes', 'mirror_data', 'Off-category: magnification loupes'),
        ('lupas', 'mirror_data', 'Off-category: loupes (Spanish)'),
        ('scaler', 'mirror_data', 'Off-category dental instrument'),
        ('scalers', 'mirror_data', 'Off-category dental instrument'),
        ('burs', 'mirror_data', 'Off-category dental consumable'),
        ('file', 'mirror_data', 'Off-category dental/DIY file'),
        ('ultrasonic', 'mirror_data', 'Off-category dental equipment'),
        ('ultrasonido', 'mirror_data', 'Off-category dental equipment (Spanish)'),
        ('ultrasound', 'mirror_data', 'Off-category dental equipment'),
        ('materials', 'mirror_data', 'Off-category dental materials'),
        ('composite', 'mirror_data', 'Off-category dental instruments/materials'),
        ('high speed', 'mirror_data', 'Off-category dental handpieces'),
        ('instruments', 'mirror_data', 'Generic instrument searches (non-mirror); 0 orders'),
        ('otoscope', 'derm', 'Different device (otoscope)'),
        ('ophthalmoscope', 'derm', 'Different device (ophthalmoscope)'),
        ('loupe', 'derm', 'Different device (loupe)'),
        ('esthetician', 'derm', 'Esthetician supplies, not dermoscopy'),
        ('phone', 'derm', 'Phone-attachment dermatoscopes (ILLUCO units are handheld)'),
        ('iphone', 'derm', 'Phone-attachment dermatoscopes (ILLUCO units are handheld)'),
        ('smartphone', 'derm', 'Phone-attachment dermatoscopes (ILLUCO units are handheld)'),
    ]

    def phrase_rx(p):
        return re.compile(r'(?<![a-z0-9])' + re.escape(p) + r'(?![a-z0-9])')

    neg = []
    phrase_cover = {}   # code -> list of compiled phrases included
    for phrase, scope, reason in PHRASES:
        rx = phrase_rx(phrase)
        if scope == 'derm':
            codes = ['DERM'] if 'DERM' in enabled_codes else []
        elif scope == 'mirror_pro':
            codes = sorted((MIRROR_PRO_CAMPS & enabled_codes))
        else:
            codes = sorted(((MIRROR_PRO_CAMPS | MIRROR_SINGLE_CAMPS) & enabled_codes))
        for code_ in codes:
            sub = by_cat[(by_cat.code == code_) & by_cat.term.map(lambda x: bool(rx.search(x)))]
            if scope == 'mirror_data' and (sub.spend.sum() == 0 or not sub.cls.isin(CONSUMER_CLASSES + IRRELEVANT_CLASSES).any()):
                continue                         # off-category words only where they actually leaked off-category traffic
            if scope == 'derm' and sub.spend.sum() == 0 and phrase not in ('otoscope', 'ophthalmoscope', 'phone', 'iphone', 'smartphone'):
                continue
            if sub.orders.sum() > 0 and div(sub.spend.sum(), sub.sales.sum()) < harvest_acos:
                continue                         # never negate a phrase that is profitable in this campaign
            spend_, clicks_, orders_ = sub.spend.sum(), sub.clicks.sum(), sub.orders.sum()
            ex = ', '.join(f'"{t}"' for t in sub.sort_values('spend', ascending=False).term.head(3))
            why = reason + (f'. Blocks {len(sub)} terms seen {st_start:%b %-d}-{st_end:%b %-d}, e.g. {ex}' if len(sub) else
                            '. Preventive (no spend yet in this campaign)')
            if orders_:
                why += f'; those terms had {int(orders_)} order(s) / {fm(sub.sales.sum())} sales (ACoS {fp(div(spend_, sub.sales.sum()))})'
            rel_hit = sub[sub.cls.isin(['Relevant mirror term', 'Relevant dermatoscope term'])]
            if len(rel_hit):
                why += (f'. Side effect: also blocks {len(rel_hit)} on-topic quer{"y" if len(rel_hit) == 1 else "ies"} '
                        f'({", ".join(repr(t) for t in rel_hit.term.head(2))}; {fm(rel_hit.spend.sum())}, {int(rel_hit.orders.sum())} orders)')
            neg.append(dict(campaign=name_of[code_], ad_group=adg_of[code_], keyword=phrase, match_type='negative phrase',
                            reason=why, spend_to_date=round(spend_, 2), clicks=int(clicks_), orders=int(orders_)))
            phrase_cover.setdefault(code_, []).append(rx)

    def blocked_by_phrase(code_, term):
        return any(rx.search(term) for rx in phrase_cover.get(code_, []))

    # exact negatives: wasted rows (campaign level) + rows of terms that are wasted account-wide
    exact_cand = by_cat[(waste_mask | (by_cat.term.isin(w_term.term) & (by_cat.orders == 0))) & by_cat.code.isin(enabled_codes)]
    for r in exact_cand.sort_values('spend', ascending=False).itertuples():
        act = waste_action(r)
        if blocked_by_phrase(r.code, r.term):
            continue
        if act.startswith('Negate'):
            neg.append(dict(campaign=r.campaign, ad_group=r.ad_group, keyword=r.term, match_type='negative exact',
                            reason=f'{r.cls}: {int(r.clicks)} clicks, {fm(r.spend)}, 0 orders', spend_to_date=round(r.spend, 2),
                            clicks=int(r.clicks), orders=0))
        elif act.startswith('Negative exact here'):
            neg.append(dict(campaign=r.campaign, ad_group=r.ad_group, keyword=r.term, match_type='negative exact',
                            reason=f'Relevant term, 0 orders here ({int(r.clicks)} clicks, {fm(r.spend)}); converts in {conv_where.get(r.term)}: route it there',
                            spend_to_date=round(r.spend, 2), clicks=int(r.clicks), orders=0))
        elif act == 'Negative product target':
            who = comp.get(r.term)
            whos = f'{who.get("brand")} {who.get("price")}' if who else 'ASIN not in data/raw/competitor_search.json'
            neg.append(dict(campaign=r.campaign, ad_group=r.ad_group, keyword=r.term.upper(), match_type='negative product target (ASIN)',
                            reason=f'Product-page placement ({whos}): {int(r.clicks)} clicks, {fm(r.spend)}, 0 orders. ASINs need negative product targeting, not a negative keyword',
                            spend_to_date=round(r.spend, 2), clicks=int(r.clicks), orders=0))
    # route harvested winners: negative exact in campaigns where the same term bleeds (>= $5, 0 orders)
    for h in hv.itertuples():
        bleed = by_cat[(by_cat.term == h.term) & (by_cat.orders == 0) & (by_cat.spend >= 5) & by_cat.code.isin(enabled_codes)
                       & (by_cat.code != h.src_code)]
        for r in bleed.itertuples():
            if any((n['campaign'] == r.campaign and n['keyword'] == r.term) for n in neg):
                continue
            neg.append(dict(campaign=r.campaign, ad_group=r.ad_group, keyword=r.term, match_type='negative exact',
                            reason=f'Harvest routing: wins in {h.src_code} ({int(h.orders)} orders), 0 orders here ({int(r.clicks)} clicks, {fm(r.spend)})',
                            spend_to_date=round(r.spend, 2), clicks=int(r.clicks), orders=0))
    negdf = pd.DataFrame(neg, columns=['campaign', 'ad_group', 'keyword', 'match_type', 'reason', 'spend_to_date', 'clicks', 'orders'])
    camp_order = {c: i for i, c in enumerate(['BRAND-KW', 'HEADS-KW', 'CATEGORY', 'AUTO-1PK', 'AUTO-HEADS', 'DERM', 'AUTO-5PK', 'AUTO-LEGACY'])}
    mt_order = {'negative exact': 0, 'negative product target (ASIN)': 1, 'negative phrase': 2}
    negdf['_c'] = negdf.campaign.map(lambda n: camp_order[code_of[n]])
    negdf['_m'] = negdf.match_type.map(mt_order)
    negdf = negdf.sort_values(['_c', '_m', 'spend_to_date', 'keyword'], ascending=[True, True, False, True]).drop(columns=['_c', '_m'])
    negdf.to_csv(OUT / 'negative_keywords.csv', index=False)
    neg_top = (negdf.groupby(['keyword', 'match_type'])
               .agg(spend=('spend_to_date', 'sum'), clicks=('clicks', 'sum'), orders=('orders', 'sum'),
                    camps=('campaign', lambda s: ', '.join(sorted({code_of[x] for x in s}))))
               .sort_values('spend', ascending=False).reset_index())
    n_preventive = int((negdf.spend_to_date == 0).sum())

    # ------------------------------------------------------------ savings estimate
    pause_kw = [('BRAND-KW', 'dental', 'PHRASE'), ('BRAND-KW', 'dental tools home use', 'BROAD'),
                ('BRAND-KW', 'dental hygienist must haves', 'EXACT')]
    neg_exact = {(code_of[n['campaign']], n['keyword'].lower()) for n in neg if n['match_type'] != 'negative phrase'}

    def is_blocked(r):
        if (r.code, r.target, r.match) in pause_kw:
            return 'pause keyword'
        if (r.code, r.term) in neg_exact:
            return 'negative exact / ASIN'
        if blocked_by_phrase(r.code, r.term):
            return 'negative phrase'
        return ''
    st['blocked'] = [is_blocked(r) for r in st.itertuples()]
    blk = st[st.blocked != '']
    blk_by = blk.groupby('blocked')[['clicks', 'spend', 'orders', 'sales']].sum()
    blk_tot = blk[['clicks', 'spend', 'orders', 'sales']].sum()
    pause_stats = {k: st[(st.code == k[0]) & (st.target == k[1]) & (st.match == k[2])][['clicks', 'spend', 'orders', 'sales']].sum()
                   for k in pause_kw}
    pause_tg = {k: tg[(tg.code == k[0]) & (tg.target == k[1]) & (tg.match == k[2])][['clicks', 'spend', 'orders', 'sales']].sum()
                for k in pause_kw}

    # ------------------------------------------------------------ harvest CSV
    hcsv = pd.DataFrame({
        'search_term': hv.term, 'source_campaign': hv.src, 'orders': hv.orders.astype(int), 'spend': hv.spend.round(2),
        'sales': hv.sales.round(2), 'acos': (hv.acos * 100).round(1).astype(str) + '%', 'suggested_match': 'exact',
        'suggested_family': hv.family, 'notes': hv.notes})
    hcsv.to_csv(OUT / 'harvest_keywords.csv', index=False)

    # ------------------------------------------------------------ SQP
    ads_term = by_term.set_index('term')
    br_title = {f: ' '.join(br[br.family == f].Title).lower() for f in br.family.unique()}

    mirror_titles = ' '.join(br_title.get(k, '') for k in ('5-pack kit', 'single', 'heads'))
    mirror_copy = ' '.join(copy.get(k, '') for k in ('5-pack kit', 'single', 'heads'))
    harvest_terms = set(hv.term)
    near_terms = set(near.term)
    NOT_FOR_COPY = ('Off-category', 'Dermatology: adjacent (magnifiers, tools)')

    def placement(q, rel, vol_month):
        a = ads_term.loc[q] if q in ads_term.index else None
        clicks, orders, spend, sales = (a.clicks, a.orders, a.spend, a.sales) if a is not None else (0, 0, 0.0, 0.0)
        spanish = bool(RX_SPANISH.search(q))
        # ---- copy (title / backend)
        if rel in NOT_FOR_COPY or rel.startswith('Mirror: consumer (') or rel.startswith('Mirror: rhodium'):
            copy_p = 'Not for copy'
        elif rel == 'Brand (ILLUCO)':
            copy_p = 'Brand (in every title)'
        elif RX_COMP_BRAND.search(q):
            copy_p = 'Not for copy (competitor brand; PPC only)'
        elif rel in ('Dermatoscope', 'Photo mirror'):
            title = br_title.get('dermatoscope' if rel == 'Dermatoscope' else 'photo', '')
            copy_p = 'In current title' if covered(q, title) else ('Not in title: add to backend' + (' (Spanish)' if spanish else ''))
        elif covered(q, mirror_titles):
            copy_p = 'In current title'
        elif covered(q, mirror_copy):
            copy_p = ('In proposed backend/bullets; title words would add rank weight' if vol_month >= 800 and rel == 'Mirror: core'
                      else 'In proposed backend/bullets')
        else:
            copy_p = 'Missing from proposed copy: add to backend' + (' (Spanish)' if spanish else '')
        # ---- PPC
        acos_txt = f', ACoS {fp(div(spend, sales))}' if sales else ''
        if rel in NOT_FOR_COPY:
            ppc = 'None (off-category)'
        elif rel.startswith('Mirror: consumer (') or rel.startswith('Mirror: rhodium'):
            ppc = 'Negative in pro campaigns'
        elif rel == 'Brand (ILLUCO)':
            ppc = 'Brand Exact (defend)'
        elif q in harvest_terms:
            ppc = 'Exact: harvest (harvest_keywords.csv)'
        elif q in near_terms:
            ppc = f'Near-miss winner ({int(orders)} ad orders{acos_txt}): keep in single-mirror campaigns'
        elif q in exact_terms and orders >= 1:
            where = ', '.join(sorted(c for t, c in exact_kw if t == q))
            ppc = (f'Already Exact in {where}: lower the bid ({int(orders)} ad order{acos_txt})' if div(spend, sales) > harvest_acos
                   else f'Already Exact in {where}: keep ({int(orders)} ad order{acos_txt})')
        elif rel == 'Dermatoscope' and clicks > 0 and orders == 0:
            ppc = f'Keep at a low bid (0 orders on {int(clicks)} ad clicks is too few at DERM\'s ~0.4% CVR)'
        elif orders >= 1:
            ppc = f'Test Exact at a capped bid ({int(orders)} ad order{"s" if orders > 1 else ""}{acos_txt})'
        elif clicks >= WASTE_MIN_CLICKS or spend >= WASTE_MIN_SPEND:
            ppc = f'No: 0 orders on {int(clicks)} ad clicks (organic only)'
        elif clicks > 0:
            ppc = f'Watch (only {int(clicks)} ad click{"s" if clicks > 1 else ""})'
        else:
            ppc = 'Optional low-bid Exact test (no ad data)'
        if rel == 'Mirror: consumer-leaning (teeth)' and ppc.startswith(('Test', 'Watch', 'Optional', 'Exact')):
            ppc += '; single mirror only'
        return copy_p, ppc, clicks, orders, spend, sales

    def sqp_rows(period):
        df = sqp[period][0].copy()
        df['relevance'] = df['query'].map(sqp_relevance)
        return df
    oct_df, q3_df = sqp_rows('2026-10'), sqp_rows('2026-Q3')
    relevant_cls = {'Mirror: core', 'Mirror heads', 'Photo mirror', 'Dermatoscope', 'Mirror: consumer-leaning (teeth)'}
    # gaps: relevant queries with real volume and ILLUCO click share < 2%
    GAP_SHARE = 2.0
    GAP_VOL = {'2026-10': 150, '2026-Q3': 450}
    out_rows = []
    for period, df in (('2026-10', oct_df), ('2026-Q3', q3_df)):
        top30 = set(df.nsmallest(30, 'vol_rank')['query'])
        wins = set(df[df.purch_brand > 0]['query'])
        gaps = set(df[df.relevance.isin(relevant_cls) & (df.volume >= GAP_VOL[period]) &
                      (df.click_share.fillna(0) < GAP_SHARE)]['query'])
        months = 3 if period == '2026-Q3' else 1
        for r in df[df['query'].isin(top30 | wins | gaps)].itertuples():
            copy_p, ppc, a_clk, a_ord, a_sp, a_sa = placement(r.query, r.relevance, r.volume / months)
            out_rows.append(dict(
                period=('Oct 2026 (month)' if period == '2026-10' else 'Q3 2026 (Jul-Sep, quarter)'),
                search_query=r.query, volume_rank=r.vol_rank, search_query_volume=r.volume, relevance=r.relevance,
                in_top30_by_volume=r.query in top30, illuco_purchase_win=r.query in wins, relevant_gap=r.query in gaps,
                impressions_total=r.impr_total, illuco_impressions=r.impr_brand, illuco_impression_share_pct=round(r.impr_share, 2),
                clicks_total=r.clicks_total, illuco_clicks=r.clicks_brand,
                illuco_click_share_pct=round(r.click_share, 2) if pd.notna(r.click_share) else None,
                cart_adds_total=r.carts_total, illuco_cart_adds=r.carts_brand,
                purchases_total=r.purch_total, illuco_purchases=r.purch_brand,
                illuco_purchase_share_pct=round(r.purch_share, 2) if pd.notna(r.purch_share) else None,
                market_median_purchase_price=r.mkt_purch_price, illuco_median_click_price=r.brand_click_price,
                ads_clicks_sep17_nov20=int(a_clk), ads_orders_sep17_nov20=int(a_ord), ads_spend_sep17_nov20=round(a_sp, 2),
                copy_placement=copy_p, ppc_recommendation=ppc))
    sqp_out = pd.DataFrame(out_rows)
    sqp_out['_p'] = sqp_out.period.str.startswith('Q3').astype(int)       # Oct (latest month) first
    sqp_out = sqp_out.sort_values(['_p', 'volume_rank']).drop(columns='_p')
    sqp_out.to_csv(OUT / 'sqp_top_queries.csv', index=False)

    # md tables for SQP
    o_top = oct_df.nsmallest(30, 'vol_rank').set_index('query')
    q_top = q3_df.nsmallest(30, 'vol_rank').set_index('query')
    q3i, octi = q3_df.set_index('query'), oct_df.set_index('query')
    union = list(o_top.index) + [q for q in q_top.index if q not in o_top.index]
    top_rows = []
    for q in union:
        o = octi.loc[q] if q in octi.index else None
        t = q3i.loc[q] if q in q3i.index else None
        rel = sqp_relevance(q)

        def sh(x, f):
            return fsp(x[f]) if x is not None and pd.notna(x[f]) else '-'
        top_rows.append([q, rel,
                         fi(o.volume) if o is not None else '-', f'#{int(o.vol_rank)}' if o is not None else '-',
                         sh(o, 'impr_share'), sh(o, 'click_share'), sh(o, 'purch_share'),
                         fi(t.volume) if t is not None else '-', f'#{int(t.vol_rank)}' if t is not None else '-',
                         sh(t, 'impr_share'), sh(t, 'click_share'), sh(t, 'purch_share')])
    sqp_top_table = md_table(top_rows, ['Search query', 'Relevance', 'Oct vol', 'Oct rank', 'Oct impr. share', 'Oct click share',
                                        'Oct purch. share', 'Q3 vol', 'Q3 rank', 'Q3 impr. share', 'Q3 click share', 'Q3 purch. share'],
                             'llrrrrrrrrrr')
    n_off_top = sum(1 for q in union if sqp_relevance(q) == 'Off-category')

    win_q = sorted(set(oct_df[oct_df.purch_brand > 0]['query']) | set(q3_df[q3_df.purch_brand > 0]['query']),
                   key=lambda q: -((octi.loc[q].purch_brand if q in octi.index else 0) + (q3i.loc[q].purch_brand if q in q3i.index else 0)))
    win_rows, win_small, nb_wins, nb_over = [], [], 0, 0
    for q in win_q:
        o = octi.loc[q] if q in octi.index else None
        t = q3i.loc[q] if q in q3i.index else None
        rel = sqp_relevance(q)
        for x in (o, t):
            if x is not None and x.purch_brand > 0 and rel not in ('Brand (ILLUCO)', 'Off-category'):
                nb_wins += 1
                nb_over += int(pd.notna(x.click_share) and x.purch_share > x.click_share)

        def cell(x):
            if x is None:
                return '-', '-', '-', '-'
            return fi(x.volume), f'{int(x.purch_brand)}/{int(x.purch_total)}', fsp(x.purch_share, 1), fsp(x.click_share, 1)
        ov, op, ops, ocs = cell(o)
        tv, tp, tps, tcs = cell(t)
        if (o is not None and o.volume >= 10) or (t is not None and t.volume >= 25):
            win_rows.append([q, rel, ov, op, ops, ocs, tv, tp, tps, tcs])
        else:
            win_small.append(q)
    sqp_win_table = md_table(win_rows, ['Search query', 'Relevance', 'Oct vol', 'Oct ILLUCO/total purchases', 'Oct purch. share',
                                        'Oct click share', 'Q3 vol', 'Q3 ILLUCO/total purchases', 'Q3 purch. share', 'Q3 click share'],
                             'llrrrrrrrr')
    gap_df = sqp_out[sqp_out.relevant_gap].copy()
    gap_oct = gap_df[gap_df.period.str.startswith('Oct')].sort_values('search_query_volume', ascending=False)
    gap_q3_only = gap_df[gap_df.period.str.startswith('Q3') & ~gap_df.search_query.isin(gap_oct.search_query)]
    gap_rows = []
    for r in gap_oct.itertuples():
        t = q3i.loc[r.search_query] if r.search_query in q3i.index else None
        gap_rows.append([r.search_query, r.relevance, fi(r.search_query_volume), fsp(r.illuco_impression_share_pct),
                         fsp(r.illuco_click_share_pct), f'{int(r.illuco_purchases)}/{int(r.purchases_total)}',
                         fm(r.market_median_purchase_price) if pd.notna(r.market_median_purchase_price) else '-',
                         fsp(t.click_share) if t is not None and pd.notna(t.click_share) else '-',
                         f'{r.ads_clicks_sep17_nov20} / {r.ads_orders_sep17_nov20}', r.copy_placement, r.ppc_recommendation])
    sqp_gap_table = md_table(gap_rows, ['Search query', 'Relevance', 'Oct vol', 'Oct impr. share', 'Oct click share',
                                        'Oct ILLUCO/total purch.', 'Market median purchase price', 'Q3 click share',
                                        'Ad clicks / orders (Sep 17-Nov 20)', 'Copy (title/backend)', 'PPC'],
                             'llrrrrrrrll')
    gap_q3_rows = [[r.search_query, r.relevance, fi(r.search_query_volume), fsp(r.illuco_click_share_pct),
                    f'{r.ads_clicks_sep17_nov20} / {r.ads_orders_sep17_nov20}', r.copy_placement, r.ppc_recommendation]
                   for r in gap_q3_only.sort_values('search_query_volume', ascending=False).itertuples()]
    sqp_gap_q3_table = md_table(gap_q3_rows, ['Search query', 'Relevance', 'Q3 vol', 'Q3 click share', 'Ad clicks / orders',
                                              'Copy (title/backend)', 'PPC'], 'llrrrll')

    def kq(q, df_i, f):
        return df_i.loc[q][f] if q in df_i.index else float('nan')

    # ------------------------------------------------------------ business report
    fam_br = br.groupby('family')[['Sessions - Total', 'Units Ordered', 'Ordered Product Sales', 'Total Order Items']].sum()
    fam_br = fam_br.sort_values('Ordered Product Sales', ascending=False)
    br_tot = fam_br.sum()
    br_rows = [[f, fi(r['Sessions - Total']), fi(r['Units Ordered']), fp(div(r['Units Ordered'], r['Sessions - Total'])),
                fm(r['Ordered Product Sales']), fp(r['Ordered Product Sales'] / br_tot['Ordered Product Sales'])]
               for f, r in fam_br.iterrows()]
    br_rows.append(['**Total**', fi(br_tot['Sessions - Total']), fi(br_tot['Units Ordered']),
                    fp(div(br_tot['Units Ordered'], br_tot['Sessions - Total'])), fm(br_tot['Ordered Product Sales']), '100.0%'])
    br_table = md_table(br_rows, ['Family', 'Sessions', 'Units', 'Unit session %', 'Ordered product sales', '% of sales'], 'lrrrrr')
    kit_rows = br[br.family == '5-pack kit'].sort_values('Sessions - Total', ascending=False)

    # ================================================================ write markdown
    W = md.append
    W('# ILLUCO Amazon Sponsored Products and Search Query Performance audit')
    W('')
    W(f'Prepared 2026-11-20 by `scripts/ppc_sqp_audit.py` from the exports in `data/account/` (read-only). '
      'Analysis only: the owner has put budget increases on hold, so every recommendation below cuts, negates, harvests '
      'or re-routes within the current budgets. Nothing here raises a budget.')
    W('')
    W('## Data windows and definitions')
    W('')
    W(md_table([
        ['SP campaign report', '`CHECK-_ILLUCO_3.csv`', f'{d(c_start)} - {d(c_end)} ({c_days} days); paused campaigns end on their last active day',
         '1 row per campaign (8)'],
        ['SP search term report', '`CHECK-_ILLUCO_1.xlsx`', f'{d(st_start)} - {d(st_end)} ({st_days} days)',
         f'{len(st)} rows, one per campaign / ad group / target / match type / search term; Start/End = first/last active day '
         f'({single_day_rows} rows are single-day). Aggregated by campaign + ad group + term and by term overall'],
        ['SP targeting report', '`CHECK-_ILLUCO_2.xlsx`', f'{d(tg_start)} - {d(tg_end)} (90 days)', f'{len(tg)} targets'],
        ['Brand Analytics SQP (Brand View)', '`SQP_Brand_Month_2026_10_31.csv` (latest month), `SQP_Brand_Quarter_2026_09_30.csv`, '
         '`SQP_Brand_Month_2026_09_30.csv`', 'Oct 2026; Q3 2026 (Jul 1 - Sep 30); Sep 2026',
         f'{len(oct_df)} / {len(q3_df)} / {len(sqp["2026-09"][0])} queries; first line is a metadata row, skipped'],
        ['Business Report (child ASIN)', '`BusinessReport-11-20-26.csv`', 'Not stated in the export (file dated 11/20/26)',
         f'{len(br)} child-ASIN rows; context only'],
    ], ['Source', 'File', 'Window', 'Grain'], 'llll'))
    W('')
    W('- Orders = `7 Day Total Orders (#)`, Sales = `7 Day Total Sales` (7-day attribution, includes other-SKU "halo" sales: '
      f'{fm(st_tot.other_sales)} = {fp(st_tot.other_sales / st_tot.sales)} of search-term sales). ACoS = spend / sales, ROAS = sales / spend, '
      'CTR = clicks / impressions, CVR = orders / clicks, AOV = sales / orders. All ratios are recomputed from the sums, not averaged.')
    W(f'- The three ad reports cover different windows, so their totals differ (spend: campaign {fm(tot.spend)}, targeting '
      f'{fm(tg_tot.spend)}, search terms {fm(st_tot.spend)}). Search-term sections use the {d(st_start)} - {d(st_end)} window only.')
    W(f'- Account average ACoS: {fp(acct_acos)} (campaign report, {c_days} days) and {fp(st_acos)} (search-term report, same window as the terms). '
      f'Harvest and keep/cut tests use the stricter {fp(harvest_acos)}.')
    W('- Brand terms = search terms containing "illuco" (incl. misspellings "ulluco", "illuc") or an ILLUCO model code (IDM, IDS-xxxx).')
    W('- SQP share columns are already percentages in the export (0.60 means 0.60%). Top-of-search impression share in the '
      'targeting report is a fraction, shown here as a percentage.')
    W('')

    # ---- headline
    W('## Headline')
    W('')
    W(f'- **Campaign report ({d(c_start)} - {d(c_end)}): {fm(tot.spend)} spend, {fm(tot.sales)} sales, {fi(tot.orders)} orders, '
      f'ACoS {fp(acct_acos)}, ROAS {div(tot.sales, tot.spend):.2f}.** Budgets are not the constraint: in the last {st_days} days the '
      f'account spent {fm(st_tot.spend / st_days)}/day against {fm(enabled_budget, 0)}/day of enabled budgets '
      f'({fp(div(st_tot.spend / st_days, enabled_budget), 0)}); only DERM runs near its cap.')
    W(f'- **Brand searches flatter the account.** Brand/model terms took {fp(brand_b.spend / st_tot.spend)} of search-term spend but '
      f'{fp(brand_b.sales / st_tot.sales)} of sales (ACoS {fp(div(brand_b.spend, brand_b.sales))}). Everything else ran at '
      f'ACoS {fp(div(nb.spend, nb.sales))}.')
    W(f'- **Wasted spend ({WASTE_MIN_CLICKS}+ clicks or ${WASTE_MIN_SPEND:.0f}+ and 0 orders): {fm(w_cat.spend.sum())} '
      f'({fp(w_cat.spend.sum() / st_tot.spend)} of {fm(st_tot.spend)})** across {len(w_cat)} campaign/ad-group/term rows. '
      f'Counting every zero-order term regardless of size: {fm(zero_order_spend)} ({fp(zero_order_spend / st_tot.spend)}).')
    top2 = leak_src.head(2)
    W(f'- **Consumer + irrelevant leakage: {fm(leak_all_spend)} ({fp(leak_all_spend / st_tot.spend)} of spend)** for '
      f'{fi(leak_all_orders)} orders / {fm(leak_all_sales)}. {fp(top2.sum() / leak_all_spend, 0)} of it entered through two BRAND-KW keywords: '
      + ' and '.join(f'"{t}" ({m.lower()})' for (c, t, m) in top2.index) + '.')
    W(f'- **DERM: {fm(dc.spend)} for {fi(dc.orders)} orders (ACoS {fp(div(dc.spend, dc.sales))}).** '
      f'{fp(d_exact.spend / dt.spend.sum(), 0)} of its targeting-report spend is one Exact keyword ("dermatoscope") at '
      f'{fm(d_exact.cpc)} CPC with {fi(d_exact.orders)} order in {fi(d_exact.clicks)} clicks.')
    W(f'- Recommended pauses + negatives would have removed **{fm(blk_tot.spend)} ({fp(blk_tot.spend / st_tot.spend)})** of '
      f'{d(st_start)} - {d(st_end)} spend while putting {fm(blk_tot.sales)} of sales ({fi(blk_tot.orders)} orders) at risk; '
      'part of that demand re-routes to the campaigns where the same terms convert.')
    W('')

    # ---- a
    W(f'## a. Campaign summary ({d(c_start)} - {d(c_end)})')
    W('')
    W(campaign_table)
    W('')
    legend = [[f'**{v[0]}**', n, v[1]] for n, v in CAMP.items()]
    W(md_table(legend, ['Code', 'Campaign name (as exported)', 'What it targets (from names and targets)'], 'lll'))
    W('')
    paused = camp[camp.Status != 'ENABLED']
    W(f'- **Paused:** {", ".join(f"{r.code} (paused, last active {d(r.End)}; {fm(r.spend)} spend, {fi(r.orders)} orders, ACoS {fp(div(r.spend, r.sales))})" for r in paused.itertuples())}. '
      f'Their {fm(paused["Budget Amount"].sum(), 0)}/day of budget is idle. Keep them paused.')
    W(f'- Highest ACoS among enabled campaigns: DERM {fp(div(dc.spend, dc.sales))}, CATEGORY {fp(div(camp[camp.code == "CATEGORY"].spend.iloc[0], camp[camp.code == "CATEGORY"].sales.iloc[0]))}, '
      f'BRAND-KW {fp(div(camp[camp.code == "BRAND-KW"].spend.iloc[0], camp[camp.code == "BRAND-KW"].sales.iloc[0]))}. '
      f'CATEGORY has the most orders ({fi(camp[camp.code == "CATEGORY"].orders.iloc[0])}) but a {fm(div(camp[camp.code == "CATEGORY"].sales.iloc[0], camp[camp.code == "CATEGORY"].orders.iloc[0]))} AOV: '
      'it mostly sells the $19.99-31.90 single mirror.')
    W('- The two right-hand columns are averages; actual daily spend varies, and campaign launch dates are not in the export, so the '
      'report-window average can understate days when a campaign was live.')
    W('')
    W(f'**Brand vs non-brand ({d(st_start)} - {d(st_end)}, search-term report)**')
    W('')
    W(brand_table)
    W('')
    hb = camp_brand.loc['HEADS-KW'] if 'HEADS-KW' in camp_brand.index.get_level_values(0) else None
    if hb is not None:
        hb_b = hb.loc[True] if True in hb.index else pd.Series({'spend': 0, 'orders': 0, 'sales': 0})
        hb_n = hb.loc[False]
        W(f'- HEADS-KW looks like one of the best campaigns on paper (ACoS {fp(div(camp[camp.code == "HEADS-KW"].spend.iloc[0], camp[camp.code == "HEADS-KW"].sales.iloc[0]))}), but in this window {fi(hb_b.orders)} of its {fi(hb_b.orders + hb_n.orders)} orders '
          f'({fm(hb_b.sales)} of {fm(hb_b.sales + hb_n.sales)}) came from brand searches it caught through the "dental mirror" phrase keyword. '
          f'Its non-brand traffic cost {fm(hb_n.spend)} for {fi(hb_n.orders)} orders / {fm(hb_n.sales)} (ACoS {fp(div(hb_n.spend, hb_n.sales))}).')
    bk = camp_brand.loc['BRAND-KW']
    W(f'- BRAND-KW: brand terms {fm(bk.loc[True].spend)} spend -> {fm(bk.loc[True].sales)} sales; non-brand {fm(bk.loc[False].spend)} -> '
      f'{fm(bk.loc[False].sales)} (ACoS {fp(div(bk.loc[False].spend, bk.loc[False].sales))}).')
    W('')

    # ---- b
    W(f'## b. Wasted spend ({d(st_start)} - {d(st_end)})')
    W('')
    W(f'Rule: aggregated across days, a search term with **>= {WASTE_MIN_CLICKS} clicks or >= ${WASTE_MIN_SPEND:.0f} spend and 0 orders**.')
    W('')
    W(md_table([
        ['Campaign + ad group + term (where negatives are applied)', len(w_cat), fi(w_cat.clicks.sum()), fm(w_cat.spend.sum()),
         fp(w_cat.spend.sum() / st_tot.spend)],
        ['Term overall (all campaigns summed)', len(w_term), fi(w_term.clicks.sum()), fm(w_term.spend.sum()),
         fp(w_term.spend.sum() / st_tot.spend)],
        ['Union of both views (rows of terms that fail either test)', '', '', fm(w_union_spend), fp(w_union_spend / st_tot.spend)],
        ['Context: all zero-order term rows, any size', int((by_cat.orders == 0).sum()), fi(by_cat[by_cat.orders == 0].clicks.sum()),
         fm(zero_order_spend), fp(zero_order_spend / st_tot.spend)],
    ], ['View', 'Rows', 'Clicks', 'Wasted spend', f'% of {fm(st_tot.spend)}'], 'lrrrr'))
    W('')
    W(f'**{"Top 25" if len(w_cat) > 25 else f"All {len(w_cat)}"} wasted rows by spend (campaign + ad group + term)**')
    W('')
    W(waste_table)
    W('')
    W('Wasted rows by action: ' + '; '.join(f'{k}: {int(v["size"])} rows / {fm(v["sum"])}' for k, v in w_action_sum.sort_values('sum', ascending=False).iterrows()) + '.')
    W('')
    W('- "Relevant: keep, cut bid / watch" rows are on-target professional queries (e.g. anti-fog, front surface, dermatoscope '
      'long-tail). They are not negated; lower the bid or let the harvested Exact keywords carry them.')
    only_term = w_term[~w_term.term.isin(w_cat.term)]
    if len(only_term):
        def treat(t):
            cls = classify_term(t, by_cat[by_cat.term == t].code.iloc[0], own_asins, comp)
            if cls in CONSUMER_CLASSES or cls in IRRELEVANT_CLASSES:
                return f'{cls}, blocked by the phrase negatives'
            return f'{cls}: watch, not negated'
        W('- Terms that fail the test only when summed across campaigns (spend spread thin): '
          + '; '.join(f'"{r.term}" {fm(r.spend)} ({treat(r.term)})' for r in only_term.itertuples()) + '.')
    W('')

    # ---- c
    W(f'## c. Consumer / irrelevant leakage ({d(st_start)} - {d(st_end)})')
    W('')
    W('Each search term is counted once (first matching class). "LED" requires a mirror/teeth context so loupes or curing lights '
      'with a light are counted as off-category, not as LED mirrors. "light weight" and "without light" are not treated as light modifiers.')
    W('')
    W(leak_table)
    W('')
    W(f'- Where it came from (targeting that matched the leaking terms): {leak_src_txt}.')
    W(f'- No spend reached telescoping / automotive / mechanic inspection-mirror, makeup or hand-mirror searches in this window, '
      'so those negatives are preventive.')
    W(f'- Spanish and other non-English search terms (counted inside the classes above where they fit): {spanish.term.nunique()} terms, '
      f'{fi(spanish_stats.clicks)} clicks, {fm(spanish_stats.spend)}, {fi(spanish_stats.orders)} orders.')
    W(f'- Not leakage, but consumer-leaning and worth fencing: "teeth/tooth" terms cost {fm(teeth_tot.spend)} for {fi(teeth_tot.orders)} orders '
      f'(ACoS {fp(div(teeth_tot.spend, teeth_tot.sales))}); {fi(teeth_by.loc["CATEGORY"].orders) if "CATEGORY" in teeth_by.index else 0} of those orders came through CATEGORY '
      '(single mirror). They pay for the $19.99 single, not for 5-packs or heads.')
    W(f'- "fog" terms: {fm(fog_tot.spend)} for {fi(fog_tot.orders)} orders (ACoS {fp(div(fog_tot.spend, fog_tot.sales))}): '
      + '; '.join(f'{c} {fm(r.spend)} / {fi(r.orders)} order{"" if r.orders == 1 else "s"}' for c, r in fog_by.sort_values('spend', ascending=False).iterrows())
      + '. They convert in the single-mirror campaigns and bleed in the 5-pack/heads campaigns.')
    W('')

    # ---- d
    W(f'## d. Winners to harvest into Exact ({d(st_start)} - {d(st_end)})')
    W('')
    W(f'Rule: >= {HARVEST_MIN_ORDERS} orders and ACoS below {fp(harvest_acos)} (the lower of the two account averages, so anything under 30% '
      'also passes), tested account-wide first, then inside each campaign (a term that wins in one campaign and bleeds in others is '
      'harvested from the winning one). Brand terms are listed because they qualify, but they belong in a brand-defense Exact ad group.')
    W('')
    W(harvest_table)
    W('')
    for r in hv.itertuples():
        W(f'- **{r.term}**: {r.notes}.')
    W('')
    if len(near):
        W(f'Near misses (>= 2 orders, ACoS above the {fp(harvest_acos, 2)} threshold but below the {fp(st_acos, 2)} same-window average): ' + '; '.join(
            f'"{r.term}" {int(r.orders)} orders, ACoS {fp(r.acos, 2)}' for r in near.itertuples()) + '. Keep them running where they convert; '
            'harvest once they drop below the threshold.')
        W('')
    if len(asin_win):
        aw = asin_win.sort_values('orders', ascending=False)
        aw_pass, aw_fail = aw[aw.acos < harvest_acos], aw[aw.acos >= harvest_acos]
        W('Product pages (ASIN search terms) with >= 2 orders, for product targeting rather than Exact keywords. Pass: ' + '; '.join(
            f'{r.term.upper()} ({r.owner}) {int(r.orders)} orders / {fm(r.spend)} / ACoS {fp(r.acos)}' for r in aw_pass.itertuples())
            + '. Above the threshold: ' + ('; '.join(f'{r.term.upper()} ({r.owner}) {int(r.orders)} orders / {fm(r.spend)} / ACoS {fp(r.acos)}'
                                                      for r in aw_fail.itertuples()) or 'none')
            + '. ILLUCO\'s own pages convert cheaply (shoppers on one ILLUCO page buy another ILLUCO item); the $9.88 ffresiss LED mirror page does not pay.')
        W('')

    # ---- e
    W(f'## e. Targeting report insights ({d(tg_start)} - {d(tg_end)})')
    W('')
    W(mg_table)
    W('')
    W(f'**Targets with spend >= $5 or orders > 0** (verdict: Keep = ACoS <= {fp(harvest_acos)}; Cut = ACoS >= 50%; Pause = 0 orders on '
      f'>= $8; Brand-driven = brand searches are >= 50% of the target\'s search-term sales, so its ACoS hides the non-brand cost)')
    W('')
    W(tgt_table)
    W('')
    dm_heads = tg[(tg.code == 'HEADS-KW') & (tg.target == 'dental mirror') & (tg.match == 'PHRASE')].iloc[0]
    dm_brand = tg[(tg.code == 'BRAND-KW') & (tg.target == 'dental mirror') & (tg.match == 'PHRASE')].iloc[0]
    cat_t = tg[tg.code == 'CATEGORY'].iloc[0]
    W(f'- **Converting:** "dental mirror" phrase (HEADS-KW {fi(dm_heads.orders)} orders, BRAND-KW {fi(dm_brand.orders)}), the CATEGORY target '
      f'({fi(cat_t.orders)} orders, CVR {fp(div(cat_t.orders, cat_t.clicks))}, CPC {fm(cat_t.cpc)}), AUTO-1PK substitutes, and the '
      'cheap brand keywords ("illuco" broad/phrase). Much of the "dental mirror" phrase revenue is brand queries (see the brand-share column).')
    def leak_share(k):
        x = st[(st.code == k[0]) & (st.target == k[1]) & (st.match == k[2])]
        return div(x[x.cls.isin(CONSUMER_CLASSES + IRRELEVANT_CLASSES)].spend.sum(), x.spend.sum())
    W(f'- **Wasting:** BRAND-KW "dental" phrase ({fm(pause_tg[pause_kw[0]].spend)}, ACoS {fp(div(pause_tg[pause_kw[0]].spend, pause_tg[pause_kw[0]].sales))}; '
      f'{fp(leak_share(pause_kw[0]), 0)} of its search-term spend was off-category/consumer) and "dental tools home use" broad '
      f'({fm(pause_tg[pause_kw[1]].spend)}, ACoS {fp(div(pause_tg[pause_kw[1]].spend, pause_tg[pause_kw[1]].sales))}; {fp(leak_share(pause_kw[1]), 0)} '
      'off-category/consumer/rhodium, the rest generic mirror queries that "dental mirror" phrase already covers); "dental hygienist must haves" exact '
      'has 0 orders; DERM "dermatoscope" exact carries the DERM campaign\'s cost.')
    W(f'- **Top-of-search impression share is low everywhere:** {fp(dm_heads.tos_is, 2)} on HEADS-KW "dental mirror" phrase, '
      f'{fp(dm_brand.tos_is, 2)} on BRAND-KW "dental mirror" phrase, {fp(d_exact.tos_is, 2)} on DERM "dermatoscope" exact, '
      f'{fp(cat_t.tos_is, 2)} on the category target. Brand keywords reach {fp(tg[(tg.code == "BRAND-KW") & (tg.target == "illuco") & (tg.match == "BROAD")].tos_is.iloc[0], 1)} '
      '- 25%. With budgets on hold, do not chase top-of-search on generic terms (shoppers there buy $5-10 mirrors); the one place to '
      'pay for it is brand Exact, funded by the cuts below.')
    W(f'- Auto campaigns: "substitutes" (product pages) is where auto spend goes; close/loose match produce few clicks. '
      f'{len(zero_click_kw)} keyword targets had zero clicks in 90 days (mostly DERM long-tail and BRAND-KW variants): harmless, but they clutter the account.')
    W('')

    # ---- f
    W('## f. Dermatoscope campaign (DERM): verdict')
    W('')
    o_d = sqp_oct.loc['dermatoscope']
    q_d = sqp_q3.loc['dermatoscope']
    W(md_table([
        [f'Campaign report ({d(c_start)} - {d(c_end)})', fm(dc.spend), fi(dc.clicks), fi(dc.orders), fm(dc.sales), fp(div(dc.spend, dc.sales)),
         fp(div(dc.orders, dc.clicks), 2), fm(div(dc.spend, dc.clicks))],
        ['"dermatoscope" Exact keyword (targeting report, 90 days)', fm(d_exact.spend), fi(d_exact.clicks), fi(d_exact.orders), fm(d_exact.sales),
         fp(div(d_exact.spend, d_exact.sales)), fp(d_cvr, 2), fm(d_exact.cpc)],
        ['All other DERM targets (targeting report)', fm(dt.spend.sum() - d_exact.spend), fi(dt.clicks.sum() - d_exact.clicks),
         fi(dt.orders.sum() - d_exact.orders), fm(dt.sales.sum() - d_exact.sales),
         fp(div(dt.spend.sum() - d_exact.spend, dt.sales.sum() - d_exact.sales)), fp(div(dt.orders.sum() - d_exact.orders, dt.clicks.sum() - d_exact.clicks), 2),
         fm(div(dt.spend.sum() - d_exact.spend, dt.clicks.sum() - d_exact.clicks))],
    ], ['Slice', 'Spend', 'Clicks', 'Orders', 'Sales', 'ACoS', 'CVR', 'CPC'], 'lrrrrrrr'))
    W('')
    W(f'**Verdict: keep it, but shrink it to what converts.** It is the only paid presence for a $430-1,600 line, yet as run it '
      f'returns {fm(div(dc.sales, dc.spend))} in sales per $1 of spend (ACoS {fp(div(dc.spend, dc.sales))}, the worst in the account).')
    W('')
    W(f'- One keyword is the problem: "dermatoscope" Exact took {fp(d_exact.spend / dt.spend.sum(), 0)} of DERM spend at {fm(d_exact.cpc)} CPC '
      f'(top-of-search share {fp(d_exact.tos_is, 2)}). At its observed CVR ({fi(d_exact.orders)}/{fi(d_exact.clicks)} = {fp(d_cvr, 2)}) and the '
      f'{fm(d_aov, 0)} order, the CPC that yields a given ACoS is AOV x CVR x ACoS: {fm(d_aov * d_cvr * 0.20)} for 20%, '
      f'{fm(d_aov * d_cvr * 0.30)} for 30%, {fm(d_aov * d_cvr * 0.40)} for 40%. Cut the bid to that range (target ACoS is the owner\'s call; '
      'the CVR rests on a single order, so treat it as rough).')
    W(f'- In the search-term window DERM spent {fm(d_st_spend)} = {fm(d_st_spend / st_days)}/day against a $10 budget '
      f'({fp(d_st_spend / st_days / 10, 0)} on average), so it is likely capped on many days: the only campaign where budget binds. Lowering the '
      'exact bid frees budget for the brand/model and long-tail terms without raising the cap.')
    W(f'- The market buys cheap units on generic searches. SQP "dermatoscope": Oct {fi(o_d.volume)} searches, ILLUCO click share {fsp(o_d.click_share)}, '
      f'purchase share {fsp(o_d.purch_share)} ({int(o_d.purch_brand)} of {int(o_d.purch_total)}), market median purchase price {fm(o_d.mkt_purch_price)} vs '
      f'ILLUCO {fm(o_d.brand_click_price, 0)}; Q3 {int(q_d.purch_brand)} of {int(q_d.purch_total)} purchases (median {fm(q_d.mkt_purch_price)}). '
      f'ILLUCO click share rose from {fsp(sqp_sep.loc["dermatoscope"].click_share)} (Sep) to {fsp(o_d.click_share)} (Oct). '
      f'SQP counts {int(o_d.purch_brand)} ILLUCO purchases from this query in October alone against {fi(d_exact.orders)} ad-attributed order in 90 days: '
      'buyers reach ILLUCO organically and/or buy outside the 7-day ad window, so the keyword\'s true return is uncertain. '
      'That argues for a lower bid, not for pausing.')
    d_phrase = dt[(dt.target == 'dermatoscope') & (dt.match.isin(['PHRASE', 'BROAD']))]
    d_rest = dt.drop(index=d_exact.name)
    W(f'- The rest of DERM is cheaper than it looks: all other targets ran at {fm(div(d_rest.spend.sum(), d_rest.clicks.sum()))} CPC and '
      f'{fp(div(d_rest.spend.sum(), d_rest.sales.sum()))} ACoS. "dermatoscope" phrase + broad ({fm(d_phrase.spend.sum())}, {fi(d_phrase.clicks.sum())} clicks, '
      f'{fi(d_phrase.orders.sum())} orders in 90 days) are already under the cap; {fi(d_phrase.clicks.sum())} clicks without an order is within what a '
      f'{fp(d_cvr, 2)} CVR predicts (~{d_phrase.clicks.sum() * d_cvr:.1f} orders), so the data cannot condemn them. Keep every DERM bid at or below '
      f'~{fm(d_aov * d_cvr * 0.30)} and trim off-target matches with negatives instead of pausing.')
    W(f'- Negate non-dermatoscope traffic ({fm(d_off.spend.sum())} in the window: '
      + ', '.join(f'"{t}"' for t in d_off.sort_values('spend', ascending=False).term.head(5)) + '). Pause the odd keyword '
      '"dermatoscope otoscopes & ophthalmoscopes" (broad) and the phone-attachment keywords ("dermatoscope iphone", "smartphone dermatoscope", '
      '"dermatoscope for smart phone", "dermatoscope attachment for iphone"): ILLUCO units are handheld.')
    W(f'- {len(derm_kw_zero)} of {len(dt)} DERM targets had zero clicks in 90 days. The one non-brand long-tail winner was "dermatology equipment" broad '
      f'(1 order, {fm(dt[(dt.target == "dermatology equipment") & (dt.match == "BROAD")].sales.iloc[0], 0)}). Keep brand/model terms ("illuco dermatoscope", '
      '"illuco ids-1100 dermatoscope") and cheap synonyms ("dermascope", "dermoscope", "dermatoscopio" at ~$0.70 CPC) running.')
    W(f'- Business Report (window not stated): dermatoscopes {fi(derm_br["Units Ordered"])} units / {fm(derm_br["Ordered Product Sales"], 0)} on '
      f'{fi(derm_br["Sessions - Total"])} sessions vs {fi(dc.orders)} ad-attributed orders in {c_days} days, so most dermatoscope revenue appears to arrive '
      'without an attributed ad click (approximate: the windows differ). The listings sit in Home Decor / Automotive browse nodes '
      '(`listings/Existing_Listings_Update_Sheet.xlsx`, Attribute Fixes): fixing categorization is cheaper than buying relevance with bids.')
    W('')

    # ---- g
    W('## g. Recommended changes that need no budget increase')
    W('')
    pk = pause_stats
    n_asin_rows = int((negdf.match_type == 'negative product target (ASIN)').sum())
    n_asin_unique = negdf[negdf.match_type == 'negative product target (ASIN)'].keyword.nunique()
    bk_spend_day = st_camp.spend.get('BRAND-KW', 0) / st_days
    comp_pages = bsplit.loc['Competitor product pages (ASINs)']
    W(md_table([
        ['1', 'Pause BRAND-KW keyword "dental" (phrase)', f'{fm(pk[pause_kw[0]].spend)} / {fi(pk[pause_kw[0]].orders)} orders / {fm(pk[pause_kw[0]].sales)}',
         f'{fp(leak_share(pause_kw[0]), 0)} of its search-term spend went to off-category/consumer searches (handpieces, loupes, drills, materials)'],
        ['2', 'Pause BRAND-KW keyword "dental tools home use" (broad)', f'{fm(pk[pause_kw[1]].spend)} / {fi(pk[pause_kw[1]].orders)} orders / {fm(pk[pause_kw[1]].sales)}',
         f'Consumer intent; {fp(leak_share(pause_kw[1]), 0)} off-category/consumer/rhodium, the rest is covered by "dental mirror" phrase'],
        ['3', 'Pause BRAND-KW "dental hygienist must haves" (exact)', f'{fm(pk[pause_kw[2]].spend)} / {fi(pk[pause_kw[2]].orders)} orders',
         'Gift-list query, 0 orders'],
        ['4', 'Upload `negative_keywords.csv`', f'{len(negdf)} rows ({n_preventive} preventive, 0 spend so far): '
         + ', '.join(f'{v} {k}' for k, v in negdf.match_type.value_counts().items()),
         f'Consumer modifiers, rhodium, off-category words, wasted terms, harvest routing, {n_asin_unique} ASINs ({n_asin_rows} rows)'],
        ['5', f'DERM: cut "dermatoscope" exact bid from {fm(d_exact.cpc)} to ~{fm(d_aov * d_cvr * 0.30)} (30% ACoS at observed CVR) and keep every '
         'other DERM bid under that cap; pause "dermatoscope otoscopes & ophthalmoscopes" and the phone-attachment keywords',
         f'{fm(d_exact.spend)} on the exact keyword in 90 days for {fi(d_exact.orders)} order; the other targets ran at '
         f'{fp(div(d_rest.spend.sum(), d_rest.sales.sum()))} ACoS', 'See section f'],
        ['6', 'Add an Exact ad group inside BRAND-KW (advertising the single mirror) with the non-brand winners from `harvest_keywords.csv`; '
         'negative-exact them where they bleed (routing rows in the negatives file)',
         f'{len(hv[~hv.term.str.contains(RX_BRAND)])} non-brand terms, {fi(hv[~hv.term.str.contains(RX_BRAND)].orders.sum())} orders',
         f'Uses BRAND-KW\'s existing $30/day (it spends {fm(bk_spend_day)}/day, less after items 1-3); stops 3-4 campaigns bidding on the same query'],
        ['7', 'Add a Brand Exact ad group inside BRAND-KW (all mirror ASINs): "illuco dental mirror", "illuco dental mirrors", "illuco", "illuco mirror", '
         'model codes; the existing "illuco" Exact keywords served 1 impression each in 90 days, so check they are enabled and bid at least as high as '
         'the broad/phrase versions; once live, add "illuco" as negative phrase in HEADS-KW and CATEGORY',
         f'Brand terms: {fm(brand_b.spend)} spend, {fm(brand_b.sales)} sales, ACoS {fp(div(brand_b.spend, brand_b.sales))}',
         'Cheap; makes non-brand ACoS visible; brand top-of-search share is only 20-25%'],
        ['8', 'Route generic mirror queries to the single mirror: keep "dental mirror", "dental mirror for teeth" and fog terms in CATEGORY/AUTO-1PK; '
         'negative-exact them in HEADS-KW and BRAND-KW', 'Routing rows in `negative_keywords.csv`',
         'Generic shoppers buy the $19.99 single (CATEGORY AOV $24), not $60-140 packs'],
        ['9', 'Optional, budget-neutral: if you prefer separate campaigns for items 6-7, fund them by lowering AUTO-1PK and AUTO-HEADS budgets '
         'by the same amount', f'AUTO-1PK spends {fm(st_camp.spend.get("AUTO-1PK", 0) / st_days)}/day of $20; AUTO-HEADS '
         f'{fm(st_camp.spend.get("AUTO-HEADS", 0) / st_days)}/day of $20', f'Account total stays at {fm(enabled_budget, 0)}/day enabled'],
        ['10', 'Keep AUTO-5PK and AUTO-LEGACY paused', 'Their $45/day of budget stays idle', '0 orders in the targeting window (Aug 23 on)'],
        ['11', 'CATEGORY: apply the negative product targets and consumer negatives; review competitor-ASIN placements monthly',
         f'Competitor product pages: {fm(comp_pages.spend)} spend, {fi(comp_pages.orders)} orders, ACoS {fp(div(comp_pages.spend, comp_pages.sales))}',
         f'Clicks are spread thin (1-2 per ASIN); only {n_asin_unique} ASINs meet the waste rule so far'],
    ], ['#', 'Change', 'Evidence (spend / orders / sales)', 'Why'], 'rlll'))
    W('')
    W(f'Estimated effect on {d(st_start)} - {d(st_end)}: items 1-4 would have blocked {fm(blk_tot.spend)} of spend '
      f'({fp(blk_tot.spend / st_tot.spend)}; ' + ', '.join(f'{k}: {fm(v.spend)}' for k, v in blk_by.iterrows()) +
      f') and {fi(blk_tot.orders)} orders / {fm(blk_tot.sales)} sales (ACoS of the blocked traffic {fp(div(blk_tot.spend, blk_tot.sales))}). '
      'Hold the freed money inside the existing budgets; let the harvested Exact and brand ad groups absorb it through bids.')
    W('')
    W('**Largest negatives by spend they would have blocked** (all campaigns summed; full list in `negative_keywords.csv`)')
    W('')
    W(md_table([[r.keyword, r.match_type, r.camps, fm(r.spend), fi(r.clicks), fi(r.orders)] for r in neg_top.head(10).itertuples()],
               ['Negative', 'Match type', 'Campaigns', f'Spend {st_start:%b %-d}-{st_end:%b %-d}', 'Clicks', 'Orders'], 'lllrrr'))
    W('')
    W('Negative phrase rows are written per campaign (each campaign has one ad group, so campaign- and ad-group-level negatives are '
      'equivalent today). ASIN rows go in as negative product targets. "Preventive" rows have no spend yet; they cover consumer '
      'modifiers (LED, kids, disposable, picks/plaque, hand/makeup/telescoping mirrors) so auto and category targeting cannot drift into them.')
    W('')
    W('Not recommended now: new Sponsored Brands/DSP (owner has no budget for them), raising any campaign budget, or chasing '
      'top-of-search on "dental mirror" (market median purchase price is under $10).')
    W('')

    # ---- SQP
    W('## Search Query Performance (Brand Analytics, Brand View)')
    W('')
    W(f'Windows: Oct 2026 (latest month), Q3 2026 (Jul 1 - Sep 30), Sep 2026 for trend. Brand totals: ILLUCO had '
      f'{fi(oct_df.impr_brand.sum())} impressions / {fi(oct_df.clicks_brand.sum())} clicks / {fi(oct_df.purch_brand.sum())} purchases across '
      f'{len(oct_df)} Oct queries, and {fi(q3_df.impr_brand.sum())} / {fi(q3_df.clicks_brand.sum())} / {fi(q3_df.purch_brand.sum())} across {len(q3_df)} Q3 queries.')
    W('')
    W(f'**Top 30 queries by search volume, Oct 2026 and Q3 2026 (union, {len(union)} queries)**. {n_off_top} of them are off-category '
      '(hand mirrors, headlamps, generic dental shopping) where ILLUCO only got stray impressions.')
    W('')
    W(sqp_top_table)
    W('')
    W(f'**Queries where ILLUCO wins purchases** (any ILLUCO purchase in Oct or Q3; purchase share > click share means the listing '
      'converts better than the page average once clicked)')
    W('')
    W(sqp_win_table)
    W('')
    if win_small:
        W(f'Plus {len(win_small)} one-off queries (under 10 searches in Oct and under 25 in Q3) with an ILLUCO purchase: '
          + ', '.join(f'"{q}"' for q in win_small) + '.')
        W('')
    dm_o, dm_s, dm_q = sqp_oct.loc['dental mirror'], sqp_sep.loc['dental mirror'], sqp_q3.loc['dental mirror']
    idm_o, idm_q = sqp_oct.loc['illuco dental mirror'], sqp_q3.loc['illuco dental mirror']
    W(f'- Brand: on "illuco dental mirror" ({fi(idm_o.volume)} searches in Oct, {fi(idm_q.volume)} in Q3) ILLUCO gets {fsp(idm_o.click_share, 0)} of clicks '
      f'(Oct; {fsp(idm_q.click_share, 0)} in Q3) and {fsp(idm_o.purch_share, 0)} of purchases; the remaining clicks go to other brands\' listings. '
      'Defend it cheaply on Exact.')
    W(f'- Non-brand wins are few and small (anti-fog / no-fog / fog-free, front surface, professional, Zirc and Hu-Friedy queries), but in '
      f'{nb_over} of the {nb_wins} non-brand query/period pairs where ILLUCO made a sale, its purchase share beat its click share: '
      'ILLUCO converts premium-intent shoppers once they click.')
    W(f'- "dental mirror": {fi(dm_o.volume)} searches in Oct, ILLUCO click share {fsp(dm_s.click_share)} (Sep) -> {fsp(dm_o.click_share)} (Oct), '
      f'purchase share {fsp(dm_o.purch_share)}; market median purchase price {fm(dm_o.mkt_purch_price)} vs ILLUCO {fm(dm_o.brand_click_price)}. '
      'Volume is there but buyers are price-driven; win it organically (title/backend, reviews) and with the single mirror, not with bids.')
    W('- SQP purchases are attributed to the query by Amazon and are not comparable 1:1 with 7-day ad-attributed orders.')
    W('')
    W(f'**Gaps: relevant queries with real volume and ILLUCO click share < {GAP_SHARE:.0f}%** (Oct volume >= {GAP_VOL["2026-10"]}). '
      '"Copy" checks whether every word of the query already appears in the current title (dermatoscope, photo) or in the proposed '
      'title/highlight/bullets/backend in `listings/Existing_Listings_Update_Sheet.xlsx` (mirror families). "PPC" uses the ad '
      f'search-term results for the same query ({d(st_start)} - {d(st_end)}).')
    W('')
    W(sqp_gap_table)
    W('')
    if len(gap_q3_rows):
        W(f'Additional Q3-only gaps (Q3 volume >= {GAP_VOL["2026-Q3"]}, not in the Oct list):')
        W('')
        W(sqp_gap_q3_table)
        W('')
    W('**Titles/backend vs PPC** (all relevant gap queries from both tables, grouped by the two columns above)')
    W('')
    gap_all = sqp_out[sqp_out.relevant_gap].drop_duplicates('search_query')      # Oct row first, Q3-only rows after

    def qlist(mask):
        return ', '.join(f'"{q}"' for q in gap_all[mask].search_query) or '-'
    cp, pp = gap_all.copy_placement, gap_all.ppc_recommendation
    buckets = [
        ['Title: already there', qlist(cp == 'In current title'), 'Rank organically; no extra bids on the head term beyond the harvested Exact'],
        ['Title candidates: in proposed backend only, high volume', qlist(cp.str.startswith('In proposed backend/bullets; title')),
         'Add the missing words to titles/bullets (e.g. "Mouth Mirror") for rank weight'],
        ['Backend: already in proposed copy', qlist(cp == 'In proposed backend/bullets'), 'Nothing to add'],
        ['Backend: add', qlist(cp.str.startswith(('Missing from proposed copy', 'Not in title'))),
         'Synonyms, sizes, Spanish and dermatoscope variants (dermatoscope backend is not in the repo, so check it first)'],
        ['Competitor brand: PPC only', qlist(cp.str.startswith('Not for copy (competitor')),
         'Brand names of others are not allowed in ILLUCO copy; test as Exact at a capped bid'],
        ['PPC Exact: proven (harvest)', qlist(pp.str.startswith('Exact: harvest') | pp.str.startswith('Near-miss')), '`harvest_keywords.csv` + near-misses'],
        ['PPC Exact: test at a capped bid', qlist(pp.str.startswith(('Test Exact', 'Already Exact'))), 'Had ad orders but not enough to harvest'],
        ['PPC: keep at a low bid (DERM)', qlist(pp.str.startswith('Keep at a low bid')),
         f'Cheap dermatoscope variants; keep each bid under the ~{fm(derm_cap)} DERM cap'],
        ['PPC: organic only', qlist(pp.str.startswith('No:')), 'Already paid for clicks without an order'],
        ['PPC: watch / optional test', qlist(pp.str.startswith(('Watch', 'Optional'))), 'Too little ad data; low-bid Exact test only if budget frees up'],
    ]
    W(md_table([b for b in buckets if b[1] != '-'], ['Placement', 'Gap queries', 'Action'], 'lll'))
    W('')
    W('- **Neither (negative):** LED/lighted, disposable, kids and rhodium queries (e.g. "dental mirror with light" '
      f'{fi(kq("dental mirror with light", octi, "volume"))} Oct searches, "dental mirror for teeth with light" {fi(kq("dental mirror for teeth with light", octi, "volume"))}, '
      f'"lighted dental mirror" {fi(kq("lighted dental mirror", octi, "volume"))}) and the off-category top-volume queries (hand mirror, inspection mirror, headlamp, dental tools).')
    W(f'- Spanish queries show ILLUCO impressions in SQP (e.g. "espejo dental" {fsp(kq("espejo dental", octi, "impr_share"))} impression share in Oct), '
      f'but Spanish ad clicks converted 0 times ({spanish.term.nunique()} terms, {fm(spanish_stats.spend)}): backend, not PPC.')
    W(f'- **Anti-fog caution:** fog queries are among ILLUCO\'s most consistent non-brand converters in both ads ({fi(fog_tot.orders)} orders) and SQP, but {fog_returns} of the {n_returns} FBA '
      f'return records in `293310020777.csv` ({ret_window}) carry customer comments that the mirror fogged or did not stay dry, and the proposed '
      'listing copy removes "Fog-Resistant". Decide the claim '
      'first; if it goes, drop fog terms from PPC rather than scale them.')
    W('- Dermatoscope titles use "Dermatoscope" (and "Woods Lamp" on the IDS-3100) but none of the variants; put "dermascope", "dermoscope", '
      '"dermoscopy", "dermatoscopio" and "lampara de wood" in the backend. Market median purchase prices of $50-160 on these queries mean generic '
      'dermatoscope PPC should stay bid-capped.')
    W('')

    # ---- BR context
    W('## Business Report context (window not stated in the export)')
    W('')
    W(br_table)
    W('')
    W('- Replacement heads and the single mirror convert well (heads 1X '
      f'{fp(div(br[br["(Child) ASIN"] == "B0FBPG5CS9"]["Units Ordered"].sum(), br[br["(Child) ASIN"] == "B0FBPG5CS9"]["Sessions - Total"].sum()))}, '
      f'single B0G2DYRY7T {fp(div(br[br["(Child) ASIN"] == "B0G2DYRY7T"]["Units Ordered"].sum(), br[br["(Child) ASIN"] == "B0G2DYRY7T"]["Sessions - Total"].sum()))} unit session %). '
      'The 5-pack with handles converts poorly (' + ', '.join(f'{r["(Child) ASIN"]} {fp(div(r["Units Ordered"], r["Sessions - Total"]))}' for _, r in kit_rows.head(3).iterrows())
      + '), so pushing more paid clicks to the 5-pack pages is the most expensive way to grow; fix that listing first.')
    W('- The Business Report and ad reports cover different (and, for the Business Report, unknown) windows, so no TACoS is computed.')
    W('')
    W('## Files')
    W('')
    W('- `analysis/ppc_audit.md` (this report)')
    W(f'- `analysis/negative_keywords.csv` ({len(negdf)} rows; ASIN rows use match_type "negative product target (ASIN)" because Amazon blocks ASINs with negative product targeting, not negative keywords)')
    W(f'- `analysis/harvest_keywords.csv` ({len(hcsv)} rows; extra `notes` column)')
    W(f'- `analysis/sqp_top_queries.csv` ({len(sqp_out)} rows: top 30 by volume, ILLUCO purchase wins and relevant gaps for Oct 2026 and Q3 2026)')
    W('- `scripts/ppc_sqp_audit.py` regenerates all four: `python3 -I scripts/ppc_sqp_audit.py`')
    W('')
    (OUT / 'ppc_audit.md').write_text('\n'.join(md), encoding='utf-8')

    # console summary for the operator
    print(f'campaign: spend {tot.spend:.2f} sales {tot.sales:.2f} orders {tot.orders:.0f} acos {acct_acos:.4f}')
    print(f'search terms: spend {st_tot.spend:.2f} sales {st_tot.sales:.2f} acos {st_acos:.4f} harvest threshold {harvest_acos:.4f}')
    print(f'wasted (camp/ag/term): {w_cat.spend.sum():.2f} ({w_cat.spend.sum() / st_tot.spend:.4f}) rows {len(w_cat)}; term-level {w_term.spend.sum():.2f}')
    print(f'leakage consumer {leak_tot["consumer"][3]:.2f} irrelevant {leak_tot["irrelevant"][3]:.2f}')
    print(f'negatives {len(negdf)}; harvest {len(hcsv)}; sqp rows {len(sqp_out)}; blocked {blk_tot.spend:.2f}')


if __name__ == '__main__':
    main()
