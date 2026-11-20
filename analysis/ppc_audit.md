# ILLUCO Amazon Sponsored Products and Search Query Performance audit

Prepared 2026-11-20 by `scripts/ppc_sqp_audit.py` from the exports in `data/account/` (read-only). Analysis only: the owner has put budget increases on hold, so every recommendation below cuts, negates, harvests or re-routes within the current budgets. Nothing here raises a budget.

## Data windows and definitions

| Source | File | Window | Grain |
|---|---|---|---|
| SP campaign report | `CHECK-_ILLUCO_3.csv` | Aug 1, 2026 - Nov 20, 2026 (112 days); paused campaigns end on their last active day | 1 row per campaign (8) |
| SP search term report | `CHECK-_ILLUCO_1.xlsx` | Sep 17, 2026 - Nov 20, 2026 (65 days) | 720 rows, one per campaign / ad group / target / match type / search term; Start/End = first/last active day (566 rows are single-day). Aggregated by campaign + ad group + term and by term overall |
| SP targeting report | `CHECK-_ILLUCO_2.xlsx` | Aug 23, 2026 - Nov 20, 2026 (90 days) | 119 targets |
| Brand Analytics SQP (Brand View) | `SQP_Brand_Month_2026_10_31.csv` (latest month), `SQP_Brand_Quarter_2026_09_30.csv`, `SQP_Brand_Month_2026_09_30.csv` | Oct 2026; Q3 2026 (Jul 1 - Sep 30); Sep 2026 | 501 / 726 / 381 queries; first line is a metadata row, skipped |
| Business Report (child ASIN) | `BusinessReport-11-20-26.csv` | Not stated in the export (file dated 11/20/26) | 32 child-ASIN rows; context only |

- Orders = `7 Day Total Orders (#)`, Sales = `7 Day Total Sales` (7-day attribution, includes other-SKU "halo" sales: $2,183.30 = 37.8% of search-term sales). ACoS = spend / sales, ROAS = sales / spend, CTR = clicks / impressions, CVR = orders / clicks, AOV = sales / orders. All ratios are recomputed from the sums, not averaged.
- The three ad reports cover different windows, so their totals differ (spend: campaign $3,059.11, targeting $2,794.85, search terms $2,282.12). Search-term sections use the Sep 17, 2026 - Nov 20, 2026 window only.
- Account average ACoS: 36.4% (campaign report, 112 days) and 39.5% (search-term report, same window as the terms). Harvest and keep/cut tests use the stricter 36.4%.
- Brand terms = search terms containing "illuco" (incl. misspellings "ulluco", "illuc") or an ILLUCO model code (IDM, IDS-xxxx).
- SQP share columns are already percentages in the export (0.60 means 0.60%). Top-of-search impression share in the targeting report is a fraction, shown here as a percentage.

## Headline

- **Campaign report (Aug 1, 2026 - Nov 20, 2026): $3,059.11 spend, $8,400.02 sales, 129 orders, ACoS 36.4%, ROAS 2.75.** Budgets are not the constraint: in the last 65 days the account spent $35.11/day against $125/day of enabled budgets (28%); only DERM runs near its cap.
- **Brand searches flatter the account.** Brand/model terms took 4.3% of search-term spend but 37.2% of sales (ACoS 4.6%). Everything else ran at ACoS 60.2%.
- **Wasted spend (8+ clicks or $8+ and 0 orders): $298.91 (13.1% of $2,282.12)** across 22 campaign/ad-group/term rows. Counting every zero-order term regardless of size: $1,399.39 (61.3%).
- **Consumer + irrelevant leakage: $510.03 (22.3% of spend)** for 7 orders / $532.96. 55% of it entered through two BRAND-KW keywords: "dental" (phrase) and "dental tools home use" (broad).
- **DERM: $739.55 for 2 orders (ACoS 53.6%).** 75% of its targeting-report spend is one Exact keyword ("dermatoscope") at $2.31 CPC with 1 order in 224 clicks.
- Recommended pauses + negatives would have removed **$638.67 (28.0%)** of Sep 17, 2026 - Nov 20, 2026 spend while putting $585.00 of sales (4 orders) at risk; part of that demand re-routes to the campaigns where the same terms convert.

## a. Campaign summary (Aug 1, 2026 - Nov 20, 2026)

| Campaign | Status | Budget/day | Impr. | Clicks | CTR | Spend | CPC | Orders | CVR | Sales | ACoS | ROAS | Avg spend/day (report window) | Avg spend/day Sep 17-Nov 20 (% of budget) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **BRAND-KW** | ENABLED | $30 | 172,477 | 625 | 0.36% | $910.17 | $1.46 | 23 | 3.7% | $2,559.99 | 35.6% | 2.81 | $8.13 | $10.25 (34%) |
| **DERM** | ENABLED | $10 | 53,722 | 485 | 0.90% | $739.55 | $1.52 | 2 | 0.4% | $1,380.00 | 53.6% | 1.87 | $6.60 | $9.65 (96%) |
| **CATEGORY** | ENABLED | $25 | 68,408 | 555 | 0.81% | $605.29 | $1.09 | 61 | 11.0% | $1,463.06 | 41.4% | 2.42 | $5.40 | $7.61 (30%) |
| **HEADS-KW** | ENABLED | $20 | 81,600 | 252 | 0.31% | $498.69 | $1.98 | 18 | 7.1% | $1,999.99 | 24.9% | 4.01 | $4.45 | $4.86 (24%) |
| **AUTO-1PK** | ENABLED | $20 | 32,607 | 165 | 0.51% | $161.00 | $0.98 | 20 | 12.1% | $566.98 | 28.4% | 3.52 | $1.44 | $1.88 (9%) |
| **AUTO-5PK** | PAUSED (last day Oct 16, 2026) | $20 | 28,944 | 82 | 0.28% | $91.24 | $1.11 | 2 | 2.4% | $220.00 | 41.5% | 2.41 | $1.18 | $1.07 (5%) |
| **AUTO-HEADS** | ENABLED | $20 | 17,705 | 40 | 0.23% | $42.66 | $1.07 | 3 | 7.5% | $210.00 | 20.3% | 4.92 | $0.38 | $0.30 (1%) |
| **AUTO-LEGACY** | PAUSED (last day Oct 12, 2026) | $25 | 2,224 | 8 | 0.36% | $10.51 | $1.31 | 0 | 0.0% | $0.00 | - | 0.00 | $0.14 | $0.17 (1%) |
| **Total** | 6 enabled / 2 paused | $170 ($125 enabled) | 457,687 | 2,212 | 0.48% | $3,059.11 | $1.38 | 129 | 5.8% | $8,400.02 | 36.4% | 2.75 | $27.31 | $35.11 (28%) |

| Code | Campaign name (as exported) | What it targets (from names and targets) |
|---|---|---|
| **BRAND-KW** | VIC-M-SP-Dental Mirror Branded and Product KW | Manual keywords: brand + generic (illuco, dental, dental mirror, dental tools home use) |
| **HEADS-KW** | VIC-BOF \| SP \| Dental Mirror HEAD 1x 2x 3x \| SP Exact Target + Prod Exp + Brand Exp | Manual keywords for replacement heads; spend is almost all "dental mirror" phrase |
| **CATEGORY** | VIC-M- SP \| Dental Mirror Category \| Dental Mirror \| All Single Multipack | Manual category target category="Dental Mirrors" (singles + multipacks) |
| **AUTO-1PK** | VIC-SP-AUTO-DTMR-1PK-ALL | Auto: single mirror with handle |
| **AUTO-HEADS** | VIC-SP-AUTO-MRHD-5PK-ALL | Auto: replacement heads 5-pack |
| **AUTO-5PK** | VIC-SP-AUTO-DTMR-5PK-AB | Auto: 5-pack with handles |
| **AUTO-LEGACY** | VIC-SP Auto Dental Mirror Substitutes and Close Match | Auto: legacy substitutes/close match |
| **DERM** | SP-Dermatoscope-KWs-All | Manual keywords: dermatoscopes |

- **Paused:** AUTO-5PK (paused, last active Oct 16, 2026; $91.24 spend, 2 orders, ACoS 41.5%), AUTO-LEGACY (paused, last active Oct 12, 2026; $10.51 spend, 0 orders, ACoS -). Their $45/day of budget is idle. Keep them paused.
- Highest ACoS among enabled campaigns: DERM 53.6%, CATEGORY 41.4%, BRAND-KW 35.6%. CATEGORY has the most orders (61) but a $23.98 AOV: it mostly sells the $19.99-31.90 single mirror.
- The two right-hand columns are averages; actual daily spend varies, and campaign launch dates are not in the export, so the report-window average can understate days when a campaign was live.

**Brand vs non-brand (Sep 17, 2026 - Nov 20, 2026, search-term report)**

| Traffic type | Clicks | Spend | % spend | Orders | Sales | % sales | ACoS | CVR |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Brand / ILLUCO model terms | 86 | $98.90 | 4.3% | 24 | $2,149.93 | 37.2% | 4.6% | 27.9% |
| Non-brand keywords: mirrors | 808 | $1,253.65 | 54.9% | 50 | $2,294.14 | 39.7% | 54.6% | 6.2% |
| Non-brand keywords: dermatoscope | 327 | $618.00 | 27.1% | 1 | $950.00 | 16.4% | 65.1% | 0.3% |
| Own product pages (ILLUCO ASINs) | 82 | $77.93 | 3.4% | 9 | $243.55 | 4.2% | 32.0% | 11.0% |
| Competitor product pages (ASINs) | 208 | $233.64 | 10.2% | 6 | $139.85 | 2.4% | 167.1% | 2.9% |
| **All except brand terms** | 1,425 | $2,183.22 | 95.7% | 66 | $3,627.54 | 62.8% | 60.2% | 4.6% |
| **Total (search-term report)** | 1,511 | $2,282.12 | 100.0% | 90 | $5,777.47 | 100.0% | 39.5% | 6.0% |

- HEADS-KW looks like one of the best campaigns on paper (ACoS 24.9%), but in this window 11 of its 13 orders ($1,184.99 of $1,364.99) came from brand searches it caught through the "dental mirror" phrase keyword. Its non-brand traffic cost $268.82 for 2 orders / $180.00 (ACoS 149.3%).
- BRAND-KW: brand terms $29.13 spend -> $845.00 sales; non-brand $637.24 -> $1,195.00 (ACoS 53.3%).

## b. Wasted spend (Sep 17, 2026 - Nov 20, 2026)

Rule: aggregated across days, a search term with **>= 8 clicks or >= $8 spend and 0 orders**.

| View | Rows | Clicks | Wasted spend | % of $2,282.12 |
|---|---:|---:|---:|---:|
| Campaign + ad group + term (where negatives are applied) | 22 | 174 | $298.91 | 13.1% |
| Term overall (all campaigns summed) | 17 | 151 | $232.46 | 10.2% |
| Union of both views (rows of terms that fail either test) |  |  | $359.07 | 15.7% |
| Context: all zero-order term rows, any size | 629 | 987 | $1,399.39 | 61.3% |

**All 22 wasted rows by spend (campaign + ad group + term)**

| # | Campaign | Search term | Class | Clicks | Spend | Orders in other campaigns | Action |
|---:|---|---|---|---:|---:|---:|---|
| 1 | BRAND-KW | dental mirror | Relevant mirror term | 18 | $31.43 | 10 | Negative exact here; converts in CATEGORY (10) |
| 2 | HEADS-KW | dental mirror | Relevant mirror term | 13 | $29.53 | 10 | Negative exact here; converts in CATEGORY (10) |
| 3 | HEADS-KW | dental mirrors | Relevant mirror term | 11 | $23.79 | 1 | Negative exact here; converts in BRAND-KW (1) |
| 4 | BRAND-KW | dental rhodium mirrors | Rhodium (competing coating) | 12 | $23.49 | 0 | Negate (consumer / irrelevant) |
| 5 | DERM | dermatoscope medical grade | Relevant dermatoscope term | 14 | $19.79 | 0 | Relevant: keep, cut bid / watch (no orders anywhere yet) |
| 6 | BRAND-KW | dental hygienist must haves | Off-category: non-mirror dental / generic | 10 | $16.32 | 0 | Negate (consumer / irrelevant) |
| 7 | CATEGORY | b077t1dwdr | ASIN: other competitor | 14 | $15.72 | 0 | Negative product target |
| 8 | BRAND-KW | dental mirror anti fog | Relevant mirror term | 7 | $13.67 | 2 | Negative exact here; converts in HEADS-KW (1), CATEGORY (1) |
| 9 | HEADS-KW | dental mirror with light | LED / lighted / rechargeable | 6 | $12.91 | 0 | Negate (consumer / irrelevant) |
| 10 | BRAND-KW | dental mirror handles | Relevant mirror term | 5 | $10.06 | 0 | Relevant: keep, cut bid / watch (no orders anywhere yet) |
| 11 | HEADS-KW | dental mirror for teeth | Relevant mirror term | 4 | $9.59 | 5 | Negative exact here; converts in CATEGORY (4), BRAND-KW (1) |
| 12 | HEADS-KW | magnifying dental mirror | Relevant mirror term | 4 | $9.35 | 1 | Negative exact here; converts in CATEGORY (1) |
| 13 | HEADS-KW | zirc dental mirror | Relevant mirror term | 4 | $9.25 | 1 | Negative exact here; converts in BRAND-KW (1) |
| 14 | BRAND-KW | hu friedy dental instruments | Off-category: non-mirror dental / generic | 7 | $8.82 | 0 | Negate (consumer / irrelevant) |
| 15 | BRAND-KW | dental instruments | Off-category: non-mirror dental / generic | 5 | $8.80 | 0 | Negate (consumer / irrelevant) |
| 16 | BRAND-KW | dental rhodium mirror | Rhodium (competing coating) | 4 | $8.58 | 0 | Negate (consumer / irrelevant) |
| 17 | AUTO-1PK | b0dyp3kgtx | ASIN: other competitor | 8 | $8.44 | 0 | Negative product target |
| 18 | CATEGORY | professional dental mirror | Relevant mirror term | 7 | $8.29 | 0 | Relevant: keep, cut bid / watch (no orders anywhere yet) |
| 19 | HEADS-KW | anti-fog dental mirror | Relevant mirror term | 3 | $8.25 | 0 | Relevant: keep, cut bid / watch (no orders anywhere yet) |
| 20 | BRAND-KW | dental materials | Off-category: non-mirror dental / generic | 6 | $8.14 | 0 | Negate (consumer / irrelevant) |
| 21 | HEADS-KW | anti fog dental mirror | Relevant mirror term | 3 | $8.11 | 0 | Relevant: keep, cut bid / watch (no orders anywhere yet) |
| 22 | DERM | dermascope | Relevant dermatoscope term | 9 | $6.58 | 0 | Relevant: keep, cut bid / watch (no orders anywhere yet) |

Wasted rows by action: Negative exact here: 7 rows / $126.61; Negate: 7 rows / $87.06; Relevant: keep, cut bid / watch: 6 rows / $61.08; Negative product target: 2 rows / $24.16.

- "Relevant: keep, cut bid / watch" rows are on-target professional queries (e.g. anti-fog, front surface, dermatoscope long-tail). They are not negated; lower the bid or let the harvested Exact keywords carry them.
- Terms that fail the test only when summed across campaigns (spend spread thin): "magnifying dental mirror for teeth" $9.46 (Relevant mirror term: watch, not negated); "rhodium dental mirror" $9.01 (Rhodium (competing coating), blocked by the phrase negatives).

## c. Consumer / irrelevant leakage (Sep 17, 2026 - Nov 20, 2026)

Each search term is counted once (first matching class). "LED" requires a mirror/teeth context so loupes or curing lights with a light are counted as off-category, not as LED mirrors. "light weight" and "without light" are not treated as light modifiers.

| Group | Class | Terms | Clicks | Spend | % of spend | Orders | Sales | Main campaigns | Examples (spend) |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| Consumer | LED / lighted / rechargeable | 20 | 42 | $66.02 | 2.9% | 1 | $19.99 | CATEGORY, BRAND-KW, HEADS-KW | "dental mirror with light" $22.02, "dental mirror with light and magnification" $4.52, "dental mirror for teeth with light" $4.20, "dental mirrors with light" $4.08 |
| Consumer | Home use | 2 | 6 | $9.59 | 0.4% | 1 | $19.99 | BRAND-KW, CATEGORY | "dental tools for home use" $7.09, "dental mirrors for home use" $2.50 |
| Consumer | Kids / child / classroom | 1 | 1 | $1.77 | 0.1% | 0 | $0.00 | BRAND-KW | "dental mirror for kids" $1.77 |
| Consumer | Disposable / plastic | 5 | 6 | $11.83 | 0.5% | 0 | $0.00 | HEADS-KW, BRAND-KW, CATEGORY | "plastic dental mirror" $5.00, "plastic magnifying dental mirrors" $2.80, "disposable mirrors dental bulk" $1.50, "dental mirror plastic" $1.30 |
| Consumer | Pick sets / plaque / tartar / cleaning | 1 | 1 | $1.84 | 0.1% | 0 | $0.00 | BRAND-KW | "teeth cleaning tools" $1.84 |
| Consumer | Hand / makeup / telescoping / car inspection | 0 | 0 | $0.00 | 0.0% | 0 | $0.00 | - | none in this window |
| Consumer | ASIN: low-price / LED competitor | 10 | 55 | $65.19 | 2.9% | 2 | $47.98 | CATEGORY, AUTO-1PK, AUTO-5PK | "b08gsqwy5s" $31.70, "b00nfg3wmo" $7.57, "b0811szwv7" $6.56, "b0fdwjfmfm" $5.01 |
| Irrelevant | Rhodium (competing coating) | 15 | 39 | $73.50 | 3.2% | 0 | $0.00 | BRAND-KW, HEADS-KW, CATEGORY | "dental rhodium mirrors" $24.76, "dental rhodium mirror" $10.10, "rhodium dental mirror" $9.01, "espejos de rodio dental" $6.12 |
| Irrelevant | Off-category: non-mirror dental / generic | 144 | 208 | $269.78 | 11.8% | 3 | $445.00 | BRAND-KW, CATEGORY, AUTO-5PK | "dental hygienist must haves" $16.32, "hu friedy dental instruments" $12.27, "dental instruments" $8.80, "dental materials" $8.14 |
| Irrelevant | Off-category: not a dermatoscope | 6 | 13 | $9.01 | 0.4% | 0 | $0.00 | DERM | "otoscope with light medical grade" $4.55, "esthetician supplies" $1.46, "loupe" $0.75, "loupes" $0.75 |
| Irrelevant | Phone-attachment dermatoscope | 1 | 1 | $1.50 | 0.1% | 0 | $0.00 | DERM | "dermatoscope for cell phone" $1.50 |
| **Consumer subtotal** |  | 39 | 111 | $156.24 | 6.8% | 4 | $87.96 | 177.6% ACoS |  |
| **Irrelevant subtotal** |  | 166 | 261 | $353.79 | 15.5% | 3 | $445.00 | 79.5% ACoS |  |
| **Consumer + irrelevant** |  |  |  | $510.03 | 22.3% | 7 | $532.96 | 95.7% ACoS |  |

- Where it came from (targeting that matched the leaking terms): BRAND-KW "dental" (phrase) $176.28 = 35%; BRAND-KW "dental tools home use" (broad) $105.26 = 21%; CATEGORY "category="Dental Mirrors"" (auto/category) $94.34 = 18%; HEADS-KW "dental mirror" (phrase) $38.79 = 8%.
- No spend reached telescoping / automotive / mechanic inspection-mirror, makeup or hand-mirror searches in this window, so those negatives are preventive.
- Spanish and other non-English search terms (counted inside the classes above where they fit): 30 terms, 51 clicks, $63.77, 0 orders.
- Not leakage, but consumer-leaning and worth fencing: "teeth/tooth" terms cost $97.90 for 8 orders (ACoS 49.0%); 7 of those orders came through CATEGORY (single mirror). They pay for the $19.99 single, not for 5-packs or heads.
- "fog" terms: $143.40 for 11 orders (ACoS 46.0%): CATEGORY $55.17 / 8 orders; BRAND-KW $52.43 / 0 orders; HEADS-KW $32.96 / 1 order; AUTO-1PK $2.84 / 2 orders. They convert in the single-mirror campaigns and bleed in the 5-pack/heads campaigns.

## d. Winners to harvest into Exact (Sep 17, 2026 - Nov 20, 2026)

Rule: >= 2 orders and ACoS below 36.4% (the lower of the two account averages, so anything under 30% also passes), tested account-wide first, then inside each campaign (a term that wins in one campaign and bleeds in others is harvested from the winning one). Brand terms are listed because they qualify, but they belong in a brand-defense Exact ad group.

| Search term | Main source | Qualifies | Orders | Spend | Sales | ACoS | AOV | Suggested family | Already Exact? |
|---|---|---|---:|---:|---:|---:|---:|---|---|
| illuco dental mirror | HEADS-KW | account-wide | 18 | $75.46 | $1,679.94 | 4.5% | $93.33 | 5-pack kit | no |
| dental mirror | CATEGORY | within CATEGORY only | 10 | $51.08 | $219.81 | 23.2% | $21.98 | single | no |
| illuco | BRAND-KW | account-wide | 2 | $3.64 | $79.99 | 4.6% | $39.99 | single | yes |
| dentist mirror | CATEGORY | account-wide | 2 | $3.53 | $39.98 | 8.8% | $19.99 | single | no |
| fog free dental mirror | CATEGORY | account-wide | 2 | $6.71 | $59.89 | 11.2% | $29.95 | single | no |
| no fog dental mirror | CATEGORY | account-wide | 2 | $10.93 | $39.98 | 27.3% | $19.99 | single | no |

- **illuco dental mirror**: Brand term: run as Exact in a brand ad group that serves all families; family shown is from order value. Now captured by HEADS-KW: 10 ord / $45.08; BRAND-KW: 4 ord / $19.93; CATEGORY: 4 ord / $10.45.
- **dental mirror**: Account-wide 10 orders / $112.78 / ACoS 51.3%: negative-exact it where it does not convert. Now captured by CATEGORY: 10 ord / $51.08; HEADS-KW: 0 ord / $29.53; BRAND-KW: 0 ord / $31.43; AUTO-1PK: 0 ord / $0.74.
- **illuco**: Brand term: run as Exact in a brand ad group that serves all families; family shown is from order value. Already an Exact keyword in BRAND-KW (1 impr. in 90 days), HEADS-KW (1 impr. in 90 days) although SQP shows 21 searches in Oct: check it is enabled and bid at least as high as the broad/phrase versions. Now captured by BRAND-KW: 1 ord / $0.06; AUTO-1PK: 1 ord / $0.38; DERM: 0 ord / $1.45; CATEGORY: 0 ord / $1.75.
- **dentist mirror**: Now captured by CATEGORY: 2 ord / $3.53.
- **fog free dental mirror**: Anti-fog claim: proposed listing copy drops "Fog-Resistant" and 3 return comments cite fogging/water - harvest only if the claim stays. Now captured by CATEGORY: 2 ord / $5.00; BRAND-KW: 0 ord / $1.71.
- **no fog dental mirror**: Anti-fog claim: proposed listing copy drops "Fog-Resistant" and 3 return comments cite fogging/water - harvest only if the claim stays. Now captured by CATEGORY: 2 ord / $6.06; HEADS-KW: 0 ord / $2.40; BRAND-KW: 0 ord / $2.47.

Near misses (>= 2 orders, ACoS above the 36.42% threshold but below the 39.50% same-window average): "dental mirror for teeth" 5 orders, ACoS 36.78%; "dental mirror anti fog" 2 orders, ACoS 36.43%. Keep them running where they convert; harvest once they drop below the threshold.

Product pages (ASIN search terms) with >= 2 orders, for product targeting rather than Exact keywords. Pass: B0F84TKGLS (ILLUCO) 3 orders / $5.44 / ACoS 5.9%; B0G2DYRY7T (ILLUCO) 2 orders / $13.02 / ACoS 21.7%. Above the threshold: B0FCZBD1KY (ILLUCO) 3 orders / $27.78 / ACoS 38.6%; B08GSQWY5S (ffresiss $9.88) 2 orders / $31.70 / ACoS 66.1%. ILLUCO's own pages convert cheaply (shoppers on one ILLUCO page buy another ILLUCO item); the $9.88 ffresiss LED mirror page does not pay.

## e. Targeting report insights (Aug 23, 2026 - Nov 20, 2026)

| Match type / target type | Targets | Impr. | Clicks | CTR | CPC | Spend | Orders | Sales | ACoS | CVR |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Keyword phrase | 21 | 194,709 | 691 | 0.35% | $1.54 | $1,064.72 | 31 | $3,404.99 | 31.3% | 4.5% |
| Category target | 1 | 63,544 | 513 | 0.81% | $1.12 | $572.42 | 58 | $1,403.09 | 40.8% | 11.3% |
| Keyword exact | 25 | 28,786 | 237 | 0.82% | $2.26 | $536.21 | 1 | $950.00 | 56.4% | 0.4% |
| Keyword broad | 56 | 44,825 | 247 | 0.55% | $1.42 | $350.66 | 8 | $1,274.99 | 27.5% | 3.2% |
| Auto: substitutes | 4 | 56,961 | 218 | 0.38% | $1.08 | $236.00 | 16 | $491.30 | 48.0% | 7.3% |
| Auto: close-match | 4 | 4,875 | 16 | 0.33% | $1.15 | $18.43 | 4 | $173.79 | 10.6% | 25.0% |
| Auto: loose-match | 3 | 6,084 | 12 | 0.20% | $0.91 | $10.92 | 2 | $51.89 | 21.0% | 16.7% |
| Keyword group (theme) | 3 | 1,087 | 6 | 0.55% | $0.92 | $5.49 | 0 | $0.00 | - | 0.0% |
| Auto: complements | 2 | 8 | 0 | 0.00% | - | $0.00 | 0 | $0.00 | - | - |
| **Total** | 119 | 400,879 | 1,940 | 0.48% | $1.44 | $2,794.85 | 120 | $7,750.05 | 36.1% | 6.2% |

**Targets with spend >= $5 or orders > 0** (verdict: Keep = ACoS <= 36.4%; Cut = ACoS >= 50%; Pause = 0 orders on >= $8; Brand-driven = brand searches are >= 50% of the target's search-term sales, so its ACoS hides the non-brand cost)

| Campaign | Target | Match | Top-of-search IS | Impr. | Clicks | CPC | Spend | Orders | Sales | ACoS | Brand-term share of sales (Sep 17-Nov 20) | Verdict |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| CATEGORY | category="Dental Mirrors" | - | 0.53% | 63,544 | 513 | $1.12 | $572.42 | 58 | $1,403.09 | 40.8% | 10% of $1,051 | Tighten (negatives, lower bid) |
| DERM | dermatoscope | EXACT | 5.61% | 24,765 | 224 | $2.31 | $517.64 | 1 | $950.00 | 54.5% | 0% of $950 | Cut bid $2.31 -> <= $1.27 |
| HEADS-KW | dental mirror | PHRASE | 1.64% | 73,689 | 224 | $2.03 | $454.27 | 17 | $1,939.99 | 23.4% | 87% of $1,365 | Brand-driven: non-brand ACoS 147.5%; split brand out, cut bid |
| BRAND-KW | dental mirror | PHRASE | 0.90% | 33,832 | 152 | $1.70 | $259.07 | 9 | $1,015.00 | 25.5% | 45% of $1,015 | Keep |
| BRAND-KW | dental | PHRASE | 0.25% | 76,905 | 192 | $1.20 | $229.92 | 4 | $390.00 | 59.0% | 0% of $235 | Cut bid / pause |
| BRAND-KW | dental tools home use | BROAD | 0.07% | 25,238 | 120 | $1.86 | $223.55 | 3 | $445.00 | 50.2% | 40% of $350 | Cut bid / pause |
| AUTO-1PK | substitutes | - | 0.01% | 29,761 | 150 | $1.00 | $150.67 | 15 | $431.30 | 34.9% | 0% of $235 | Keep |
| DERM | dermatoscope | PHRASE | 0.16% | 5,919 | 82 | $1.13 | $92.55 | 0 | $0.00 | - | no sales | Low data at DERM CVR; keep CPC <= $1.27 |
| BRAND-KW | dental mirror | BROAD | 0.69% | 6,807 | 46 | $1.45 | $66.56 | 3 | $304.99 | 21.8% | 33% of $285 | Keep |
| AUTO-5PK | substitutes | - | 0.15% | 18,885 | 44 | $1.32 | $58.17 | 0 | $0.00 | - | no sales | Campaign paused |
| AUTO-HEADS | substitutes | - | 0.12% | 6,222 | 17 | $1.03 | $17.46 | 1 | $60.00 | 29.1% | no sales | Keep |
| BRAND-KW | dental hygienist must haves | EXACT | 0.62% | 3,225 | 10 | $1.63 | $16.32 | 0 | $0.00 | - | no sales | Pause / negate |
| DERM | dermatoscope | BROAD | 0.04% | 2,758 | 14 | $0.74 | $10.42 | 0 | $0.00 | - | no sales | Low data at DERM CVR; keep CPC <= $1.27 |
| AUTO-HEADS | close-match | - | 0.21% | 2,956 | 7 | $1.48 | $10.35 | 1 | $90.00 | 11.5% | no sales | Keep |
| AUTO-LEGACY | substitutes | - | 0.00% | 2,093 | 7 | $1.39 | $9.70 | 0 | $0.00 | - | no sales | Campaign paused |
| HEADS-KW | dental mirror | BROAD | 0.42% | 877 | 7 | $1.22 | $8.55 | 0 | $0.00 | - | no sales | Pause / negate |
| DERM | dermoscope | PHRASE | 0.08% | 1,839 | 11 | $0.74 | $8.10 | 0 | $0.00 | - | no sales | Low data at DERM CVR; keep CPC <= $1.27 |
| DERM | dermatoscope otoscopes & ophthalmoscopes | BROAD | 0.00% | 2,602 | 11 | $0.69 | $7.55 | 0 | $0.00 | - | no sales | Pause (off-target keyword) |
| DERM | dermatoscopio | PHRASE | 0.99% | 437 | 9 | $0.71 | $6.40 | 0 | $0.00 | - | no sales | Low data at DERM CVR; keep CPC <= $1.27 |
| DERM | illuco dermatoscope | BROAD | 0.02% | 1,071 | 8 | $0.78 | $6.22 | 0 | $0.00 | - | no sales | Keep (brand) |
| DERM | dermascope | PHRASE | 0.20% | 867 | 9 | $0.68 | $6.10 | 0 | $0.00 | - | no sales | Low data at DERM CVR; keep CPC <= $1.27 |
| DERM | dermatology equipment | BROAD | 0.00% | 733 | 8 | $0.74 | $5.96 | 1 | $430.00 | 1.4% | no sales | Keep |
| AUTO-5PK | close-match | - | 0.04% | 1,100 | 5 | $1.09 | $5.47 | 0 | $0.00 | - | - | Campaign paused |
| AUTO-HEADS | loose-match | - | 0.21% | 4,694 | 6 | $0.91 | $5.44 | 0 | $0.00 | - | no sales | Low data |
| AUTO-1PK | close-match | - | 0.00% | 745 | 4 | $0.65 | $2.61 | 3 | $83.79 | 3.1% | 0% of $84 | Keep |
| AUTO-1PK | loose-match | - | 0.00% | 592 | 2 | $0.38 | $0.76 | 2 | $51.89 | 1.5% | 39% of $52 | Keep |
| BRAND-KW | illuco | BROAD | 20.65% | 59 | 2 | $0.26 | $0.51 | 1 | $95.00 | 0.5% | 100% of $95 | Keep (brand) |
| BRAND-KW | illuco | PHRASE | 25.00% | 7 | 1 | $0.06 | $0.06 | 1 | $60.00 | 0.1% | 100% of $60 | Keep (brand) |

- **Converting:** "dental mirror" phrase (HEADS-KW 17 orders, BRAND-KW 9), the CATEGORY target (58 orders, CVR 11.3%, CPC $1.12), AUTO-1PK substitutes, and the cheap brand keywords ("illuco" broad/phrase). Much of the "dental mirror" phrase revenue is brand queries (see the brand-share column).
- **Wasting:** BRAND-KW "dental" phrase ($229.92, ACoS 59.0%; 92% of its search-term spend was off-category/consumer) and "dental tools home use" broad ($223.55, ACoS 50.2%; 62% off-category/consumer/rhodium, the rest generic mirror queries that "dental mirror" phrase already covers); "dental hygienist must haves" exact has 0 orders; DERM "dermatoscope" exact carries the DERM campaign's cost.
- **Top-of-search impression share is low everywhere:** 1.64% on HEADS-KW "dental mirror" phrase, 0.90% on BRAND-KW "dental mirror" phrase, 5.61% on DERM "dermatoscope" exact, 0.53% on the category target. Brand keywords reach 20.6% - 25%. With budgets on hold, do not chase top-of-search on generic terms (shoppers there buy $5-10 mirrors); the one place to pay for it is brand Exact, funded by the cuts below.
- Auto campaigns: "substitutes" (product pages) is where auto spend goes; close/loose match produce few clicks. 60 keyword targets had zero clicks in 90 days (mostly DERM long-tail and BRAND-KW variants): harmless, but they clutter the account.

## f. Dermatoscope campaign (DERM): verdict

| Slice | Spend | Clicks | Orders | Sales | ACoS | CVR | CPC |
|---|---:|---:|---:|---:|---:|---:|---:|
| Campaign report (Aug 1, 2026 - Nov 20, 2026) | $739.55 | 485 | 2 | $1,380.00 | 53.6% | 0.41% | $1.52 |
| "dermatoscope" Exact keyword (targeting report, 90 days) | $517.64 | 224 | 1 | $950.00 | 54.5% | 0.45% | $2.31 |
| All other DERM targets (targeting report) | $173.48 | 195 | 1 | $430.00 | 40.3% | 0.51% | $0.89 |

**Verdict: keep it, but shrink it to what converts.** It is the only paid presence for a $430-1,600 line, yet as run it returns $1.87 in sales per $1 of spend (ACoS 53.6%, the worst in the account).

- One keyword is the problem: "dermatoscope" Exact took 75% of DERM spend at $2.31 CPC (top-of-search share 5.61%). At its observed CVR (1/224 = 0.45%) and the $950 order, the CPC that yields a given ACoS is AOV x CVR x ACoS: $0.85 for 20%, $1.27 for 30%, $1.70 for 40%. Cut the bid to that range (target ACoS is the owner's call; the CVR rests on a single order, so treat it as rough).
- In the search-term window DERM spent $627.03 = $9.65/day against a $10 budget (96% on average), so it is likely capped on many days: the only campaign where budget binds. Lowering the exact bid frees budget for the brand/model and long-tail terms without raising the cap.
- The market buys cheap units on generic searches. SQP "dermatoscope": Oct 7,312 searches, ILLUCO click share 3.89%, purchase share 2.97% (3 of 101), market median purchase price $59.99 vs ILLUCO $950; Q3 4 of 225 purchases (median $99.99). ILLUCO click share rose from 2.20% (Sep) to 3.89% (Oct). SQP counts 3 ILLUCO purchases from this query in October alone against 1 ad-attributed order in 90 days: buyers reach ILLUCO organically and/or buy outside the 7-day ad window, so the keyword's true return is uncertain. That argues for a lower bid, not for pausing.
- The rest of DERM is cheaper than it looks: all other targets ran at $0.89 CPC and 40.3% ACoS. "dermatoscope" phrase + broad ($102.97, 96 clicks, 0 orders in 90 days) are already under the cap; 96 clicks without an order is within what a 0.45% CVR predicts (~0.4 orders), so the data cannot condemn them. Keep every DERM bid at or below ~$1.27 and trim off-target matches with negatives instead of pausing.
- Negate non-dermatoscope traffic ($10.51 in the window: "otoscope with light medical grade", "dermatoscope for cell phone", "esthetician supplies", "loupe", "loupes"). Pause the odd keyword "dermatoscope otoscopes & ophthalmoscopes" (broad) and the phone-attachment keywords ("dermatoscope iphone", "smartphone dermatoscope", "dermatoscope for smart phone", "dermatoscope attachment for iphone"): ILLUCO units are handheld.
- 32 of 63 DERM targets had zero clicks in 90 days. The one non-brand long-tail winner was "dermatology equipment" broad (1 order, $430). Keep brand/model terms ("illuco dermatoscope", "illuco ids-1100 dermatoscope") and cheap synonyms ("dermascope", "dermoscope", "dermatoscopio" at ~$0.70 CPC) running.
- Business Report (window not stated): dermatoscopes 9 units / $8,680 on 836 sessions vs 2 ad-attributed orders in 112 days, so most dermatoscope revenue appears to arrive without an attributed ad click (approximate: the windows differ). The listings sit in Home Decor / Automotive browse nodes (`listings/Existing_Listings_Update_Sheet.xlsx`, Attribute Fixes): fixing categorization is cheaper than buying relevance with bids.

## g. Recommended changes that need no budget increase

| # | Change | Evidence (spend / orders / sales) | Why |
|---:|---|---|---|
| 1 | Pause BRAND-KW keyword "dental" (phrase) | $191.12 / 2 orders / $235.00 | 92% of its search-term spend went to off-category/consumer searches (handpieces, loupes, drills, materials) |
| 2 | Pause BRAND-KW keyword "dental tools home use" (broad) | $168.48 / 2 orders / $350.00 | Consumer intent; 62% off-category/consumer/rhodium, the rest is covered by "dental mirror" phrase |
| 3 | Pause BRAND-KW "dental hygienist must haves" (exact) | $16.32 / 0 orders | Gift-list query, 0 orders |
| 4 | Upload `negative_keywords.csv` | 150 rows (90 preventive, 0 spend so far): 139 negative phrase, 8 negative exact, 3 negative product target (ASIN) | Consumer modifiers, rhodium, off-category words, wasted terms, harvest routing, 2 ASINs (3 rows) |
| 5 | DERM: cut "dermatoscope" exact bid from $2.31 to ~$1.27 (30% ACoS at observed CVR) and keep every other DERM bid under that cap; pause "dermatoscope otoscopes & ophthalmoscopes" and the phone-attachment keywords | $517.64 on the exact keyword in 90 days for 1 order; the other targets ran at 40.3% ACoS | See section f |
| 6 | Add an Exact ad group inside BRAND-KW (advertising the single mirror) with the non-brand winners from `harvest_keywords.csv`; negative-exact them where they bleed (routing rows in the negatives file) | 4 non-brand terms, 16 orders | Uses BRAND-KW's existing $30/day (it spends $10.25/day, less after items 1-3); stops 3-4 campaigns bidding on the same query |
| 7 | Add a Brand Exact ad group inside BRAND-KW (all mirror ASINs): "illuco dental mirror", "illuco dental mirrors", "illuco", "illuco mirror", model codes; the existing "illuco" Exact keywords served 1 impression each in 90 days, so check they are enabled and bid at least as high as the broad/phrase versions; once live, add "illuco" as negative phrase in HEADS-KW and CATEGORY | Brand terms: $98.90 spend, $2,149.93 sales, ACoS 4.6% | Cheap; makes non-brand ACoS visible; brand top-of-search share is only 20-25% |
| 8 | Route generic mirror queries to the single mirror: keep "dental mirror", "dental mirror for teeth" and fog terms in CATEGORY/AUTO-1PK; negative-exact them in HEADS-KW and BRAND-KW | Routing rows in `negative_keywords.csv` | Generic shoppers buy the $19.99 single (CATEGORY AOV $24), not $60-140 packs |
| 9 | Optional, budget-neutral: if you prefer separate campaigns for items 6-7, fund them by lowering AUTO-1PK and AUTO-HEADS budgets by the same amount | AUTO-1PK spends $1.88/day of $20; AUTO-HEADS $0.30/day of $20 | Account total stays at $125/day enabled |
| 10 | Keep AUTO-5PK and AUTO-LEGACY paused | Their $45/day of budget stays idle | 0 orders in the targeting window (Aug 23 on) |
| 11 | CATEGORY: apply the negative product targets and consumer negatives; review competitor-ASIN placements monthly | Competitor product pages: $233.64 spend, 6 orders, ACoS 167.1% | Clicks are spread thin (1-2 per ASIN); only 2 ASINs meet the waste rule so far |

Estimated effect on Sep 17, 2026 - Nov 20, 2026: items 1-4 would have blocked $638.67 of spend (28.0%; negative exact / ASIN: $136.52, negative phrase: $126.23, pause keyword: $375.92) and 4 orders / $585.00 sales (ACoS of the blocked traffic 109.2%). Hold the freed money inside the existing budgets; let the harvested Exact and brand ad groups absorb it through bids.

**Largest negatives by spend they would have blocked** (all campaigns summed; full list in `negative_keywords.csv`)

| Negative | Match type | Campaigns | Spend Sep 17-Nov 20 | Clicks | Orders |
|---|---|---|---:|---:|---:|
| dental mirror | negative exact | BRAND-KW, HEADS-KW | $60.96 | 31 | 0 |
| with light | negative phrase | AUTO-1PK, AUTO-HEADS, BRAND-KW, CATEGORY, HEADS-KW | $58.40 | 38 | 0 |
| rhodium | negative phrase | AUTO-1PK, AUTO-HEADS, BRAND-KW, CATEGORY, HEADS-KW | $54.77 | 30 | 0 |
| instruments | negative phrase | AUTO-HEADS, BRAND-KW, CATEGORY | $37.06 | 26 | 0 |
| dental mirrors | negative exact | HEADS-KW | $23.79 | 11 | 0 |
| handpiece | negative phrase | BRAND-KW | $16.72 | 13 | 0 |
| dental hygienist must haves | negative exact | BRAND-KW | $16.32 | 10 | 0 |
| B077T1DWDR | negative product target (ASIN) | CATEGORY | $15.72 | 14 | 0 |
| loupes | negative phrase | BRAND-KW | $13.82 | 10 | 0 |
| dental mirror anti fog | negative exact | BRAND-KW | $13.67 | 7 | 0 |

Negative phrase rows are written per campaign (each campaign has one ad group, so campaign- and ad-group-level negatives are equivalent today). ASIN rows go in as negative product targets. "Preventive" rows have no spend yet; they cover consumer modifiers (LED, kids, disposable, picks/plaque, hand/makeup/telescoping mirrors) so auto and category targeting cannot drift into them.

Not recommended now: new Sponsored Brands/DSP (owner has no budget for them), raising any campaign budget, or chasing top-of-search on "dental mirror" (market median purchase price is under $10).

## Search Query Performance (Brand Analytics, Brand View)

Windows: Oct 2026 (latest month), Q3 2026 (Jul 1 - Sep 30), Sep 2026 for trend. Brand totals: ILLUCO had 50,490 impressions / 768 clicks / 27 purchases across 501 Oct queries, and 85,635 / 1,072 / 45 across 726 Q3 queries.

**Top 30 queries by search volume, Oct 2026 and Q3 2026 (union, 42 queries)**. 37 of them are off-category (hand mirrors, headlamps, generic dental shopping) where ILLUCO only got stray impressions.

| Search query | Relevance | Oct vol | Oct rank | Oct impr. share | Oct click share | Oct purch. share | Q3 vol | Q3 rank | Q3 impr. share | Q3 click share | Q3 purch. share |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| hand mirror | Off-category | 52,804 | #1 | 0.01% | 0.00% | 0.00% | - | - | - | - | - |
| dental tools | Off-category | 42,255 | #2 | 0.01% | 0.00% | 0.00% | 130,766 | #2 | 0.00% | 0.00% | 0.00% |
| hand held mirror | Off-category | 30,652 | #3 | 0.01% | 0.00% | 0.00% | - | - | - | - | - |
| dental | Off-category | 20,106 | #4 | 0.05% | 0.05% | 0.00% | 58,628 | #4 | 0.02% | 0.00% | 0.00% |
| dental assistant accessories | Off-category | 19,017 | #5 | 0.03% | 0.00% | 0.00% | 61,455 | #3 | 0.02% | 0.00% | 0.00% |
| inspection mirror | Off-category | 13,683 | #6 | 0.05% | 0.02% | 0.00% | 38,336 | #8 | 0.01% | 0.00% | 0.00% |
| dental mirror | Mirror: core | 11,550 | #7 | 1.65% | 0.60% | 0.10% | 34,244 | #10 | 0.47% | 0.18% | 0.03% |
| dental assistant must haves | Off-category | 10,790 | #8 | 0.05% | 0.00% | 0.00% | 37,651 | #9 | 0.02% | 0.00% | 0.00% |
| dental hygienist gifts | Off-category | 10,547 | #9 | 0.06% | 0.02% | 0.00% | 13,267 | #20 | 0.01% | 0.00% | 0.00% |
| dentist tools | Off-category | 8,011 | #10 | 0.05% | 0.00% | 0.00% | 22,611 | #13 | 0.01% | 0.00% | 0.00% |
| dental hygiene student must haves | Off-category | 7,810 | #11 | 0.07% | 0.00% | 0.00% | 38,406 | #7 | 0.03% | 0.01% | 0.00% |
| dermatoscope | Dermatoscope | 7,312 | #12 | 5.71% | 3.89% | 2.97% | 22,815 | #12 | 1.98% | 1.03% | 1.78% |
| dental loupes | Off-category | 6,820 | #13 | 0.32% | 0.03% | 0.00% | 19,548 | #15 | 0.23% | 0.02% | 0.00% |
| odontologia | Off-category | 5,716 | #14 | 0.70% | 0.54% | 0.00% | 17,661 | #16 | 0.15% | 0.14% | 0.00% |
| dental mirror for teeth | Mirror: consumer-leaning (teeth) | 5,175 | #15 | 1.88% | 0.68% | 0.20% | 15,066 | #19 | 0.34% | 0.14% | 0.00% |
| teeth cleaning | Off-category | 4,883 | #16 | 0.00% | 0.06% | 0.00% | - | - | - | - | - |
| dental assistant | Off-category | 4,864 | #17 | 0.08% | 0.00% | 0.00% | 15,994 | #18 | 0.05% | 0.02% | 0.00% |
| dental loupes with light | Off-category | 4,562 | #18 | 0.34% | 0.00% | 0.00% | 13,100 | #21 | 0.28% | 0.02% | 0.00% |
| dentist | Off-category | 4,434 | #19 | 0.04% | 0.00% | 0.00% | - | - | - | - | - |
| dental office decor | Off-category | 4,180 | #20 | 0.04% | 0.00% | 0.00% | 16,203 | #17 | 0.02% | 0.00% | 0.00% |
| dental mirror with light | Mirror: consumer (LED/disposable/kids/home) | 3,134 | #21 | 0.49% | 0.12% | 0.00% | 9,156 | #28 | 0.36% | 0.04% | 0.00% |
| dentist gift | Off-category | 2,912 | #22 | 0.08% | 0.00% | 0.00% | - | - | - | - | - |
| dental curing light | Off-category | 2,769 | #23 | 0.06% | 0.00% | 0.00% | 8,198 | #29 | 0.02% | 0.00% | 0.00% |
| dental glasses | Off-category | 2,638 | #24 | 0.11% | 0.00% | 0.00% | 7,099 | #31 | 0.05% | 0.00% | 0.00% |
| dental hygienist | Off-category | 2,625 | #25 | 0.17% | 0.13% | 0.00% | 7,069 | #33 | 0.08% | 0.05% | 0.00% |
| dental instruments | Off-category | 2,405 | #26 | 0.07% | 0.00% | 0.00% | 6,936 | #34 | 0.05% | 0.04% | 0.00% |
| tooth mirror | Mirror: consumer-leaning (teeth) | 2,377 | #27 | 0.20% | 0.00% | 0.00% | 7,070 | #32 | 0.14% | 0.08% | 0.00% |
| dental supplies | Off-category | 2,016 | #28 | 0.07% | 0.00% | 0.00% | 6,092 | #38 | 0.07% | 0.00% | 0.00% |
| large hand mirror | Off-category | 1,984 | #29 | 0.03% | 0.10% | 0.00% | - | - | - | - | - |
| odontologia materiales dentales | Off-category | 1,966 | #30 | 0.35% | 0.38% | 0.00% | 5,914 | #39 | 0.27% | 0.27% | 0.00% |
| headlamp | Off-category | - | - | - | - | - | 657,615 | #1 | 0.00% | 0.00% | 0.00% |
| estetoscopio | Off-category | - | - | - | - | - | 55,678 | #5 | 0.00% | 0.01% | 0.00% |
| true mirror | Off-category | - | - | - | - | - | 49,292 | #6 | 0.01% | 0.00% | 0.00% |
| ghost mirror | Off-category | - | - | - | - | - | 26,432 | #11 | 0.03% | 0.00% | 0.00% |
| dental scaler | Off-category | - | - | - | - | - | 21,106 | #14 | 0.01% | 0.00% | 0.00% |
| dental gifts | Off-category | - | - | - | - | - | 11,970 | #22 | 0.01% | 0.03% | 0.00% |
| dental hygienist must haves | Off-category | 1,859 | #33 | 0.21% | 0.00% | 0.00% | 10,383 | #23 | 0.13% | 0.03% | 0.00% |
| dental tools for home use | Off-category | - | - | - | - | - | 10,322 | #24 | 0.03% | 0.02% | 0.00% |
| cheek retractor | Off-category | - | - | - | - | - | 10,130 | #25 | 0.00% | 0.02% | 0.00% |
| dental decor | Off-category | - | - | - | - | - | 9,476 | #26 | 0.04% | 0.00% | 0.00% |
| blue mirror | Off-category | - | - | - | - | - | 9,176 | #27 | 0.03% | 0.00% | 0.00% |
| dental stickers | Off-category | - | - | - | - | - | 7,631 | #30 | 0.00% | 0.03% | 0.00% |

**Queries where ILLUCO wins purchases** (any ILLUCO purchase in Oct or Q3; purchase share > click share means the listing converts better than the page average once clicked)

| Search query | Relevance | Oct vol | Oct ILLUCO/total purchases | Oct purch. share | Oct click share | Q3 vol | Q3 ILLUCO/total purchases | Q3 purch. share | Q3 click share |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| illuco dental mirror | Brand (ILLUCO) | 75 | 4/4 | 100.0% | 93.3% | 280 | 16/16 | 100.0% | 93.1% |
| dermatoscope | Dermatoscope | 7,312 | 3/101 | 3.0% | 3.9% | 22,815 | 4/225 | 1.8% | 1.0% |
| dental mirror | Mirror: core | 11,550 | 2/1975 | 0.1% | 0.6% | 34,244 | 2/6030 | 0.0% | 0.2% |
| dental mirror for teeth | Mirror: consumer-leaning (teeth) | 5,175 | 2/996 | 0.2% | 0.7% | 15,066 | 0/3009 | 0.0% | 0.1% |
| stainless steel dental mirror | Mirror: core | 93 | 0/8 | 0.0% | 0.0% | 241 | 1/20 | 5.0% | 1.8% |
| dentist magnifying mirror | Mirror: core | - | - | - | - | 155 | 1/26 | 3.8% | 2.2% |
| illuco | Brand (ILLUCO) | 21 | 1/1 | 100.0% | 100.0% | 59 | 0/0 | - | 92.3% |
| dentist mirror | Mirror: core | 862 | 1/122 | 0.8% | 0.6% | 2,513 | 0/392 | 0.0% | 0.0% |
| no fog dental mirror | Mirror: core | 56 | 1/5 | 20.0% | 9.5% | 59 | 0/6 | 0.0% | 6.1% |
| professional dental mirror | Mirror: core | 41 | 0/4 | 0.0% | 25.9% | 117 | 1/10 | 10.0% | 13.6% |
| professional dental mirror for teeth | Mirror: consumer-leaning (teeth) | 65 | 1/9 | 11.1% | 2.9% | 51 | 0/10 | 0.0% | 8.3% |
| dental lighted mouth mirror | Mirror: consumer (LED/disposable/kids/home) | 11 | 1/2 | 50.0% | 14.3% | - | - | - | - |
| illuco ids-1100 dermatoscope | Brand (ILLUCO) | 12 | 0/0 | - | 66.7% | 75 | 1/1 | 100.0% | 64.5% |
| zirc dental mirror | Mirror: core | 116 | 0/3 | 0.0% | 8.6% | 478 | 1/10 | 10.0% | 1.5% |
| front surface dental mirror | Mirror: core | 45 | 1/7 | 14.3% | 12.0% | 77 | 0/6 | 0.0% | 4.9% |
| dr head mirror | Off-category | 279 | 1/17 | 5.9% | 1.2% | 220 | 0/8 | 0.0% | 0.0% |
| anti fog dental mirror | Mirror: core | 326 | 1/12 | 8.3% | 3.5% | 626 | 0/27 | 0.0% | 4.7% |
| non fog dental mirror | Mirror: core | 17 | 0/1 | 0.0% | 0.0% | 35 | 1/3 | 33.3% | 25.0% |
| hu friedy dental mirror | Mirror: core | 14 | 0/4 | 0.0% | 0.0% | 80 | 1/5 | 20.0% | 7.1% |
| fog proof dental mirror | Mirror: core | 18 | 0/1 | 0.0% | 7.7% | 28 | 1/3 | 33.3% | 10.0% |
| dental mirrors | Mirror: core | 821 | 0/75 | 0.0% | 1.0% | 2,010 | 1/182 | 0.5% | 0.9% |

Plus 22 one-off queries (under 10 searches in Oct and under 25 in Q3) with an ILLUCO purchase: "illuco dental mirror replacement heads", "dental miror illuco 3 mag", "fog proof dental mirrors", "dental mirror for professional grade", "illuc dental mirror", "dental+mirrors+heads+sapphire+#4", "dental mirror 3x magnificatikn", "for free excellent dental mirror", "ulluco dental mirrors", "illuco dental mirrors", "dental mirror fog free", "dental mirror ergo", "dental mirror for teeth illuco", "dermatoscopio illuco", "real dental mirror", "dental loops magnification high quality", "cialegese dental mirror", "dental handheld mouth anti-fog mirror autoclave safel", "double sided illuco dental mirrors", "illuco mirror dentistry", "dental mirror with handle fog resistant 3x", "water resistant dental mirror".

- Brand: on "illuco dental mirror" (75 searches in Oct, 280 in Q3) ILLUCO gets 93% of clicks (Oct; 93% in Q3) and 100% of purchases; the remaining clicks go to other brands' listings. Defend it cheaply on Exact.
- Non-brand wins are few and small (anti-fog / no-fog / fog-free, front surface, professional, Zirc and Hu-Friedy queries), but in 18 of the 31 non-brand query/period pairs where ILLUCO made a sale, its purchase share beat its click share: ILLUCO converts premium-intent shoppers once they click.
- "dental mirror": 11,550 searches in Oct, ILLUCO click share 0.29% (Sep) -> 0.60% (Oct), purchase share 0.10%; market median purchase price $6.96 vs ILLUCO $19.99. Volume is there but buyers are price-driven; win it organically (title/backend, reviews) and with the single mirror, not with bids.
- SQP purchases are attributed to the query by Amazon and are not comparable 1:1 with 7-day ad-attributed orders.

**Gaps: relevant queries with real volume and ILLUCO click share < 2%** (Oct volume >= 150). "Copy" checks whether every word of the query already appears in the current title (dermatoscope, photo) or in the proposed title/highlight/bullets/backend in `listings/Existing_Listings_Update_Sheet.xlsx` (mirror families). "PPC" uses the ad search-term results for the same query (Sep 17, 2026 - Nov 20, 2026).

| Search query | Relevance | Oct vol | Oct impr. share | Oct click share | Oct ILLUCO/total purch. | Market median purchase price | Q3 click share | Ad clicks / orders (Sep 17-Nov 20) | Copy (title/backend) | PPC |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| dental mirror | Mirror: core | 11,550 | 1.65% | 0.60% | 2/1975 | $6.96 | 0.18% | 72 / 10 | In current title | Exact: harvest (harvest_keywords.csv) |
| dental mirror for teeth | Mirror: consumer-leaning (teeth) | 5,175 | 1.88% | 0.68% | 2/996 | $9.88 | 0.14% | 36 / 5 | In proposed backend/bullets | Near-miss winner (5 ad orders, ACoS 36.8%): keep in single-mirror campaigns |
| tooth mirror | Mirror: consumer-leaning (teeth) | 2,377 | 0.20% | 0.00% | 0/390 | $6.96 | 0.08% | 2 / 0 | In proposed backend/bullets | Watch (only 2 ad clicks); single mirror only |
| dermascope | Dermatoscope | 1,865 | 2.65% | 0.81% | 0/40 | $59.99 | 0.75% | 9 / 0 | Not in title: add to backend | Keep at a low bid (0 orders on 9 ad clicks is too few at DERM's ~0.4% CVR) |
| dentist mirror for inside mouth | Mirror: core | 1,295 | 0.84% | 0.51% | 0/275 | $6.96 | 0.19% | 4 / 0 | In proposed backend/bullets; title words would add rank weight | Watch (only 4 ad clicks) |
| mouth mirror dental | Mirror: core | 1,169 | 0.97% | 0.17% | 0/206 | $9.88 | 0.12% | 5 / 0 | In proposed backend/bullets; title words would add rank weight | Watch (only 5 ad clicks) |
| mouth mirror | Mirror: core | 934 | 0.64% | 0.00% | 0/123 | $8.49 | 0.14% | 3 / 1 | In proposed backend/bullets; title words would add rank weight | Already Exact in HEADS-KW: keep (1 ad order, ACoS 20.4%) |
| dentist mirror | Mirror: core | 862 | 0.94% | 0.60% | 1/122 | $6.96 | 0.00% | 3 / 2 | In proposed backend/bullets; title words would add rank weight | Exact: harvest (harvest_keywords.csv) |
| dermoscope | Dermatoscope | 825 | 2.67% | 0.68% | 0/7 | $159.99 | 1.11% | 2 / 0 | Not in title: add to backend | Keep at a low bid (0 orders on 2 ad clicks is too few at DERM's ~0.4% CVR) |
| dental mirrors | Mirror: core | 821 | 2.79% | 1.00% | 0/75 | $9.88 | 0.87% | 31 / 1 | In current title | Test Exact at a capped bid (1 ad order, ACoS 40.5%) |
| teeth mirror | Mirror: consumer-leaning (teeth) | 747 | 0.32% | 0.51% | 0/105 | $6.76 | 0.00% | 2 / 1 | In proposed backend/bullets | Test Exact at a capped bid (1 ad order, ACoS 13.7%); single mirror only |
| dermoscopy | Dermatoscope | 579 | 1.25% | 1.91% | 0/18 | $96.99 | 0.27% | 3 / 0 | Not in title: add to backend | Keep at a low bid (0 orders on 3 ad clicks is too few at DERM's ~0.4% CVR) |
| dermatoscope for skin | Dermatoscope | 552 | 2.51% | 0.85% | 0/6 | $52.99 | 0.37% | 5 / 0 | Not in title: add to backend | Keep at a low bid (0 orders on 5 ad clicks is too few at DERM's ~0.4% CVR) |
| dermascope for skin | Dermatoscope | 546 | 1.88% | 1.67% | 0/16 | $52.99 | 0.75% | 2 / 0 | Not in title: add to backend | Keep at a low bid (0 orders on 2 ad clicks is too few at DERM's ~0.4% CVR) |
| woods lamp medical | Dermatoscope | 436 | 0.77% | 0.00% | 0/13 | $12.99 | 0.00% | 0 / 0 | Not in title: add to backend | Optional low-bid Exact test (no ad data) |
| woods lamp esthetician | Dermatoscope | 427 | 0.84% | 0.59% | 0/7 | $70.99 | 0.00% | 0 / 0 | Not in title: add to backend | Optional low-bid Exact test (no ad data) |
| dental mouth mirror | Mirror: core | 313 | 1.54% | 0.00% | 0/51 | $9.88 | 0.00% | 1 / 0 | In proposed backend/bullets | Watch (only 1 ad click) |
| espejo dental | Mirror: core | 303 | 3.62% | 1.57% | 0/23 | $6.99 | 1.27% | 2 / 0 | Missing from proposed copy: add to backend (Spanish) | Watch (only 2 ad clicks) |
| small dental mirror | Mirror: core | 302 | 1.53% | 0.65% | 0/44 | $6.96 | 0.31% | 2 / 0 | Missing from proposed copy: add to backend | Watch (only 2 ad clicks) |
| oral mirror | Mirror: core | 259 | 1.00% | 0.69% | 0/39 | $9.88 | 0.00% | 1 / 0 | In proposed backend/bullets | Watch (only 1 ad click) |
| espejos intraorales odontologia | Mirror: core | 233 | 3.65% | 1.87% | 0/6 | $11.99 | 0.75% | 1 / 0 | Missing from proposed copy: add to backend (Spanish) | Watch (only 1 ad click) |
| dermascope for skin cancer | Dermatoscope | 196 | 2.50% | 0.00% | 0/3 | $54.99 | 1.03% | 0 / 0 | Not in title: add to backend | Optional low-bid Exact test (no ad data) |
| dermatoscope skin | Dermatoscope | 193 | 3.31% | 1.92% | 0/1 | $52.99 | 0.00% | 1 / 0 | Not in title: add to backend | Keep at a low bid (0 orders on 1 ad clicks is too few at DERM's ~0.4% CVR) |
| dental photography mirrors | Photo mirror | 155 | 1.66% | 0.00% | 0/14 | $12.99 | 0.00% | 0 / 0 | Not in title: add to backend | Optional low-bid Exact test (no ad data) |
| zirc mirror | Mirror: core | 154 | 0.97% | 0.00% | 0/3 | $43.64 | 0.58% | 1 / 0 | Not for copy (competitor brand; PPC only) | Watch (only 1 ad click) |
| luz de wood dermatologia | Dermatoscope | 152 | 1.69% | 0.00% | 0/1 | $39.99 | 0.00% | 0 / 0 | Not in title: add to backend (Spanish) | Optional low-bid Exact test (no ad data) |

Additional Q3-only gaps (Q3 volume >= 450, not in the Oct list):

| Search query | Relevance | Q3 vol | Q3 click share | Ad clicks / orders | Copy (title/backend) | PPC |
|---|---|---:|---:|---:|---|---|
| dermatoscope | Dermatoscope | 22,815 | 1.03% | 231 / 1 | In current title | Already Exact in DERM: lower the bid (1 ad order, ACoS 54.7%) |
| dermatoscopio | Dermatoscope | 3,412 | 1.18% | 4 / 0 | Not in title: add to backend (Spanish) | Keep at a low bid (0 orders on 4 ad clicks is too few at DERM's ~0.4% CVR) |
| lampara de wood dermatologia | Dermatoscope | 1,153 | 0.18% | 0 / 0 | Not in title: add to backend (Spanish) | Optional low-bid Exact test (no ad data) |
| dermatoscopio profesional | Dermatoscope | 1,109 | 1.06% | 2 / 0 | Not in title: add to backend (Spanish) | Keep at a low bid (0 orders on 2 ad clicks is too few at DERM's ~0.4% CVR) |
| espejos dentales | Mirror: core | 883 | 1.55% | 5 / 0 | Missing from proposed copy: add to backend (Spanish) | Watch (only 5 ad clicks) |
| woods lamp medical grade | Dermatoscope | 750 | 0.34% | 0 / 0 | Not in title: add to backend | Optional low-bid Exact test (no ad data) |
| dermatoscope dermlite | Dermatoscope | 622 | 1.00% | 2 / 0 | Not for copy (competitor brand; PPC only) | Keep at a low bid (0 orders on 2 ad clicks is too few at DERM's ~0.4% CVR) |
| dermlite dermatoscope | Dermatoscope | 594 | 0.00% | 2 / 0 | Not for copy (competitor brand; PPC only) | Keep at a low bid (0 orders on 2 ad clicks is too few at DERM's ~0.4% CVR) |
| dermoscope for skin | Dermatoscope | 532 | 1.76% | 0 / 0 | Not in title: add to backend | Optional low-bid Exact test (no ad data) |
| intraoral mirror | Mirror: core | 518 | 0.00% | 0 / 0 | In proposed backend/bullets | Optional low-bid Exact test (no ad data) |
| intraoral mirrors dental photography | Photo mirror | 480 | 0.00% | 0 / 0 | Not in title: add to backend | Optional low-bid Exact test (no ad data) |
| zirc dental mirror | Mirror: core | 478 | 1.54% | 13 / 1 | Not for copy (competitor brand; PPC only) | Test Exact at a capped bid (1 ad order, ACoS 20.6%) |

**Titles/backend vs PPC** (all relevant gap queries from both tables, grouped by the two columns above)

| Placement | Gap queries | Action |
|---|---|---|
| Title: already there | "dental mirror", "dental mirrors", "dermatoscope" | Rank organically; no extra bids on the head term beyond the harvested Exact |
| Title candidates: in proposed backend only, high volume | "dentist mirror for inside mouth", "mouth mirror dental", "mouth mirror", "dentist mirror" | Add the missing words to titles/bullets (e.g. "Mouth Mirror") for rank weight |
| Backend: already in proposed copy | "dental mirror for teeth", "tooth mirror", "teeth mirror", "dental mouth mirror", "oral mirror", "intraoral mirror" | Nothing to add |
| Backend: add | "dermascope", "dermoscope", "dermoscopy", "dermatoscope for skin", "dermascope for skin", "woods lamp medical", "woods lamp esthetician", "espejo dental", "small dental mirror", "espejos intraorales odontologia", "dermascope for skin cancer", "dermatoscope skin", "dental photography mirrors", "luz de wood dermatologia", "dermatoscopio", "lampara de wood dermatologia", "dermatoscopio profesional", "espejos dentales", "woods lamp medical grade", "dermoscope for skin", "intraoral mirrors dental photography" | Synonyms, sizes, Spanish and dermatoscope variants (dermatoscope backend is not in the repo, so check it first) |
| Competitor brand: PPC only | "zirc mirror", "dermatoscope dermlite", "dermlite dermatoscope", "zirc dental mirror" | Brand names of others are not allowed in ILLUCO copy; test as Exact at a capped bid |
| PPC Exact: proven (harvest) | "dental mirror", "dental mirror for teeth", "dentist mirror" | `harvest_keywords.csv` + near-misses |
| PPC Exact: test at a capped bid | "mouth mirror", "dental mirrors", "teeth mirror", "dermatoscope", "zirc dental mirror" | Had ad orders but not enough to harvest |
| PPC: keep at a low bid (DERM) | "dermascope", "dermoscope", "dermoscopy", "dermatoscope for skin", "dermascope for skin", "dermatoscope skin", "dermatoscopio", "dermatoscopio profesional", "dermatoscope dermlite", "dermlite dermatoscope" | Cheap dermatoscope variants; keep each bid under the ~$1.27 DERM cap |
| PPC: watch / optional test | "tooth mirror", "dentist mirror for inside mouth", "mouth mirror dental", "woods lamp medical", "woods lamp esthetician", "dental mouth mirror", "espejo dental", "small dental mirror", "oral mirror", "espejos intraorales odontologia", "dermascope for skin cancer", "dental photography mirrors", "zirc mirror", "luz de wood dermatologia", "lampara de wood dermatologia", "espejos dentales", "woods lamp medical grade", "dermoscope for skin", "intraoral mirror", "intraoral mirrors dental photography" | Too little ad data; low-bid Exact test only if budget frees up |

- **Neither (negative):** LED/lighted, disposable, kids and rhodium queries (e.g. "dental mirror with light" 3,134 Oct searches, "dental mirror for teeth with light" 977, "lighted dental mirror" 284) and the off-category top-volume queries (hand mirror, inspection mirror, headlamp, dental tools).
- Spanish queries show ILLUCO impressions in SQP (e.g. "espejo dental" 3.62% impression share in Oct), but Spanish ad clicks converted 0 times (30 terms, $63.77): backend, not PPC.
- **Anti-fog caution:** fog queries are among ILLUCO's most consistent non-brand converters in both ads (11 orders) and SQP, but 3 of the 16 FBA return records in `293310020777.csv` (Nov 2025 - Oct 2026) carry customer comments that the mirror fogged or did not stay dry, and the proposed listing copy removes "Fog-Resistant". Decide the claim first; if it goes, drop fog terms from PPC rather than scale them.
- Dermatoscope titles use "Dermatoscope" (and "Woods Lamp" on the IDS-3100) but none of the variants; put "dermascope", "dermoscope", "dermoscopy", "dermatoscopio" and "lampara de wood" in the backend. Market median purchase prices of $50-160 on these queries mean generic dermatoscope PPC should stay bid-capped.

## Business Report context (window not stated in the export)

| Family | Sessions | Units | Unit session % | Ordered product sales | % of sales |
|---|---:|---:|---:|---:|---:|
| dermatoscope | 836 | 9 | 1.1% | $8,680.00 | 36.5% |
| 5-pack kit | 2,236 | 69 | 3.1% | $7,650.00 | 32.2% |
| heads | 614 | 67 | 10.9% | $4,395.00 | 18.5% |
| single | 1,019 | 126 | 12.4% | $2,877.30 | 12.1% |
| photo | 20 | 1 | 5.0% | $165.00 | 0.7% |
| other (headlight, Hansderma brushes) | 63 | 2 | 3.2% | $19.98 | 0.1% |
| **Total** | 4,788 | 274 | 5.7% | $23,787.28 | 100.0% |

- Replacement heads and the single mirror convert well (heads 1X 17.4%, single B0G2DYRY7T 16.8% unit session %). The 5-pack with handles converts poorly (B0FCZBD1KY 2.3%, B0FCMVZH31 1.5%, B0F84TKGLS 6.7%), so pushing more paid clicks to the 5-pack pages is the most expensive way to grow; fix that listing first.
- The Business Report and ad reports cover different (and, for the Business Report, unknown) windows, so no TACoS is computed.

## Files

- `analysis/ppc_audit.md` (this report)
- `analysis/negative_keywords.csv` (150 rows; ASIN rows use match_type "negative product target (ASIN)" because Amazon blocks ASINs with negative product targeting, not negative keywords)
- `analysis/harvest_keywords.csv` (6 rows; extra `notes` column)
- `analysis/sqp_top_queries.csv` (154 rows: top 30 by volume, ILLUCO purchase wins and relevant gaps for Oct 2026 and Q3 2026)
- `scripts/ppc_sqp_audit.py` regenerates all four: `python3 -I scripts/ppc_sqp_audit.py`
