# New Dental Mirror Listings: What We Need for a Perfect Listing

**Date:** 11/18/2026 · **Owner:** Cenk · **Products:** the 7 new mirror UPCs (loupes come next)
**Fill-in workbook:** `ILLUCO_New_Mirror_Listing_Input.xlsx`, with tabs for facts, variations, copy, images, Amazon items and the launch plan.
**Rules behind this:** `../audit/amazon-rules-checklist.md`

| Model | Product | UPC |
|---|---|---|
| IDM-2C101DB | Grand Dental Mirror 1x (Dark Blue) | 810194860836 |
| IDM-2C101LB | Grand Dental Mirror 1x (Light Blue) | 810194860843 |
| IDM-2C102DB | Grand Dental Mirror 2x (Dark Blue) | 810194860850 |
| IDM-2C102LB | Grand Dental Mirror 2x (Light Blue) | 810194860867 |
| IDM-2CD41DB | Double-sided Dental Mirror (Dark Blue) | 810194860874 |
| IDM-2CD41LB | Double-sided Dental Mirror (Light Blue) | 810194860881 |
| IDM-3CD41H | Double-Sided Dental Mirror Head | 810194860898 |

---

## 1. Already confirmed (11/18)

- **Product type:** `PROFESSIONAL_HEALTHCARE`. The live ILLUCO mirrors, Hu-Friedy, Zirc and Ceonam all use it. Artman uses `LAB_SUPPLY`.
- **Category:** Industrial & Scientific › Professional Dental Supplies › Handpieces & Instruments › Mirrors (browse node **8297616011**).
- **UPCs:** all 7 mirror UPCs and all 5 loupe UPCs have valid check digits. None of them is on Amazon yet.
- **How the live listings show options:** families A and B use a single "Model" selector that mixes magnification and colour (for example "1X Magnification Dark Blue Handle"). The photo mirrors use "Size". For the new listings, use **separate Colour and Magnification selectors** so shoppers see colour swatches.

---

## 2. What we need from Amazon (Seller Central)

| # | Item | Where | Why |
|---|---|---|---|
| 1 | **Exact brand name** in Brand Registry, plus your Brand Representative role | Brand Registry | The live store says "Illuco" but titles say "ILLUCO". The brand field must match Brand Registry and GS1 exactly. |
| 2 | **Upload template for PROFESSIONAL_HEALTHCARE** | Catalog › Add Products via Upload › Download spreadsheet | The only full list of required fields, allowed values and allowed variation themes |
| 3 | **Listing check per UPC** | Catalog › Add a Product › search the UPC | Shows any "listing limitations apply" warning (approval or gating) |
| 4 | **GS1 match** | Add a Product (Amazon flags a mismatch) + our GS1 account | Amazon checks each UPC against GS1. A brand mismatch blocks the listing. |
| 5 | **Search volume** | Growth › Product Opportunity Explorer | Real search volume for picking title and backend keywords |
| 6 | **Brand Analytics**: Top Search Terms + Search Query Performance | Brands › Brand Analytics | Which terms convert for us today |
| 7 | **Search term report** for live mirror ads, last 60 days | Ads console › Reports | Keywords that already sell |
| 8 | **Premium A+ + Brand Story** | Brands › A+ Content Manager | Premium A+ is now free for brand owners. One comparison chart per page. |
| 9 | **Video upload** | Catalog › Upload and manage videos | Listing video, later reused for Sponsored Brands Video |
| 10 | **FBA barcode setting** | Settings › Fulfillment by Amazon | Brand owners can now ship on our own UPC, no Amazon (FNSKU) sticker needed. Commingling ended for inventory shipped from 03/31/2026.¹ |
| 11 | **FBA prep guidance** for glass | Send to Amazon | Amazon stopped prepping and labeling FBA inventory on 01/01/2026, so we prep ourselves.² Glass must survive a 3-foot drop test, or be bubble-wrapped or overboxed.³ |
| 12 | **FBA capacity limits** | Inventory › Capacity monitor | Make sure the launch stock can be sent |
| 13 | **Vine** (after units arrive at FBA) | Advertising › Vine | Up to 30 units per parent. Fee $0 / $75 / $200 depending on units. |
| 14 | **Amazon Business price + quantity discounts** | Manage pricing › Business price | Dental offices buy in bulk |
| 15 | **Amazon Attribution tags** | Ads console › Amazon Attribution | Measure Google, social and creator traffic. Earns the Brand Referral Bonus. |
| 16 | **Manage Your Experiments** | Brands › Manage Experiments | A/B test the main image, title and A+ once there is traffic |
| 17 | **Coupon / Prime Exclusive Discount eligibility** | Advertising › Coupons / PED | New ASINs with 0 ratings qualify. Prime (FBA) is required. |
| 18 | **Compliance fields** in the template | Inside the template | Shows what FDA or regulatory proof Amazon may ask for |

¹ Every source on the barcode change is a third-party seller blog. Confirm in Seller Central. Sources: [PPC Land](https://ppc.land/amazon-ends-fba-commingling-on-march-31-what-really-changes-for-sellers/), [SalesDuo](https://salesduo.com/blog/amazon-commingling-stickerless-inventory-fnsku-labeling-guide/)
² [Pattern](https://www.pattern.com/blog/amazon-is-ending-fba-prep-services-in-2026), [Fulfill.com](https://www.fulfill.com/blog-posts/amazon-fba-prep-shutdown)
³ [Seller Central: Packaging glass, ceramic, breakable and fragile units](https://sellercentral.amazon.com/gp/help/external/G200280160) (login needed)

---

## 3. What we need from ILLUCO (product team, ops, manager)

The full list is in the workbook tab **"SKU Fact Sheet"**: 42 fields per SKU, with yellow cells to fill. The ones that matter most:

**Open questions that block the copy:**
1. What does **"Grand"** mean: a larger head (#5)? A longer handle? Something else?
2. **Head size** (#4 / #5) and diameter in mm for every SKU.
3. **Pack count**: 1 mirror or 5? This sets the price per mirror, the title and the main image.
4. Grand mirrors: **single- or double-sided?** Double-sided: **1X only?**
5. Is "Grand 1x Dark Blue" a **new product**, or the same mirror as the live 5-pack (B0FCZBD1KY) in a different pack size? If it is the same mirror, it may belong in that family. Otherwise it gets a new parent listing.

**Facts and proof:**
- Glass and coating (front surface? dielectric?), reflectance % **with a test report**
- Sterilization limits (temperature, time, max cycles) **with a test report**, allowed cleaners, and whether ultrasonic cleaning is OK
- Socket/thread type and compatible handle brands
- Handle material and whether it can be autoclaved, total length, weight, what's in the box, country of origin
- Supplied sterile or non-sterile (expected: non-sterile, sterilize before first use)

**Packaging and FBA:** unit box size and weight; UPC printed on the box and scannable; drop-test result; carton count, size and weight.

**Compliance:**
- FDA establishment registration and device listing numbers. Mouth mirrors are Class I, 21 CFR 872.4565, product code EAX.
- GS1 owner and brand name.
- Prop 65 material check.

**Commercial (manager):** price, Business price tiers, landed cost and margin, launch stock and ship date, Vine fee, PPC budget.

**Assets:** samples of every SKU for the photo and video shoot.

---

## 4. What the "perfect listing" looks like

**Parent listings (workbook tab "Variation Plan"):**
- **P1 Grand Dental Mirror:** the 4 Grand SKUs, with Colour and Magnification as separate selectors.
- **P2 Double-Sided Dental Mirror:** the 2 double-sided colours.
- **Double-sided head:** its own listing for now. Do *not* put it in head family B (2.0★), and do not borrow reviews from other families.
- Start new parents fresh instead of merging into family A (3.4★), unless it is the exact same product.

**Copy (workbook tab "Content Builder", with live character counters):**
- **Title, max 75 characters:** brand + product + key fact + colour. Example draft (67 characters): `ILLUCO Grand Front Surface Dental Mirror with Handle, 1X, Dark Blue`. Add the size or pack count once confirmed.
- **Item Highlights, max 125 characters:** size | pack | autoclave limit | thread type | anti-fog.
- **5 bullets, max 255 characters each**, sentence case:
  1. Size and fit
  2. Clear view (front surface, no ghost image)
  3. Anti-fog
  4. Sterilization and care
  5. What's in the box
- **Backend search terms, under 250 bytes:** synonyms only, with no brand names and no repeats from the title.
- **Never write:** "FDA approved", "antibacterial", "best-selling", "guaranteed", "competitive pricing", or "rhodium" (unless the coating really is rhodium). Use 99%, 100 cycles or 40% only with proof.

**Images, 7–9 per ASIN plus video (workbook tab "Image & Video Plan"):**
- Main image: product only, pure white background, fills about 85% of the frame, 2000 px+.
- Then, in order:
  1. Size and spec chart
  2. **Proof**: our mirror next to a standard one, no ghost image
  3. Anti-fog test
  4. 1X vs 2X on a real tooth, or double-sided in use
  5. Fit chart
  6. Gloved hand in use
  7. Care and sterilization
  8. What's in the box
- Colour swatches.
- **Video, 15–30 s:** fog test, ghost-image test, 1X vs 2X. Cut a 16:9 version (6–45 s, captions, works on mute) for Sponsored Brands Video.
- **Premium A+:** hero banner, proof, size and fit, care, and **one comparison chart** of all ILLUCO mirrors. Design for mobile first. Also remove "Best selling dental mirrors" from the Brand Story.

**Offer:**
- FBA (Prime). Amazon Business tiers.
- Real prices only (Amazon checks reference prices since 04/23/2026).
- Optional launch coupon.

**Reviews:** Vine for each parent as soon as stock arrives, plus Request a Review on every order. Nothing else.

---

## 5. Launch plan (workbook tab "Launch Plan")

| Step | What | Owner | Approval | Target |
|---|---|---|---|---|
| 1 | Fill SKU Fact Sheet + answer the 5 open questions | Product team | – | Day 1–3 |
| 2 | Pull the 18 Amazon items | Cenk | – | Day 1–3 |
| 3 | Confirm price, cost, stock, FDA registration, GS1 | Manager / ops | **Manager** | Day 3 |
| 4 | Write titles, highlights, bullets, backend terms | Cenk | **Manager** | Day 4–5 |
| 5 | Photo + video shoot | Design team | – | Day 4–10 |
| 6 | Create parents + children from the template | Cenk | – | Day 6 |
| 7 | Upload images and video; submit Premium A+ (3–7 day review) | Cenk / design | **Manager** (A+) | Day 10–11 |
| 8 | Prep (fragile glass), label, Send to Amazon | Ops | – | Day 7–12 |
| 9 | On FBA receipt: Vine + Request a Review routine | Cenk | **Manager** (Vine fee) | Receipt day |
| 10 | Sponsored Products launch (proven terms + auto) | Cenk | **Manager** (budget) | Receipt day |
| 11 | Optional coupon / Prime Exclusive Discount | Cenk | **Manager** | Week 1 live |
| 12 | Attribution tags → Chiru, Shery, Annabelle | Cenk | – | Week 1 live |
| 13 | Weekly: sessions, CVR, ACoS/TACoS, reviews, rank; A/B test main image | Cenk | – | Weekly |

---

## 6. Loupes (next, same kit)

These 5 loupes were in the same UPC table. None appeared in the 11/05 ILLUCO brand search on Amazon. They are listed in the workbook tab "Loupes (next)".

| Model | Product | UPC |
|---|---|---|
| IAL-1055 | 5.5x Angled Loupes | 810194860782 |
| IFL-1030G | 3.0x Flip-Up Headband Loupes | 810194860171 |
| IAL-1030F | 3.0x Ergo Flip-Up Loupes | 810194860751 |
| IAL-1040F | 4.0x Ergo Flip-Up Loupes | 810194860768 |
| IAL-1055F | 5.5x Ergo Flip-Up Loupes | 810194860775 |
