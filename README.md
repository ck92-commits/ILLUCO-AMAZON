# ILLUCO-AMAZON

Amazon store and listing audit for ILLUCO dental mirrors (captured 2026-11-20).

| Path | What it is |
|---|---|
| `ILLUCO_Amazon_ASIN_Report.xlsx` | ASIN report: rating, reviews, BSR, input cells for sessions/sales/CVR/PPC, complaints, fixes; plus review log, competitors, keywords, PPC plan, creative plan, external traffic, action plan, data needs |
| `listings/ILLUCO_Grand_DoubleSided_Mirrors_Amazon_Upload_READY.xlsx` | ILLUCO's Grand / Double-Sided upload template with UPCs, the Double-Sided head row and copy fixes (see `Grand_DoubleSided_upload_changelog.csv`) |
| `listings/Existing_Listings_Update_Sheet.xlsx` | New titles, Item Highlights, bullets, descriptions and backend keywords for all 21 live dental-mirror ASINs, keyed by ASIN |
| `listings/Existing_Listings_PartialUpdate_Template.xlsx` | Same updates in Amazon's PROFESSIONAL_HEALTHCARE template as "Edit (Partial Update)"; paste SKUs into column A |
| `uploads_in/` | Original upload file as received |
| `data/raw/` | Scraped catalog, competitor search results and image galleries used for the audit |
| `scripts/` | Scripts that generate the files above |

Regenerate:

```bash
python3 scripts/fill_grand_ds_upload.py uploads_in/ILLUCO_Grand_DoubleSided_Mirrors_Amazon_Upload_original.xlsx listings/ILLUCO_Grand_DoubleSided_Mirrors_Amazon_Upload_READY.xlsx listings/Grand_DoubleSided_upload_changelog.csv
python3 scripts/build_existing_updates.py uploads_in/ILLUCO_Grand_DoubleSided_Mirrors_Amazon_Upload_original.xlsx listings/Existing_Listings_Update_Sheet.xlsx listings/Existing_Listings_PartialUpdate_Template.xlsx
python3 scripts/build_asin_report.py ILLUCO_Amazon_ASIN_Report.xlsx
```
