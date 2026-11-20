# Apply today: negative keywords and pauses (Sponsored Products)

Advertising console > Campaign manager. No budget changes. About 15 minutes.
Source: `analysis/ppc_audit.md` (search terms Sep 17 - Nov 20, 2026). Tick each box as you go.

## 1. Pause these keywords

Campaign > ad group > **Targeting** tab > find the keyword > switch it off.

| Done | Campaign | Keyword | Match | Why |
|---|---|---|---|---|
| [ ] | BRAND-KW | dental | Phrase | $191 spend, 2 orders ($235); 92% of its spend went to handpieces, loupes, drills, materials |
| [ ] | BRAND-KW | dental tools home use | Broad | $168 spend, 2 orders ($350); consumer intent |
| [ ] | BRAND-KW | dental hygienist must haves | Exact | $16 spend, 0 orders; gift-list search |
| [ ] | HEADS-KW | dental mirror | Broad | $8.55 spend, 0 orders (the converting "dental mirror" PHRASE keyword stays on) |
| [ ] | DERM | dermatoscope otoscopes & ophthalmoscopes | Broad | Off-target keyword, 0 orders |
| [ ] | DERM | dermatoscope iphone | any | Phone-attachment search; ILLUCO units are handheld |
| [ ] | DERM | smartphone dermatoscope | any | Phone-attachment search |
| [ ] | DERM | dermatoscope for smart phone | any | Phone-attachment search |
| [ ] | DERM | dermatoscope attachment for iphone | any | Phone-attachment search |

Not a pause, so not applied here: cutting the DERM "dermatoscope" exact bid from $2.31 to about $1.27 (your call).

## 2. Add negative keywords and negative products

Campaign > ad group > **Negative targeting** tab > **Add negative keywords** > pick the match type > paste the block (one per line) > Add > Save. For ASINs use **Add negative products**.
If an ad group does not offer negative keywords (the CATEGORY ad group is a category target), add only its negative products and skip its keyword blocks.

### BRAND-KW

Campaign: `VIC-M-SP-Dental Mirror Branded and Product KW`  
Ad group: `VIC-M-SP-Dental Mirror | Branded and Product KW | Catch All`

- [ ] **Negative exact** (3; $61.42 spent on these with 0 orders)

```
dental mirror
dental hygienist must haves
dental mirror anti fog
```

- [ ] **Negative phrase** (40; $212.28 spent on these with 0 orders)

```
rhodium
instruments
with light
handpiece
loupes
materials
home
drill
high speed
rodio
composite
scalers
file
radio
loupe
lupas
lighted
ultrasound
hand piece
ultrasonic
ultrasonido
burs
cleaning
kids
disposable
scaler
plastic
automotive
child
classroom
hand mirror
led
light up
makeup
mechanic
pick
plaque
rechargeable
tartar
telescoping
```

### HEADS-KW

Campaign: `VIC-BOF | SP | Dental Mirror HEAD 1x 2x 3x | SP Exact Target + Prod Exp + Brand Exp`  
Ad group: `Dental Mirror Head 1x 2x 3x | SP Exact Target + Prod Exp + Brand Exp | SP | BOF`

- [ ] **Negative exact** (5; $81.51 spent on these with 0 orders)

```
dental mirror
dental mirrors
dental mirror for teeth
magnifying dental mirror
zirc dental mirror
```

- [ ] **Negative phrase** (24; $40.31 spent on these with 0 orders)

```
with light
plastic
rhodium
lighted
radio
rhoid
automotive
child
classroom
cleaning
disposable
hand mirror
home
kids
led
light up
makeup
mechanic
pick
plaque
rechargeable
rodio
tartar
telescoping
```

### CATEGORY

Campaign: `VIC-M- SP | Dental Mirror Category | Dental Mirror | All Single Multipack`  
Ad group: `VIC-M-SP-KWT- Dental Mirror Category- Dental Mirror- All Multipack`

- [ ] **Negative phrase** (22; $40.19 spent on these with 0 orders)

```
with light
rhodium
rechargeable
instruments
led
plastic
rodio
radio
automotive
child
classroom
cleaning
disposable
hand mirror
kids
light up
makeup
mechanic
pick
plaque
tartar
telescoping
```

- [ ] **Negative products (ASIN)** (2; $19.63 spent on these with 0 orders)

```
B077T1DWDR
B0DYP3KGTX
```

### AUTO-1PK

Campaign: `VIC-SP-AUTO-DTMR-1PK-ALL`  
Ad group: `illuco Dental Mirror Collection - 1pk`

- [ ] **Negative phrase** (21; $0.00 spent on these with 0 orders)

```
automotive
child
classroom
cleaning
disposable
hand mirror
kids
led
light up
lighted
makeup
mechanic
pick
plaque
plastic
rechargeable
rhodium
rodio
tartar
telescoping
with light
```

- [ ] **Negative products (ASIN)** (1; $8.44 spent on these with 0 orders)

```
B0DYP3KGTX
```

### AUTO-HEADS

Campaign: `VIC-SP-AUTO-MRHD-5PK-ALL`  
Ad group: `VIC-Mirror Head 5pk Set All`

- [ ] **Negative phrase** (25; $2.57 spent on these with 0 orders)

```
composite
instruments
lupas
automotive
child
classroom
cleaning
disposable
hand mirror
home
kids
led
light up
lighted
makeup
mechanic
pick
plaque
plastic
rechargeable
rhodium
rodio
tartar
telescoping
with light
```

### DERM

Campaign: `SP-Dermatoscope-KWs-All`  
Ad group: `VIC-SP-Dermatoscope-KWs-All`

- [ ] **Negative phrase** (7; $10.51 spent on these with 0 orders)

```
otoscope
ophthalmoscope
phone
esthetician
loupe
iphone
smartphone
```

## 3. Check after 7 days

- Search term report: none of the negated terms should appear again in these ad groups.
- "dental mirror" orders should keep coming through CATEGORY (where it converts at 23% ACoS).
- If brand sales ("illuco ...") drop, a negative is too broad: tell me which ad group.

Totals: 150 negatives (8 exact, 139 phrase, 3 ASIN) and 9 pauses. Negated terms spent $476.86 with 0 orders; with the 3 BRAND-KW pauses the audit estimates $639 (28%) less spend for $585 of sales at risk.
