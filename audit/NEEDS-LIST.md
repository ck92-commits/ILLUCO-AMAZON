# Needs List: Dental Mirror Revamp

**Updated:** 11/05/2026 · **Owner:** Cenk
Everything we need to finish the audit (due 11/10) and start changes (due 11/20).
The same list is in the Excel tracker (tab "Needs List") with a status column.

Items needed by **11/09** block the 11/10 findings review.

## Data from Seller Central, Ads console and Finance

| # | What we need | Why | From | Needed by |
|---|---|---|---|---|
| 1 | Business Report by child ASIN: sessions, page views, units, sales, unit session % - last 30, 60, 90 days | Fill sales + conversion columns; find where traffic leaks | Cenk (Seller Central) | 11/09/2026 |
| 2 | Sponsored Products search term report + targeting report, last 60 days | Find wasted spend and winning keywords for PPC audit | Cenk (Ads console) | 11/09/2026 |
| 3 | Sponsored Brands + SB Video campaign reports, last 60 days; current budgets, bids, campaign list | PPC audit and new structure | Cenk (Ads console) | 11/09/2026 |
| 4 | Search Query Performance (brand + ASIN view) and Top Search Terms for 'dental mirror' terms | Real search volume and our share; keyword plan | Cenk (Brand Analytics) | 11/09/2026 |
| 5 | Returns report with reasons + Voice of the Customer (NCX) for all mirror ASINs | Find the real product issues behind low ratings | Cenk (Seller Central) | 11/09/2026 |
| 6 | Full list of ALL active ILLUCO ASINs with parent/child structure (dental mirrors + dermatoscopes + headlight + any others) | Public search found 15 mirror ASINs; we may be missing some | Cenk (Inventory report) | 11/09/2026 |
| 7 | Current backend search terms, item attributes and A+ content list per ASIN | Baseline before rewrite | Cenk (Seller Central) | 11/09/2026 |
| 8 | Landed cost / margin per ASIN and target ACoS | Needed to set PPC budgets and any price change | Manager / Finance | 11/09/2026 |
| 9 | Vine status: which parents are enrolled, units left, Vine credits/cost | Plan to grow review count fast and within the rules | Cenk (Seller Central) | 11/09/2026 |

## Product facts to confirm (product / supplier / QC)

| # | What we need | Why | From | Needed by |
|---|---|---|---|---|
| 10 | Mirror head size for handle pack and single mirror (#4 = 22 mm?) and why no #5 option | Dentists buy by size; most competitors sell #5 | Product / supplier | 11/13/2026 |
| 11 | Thread / socket standard (cone socket, simple stem, European thread) + list of handle brands it fits | Review says heads only fit specific handles | Product / supplier | 11/13/2026 |
| 12 | Test reports: 99% reflectance, 100 autoclave cycles, '40% clearer', German glass source | Claims need proof (Amazon may ask); proof also sells | Product / supplier | 11/13/2026 |
| 13 | Root-cause check on 1-star 'only clear the first couple of times' (lot, cleaning method, coating) | Fix the product before pushing traffic | Product / QC | 11/13/2026 |
| 14 | Care and cleaning instructions (allowed chemicals, ultrasonic yes/no, max temp) | Prevent coating damage; add to listing and insert | Product / supplier | 11/13/2026 |
| 15 | Handle material, total length, weight, single- or double-sided mirror, magnification focal distance | Missing specs confuse buyers | Product / supplier | 11/13/2026 |
| 16 | Photo mirrors: pieces per box, exact size of all 5 shapes, single- or double-sided, why FBM | Price clarity and Prime | Product / ops | 11/13/2026 |

## Compliance

| # | What we need | Why | From | Needed by |
|---|---|---|---|---|
| 17 | FDA establishment registration + device listing status for dental mirrors (and the correct device class / product code) | Medical-device rules; what claims we can make | Regulatory / manager | 11/13/2026 |

## Creative assets (design team)

| # | What we need | Why | From | Needed by |
|---|---|---|---|---|
| 18 | Original hi-res files (2000 px+) for all product images, logo files, brand colours and fonts | Image and A+ rebuild | Design team | 11/16/2026 |
| 19 | Product samples of every SKU for new photos + video (fog test, ghost-image test, size, in-use) | New images + SB Video | Ops -> Design team | 11/16/2026 |
| 20 | Existing video files (the video on handle + head families) and any raw footage | Re-edit for SB Video and other ASINs | Design team | 11/16/2026 |

## Access

| # | What we need | Why | From | Needed by |
|---|---|---|---|---|
| 21 | Seller Central roles for Cenk: Brand Registry, A+, Brand Store, Brand Analytics, Vine, Amazon Attribution, Ads console | Needed to audit and implement | Account admin | 11/09/2026 |
| 22 | Google Ads account (Chiru) and social accounts (Shery) to set up Amazon Attribution tags | Measure outside traffic | Chiru, Shery | 11/16/2026 |

## Tools

| # | What we need | Why | From | Needed by |
|---|---|---|---|---|
| 23 | Keyword volume tool (Helium 10, Jungle Scout or similar) or confirm Brand Analytics is enough | Search volume for long-tail keyword plan | Manager | 11/10/2026 |

## Decisions and approvals (manager)

| # | What we need | Why | From | Needed by |
|---|---|---|---|---|
| 24 | Who is the main buyer: dental pros only, or pros + home users? (top sellers are $5-$10 home mirrors) | Sets keywords, images, price ladder | Manager | 11/10/2026 |
| 25 | Approve Vine enrollment for each parent family (cost per parent) | Fastest compliant way to more reviews | Manager | 11/10/2026 |
| 26 | Approve moving single mirror + photo mirrors to FBA | Prime badge and faster delivery | Manager | 11/10/2026 |
| 27 | Approve listing rewrites (titles, bullets, specs) and A+ / Brand Story fixes | Rule: no major changes before review | Manager | 11/10/2026 |
| 28 | PPC budget range and target ACoS after audit | Rule: no budget increase before review | Manager | 11/10/2026 |

## Tool limits found during the audit

- **Firecrawl:** out of credits today; the daily allowance refreshes 11/06.
- **Apify (free plan):** the review scraper returns only 5–10 reviews per run and runs are capped at 16 GB memory in total. That was enough for ILLUCO (we have only 7 written reviews), but it limits deep competitor review mining. A paid plan or a review tool is needed for the full competitor complaint study.
- **No search volume data yet.** We have rank positions but not how many people search each term. Brand Analytics (Search Query Performance) or a keyword tool fills this gap.
