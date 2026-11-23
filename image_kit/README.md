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
| 01 main | Single LB `617bfZwQclL`, single DB `61FcYqxQdHL`, kit DB `71549oTdxFL` (1X only) | Every main is the product alone on pure white: no box, no text (owner, 11/23). Kit LB: 5 cutouts of the single LB photo. Kit DB 2X/3X (`main_alt_2x3x`): 5 cutouts of the front mirror of `71549oTdxFL`, because Amazon will not attach the 1X photo to a second ASIN (error 100560). Double-Sided LB/DB: the real Double-Sided head and shank from main.jpg / main_db.jpg seated on the real handle of the same colour, 5 in a row (no photo shows a whole Double-Sided mirror). Grand LB/DB: 2 cutouts of the full Grand mirror from grand-01 / grand-01_db. Single-sided heads: 5 cutouts of the single-head photo. Double-sided heads: 5 face-on heads, each the real Double-Sided head from main.jpg with the real cone-socket thread of the single head (the only bare Double-Sided head photo is edge-on and hides the mirror) |
| 02 in the box | dsdm-03 / dsdm-03_db (Double-Sided, correct count and colour) | Count callouts for single (1 mirror + 1 handle), 5-pack (5 heads + 5 handles + care guide), Grand (2 + 2 + care guide), heads (5 replacement heads, handles not included) |
| 03 key benefit | none | Corrected redraws of the copy card in 7121KSv2hrL, 71fDe5PolUL, 71f0mMI002L, dsdm-01(_db), grand-01(_db), each now led by "Ultra High Definition" and with a "5-Minute Autoclave" item; new "Ultra High Definition" card for double-sided heads |
| 04 | none | "2X & 3X: see fine detail larger" guide (2X/3X marked premium, 1X standard; uses ILLUCO's view circles), Size 4 vs Grand Size 10 at true 22 : 34 scale, both-faces diagram |
| 05 comparison | none | Family A chart headed "ILLUCO Ultra High Definition" (Single / 5-Pack Kit / Double-Sided / Grand), family B chart "Ultra High Definition Heads"; both have an autoclave row (5 min at 273°F / 134°C) |
| 06 | none | Handle callouts per head type and colour; cone-socket compatibility for heads |
| 07 care | none | One care card for all groups, built around the 5-minute autoclave |
| 08 | dsdm-04, grand-04 (stock "Professional Applications", flagged) | Lifestyle collage from ILLUCO's own Light Blue photos; head size-spec images for family B |

### Copy rules (revised 2026-11-20 with the sales lead's direction)
- **Lead with Ultra High Definition**: 99% reflectance, front-surface dielectric coating on German optical glass,
  true color, no ghost image. It is the first item on every key-benefit card and heads both comparison charts.
- **2X and 3X are the premium feature**: "2X & 3X: see fine detail larger - most mouth mirrors are 1X". Always
  keep the honest trade-off: magnified mirrors show a smaller area and work best close to the tooth.
- **5-minute autoclave is the key care message and a time saver**: 273°F (134°C) for just 5 minutes, faster than
  a standard 20-minute instrument cycle; secondary option 20 minutes at 250°F (121°C); no standard 20-minute
  cycle at 273°F and never above 277°F (136°C), because extra heat strips the high-definition coating; avoid abrasive wiping; follow
  the autoclave manufacturer's instructions.
- **"100+ autoclave cycles on the 5-minute setting" is on the care card (image 7).** The owner confirmed it on
  Nov 20. `kitlib.check_copy` accepts only that form: plain "100 autoclave cycles" and "100X" stay rejected, and
  "100+" must sit next to the 5-minute qualifier.
- **No fog claims** (owner, Nov 20): never "anti-fog", "fog-proof", "fog-resistant" or "stays dry", and no
  water-repellent line.
- Never: "40% clearer", any rhodium percentage, or unverified specs (handle length/weight, "1/4 lambda").
- Typos fixed: grand-01(_db) "quandrant" -> "quadrant"; grand-01(_db) and dsdm-01(_db) "minimizing light" ->
  "minimizing light loss". The original moisture / "spot-free" lines are gone, and the heads card's "compatible
  with most standard mirror handles" became "not for simple stem or European-thread handles".
- Cards hold 4-5 items so body copy stays at least 56 px (headlines 96 px) at 2000 px.
- Every rendered string passes `kitlib.check_copy`.

### Existing images NOT to use any more
- `71Ciw0nr7KL`, `71fFYQpHu+L`, `71zox6KeqwL`, Shopify `illuco_dental_mirror_clarity.jpg`, `dental_mirror_reflectance.jpg`:
  "100 AUTOCLAVE CYCLES" (no "+", no 5-minute qualifier) and "40% clearer". `71fFYQpHu+L` also shows 5 mirrors on
  the 1-pack listings.
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
Every listing has its full set of images; these slots use a composite, a recolour, stock photos or a box print that
should be replaced by a real photo (2000 x 2000 px or larger; mains on pure white, product only, about 85% fill).

Live listings:
1. **Dark Blue 5-pack** (B0F84TKGLS 2X, B0F85B5BDC 3X; suppressed): 5 mirrors + 5 handles on white, a new photo, not the
   1X listing's photo. The main is now 5 copies of one mirror cut from that photo; if Amazon refuses it again (100560),
   this photo is the fix.
2. **Light Blue 5-pack** (B0F84VWGG5, B0FCMVZH31, B0F857HKBG): 5 mirrors + 5 handles on white, true colour. The main is
   5 copies of the single Light Blue photo; the only hi-res Light Blue kit image (Shopify `light_blue.jpg`) is a
   recolour of the Dark Blue shot and renders royal blue.
3. **Single-sided heads** (B0FBPG5CS9, B0FCHH2SQB, B0FCJY3H9H): 5 heads on white, no box. The main is 5 copies of one
   head photo.
4. **In-use / clinical photos with real ILLUCO mirrors**, both colours: slot 8 of the Dark Blue 5-pack, Dark Blue single,
   Double-Sided and Grand groups uses ILLUCO's "Professional Applications" stock tiles (the mirrors are not ILLUCO's).
5. **Box photos without legible "Anti-Fog" print** (or new box artwork): slot 2 of the 5-pack and Double-Sided groups
   (see Packaging claims below).
6. Optional: a **Dark Blue single** mirror on white without the blown-out highlight on the rim (main of the 3 Dark Blue
   singles).
7. Confirm: the Light Blue lifestyle photos in slot 8 come from B0G2DYRY7T (black-shank version); check they show the
   current product.

New products (not live until GS1 shows brand ILLUCO; shoot in that window):
8. **Double-Sided 5-pack**, Light Blue and Dark Blue: 5 assembled mirrors full length on white. Every existing photo
   crops the handles; the main seats the real Double-Sided head on the real handle.
9. **Double-Sided heads** IDM-3CD41H: 5 heads face-on on white. The only bare-head photo is edge-on; the main is a
   composite (the Double-Sided head from main.jpg with the single head's thread).
10. **Grand 2-pack**, both colours: 2 complete mirrors on white (the main uses one photo twice), and the Grand kit box
    with two same-colour handles (grand-03 shows one Light Blue and one Dark Blue handle, so it is not used).
11. **Dark Blue Grand and Double-Sided**: real Dark Blue photos. ILLUCO's Dark Blue files (main_db, grand-01_db,
    dsdm-0x_db) are pixel-identical recolours of the Light Blue photos; the colour has not been checked against the
    product.

**Packaging claims.** The real box print reads "Anti-Fog technology" (5-pack and heads boxes) and
"water-repellent coating for fog resistance" (Double-Sided / Grand box). It is legible when the box shots are
zoomed (slot 2 of the Dark Blue 5-pack, the heads and the Double-Sided 5-pack; no main shows a box any more). That conflicts with the
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
