# ILLUCO-AMAZON

Amazon audit and listing rebuild for ILLUCO dental mirrors (Nov 20, 2026). **Deliverables:**

| File | What it is |
|---|---|
| `ILLUCO_Amazon_UPLOAD.xlsx` | **Step 2, once step 1 has processed:** 22 rows, no UPCs: 3 parents and the 19 rows of existing listings (Seller Central > Catalog > Add Products via Upload). Puts every dental mirror except the photo mirrors into four variation families with one pack size each (5 Pack, 1 Pack, Grand 2 Pack, Heads 5 Pack) and Color and Size as the choices (heads: Size), rewrites all copy to the sales direction (Ultra High Definition first, 2X / 3X as premium, 5-minute autoclave, 100+ cycles), keeps the current Amazon prices  Images: real photos only, nothing generated and nothing requested for now. Live listings get none (a partial update keeps what they show), except where an earlier upload left something wrong: the Dark Blue 2X/3X and the Light Blue 5-packs get back their own mains from before 11/21, and the heads get ILLUCO's single-head photo as image 2 in place of a composite. New products get ILLUCO's own photos. Every main is on white. Checked against the template's own rules: 0 errors (see the Upload Check tab of the report). |
| `ILLUCO_Amazon_NEW_PRODUCTS.xlsx` | **Step 3, after the GS1 fix:** the 7 new products (Double-Sided 5-pack x2, Grand 2-pack x4, Double-Sided heads) and the Grand parent, with ILLUCO's own photos. Amazon rejects their UPCs until Verified by GS1 shows brand ILLUCO (it shows IDM SERIES today). |
| `ILLUCO_Amazon_STEP1_delete_parent.xlsx` | **Step 1, upload first (1 row):** deletes only `IDM-HANDLE-FAMILY-PARENT`, the 11/21 family that mixed pack sizes, so its listings can join the new families (a live family's theme cannot be changed in place, and a child can have only one parent: Amazon warning 8032). The listings keep their ASINs, reviews and stock. Replaces the earlier delete file, which removed the three original parents on 11/21. |
| `ILLUCO_Amazon_SINGLES_relink.xlsx` | **Fix, 11/24:** 9 link-only rows that attach the 6 single mirrors to IDM-SINGLE-FAMILY-PARENT (ASIN B0HSQBPPDM). The 11/24 upload created that parent, but no single joined it and the report showed no error. If Amazon refuses a row, its report names the reason. |
| `ILLUCO_Amazon_DELETE_unused_SKUs.xlsx` | **Cleanup, 11/24 (7 rows; 8 uploaded):** deletes SKUs with no reason to stay: extra SKUs on listings that another SKU sells (B0G2DYRY7T, B0GGF37FSB), the retired duplicate B0GGDQ15DD, the inactive FBA copy of IDS-1100, and the dead Skinsoft 1-pack. Deleting a SKU removes only that offer; reviews stay with the ASIN. "SKU not found" on a row means it was already deleted. **Correction:** the uploaded version also deleted HD-FBGB (B0GXC5GWBL), which was the parent of the Skinsoft 2/3/5 pack family, not a draft; it is out of the file now and the family needs a new parent. |
| `ILLUCO_Amazon_LOUPES_family.xlsx` | **Loupes, 11/24 (10 rows):** creates IDM-LOUPE-FAMILY-PARENT (COLOR/SIZE) and links the 9 flip-up loupes to it: Color = frame (Matte Black, Coffee, Sports), Size = working distance (37, 42, 47 cm). The children are link-only rows. Assumes the loupes' product type is PROFESSIONAL_HEALTHCARE. |
| `ILLUCO_SKU_Images.xlsx` | **Reference, not an upload:** one row per listing with a thumbnail per image slot, showing what each listing shows after the upload (green = real photo, orange = live image with a known issue for later, NEW = set by this upload). |
| `ILLUCO_Amazon_Report.xlsx` | Everything else in one workbook (16 tabs): Summary, Shopper Preview, What I Need, ASIN Report, Upload Check, Listing Copy, Sales Direction (brief for design), Review Analysis, Competitors, Keywords + Search Query Performance, PPC Plan, PPC Apply (pauses, negatives, harvests), Images A+ Video, Image Kit, External Traffic, Action Plan. |
| `image_kit/` | Amazon images per product and color (2000 x 2000) with `manifest.csv`, contact sheets and `README.md`. Reference only: the upload no longer links these images (owner, 11/23: real photos from Ashley); the images live on the listings since 11/21-11/23 came from here. |

Findings doc: https://claude.ai/artifact/Xmwhj6EuFnc7G8b6uaePFV

The repository is public, which lets Amazon read those image links. It also exposes `data/account/` (Seller Central exports). Keep it public until Amazon has processed steps 1-3 (step 3 = ILLUCO_Amazon_NEW_PRODUCTS.xlsx after the GS1 fix) (each processing downloads the images from these links), then make it private.

Not in the upload on purpose: photo mirrors (unchanged) and `B0GGDQ15DD` (duplicate of `B0G2DYRY7T`; merged through a Seller Support case).

## Sources and build

- `data/account/`: ILLUCO Seller Central exports shared on Nov 20. `data/raw/`: public amazon.com scrape and the illuco.com product feed. `uploads_in/`: ILLUCO's original Grand / Double-Sided template.
- `analysis/`: PPC and Search Query Performance audit (`ppc_audit.md` + CSVs) that feeds the report.
- `data/build/`: generated by the scripts below (upload contents, upload check, changes to the original Grand file).

```bash
python3 scripts/fill_grand_ds_upload.py uploads_in/ILLUCO_Grand_DoubleSided_Mirrors_Amazon_Upload_original.xlsx /tmp/ready.xlsx data/build/grand_ds_changes.csv
python3 scripts/build_merge_upload.py uploads_in/ILLUCO_Grand_DoubleSided_Mirrors_Amazon_Upload_original.xlsx /tmp/ready.xlsx ILLUCO_Amazon_UPLOAD.xlsx data/build/upload_rows.csv
python3 scripts/build_step1.py uploads_in/ILLUCO_Grand_DoubleSided_Mirrors_Amazon_Upload_original.xlsx ILLUCO_Amazon_STEP1_delete_parent.xlsx
python3 scripts/split_new_products.py
python3 scripts/validate_upload.py ILLUCO_Amazon_UPLOAD.xlsx
python3 scripts/validate_upload.py ILLUCO_Amazon_NEW_PRODUCTS.xlsx data/build/upload_check_new_products.csv
python3 scripts/build_image_sheet.py ILLUCO_SKU_Images.xlsx
python3 scripts/validate_upload.py ILLUCO_Amazon_STEP1_delete_parent.xlsx data/build/upload_check_step1.csv
python3 scripts/build_asin_report.py ILLUCO_Amazon_Report.xlsx
python3 scripts/build_delete_unused.py uploads_in/ILLUCO_Grand_DoubleSided_Mirrors_Amazon_Upload_original.xlsx ILLUCO_Amazon_DELETE_unused_SKUs.xlsx
python3 scripts/build_loupes_family.py uploads_in/ILLUCO_Grand_DoubleSided_Mirrors_Amazon_Upload_original.xlsx ILLUCO_Amazon_LOUPES_family.xlsx
```
