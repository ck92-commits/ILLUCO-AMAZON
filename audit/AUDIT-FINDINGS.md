# Dental Mirror Audit: Initial Findings

**Date:** Thu 11/05/2026 · **By:** Cenk · **Status:** Draft for the manager review on Tue 11/10/2026
**Source:** Public Amazon.com pages only (search results, product pages, reviews), pulled 11/05/2026.
**Not included yet:** Sales, sessions, conversion rate and PPC data. Those come from Seller Central and the Ads console (see `NEEDS-LIST.md`).

Files in this folder:
- `ILLUCO_Dental_Mirror_ASIN_Tracker.xlsx`: the Excel report, one row per ASIN, plus keyword, competitor, review, issue and needs tabs
- `amazon-rules-checklist.md`: Amazon rules that apply to our listings, images, A+, reviews, promotions and claims
- `NEEDS-LIST.md`: data, facts, assets, access and approvals we need
- `data/`: raw data behind every number in this document

> Rule for this project: nothing below has been changed on Amazon. Everything is a recommendation until the manager approves it.

---

## 1. The 8 things that matter most

1. **The low rating comes from having very few reviews.** Our 15 dental mirror ASINs have only **9 ratings in total**. One unhappy buyer can pull a whole family down to 3.4★ or 2.0★. The fix is more honest reviews (Vine, the Request a Review button) plus fixing the cause of the one real complaint.
2. **Shoppers can't find us.** ILLUCO does not appear in the first 48 results for "dental mirror", "mouth mirror dental", "dental mirror with light", "dental photography mirror" or "double sided dental mirror". We rank only for long-tail terms such as "anti fog dental mirror" and "autoclavable dental mirror".
3. **We charge 2 to 4 times more per mirror than professional brands, with no proof on the page.** ILLUCO's handle 5-pack works out to $19–$28 per mirror. Hu-Friedy is $9.19, Zirc Crystal HD $8.00 and Artman sets $4.60. 3 of our 5 written reviews say "expensive".
4. **One complaint may point to a real product problem.** A verified 1★ review says: *"Waste of money. It's only clear the first couple of times you would use it."* We promise "100 autoclave cycles". This must be checked before we send more traffic. Competitors get the same complaint, so if we can **prove** durability it becomes our strongest selling point.
5. **The listings confuse buyers.**
   - "Autoclavable 100X" sits next to "1X/2X/3X Magnification", so it reads like 100X magnification.
   - The handle pack never says the mirror size. Photos show **#4**, but most competitors sell **#5**.
   - The head-only pack says "universal fit", but a review says it "only fits specific handles".
   - The photo mirror costs $165, and the title doesn't say it is **one mirror**.
6. **Some content may break Amazon rules.** The Brand Story says "Best selling dental mirrors". The A+ says "Quality guaranteed". The "40% clearer than standard mirrors" claim has no proof shown. See `amazon-rules-checklist.md`.
7. **The single mirror listing (B0G2DYRY7T) doesn't match the brand.** Its title has no brand name, the photos look like stock images, and its A+ advertises 2X/3X magnification and replaceable heads, which that ASIN doesn't offer.
8. **The photo mirrors and the single mirror are not Prime.** Both are seller-fulfilled (FBM), so they arrive about 3 days later than our FBA mirrors.

---

## 2. What we sell: 4 dental mirror families, 15 ASINs

| Family | ASINs | Price | Per mirror | Fulfilment | Rating | BSR in Dental Mirrors | Est. units/mo* |
|---|---|---|---|---|---|---|---|
| **A. Handle 5-Pack** (1X/2X/3X × dark/light blue) | B0FCZBD1KY, B0F84VWGG5, B0F84TKGLS, B0FCMVZH31, B0F85B5BDC, B0F857HKBG | $95 / $125 / $140 | $19–$28 | FBA (Prime) | **3.4★ (5)** | #48 | ~15 |
| **B. Head-Only 5-Pack** (#4, cone socket, 1X/2X/3X) | B0FBPG5CS9, B0FCHH2SQB, B0FCJY3H9H | $60 / $90 / $105 | $12–$21 | FBA (Prime) | **2.0★ (2)** | #80 | ~6 |
| **C. Single Mirror w/ Handle** | B0G2DYRY7T | $19.99 | $19.99 | FBM (no Prime) | 5.0★ (2) | #57 | ~10 |
| **D. Photo Mirror** (S/M/L occlusal, lingual, buccal) | B0F86CJ7R6, B0FCNG7T9P, B0F86DNNSV, B0FCNRP7NF, B0FCN9V5G4 | $165 each | $165 | FBM (no Prime) | none (0) | #461 | ~1 |

\*Estimate from a third-party scraper, not Amazon data. To be replaced with Business Report numbers.

Other ILLUCO products found (not audited yet): dermatoscopes IDS-1000, IDS-1100, IDS-3100 and IDS-9100, and a wired headlight for dental loupes.

---

## 3. Listing content audit

### Titles
| Problem | Where | Fix |
|---|---|---|
| Brand name is missing from the title field. It shows only in the browser tab. | All | Start every title with "ILLUCO". |
| "Autoclavable 100X" reads like magnification | All | "Autoclavable up to 100 Cycles" |
| No mirror size (#4 / 22 mm) | A, C | Add the size to the title and bullet 1 |
| No socket/thread type | A | Add "Cone Socket" if confirmed |
| Missing words buyers use: *mouth mirror, front surface, intraoral, double-sided, photography, orthodontic* | All | Use them in titles and bullets (after keyword volume check) |
| Variant name "1X Magnification" is odd for a flat mirror | A, B | "Standard (1X)", "Magnifying 2X", "Magnifying 3X" |
| Title starts with "1 Dental Mirror…" | C | Brand first, then product |
| Pack quantity not stated at $165 | D | "1 Photo Mirror, Large Occlusal, 137 × 76 mm…" |

### Bullets and description
- **A (handle pack):** 7 bullets with good facts (German glass, dielectric front-surface coating, autoclave temperatures). It never states the size, socket type, handle material or length, or what is in the box.
- **B (head pack):** 5 bullets of only 49–84 characters, the weakest content we have. It needs size, thread type, a list of compatible handles, care instructions and box contents.
- **C (single):** 5 clean bullets, but they copy the 5-pack.
- **D (photo):** It says "competitive pricing" at $165 and "unparalleled quality". Remove both. It also needs the size of each shape and the number of mirrors per box.
- **Description:** Blank on all listings. That is normal when A+ is live, but the plain-text fallback is empty.

### Specs and attributes (item details table)
- Photo mirrors list the model number as **"IDMXXX"**, which is a placeholder.
- The handle 5-pack lists a weight of **2 pounds**, which is probably wrong. The head pack lists **1 × 1 × 1 inches**.
- Missing everywhere: material, mirror diameter, coating type, sterilization temperature, number of items, and whether the mirror is single- or double-sided.

---

## 4. Images, A+, video, Brand Store

| | A. Handle 5-Pack | B. Head 5-Pack | C. Single | D. Photo |
|---|---|---|---|---|
| Images | 6, clean blue infographics | 5, main image includes the box | 4, stock-style, mirror small in main image | 7, good mix plus lifestyle shots |
| Video | Yes | Yes | **No** | **No** |
| A+ | Yes (3 banners + Brand Story) | Yes | Yes, but copied from the 5-pack (wrong features) | Yes, good shape guide |
| Brand Story | Yes | Yes | **No** | Yes |

**What works:** The brand look is consistent (navy and blue). The infographics make the specs clear (99% reflectance, dielectric coating, 100 cycles). The photo mirror A+ explains each shape well.

**What's missing or weak:**
- **No proof images.** Our main benefits are no ghost image, 99% reflectance and anti-fog, and none of them is *shown* (no side-by-side with a standard mirror, no fog test, no autoclave test). Proof is what justifies a 2–4× price.
- **The 1X/2X/3X image** uses three nearly identical teeth illustrations, so the magnification difference is hard to see.
- **No size chart** for the handle and head packs. Only the Large Occlusal photo mirror has a dimension image.
- **No in-use clinical shot** (gloved hand, real patient or typodont, loupe light).
- **No handle-compatibility chart** for the head pack.
- **No "what's in the box" image** for the handle pack.
- **Photo mirror image 6 has a typo:** "Autocalvable".
- **A+ banners cut text across image edges.** For example, "Our direct coating method…" starts on one banner and finishes on the next. This looks broken on mobile.
- **A+ has no comparison chart.** Nothing helps the buyer choose between the handle pack, head pack, single mirror and photo mirrors, or cross-sell between them.
- **A+ alt text is empty** on every module.
- **The single mirror's A+** shows "1x, 2x, 3x Magnification" and "Replaceable Heads". That ASIN is 1X only.
- **The Brand Store exists** ("Visit the Illuco Store"). Its layout is not reviewed yet; that is next. The brand is written "Illuco" in some places and "ILLUCO" in others.

---

## 5. Search visibility: 14 searches checked (US, logged out, 11/05)

| Search term | ILLUCO best organic rank | ILLUCO ad seen | Who is #1 |
|---|---|---|---|
| dental mirror | **not found** | #37 (single) | ffresiss LED mirror, $9.88, 5,954 ratings |
| dental mirror with light | **not found** | – | ffresiss LED mirror |
| mouth mirror dental | **not found** | – | Surgical Online 12-pack #5, $12.99 |
| dental photography mirror | **not found** | – | Ceonam photo kit, $35.99 |
| double sided dental mirror | **not found** | – | JMU double-sided #5, $9.49 |
| zirc crystal hd mirror | not found | – | Zirc |
| anti fog dental mirror | **#3** (single), #12 (head pack) | – | ffresiss LED mirror |
| autoclavable dental mirror | #4 (single), #15 (handle pack) | – | 10-pc #5 set, $10.90 |
| magnifying dental mirror | #9 (single) | **#1** (head pack) | – |
| front surface dental mirror | #17 (single) | – | – |
| hu-friedy mouth mirror | #26 (single) | #17 | Hu-Friedy |
| dental mirror heads cone socket | #30 (head pack) | #7 | – |
| rhodium dental mirror | not found | **#2, #7** | Artman gold set |
| dental mouth mirror #5 front surface | not found | #22 | – |

**What this tells us:**
- The big terms belong to $4–$10 consumer mirrors with thousands of reviews. We can't win those head-on with 9 ratings.
- Our best chances are **pro and feature terms**: anti-fog, autoclavable, magnifying, front surface, cone socket, photography mirror, and the size terms (#4, #5).
- **Magnifying (2X/3X)** is something most pro competitors don't sell. Push it.
- We are running ads on **"rhodium dental mirror"** (we use a dielectric coating, not rhodium) and **"#5 front surface"** (our heads look like #4). Check both in the search term report; they may be wasting spend.
- Ads from 3 different ILLUCO families show up on different terms. The PPC audit will check whether campaigns are split by family.

---

## 6. Reviews: every ILLUCO written review (9 ratings, 7 written)

| Family | Stars | Vine? | What they said |
|---|---|---|---|
| A | **1★** | No (verified, Apr 2026) | "Waste of money. It's only clear the first couple of times you would use it." |
| A | 5★ | No | Good quality but "fairly expensive". Front surface helps with ghosting. Uses it for scuba tanks. |
| A | 5★ | Vine | No fog, good grip. *"Company might make better sales of one to a box for personal use."* |
| A | 5★ | Vine | Feels professional, distortion-free, fog clears in a split second, premium box. |
| A | 4★ | Vine | "Expensive but good quality". Uses it to look inside walls. |
| B | 4★ | Vine | *"It only fits specific type of mirror handles, so please check your mirror type before purchasing."* Screw part longer, neck softer. |
| B | (1 star-only rating, no text) | – | – |
| C | 5★ | No | "Very happy with my new dental mirror". |
| D | – | – | No ratings yet. |

**Complaint themes:**
1. **Coating or clarity may wear off** (A). This is a product question. Investigate first.
2. **Fit and compatibility** (B). This is a listing question. State the thread type and list compatible handles.
3. **Price** (A, 3 of 5 reviews). This is a proof and value question. Show why the mirror is worth it.
4. **Wrong audience.** 3 of the 5 family-A reviews came from Vine reviewers, none of them dental professionals. 2 of the 5 reviewers used the mirror for non-dental jobs (scuba tanks, inside walls). These reviews don't help a dentist decide.

---

## 7. Competitors

| Segment | Brand (ASIN) | Price | Per mirror | Rating | Est. units/mo |
|---|---|---|---|---|---|
| Pro heads | Hu-Friedy MIR5DS/6 (B0769MYHBB) | $55.14 | $9.19 | 4.7★ (72) | ~6 |
| Pro premium | Zirc Crystal HD #5 12/pk (B0D7QV3WY1) | $95.99 | $8.00 | 5.0★ (11) | ~9 |
| Pro set w/ handles | Artman gold set of 5 (B077T1DWDR) | $22.99 | $4.60 | 4.3★ (50) | ~56 |
| Pro heads | Artman double-sided cone socket ×7 (B0DKKHZBKT) | $30.35 | $4.34 | 4.2★ (9) | ~34 |
| Photo kit | Ceonam 4 rhodium + LED/fan (B0CQ5GJQ3H) | $35.99 | $9.00 | 4.1★ (127) | ~158 |
| Photo set | Frienda 5 pcs (B096MLN8B5) | $11.19 | $2.24 | 4.5★ (298) | ~134 |
| Consumer #1 | ffresiss LED mirror (B08GSQWY5S) | $9.88 | $9.88 | 4.5★ (5,954) | ~2,261 |

**What competitors do better:**
- They **name the size and thread** in the title (#5, cone socket, European thread). Buyers filter on those.
- They use **plain words dentists search for**: "front surface", "mouth mirror", "double sided", "rhodium".
- **Zirc** puts one clear proof point up front: "40% brighter than rhodium".
- **Ceonam** sells photo mirrors as a **kit** (4 shapes plus a handle) and outsells everyone in that segment.
- **Hu-Friedy** sells on brand trust, with reviews from real dentists.

**Where competitors are weak (our opening):**
- **Artman:** "distorted after 3 months", "won't accept standard screw-in heads", flat handle reflects light into eyes.
- **Ceonam:** "scratch easily", "stained after 2–3 autoclave cycles", battery dies, arrived broken.
- **Frienda:** one buyer measured **57% reflectance**; others say "see-through" and "fogs".
- **Hu-Friedy:** a buyer suspects counterfeits.

Buyers in this category are complaining about exactly what ILLUCO claims to solve: 99% reflectance, front surface with no ghosting, and stain-free after autoclaving. **If our test data backs this up, proof-led images and video are the core strategy.** If it doesn't, we must fix the product first.

---

## 7a. Is the market big enough for us?

- The **professional** dental mirror segment on Amazon is small. Hu-Friedy and Zirc each sell an estimated 6–9 units a month.
- The **consumer** segment is huge. The #1 LED mirror sells an estimated 2,000+ a month at $9.88.
- **Decision needed:** stay pro-only, or add a consumer entry offer? Our single mirror at $19.99 already sits between the two. One Vine reviewer even asked for a single-mirror box.

---

## 8. Early recommendations (need approval before 11/10 sign-off)

**A. Fix now (small, low risk). Ready once the manager says OK:**
1. Fix the photo mirror model number ("IDMXXX") and the wrong weights and dimensions.
2. Fix the "Autocalvable" typo on the photo mirror image.
3. Remove "competitive pricing" and "unparalleled" from the photo mirror bullets.
4. Remove or support "Best selling" (Brand Story) and "Quality guaranteed" (A+).
5. Turn on Request a Review for every order, and confirm Vine enrollment for families A, B and D.

**B. Big changes (after approval):**
1. **Titles, bullets and backend terms rewrite**, starting with family B (head pack, weakest content) and family A (handle pack, most sales).
2. **New image set for each family:** a proof image (ghost-image and reflectance comparison), a size and thread chart, an in-use clinical photo, what's in the box, and a clearer 1X/2X/3X demo.
3. **A+ rebuild:** mobile-first modules, an ILLUCO comparison chart (handle pack, heads, single, photo), alt text on every image, and no prohibited claims.
4. **Video:** 15–30 s demos (fog test, ghost-image test, autoclave proof, size). Reuse them for Sponsored Brands Video.
5. **Move the single mirror and photo mirrors to FBA** to get the Prime badge.
6. **Photo mirror kit ASIN** (all 5 shapes) to compete with Ceonam's kit.
7. **Consider a #5 size line**, the size most dentists use.
8. **PPC rebuild by family and keyword group**, once the search term report is in. Pause mismatched terms (rhodium, #5) if they don't convert.

**C. Product and QC (before pushing traffic):**
1. Root-cause the "only clear the first couple of times" complaint.
2. Get test reports for 99% reflectance and 100 autoclave cycles.
3. Write care instructions (allowed cleaners, ultrasonic yes or no).
4. Confirm the thread standard and list compatible handles.
