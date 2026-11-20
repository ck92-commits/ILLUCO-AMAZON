# ILLUCO dental mirrors: Amazon listing image kit

Built 2026-11-20 from ILLUCO's own product photos only (Shopify CDN, current Amazon galleries, the
"DENTAL MIRRO IMAGES" Drive folder). Nothing is AI-generated: images are re-used, cropped, cut out,
rotated, scaled, composited onto white, cleaned up, or laid out with text and simple vector icons.
Photo mirrors are out of scope.

- **80 files** = 10 child groups x 8 slots, 2000 x 2000 px, sRGB (ICC embedded), JPEG q90, all < 1 MB.
- **47 unique images**: 9 existing images re-used with content unchanged (re-encoded to spec; 3 of them flagged
  `needs design review`), 38 new or corrected. Shared images (care card, charts, guides) are copied into
  every group that uses them.
- `manifest.csv`: one row per file with family, child group, ASINs/SKUs, slot, source (`existing:<url>` or
  `new (...)`), status and notes. `contact_sheet_<family>_<child_group>.jpg`: one review sheet per group.

## Layout

```
image_kit/
  A_handle/  single_1pack_light_blue/ single_1pack_dark_blue/ kit_5pack_light_blue/ kit_5pack_dark_blue/
             double_sided_5pack_light_blue/ double_sided_5pack_dark_blue/ grand_2pack_light_blue/ grand_2pack_dark_blue/
  B_heads/   single_sided_heads_5pack/ double_sided_heads_5pack/
  _sources/  downloaded source photos (data only) + sources_index.json (url, sha256, size)
```

Slots in every group: `01_main`, `02_whats_in_the_box`, `03_key_benefit`, `04_magnification` (Size 4 single-sided)
/ `04_size_guide` (Grand) / `04_both_faces` (double-sided), `05_comparison`, `06_handle` (family A) /
`06_compatibility` (family B), `07_care`, `08_applications` (family A) / `08_size_spec` (family B).
The 1X/2X/3X children of a group share one set (magnification is not visible in the photos); each
handle colour has its own set.

Rebuild (Python with Pillow + numpy, no network needed once sources exist):

```bash
python3 -I scripts/image_kit/download_sources.py .   # Shopify + Amazon sources; Drive files are copied in with the Drive connector
python3 -I scripts/image_kit/build_kit.py            # writes all images, manifest.csv and contact sheets
```

## Re-used vs new

| Slot | Re-used as-is | New / corrected |
|---|---|---|
| 01 main | Single LB `617bfZwQclL`, single DB `61FcYqxQdHL`, kit DB `71549oTdxFL`, heads `617IX-IYsEL`, kit LB Shopify `light_blue.jpg` (flagged) | Double-Sided LB/DB: real kit photo from dsdm-03 / dsdm-03_db with the graphic header removed, on pure white (old mains showed 2 of 5 mirrors with handles cut off). Grand LB/DB: 2 cutouts of the full Grand mirror from grand-01 / grand-01_db (old main showed 1 of 2, handle cut off). Double-sided heads: 5 cutouts of the IDM-3CD41H head photo (needs reshoot) |
| 02 in the box | dsdm-03 / dsdm-03_db (Double-Sided, correct count and colour) | Count callouts for single (1 mirror + 1 handle), 5-pack (5 heads + 5 handles + care guide), Grand (2 + 2 + care guide), heads (5 replacement heads, handles not included) |
| 03 key benefit | none | Corrected redraws of the copy card in 7121KSv2hrL, 71fDe5PolUL, 71f0mMI002L, dsdm-01(_db), grand-01(_db); new card for double-sided heads |
| 04 | none | 1X/2X/3X guide (uses ILLUCO's view circles), Size 4 vs Grand Size 10 at true 22 : 34 scale, both-faces diagram |
| 05 comparison | none | Family A chart (Single / 5-Pack Kit / Double-Sided / Grand), family B chart (single vs double-sided heads) |
| 06 | none | Handle callouts per head type and colour; cone-socket compatibility for heads |
| 07 care | none | One sterilization card for all groups |
| 08 | dsdm-04, grand-04 (stock "Professional Applications", flagged) | Lifestyle collage from ILLUCO's own Light Blue photos; head size-spec images for family B |

### Copy fixes made in the corrected cards
- grand-01 / grand-01_db: "quandrant" -> "quadrant"; "minimizing light" -> "minimizing light loss".
- dsdm-01 / dsdm-01_db: "minimizing light" -> "minimizing light loss".
- Removed every line implying fog / moisture resistance ("Stain-Resistant After Autoclaving: resists moisture
  buildup", "Consistent, Spot-Free Performance") and replaced it with "No Ghost Image".
- Heads card: "Universal Cone Socket Fit: compatible with most standard mirror handles" -> "Cone Socket Fit:
  not for simple stem or European-thread handles".
- Cards were condensed to 4-5 items so body copy is at least 56 px (headlines 96 px) at 2000 px.
- Every string rendered by the scripts passes a guard (`kitlib.check_copy`) that rejects fog, "stays dry",
  "100 autoclave cycles", "40% clearer", rhodium and the two typos.

### Existing images NOT to use any more
- `71Ciw0nr7KL`, `71fFYQpHu+L`, `71zox6KeqwL`, Shopify `illuco_dental_mirror_clarity.jpg`, `dental_mirror_reflectance.jpg`:
  "100 autoclave cycles" and "40% clearer". `71fFYQpHu+L` also shows 5 mirrors on the 1-pack listings.
- `71ycAyFx4CL`, `71KqSGYiXfL`, `71JgWcIxKeL`, Shopify `dielectric_coating_*.jpg`: "Prevents fogging".
- `61U0VXj+XHL`, `61-ZXUS96xL`, `illuco_dental_mirror_specs.jpg`: unverified "Surface roughness 1/4 lambda" spec.
- `7121KSv2hrL`, `71fDe5PolUL`, `71f0mMI002L`, `front_surface_dental_mirrors.jpg`, `dental_mirror_illuco.jpg`:
  moisture line (and "compatible with most standard handles" on the heads card); corrected versions are in slot 3.
- grand-01, grand-01_db, dsdm-01, dsdm-01_db originals (typos); use the corrected slot-3 files.
- **grand-03** ("Kit Includes", Grand): the box photo shows one Light Blue and one Dark Blue handle.
- `71UpmwAz08L`: 5-pack box shown with one Light Blue and one Dark Blue mirror.
- Double-Sided `main.jpg` / Drive `main_db.jpg` and Grand `main_*.jpg` as mains: wrong unit count and the
  handle runs off the frame.

## Still needs a real photo shoot
1. **Grand 2-pack**, both colours: 2 complete mirrors on white, and the Grand kit box with two same-colour
   handles (grand-03 must be replaced). Current main is a composite of one photo used twice.
2. **Double-Sided 5-pack**, both colours: 5 assembled mirrors full length on white (every existing photo crops
   the handles), plus a face-on shot of the double-sided head.
3. **Double-sided heads IDM-3CD41H**: 5 heads face-on (only one edge-on head photo exists); status `needs reshoot`.
4. **Light Blue 5-pack**: a true-colour photo. The only hi-res Light Blue kit image (Shopify `light_blue.jpg`) is
   a recolour of the Dark Blue shot and renders royal blue, darker than the Light Blue handle in the single and
   Grand photos (the Double-Sided box shot is similar); the Amazon Light Blue main exists only at 500 px. One
   colour-checked reference shot of each handle colour would settle which rendering is right.
5. **Dark Blue Grand / Double-Sided**: ILLUCO's Dark Blue files (main_db, grand-01_db, dsdm-0x_db) are
   pixel-identical recolours of the Light Blue photos; check the colour against real product.
6. **Clinical / lifestyle photos with real ILLUCO mirrors** (both colours) to replace the stock tiles in
   dsdm-04 / grand-04 (the instruments shown are not ILLUCO's). The Light Blue lifestyle photos used in slot 8
   come from orphan listing B0G2DYRY7T; confirm they show the current product (its main shows a black shank).
7. Optional: a single Dark Blue main without the blown-out highlight on the right of the mirror rim.

**Packaging claims.** The real box print reads "Anti-Fog technology" (5-pack and heads boxes) and
"water-repellent coating for fog resistance" (Double-Sided / Grand box). It is legible when the box shots are
zoomed (kit LB main, kit DB slot 2, heads main, Double-Sided main and slot 2). That conflicts with the
no-fog-claims policy: update the box artwork, or reshoot with the box print not legible.

## Upload notes (Amazon)
- **Main image**: pure white background (RGB 255,255,255), product fills about 85% of the frame, whole product in
  frame, no text, badges, watermarks or props. The build asserts a pure-white border on every `01_main`; the
  measured fill is in the manifest notes.
- **Zoom**: Amazon enables zoom at 1000 px and recommends 1600 px or more on the longest side; these are 2000 px.
- **Count**: up to 9 images plus video per ASIN. This kit uses 8, leaving one image slot or a video slot.
  Optional 9th images: dsdm-02 / dsdm-02_db (Double-Sided advantage) or grand-02 (Grand advantage; shows a
  Light Blue Grand next to a Dark Blue Size 4, so use it on the Light Blue Grand child only).
- **Mapping**: `01_main` -> Main image; `02`..`08` -> other images PT01..PT07, in order. Upload the same group set
  to every child SKU listed in `applies_to` (each 1X/2X/3X child of that colour). Images go on the child ASINs;
  the parent shows the children's images.
- Flat files need public URLs (e.g. host on the Shopify CDN); otherwise upload in Seller Central > Manage Images.
- Typography: headlines 96 px, body copy at least 56 px, ILLUCO navy #003060 / #0B2A5B and ILLUCO blue
  #1565C0 / #024B93. Font: Outfit could not be downloaded (github.com answered 403), so the scripts use the
  installed **Inter / Inter Display** (closer to Outfit than DejaVu Sans; DejaVu remains the fallback). To use
  Outfit, put `Outfit-Variable.ttf` in `image_kit/_sources/fonts/` and rebuild.
