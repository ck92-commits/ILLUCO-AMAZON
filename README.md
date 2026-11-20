# ILLUCO-AMAZON

Amazon store and listing audit for ILLUCO dental mirrors (Nov 20, 2026).

## Upload this

| File | What it does |
|---|---|
| `listings/ILLUCO_Dental_Mirrors_MERGE_UPLOAD.xlsx` | **The one file to upload** (Catalog > Add Products via Upload). Creates two parents (`IDM-HANDLE-FAMILY-PARENT`, `IDM-HEADS-FAMILY-PARENT`), re-parents 15 existing ASINs with "Edit (Partial Update)", creates the Grand / Double-Sided / Double-Sided head children, removes the fog and 100-cycle claims, and aligns prices with illuco.com. Yellow cells need a check before upload (3 inferred SKUs, 2 price increases, head package dimensions). |
| `listings/merge_plan.csv` | Every row of the upload in plain English: SKU, ASIN, family, variation values, old and new price. |
| `listings/Existing_Listings_Update_Sheet.xlsx` | The same copy per ASIN for reading or manual edits, with ASIN links. |
| `image_kit/` | Amazon image kit per child (see `image_kit/README.md` and `manifest.csv`). |

Photo mirrors are intentionally left unchanged. `B0GGDQ15DD` is not in the upload: it is a duplicate of `B0G2DYRY7T` and is merged through a Seller Support case.

## Reports

| File | What it is |
|---|---|
| `ILLUCO_Amazon_ASIN_Report.xlsx` | Per-ASIN report (rating, sessions, units, sales, conversion from the Business Report, complaints with evidence, fixes) plus What I Need, reviews, competitors, keywords, PPC (current campaigns + calculator), creative, external traffic and action plan tabs. Every ASIN links to its listing and its 1-3 star reviews. |
| `analysis/ppc_audit.md` | Sponsored Products and Search Query Performance audit, with `negative_keywords.csv`, `harvest_keywords.csv`, `sqp_top_queries.csv`. |
| Findings doc | https://claude.ai/artifact/Xmwhj6EuFnc7G8b6uaePFV |

## Inputs

| Path | Source |
|---|---|
| `data/account/` | ILLUCO Seller Central exports shared on Nov 20 (Business Report, Listing Summary, SP reports, SQP, FBA returns and reimbursements) |
| `data/raw/` | Public amazon.com catalog and competitor scrape; illuco.com product feed (model numbers, prices, images) |
| `uploads_in/` | ILLUCO's Grand / Double-Sided upload template as received |

## Regenerate

```bash
python3 scripts/fill_grand_ds_upload.py uploads_in/ILLUCO_Grand_DoubleSided_Mirrors_Amazon_Upload_original.xlsx /tmp/ready.xlsx listings/Grand_DoubleSided_upload_changelog.csv
python3 scripts/build_merge_upload.py uploads_in/ILLUCO_Grand_DoubleSided_Mirrors_Amazon_Upload_original.xlsx /tmp/ready.xlsx listings/ILLUCO_Dental_Mirrors_MERGE_UPLOAD.xlsx listings/merge_plan.csv
python3 scripts/build_existing_updates.py x listings/Existing_Listings_Update_Sheet.xlsx
python3 scripts/build_asin_report.py ILLUCO_Amazon_ASIN_Report.xlsx
```
