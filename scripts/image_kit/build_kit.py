"""Build the ILLUCO Amazon listing image kit.

    python3 -I scripts/image_kit/download_sources.py .   # once (Drive files copied in separately)
    python3 -I scripts/image_kit/build_kit.py

Writes image_kit/<family>/<child_group>/<NN>_<slot>.jpg (2000 x 2000, sRGB, JPEG q90),
image_kit/manifest.csv and image_kit/contact_sheet_<family>_<child_group>.jpg.
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # -I drops the script dir

from PIL import Image, ImageDraw  # noqa: E402

import assets as A  # noqa: E402
import designs as D  # noqa: E402
import kitlib as K  # noqa: E402

E = 'existing:'
U = A.URL

# ------------------------------------------------------------------ design registry
# key -> (render fn, source, status, notes)
BOX_NOTE = ('Packaging print on the box (legible when zoomed) includes ILLUCO box copy such as "Anti-Fog '
            'technology" / "water-repellent coating for fog resistance"; that is the real packaging, but it '
            'conflicts with the no-fog-claims policy - see README.')
REG = {
    # 01 MAIN -------------------------------------------------------------------------------
    'main_single_lb': (lambda: D.main_reuse('single_lb_main'), E + U['single_lb_main'], 'reused-as-is',
                       'Current Amazon main of B0GGDQ15DD: 1 mirror + 1 handle, pure white, fills ~89% x 95%. '
                       'Re-encoded to spec. Same photo serves 1X/2X/3X (magnification is not visible).'),
    'main_single_db': (lambda: D.main_reuse('single_db_main'), E + U['single_db_main'], 'reused-as-is',
                       'Current Amazon main of B0GGDGRHRR: 1 mirror + 1 handle, pure white, fills ~84% x 91%. '
                       'Re-encoded to spec. Same photo serves 1X/2X/3X.'),
    'main_kit_lb': (lambda: D.main_reuse('kit_lb_box'), E + U['kit_lb_box'], 'needs design review',
                    'Shows the full pack (5 mirrors + 5 handles + box) on pure white; resized 2048 -> 2000 px. '
                    'The Light Blue kit main on Amazon (41Uw02dXsML) only exists at 500 px. The handles here render '
                    'royal blue, darker than the Light Blue handle in the single, Grand and Double-Sided photos '
                    '(this file is a recolour of the Dark Blue box shot): confirm colour accuracy or reshoot. '
                    + BOX_NOTE),
    'main_kit_db': (lambda: D.main_reuse('kit_db_main'), E + U['kit_db_main'], 'reused-as-is',
                    'Current Amazon main of B0FCZBD1KY: 5 mirrors + 5 handles, pure white; resized 2560 -> 2000 px.'),
    'main_ds_lb': (lambda: D.main_ds_box('lb'), 'new (cleanup of ' + E + U['dsdm03_lb'] + ')', 'ready',
                   'Existing Double-Sided main (main.jpg) shows only 2 of 5 mirrors and both handles run off the '
                   'frame. New main uses ILLUCO\'s real kit photo from dsdm-03 (5 handles + 5 double-sided heads in '
                   'the box) with the graphic header removed and the background cleaned to pure white (RGB 255); '
                   'no product pixels altered. A reshoot of 5 assembled mirrors on white would be stronger. '
                   + BOX_NOTE),
    'main_ds_db': (lambda: D.main_ds_box('db'), 'new (cleanup of ' + E + U['dsdm03_db'] + ')', 'ready',
                   'As Light Blue: real kit photo from dsdm-03_db (5 Dark Blue handles + 5 heads) on pure white. '
                   'Replaces the Drive main_db.jpg, which shows 2 of 5 mirrors with handles cropped. ' + BOX_NOTE),
    'main_grand_lb': (lambda: D.main_grand_pair('lb'), 'new (2 cutouts of ' + E + U['grand01_lb'] + ')', 'ready',
                      'Existing Grand main shows 1 mirror for a 2-pack and crops the handle at the frame edge. '
                      'Composite of two cutouts of the full Grand mirror photo in grand-01 (head + handle), '
                      'pure white background with a soft contact shadow, fills ~35% x 90%. Replace with a real '
                      '2-mirror photo at the next shoot.'),
    'main_grand_db': (lambda: D.main_grand_pair('db'), 'new (2 cutouts of ' + E + U['grand01_db'] + ')', 'ready',
                      'Same composite from grand-01_db. Note: ILLUCO\'s Dark Blue Grand and Double-Sided images are '
                      'digital recolours of the Light Blue photos (pixel-identical apart from the handle); the '
                      'Dark Blue handle colour should be checked against the real product.'),
    'main_heads_ss': (lambda: D.main_reuse('heads_main'), E + U['heads_main'], 'reused-as-is',
                      'Current Amazon main of B0FBPG5CS9: box + 5 heads, pure white; no handles shown. ' + BOX_NOTE),
    'main_heads_ds': (lambda: D.main_ds_heads(), 'new (5 cutouts of ' + E + U['double_head'] + ')', 'needs reshoot',
                      'IDM-3CD41H has no multi-head photo; composite of 5 copies of ILLUCO\'s single edge-on head '
                      'photo shows the full count on pure white. Usable stopgap, but the mirror faces are not '
                      'visible: reshoot 5 heads face-on.'),
    # 02 WHAT'S IN THE BOX -----------------------------------------------------------------
    'box_single_lb': (lambda: D.in_the_box(A.img('single_lb_main'), ['1 mirror', '+ 1 handle'],
                                           ['1 × Size 4 (22 mm) UHD mirror head', '1 × Light Blue ergonomic handle'],
                                           layout='diag'),
                      'new (photo: ' + E + U['single_lb_main'] + ')', 'ready', 'Count callout: 1 mirror + 1 handle.'),
    'box_single_db': (lambda: D.in_the_box(A.img('single_db_main'), ['1 mirror', '+ 1 handle'],
                                           ['1 × Size 4 (22 mm) UHD mirror head', '1 × Dark Blue ergonomic handle'],
                                           layout='diag'),
                      'new (photo: ' + E + U['single_db_main'] + ')', 'ready', 'Count callout: 1 mirror + 1 handle.'),
    'box_kit_lb': (lambda: D.in_the_box(A.img('kit_lb_box'), ['5 mirror heads + 5 handles', '+ care guide'],
                                        ['5 × Size 4 (22 mm) UHD mirror heads', '5 × Light Blue ergonomic handles',
                                         '1 × printed autoclave & care guide'], layout='stack'),
                   'new (photo: ' + E + U['kit_lb_box'] + ')', 'needs design review',
                   'Count callout: 5 mirror heads + 5 handles + care guide. Same Light Blue colour caveat as the '
                   'main. ' + BOX_NOTE),
    'box_kit_db': (lambda: D.in_the_box(A.img('kit_db_box'), ['5 mirror heads + 5 handles', '+ care guide'],
                                        ['5 × Size 4 (22 mm) UHD mirror heads', '5 × Dark Blue ergonomic handles',
                                         '1 × printed autoclave & care guide'], layout='stack'),
                   'new (photo: ' + E + U['kit_db_box'] + ')', 'ready',
                   'Count callout: 5 mirror heads + 5 handles + care guide. ' + BOX_NOTE),
    'box_ds_lb': (lambda: D.applications_reuse('dsdm03_lb'), E + U['dsdm03_lb'], 'reused-as-is',
                  'ILLUCO "Kit Includes": 5 Double-Sided Mirror Heads, 5 Ergonomic Handles, Printed Autoclave '
                  'Instructions; Light Blue handles; resized 3000 -> 2000 px (list text ~50 px). ' + BOX_NOTE),
    'box_ds_db': (lambda: D.applications_reuse('dsdm03_db'), E + U['dsdm03_db'], 'reused-as-is',
                  'Dark Blue version of dsdm-03; correct count and colour; resized 3000 -> 2000 px. ' + BOX_NOTE),
    'box_grand_lb': (lambda: D.in_the_box(D.grand_pair_rgba('lb'), ['2 mirror heads', '+ 2 handles', '+ care guide'],
                                          ['2 × Grand Size 10 (34 mm) UHD mirror heads', '2 × Light Blue ergonomic handles',
                                           '1 × printed autoclave & care guide'], photo_is_rgba=True),
                     'new (photo: cutouts of ' + E + U['grand01_lb'] + ')', 'ready',
                     'Replaces grand-03 "Kit Includes", which must not be used: its box photo shows one Light Blue '
                     'and one Dark Blue handle. A real photo of the Grand kit box needs a reshoot.'),
    'box_grand_db': (lambda: D.in_the_box(D.grand_pair_rgba('db'), ['2 mirror heads', '+ 2 handles', '+ care guide'],
                                          ['2 × Grand Size 10 (34 mm) UHD mirror heads', '2 × Dark Blue ergonomic handles',
                                           '1 × printed autoclave & care guide'], photo_is_rgba=True),
                     'new (photo: cutouts of ' + E + U['grand01_db'] + ')', 'ready',
                     'No Dark Blue Grand box photo exists (grand-03 shows mixed handle colours).'),
    'box_heads_ss': (lambda: D.in_the_box(D.heads_row(), ['5 replacement heads'],
                                          ['5 × Size 4 (22 mm) single-sided UHD mirror heads', 'Cone socket thread'],
                                          warning='Handles not included', layout='stack', photo_is_rgba=True),
                     'new (5 cutouts of ' + E + U['single_head'] + ')', 'ready',
                     '"5 replacement heads - handles not included" callout.'),
    'box_heads_ds': (lambda: D.in_the_box(D.heads_stack_rgba(), ['5 replacement heads'],
                                          ['5 × Size 4 (22 mm) double-sided UHD mirror heads', 'Cone socket thread'],
                                          warning='Handles not included', layout='stack', photo_is_rgba=True),
                     'new (5 cutouts of ' + E + U['double_head'] + ')', 'ready',
                     '"5 replacement heads - handles not included" callout.'),
    # 03 KEY BENEFIT -----------------------------------------------------------------------
    'kb_size4_lb': (lambda: D.key_benefit_size4('lb'), 'new (corrected redraw of ' + E + U['card_lb'] + ')', 'ready',
                    'Card redrawn at >=56 px, led by "Ultra High Definition" (99% reflectance, true color, no ghost '
                    'image), then Over 40% Brighter, Front-Surface Dielectric Coating, 5-Minute Autoclave, Ergonomic '
                    'Anti-Rotation Design. Removed the original moisture / "spot-free" lines. Do not reuse '
                    '71Ciw0nr7KL / 71fFYQpHu+L ("100 autoclave cycles", "40% clearer"), 71ycAyFx4CL / 71KqSGYiXfL '
                    '("prevents fogging") or 61-ZXUS96xL (unverified 1/4 lambda).'),
    'kb_size4_db': (lambda: D.key_benefit_size4('db'), 'new (corrected redraw of ' + E + U['card_db'] + ')', 'ready',
                    'Dark Blue version of the same card (Ultra High Definition first, 5-Minute Autoclave added).'),
    'kb_ds_lb': (lambda: D.key_benefit_ds('lb'), 'new (corrected redraw of ' + E + U['dsdm01_lb'] + ')', 'ready',
                 'Led by "Ultra High Definition" (99% on both faces); Dual-Sided Viewing; Front-Surface Dielectric '
                 'Coating with "minimizing light" fixed to "minimizing light loss"; 5-Minute Autoclave. Replaced '
                 '"Consistent, Spot-Free Performance"; 4 items so body text is >=56 px.'),
    'kb_ds_db': (lambda: D.key_benefit_ds('db'), 'new (corrected redraw of ' + E + U['dsdm01_db'] + ')', 'ready',
                 'Same card as dsdm-01 corrected, on the Dark Blue base.'),
    'kb_grand_lb': (lambda: D.key_benefit_grand('lb'), 'new (corrected redraw of ' + E + U['grand01_lb'] + ')',
                    'ready', 'Led by "Ultra High Definition"; "quandrant" -> "quadrant" and "minimizing light" -> '
                    '"minimizing light loss"; Over 40% Brighter; 5-Minute Autoclave. "Clinical Photography Ready", '
                    '"Durability" and "Ergonomic" dropped to keep >=56 px (handle covered in slot 6).'),
    'kb_grand_db': (lambda: D.key_benefit_grand('db'), 'new (corrected redraw of ' + E + U['grand01_db'] + ')',
                    'ready', 'Same card as grand-01 corrected, on the Dark Blue base.'),
    'kb_heads_ss': (lambda: D.key_benefit_heads(), 'new (corrected redraw of ' + E + U['card_heads'] + ')', 'ready',
                    'Led by "Ultra High Definition"; 5-Minute Autoclave added; "Universal Cone Socket Fit - '
                    'compatible with most standard mirror handles" replaced by "Cone Socket Fit - not for simple '
                    'stem or European-thread handles"; moisture / spot-free lines removed. Do not reuse 71JgWcIxKeL '
                    '("prevents fogging") or 71zox6KeqwL ("100 autoclave cycles", "40% clearer").'),
    'kb_heads_ds': (lambda: D.key_benefit_ds_heads(), 'new (photo: ' + E + U['double_head'] + ')', 'ready',
                    'Headline "Ultra High Definition" (99% on both faces) + front-surface coating, no ghost image, '
                    '40% brighter, 5-minute autoclave; head only, no handles shown.'),
    # 04 MAGNIFICATION / SIZE / BOTH FACES ---------------------------------------------------
    'mag': (lambda: D.magnification_guide(), 'new (view circles from ' + E + U['mag_art'] + ')', 'ready',
            '"2X & 3X: see fine detail larger - most mouth mirrors are 1X": 2X/3X highlighted as premium, 1X as '
            'standard; keeps the honest note (smaller area, work close to the tooth). Reuses ILLUCO\'s three view '
            'circles from its existing "Choose your magnification" art.'),
    'size_grand': (lambda: D.size_guide_grand(), 'new (photos: ' + E + U['single_head'] + ' ; ' + E +
                   U['grand_main_lb'] + ')', 'ready',
                   'Size 4 (22 mm) vs Grand Size 10 (34 mm) heads at true relative scale (scaled on the measured '
                   'rim width), ~2.4x viewing area; notes Grand 1X/2X. Heads only, so it serves both colours.'),
    'faces': (lambda: D.both_faces(), 'new (photo: ' + E + U['double_head'] + ')', 'ready',
              'Both faces 99% reflectance; head only (no handle), so it serves both Double-Sided colours and the '
              'double-sided heads.'),
    # 05 COMPARISON -----------------------------------------------------------------------
    'chart_a': (lambda: D.chart_family_a(), 'new (photos: ' + E + U['single_lb_main'] + ' ; ' + E + U['kit_lb_box'] +
                ' ; ' + E + U['dsdm03_lb'] + ' ; ' + E + U['grand01_lb'] + ')', 'ready',
                'Shared family-A chart headed "ILLUCO Ultra High Definition": Single / 5-Pack Kit / Double-Sided / '
                'Grand x head size, faces, magnifications, handles included, mirrors per pack, autoclave (5 min at '
                '273°F / 134°C), best for.'),
    'chart_b': (lambda: D.chart_family_b(), 'new (photos: ' + E + U['single_head'] + ' ; ' + E + U['double_head'] +
                ')', 'ready', 'Shared family-B chart headed "Ultra High Definition Heads": single- vs double-sided '
                '(size, faces, magnification, thread, handles not included, pack, autoclave 5 min at 273°F / '
                '134°C, best for).'),
    # 06 HANDLE / COMPATIBILITY -------------------------------------------------------------
    'handle_size4_lb': (lambda: D.handle_size4('lb'), 'new (photo: ' + E + U['single_lb_main'] + ', rotated)', 'ready',
                        'Anti-rotation ergonomic handle + cone socket callouts; notes it takes ILLUCO Size 4 heads.'),
    'handle_size4_db': (lambda: D.handle_size4('db'), 'new (photo: ' + E + U['single_db_main'] + ', rotated)', 'ready',
                        'Dark Blue version. The source photo has a blown-out rim on the right of the head (as on the '
                        'live main).'),
    'handle_ds_lb': (lambda: D.handle_ds('lb'), 'new (photo: ' + E + U['ds_main_lb'] + ')', 'ready',
                     'Double-Sided mirror photo bleeds off the frame (no full-length Double-Sided photo exists).'),
    'handle_ds_db': (lambda: D.handle_ds('db'), 'new (photo: ' + E + U['ds_main_db'] + ')', 'ready',
                     'Dark Blue recolour photo from Drive (main_db.jpg).'),
    'handle_grand_lb': (lambda: D.handle_grand('lb'), 'new (cutout of ' + E + U['grand01_lb'] + ')', 'ready',
                        'Grand head + handle; cone socket callout does not imply separate Grand heads are sold.'),
    'handle_grand_db': (lambda: D.handle_grand('db'), 'new (cutout of ' + E + U['grand01_db'] + ')', 'ready',
                        'Dark Blue version (recoloured source photo).'),
    'compat_ss': (lambda: D.compatibility('single'), 'new (photo: ' + E + U['single_head'] + ')', 'ready',
                  'Fits cone socket handles (incl. ILLUCO) - not simple stem or European thread; thread close-up '
                  'is a crop of the same photo.'),
    'compat_ds': (lambda: D.compatibility('double'), 'new (photo: ' + E + U['double_head'] + ')', 'ready',
                  'Same compatibility message for the double-sided head.'),
    # 07 CARE -----------------------------------------------------------------------------
    'care': (lambda: D.care_card(), 'new', 'ready',
             'Hero: "5-MINUTE AUTOCLAVE - 273°F (134°C) for just 5 minutes", faster than a standard 20-minute '
             'instrument cycle; "or 20 minutes at 250°F (121°C)"; "No 20-minute cycle at 273°F / Never above '
             '277°F (136°C) - extra heat strips the high-definition coating"; avoid abrasive wiping; follow the '
             'autoclave maker\'s instructions. No fog or water-repellent line. "100+ autoclave cycles" is not '
             'shown pending the owner\'s direct confirmation (see README).'),
    # 08 APPLICATIONS / SPEC ----------------------------------------------------------------
    'life_lb': (lambda: D.lifestyle_lb(), 'new (photos: ' + E + U['life_typodont'] + ' ; ' + E + U['life_glove'] +
                ' ; ' + E + U['life_tray'] + ')', 'ready',
                'Real ILLUCO Light Blue mirror photos (typodont, gloved hand, instrument tray) captioned "Ultra high '
                'definition view", "Ergonomic anti-rotation grip", "5-minute autoclave at 273°F (134°C)". The '
                'typodont and glove photos come from the orphan listing B0G2DYRY7T - confirm they show the current '
                'product.'),
    'app_dsdm04': (lambda: D.applications_reuse('dsdm04'), E + U['dsdm04'], 'needs design review',
                   'ILLUCO "Professional Applications" reused as-is (resized 3000 -> 2000 px). The tiles are stock '
                   'photos; the mirrors shown are not ILLUCO instruments - replace with real clinical photos when '
                   'available. Applies to every Size 4 group without its own lifestyle photos.'),
    'app_grand04': (lambda: D.applications_reuse('grand04'), E + U['grand04'], 'needs design review',
                    'ILLUCO "Professional Applications" reused as-is (resized 3000 -> 2000 px). Stock photos; the '
                    'mirrors shown are not ILLUCO instruments (smooth blue handles).'),
    'spec_ss': (lambda: D.size_spec_single_head(), 'new (photo: ' + E + U['single_head'] + ')', 'ready',
                'Size 4 = 22 mm head, front-surface mirror, cone socket thread, 1X/2X/3X options.'),
    'spec_ds': (lambda: D.size_spec_double_head(), 'new (photos: ' + E + U['ds_main_lb'] + ' (head crop, no handle) ; '
                + E + U['double_head'] + ')', 'ready',
                'Face view is the head of the Double-Sided mirror photo with the handle cropped out; side view is '
                'the IDM-3CD41H head photo.'),
}

# ------------------------------------------------------------------ child groups and slots
SIZE4 = {'single': 'Single mirror with handle (1 pack)', 'kit': '5-pack kit (5 mirrors + 5 handles)'}
GROUPS = [
    dict(family='A_handle', group='single_1pack_light_blue',
         applies='Size 4 single mirror with handle, Light Blue: B0GGDQ15DD (1X), B0GGDV4J6B (2X), B0GGDS9MVF (3X); '
                 'also B0G2DYRY7T (1X orphan) if merged',
         slots=[('01_main', 'main_single_lb'), ('02_whats_in_the_box', 'box_single_lb'),
                ('03_key_benefit', 'kb_size4_lb'), ('04_magnification', 'mag'), ('05_comparison', 'chart_a'),
                ('06_handle', 'handle_size4_lb'), ('07_care', 'care'), ('08_applications', 'life_lb')]),
    dict(family='A_handle', group='single_1pack_dark_blue',
         applies='Size 4 single mirror with handle, Dark Blue: B0GGF37FSB (1X), B0GGD95T8Z (2X), B0GGDGRHRR (3X, '
                 'orphan to re-parent)',
         slots=[('01_main', 'main_single_db'), ('02_whats_in_the_box', 'box_single_db'),
                ('03_key_benefit', 'kb_size4_db'), ('04_magnification', 'mag'), ('05_comparison', 'chart_a'),
                ('06_handle', 'handle_size4_db'), ('07_care', 'care'), ('08_applications', 'app_dsdm04')]),
    dict(family='A_handle', group='kit_5pack_light_blue',
         applies='Size 4 kit, 5 mirrors + 5 handles, Light Blue: IDM-2C41LB B0F84VWGG5 (1X), IDM-2C42LB B0FCMVZH31 '
                 '(2X), IDM-2C43LB B0F857HKBG (3X)',
         slots=[('01_main', 'main_kit_lb'), ('02_whats_in_the_box', 'box_kit_lb'),
                ('03_key_benefit', 'kb_size4_lb'), ('04_magnification', 'mag'), ('05_comparison', 'chart_a'),
                ('06_handle', 'handle_size4_lb'), ('07_care', 'care'), ('08_applications', 'life_lb')]),
    dict(family='A_handle', group='kit_5pack_dark_blue',
         applies='Size 4 kit, 5 mirrors + 5 handles, Dark Blue: IDM-2C41DB B0FCZBD1KY (1X), IDM-2C42DB B0F84TKGLS '
                 '(2X), IDM-2C43DB B0F85B5BDC (3X)',
         slots=[('01_main', 'main_kit_db'), ('02_whats_in_the_box', 'box_kit_db'),
                ('03_key_benefit', 'kb_size4_db'), ('04_magnification', 'mag'), ('05_comparison', 'chart_a'),
                ('06_handle', 'handle_size4_db'), ('07_care', 'care'), ('08_applications', 'app_dsdm04')]),
    dict(family='A_handle', group='double_sided_5pack_light_blue',
         applies='Double-Sided Size 4, 5 mirrors + 5 handles, 1X, Light Blue: IDM-2CD41LB (new child)',
         slots=[('01_main', 'main_ds_lb'), ('02_whats_in_the_box', 'box_ds_lb'), ('03_key_benefit', 'kb_ds_lb'),
                ('04_both_faces', 'faces'), ('05_comparison', 'chart_a'), ('06_handle', 'handle_ds_lb'),
                ('07_care', 'care'), ('08_applications', 'app_dsdm04')]),
    dict(family='A_handle', group='double_sided_5pack_dark_blue',
         applies='Double-Sided Size 4, 5 mirrors + 5 handles, 1X, Dark Blue: IDM-2CD41DB (new child)',
         slots=[('01_main', 'main_ds_db'), ('02_whats_in_the_box', 'box_ds_db'), ('03_key_benefit', 'kb_ds_db'),
                ('04_both_faces', 'faces'), ('05_comparison', 'chart_a'), ('06_handle', 'handle_ds_db'),
                ('07_care', 'care'), ('08_applications', 'app_dsdm04')]),
    dict(family='A_handle', group='grand_2pack_light_blue',
         applies='Grand Size 10 (34 mm), 2 mirrors + 2 handles, Light Blue: IDM-2C101LB (1X), IDM-2C102LB (2X) '
                 '(new children)',
         slots=[('01_main', 'main_grand_lb'), ('02_whats_in_the_box', 'box_grand_lb'),
                ('03_key_benefit', 'kb_grand_lb'), ('04_size_guide', 'size_grand'), ('05_comparison', 'chart_a'),
                ('06_handle', 'handle_grand_lb'), ('07_care', 'care'), ('08_applications', 'app_grand04')]),
    dict(family='A_handle', group='grand_2pack_dark_blue',
         applies='Grand Size 10 (34 mm), 2 mirrors + 2 handles, Dark Blue: IDM-2C101DB (1X), IDM-2C102DB (2X) '
                 '(new children)',
         slots=[('01_main', 'main_grand_db'), ('02_whats_in_the_box', 'box_grand_db'),
                ('03_key_benefit', 'kb_grand_db'), ('04_size_guide', 'size_grand'), ('05_comparison', 'chart_a'),
                ('06_handle', 'handle_grand_db'), ('07_care', 'care'), ('08_applications', 'app_grand04')]),
    dict(family='B_heads', group='single_sided_heads_5pack',
         applies='Single-sided Size 4 heads, 5 pack, cone socket, no handles: IDM-3C41NA B0FBPG5CS9 (1X), '
                 'IDM-3C42NA B0FCHH2SQB (2X), IDM-3C43NA B0FCJY3H9H (3X)',
         slots=[('01_main', 'main_heads_ss'), ('02_whats_in_the_box', 'box_heads_ss'),
                ('03_key_benefit', 'kb_heads_ss'), ('04_magnification', 'mag'), ('05_comparison', 'chart_b'),
                ('06_compatibility', 'compat_ss'), ('07_care', 'care'), ('08_size_spec', 'spec_ss')]),
    dict(family='B_heads', group='double_sided_heads_5pack',
         applies='Double-sided Size 4 heads, 5 pack, 1X, cone socket, no handles: IDM-3CD41H (new listing)',
         slots=[('01_main', 'main_heads_ds'), ('02_whats_in_the_box', 'box_heads_ds'),
                ('03_key_benefit', 'kb_heads_ds'), ('04_both_faces', 'faces'), ('05_comparison', 'chart_b'),
                ('06_compatibility', 'compat_ds'), ('07_care', 'care'), ('08_size_spec', 'spec_ds')]),
]


def contact_sheet(group, rows, path):
    tile, gap, lab = 560, 26, 118
    cols = 4
    n = len(rows)
    rws = (n + cols - 1) // cols
    head_h = 150
    Wc = cols * tile + (cols + 1) * gap
    Hc = head_h + rws * (tile + lab) + (rws + 1) * gap
    sheet = Image.new('RGB', (Wc, Hc), (232, 236, 242))
    d = ImageDraw.Draw(sheet)
    d.text((gap, 26), f"{group['family']} / {group['group']}", font=K.font(46, 'bold', True), fill=K.NAVY_TEXT)
    d.text((gap, 88), group['applies'][:150], font=K.font(26, 'regular'), fill=K.GREY_TEXT)
    for i, r in enumerate(rows):
        x = gap + (i % cols) * (tile + gap)
        y = head_h + gap + (i // cols) * (tile + lab + gap)
        im = Image.open(r['abs']).convert('RGB').resize((tile, tile), Image.LANCZOS)
        sheet.paste(im, (x, y))
        d.rectangle((x - 1, y - 1, x + tile, y + tile), outline=(190, 198, 210))
        d.text((x, y + tile + 12), r['slot'], font=K.font(30, 'bold'), fill=K.NAVY_TEXT)
        col = {'ready': K.GREEN, 'reused-as-is': K.BLUE, 'needs reshoot': K.RED,
               'needs design review': (196, 110, 0)}[r['status']]
        d.text((x, y + tile + 56), r['status'], font=K.font(28, 'semibold'), fill=col)
    sheet.save(path, 'JPEG', quality=88, optimize=True)


def main():
    cache = {}
    manifest = []
    for g in GROUPS:
        gdir = K.OUT / g['family'] / g['group']
        gdir.mkdir(parents=True, exist_ok=True)
        rows = []
        for slot, key in g['slots']:
            fn, source, status, notes = REG[key]
            if key not in cache:
                print('render', key, flush=True)
                cache[key] = fn()
            out = gdir / f'{slot}.jpg'
            size = K.save_jpg(cache[key], out)
            if slot == '01_main':
                im = Image.open(out)
                assert K.white_border_ok(im), f'{out}: main border is not pure white'
                fw, fh = K.product_fill(im)
                notes = notes + f' [measured fill {fw:.0%} x {fh:.0%}]'
            rel = out.relative_to(K.OUT)
            row = dict(family=g['family'], child_group=g['group'], applies_to=g['applies'], slot=slot,
                       file=str(rel), source=source, status=status, notes=notes, abs=str(out), bytes=size,
                       design=key)
            rows.append(row)
            manifest.append(row)
        contact_sheet(g, rows, K.OUT / f"contact_sheet_{g['family']}_{g['group']}.jpg")
    with open(K.OUT / 'manifest.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['family', 'child_group', 'applies_to', 'slot', 'file', 'source', 'status', 'notes'])
        for r in manifest:
            w.writerow([r['family'], r['child_group'], r['applies_to'], r['slot'], r['file'], r['source'],
                        r['status'], r['notes']])
    print('files', len(manifest), 'unique designs', len(cache), 'font', K.font_family())
    big = max(manifest, key=lambda r: r['bytes'])
    print('largest', big['file'], big['bytes'])


if __name__ == '__main__':
    main()
