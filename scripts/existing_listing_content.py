"""Rewritten content for every live ILLUCO dental-mirror ASIN on amazon.com.

House style follows ILLUCO's own Grand / Double-Sided upload file: a title under 75
characters (so Amazon shows the Item Highlight in search), a feature-led Item Highlight,
five CAPS-led bullets, a description paragraph and backend generic keywords.

Facts used here come from the live Amazon listings and illuco.com (scraped 2026-11-20).
Anything not verified is marked in CONFIRM and must be checked before upload.
"""

# Copy direction from ILLUCO sales (Claudia, 2026-11-20): lead with HIGH DEFINITION; 2X / 3X magnification is the
# premium feature (1X is basic); the 5-minute autoclave at 273F is a time saver and the key care message (standard
# 20-minute cycles cook off the coating); the coating is rated for 100+ cycles, after which the mirror still works;
# fog / water-repellency is secondary.
INTRO = ("ILLUCO UHD mirrors are built for one thing: an ultra high definition view. Most dental mirrors reflect "
         "only 60-70% of available light; ILLUCO's front-surface dielectric coating on German optical glass reflects "
         "99%, so the image is over 40% brighter, sharp, true to color and free of the ghost images that cause "
         "visual fatigue. ")
CARE = ("Care is fast: autoclave for just 5 minutes at 273°F (134°C), or 20 minutes at 250°F (121°C). Do not run "
        "longer cycles or exceed 277°F (136°C), because extra heat strips the coating. On the 5-minute setting the "
        "coating is rated for 100+ autoclave cycles, and the mirror stays usable after that. ")
B_HD = ("ULTRA HIGH DEFINITION VIEW: ILLUCO's front-surface dielectric coating on German optical glass reflects 99% "
        "of light, versus 60-70% for standard dental mirrors. The image is over 40% brighter, sharp and true to "
        "color, with no ghost image, so fine detail is easy to see.")
B_AUTO = ("5-MINUTE AUTOCLAVE, 100+ CYCLES: Sterilize in just 5 minutes at 273°F (134°C), faster than a standard "
          "20-minute instrument cycle (or 20 minutes at 250°F / 121°C). Do not run longer cycles or exceed 277°F "
          "(136°C); extra heat strips the coating. On the 5-minute setting the coating is rated for 100+ cycles, "
          "and the mirror stays usable after that.")
HANDLE = ("ERGONOMIC ANTI-ROTATION HANDLE: The textured, finger-indented handle stays steady in a light or firm "
          "grip, even with wet gloves. The Size 4 head uses a standard cone socket, so ILLUCO replacement heads "
          "thread straight on.")
SMALL = {'and', 'or', 'of', 'for', 'with', 'the', 'a', 'an', 'to', 'on', 'in'}
KEEP = {'UHD', 'ILLUCO', 'HD'}


def lead_case(bullet):
    """Amazon: no all-caps in bullets. Turn a CAPS lead-in ("ULTRA HIGH DEFINITION VIEW:") into Title Case."""
    if ':' not in bullet:
        return bullet
    head, rest = bullet.split(':', 1)
    if head != head.upper():
        return bullet
    words = []
    for i, w in enumerate(head.split(' ')):
        core = w.strip('(),')
        if core in KEEP:
            words.append(w)
        elif i > 0 and core.lower() in SMALL:
            words.append(w.lower())
        else:
            parts = []
            for p_ in w.split('-'):
                if any(ch.isdigit() for ch in p_):
                    parts.append(p_.replace('MM', 'mm'))      # 1X, 2.4X, (22mm), 99%
                else:
                    parts.append(p_[:1].upper() + p_[1:].lower())
            words.append('-'.join(parts))
    return ' '.join(words) + ':' + rest


B_AUTO = ("5-MINUTE AUTOCLAVE SAVES TIME: Ready again after just 5 minutes at 273°F (134°C), a faster turnaround than a "
          "standard 20-minute instrument cycle (or 20 minutes at 250°F / 121°C). Longer cycles or more than 277°F "
          "(136°C) strip the coating. On the 5-minute setting the coating is rated for 100+ cycles, and the mirror "
          "stays usable after that.")
# names kept for older imports
B_LOOK, B_FOG, COAT, STERIL = B_HD, B_AUTO, CARE, ''


def mag_bullet(mag):
    if mag == 1:
        return ("TRUE 1X VIEW, 2X AND 3X AVAILABLE: Life-size, distortion-free reflection for routine exams and "
                "indirect vision. Most mouth mirrors stop at 1X; ILLUCO also makes 2X and 3X magnifying versions "
                "for fine detail.")
    return (f"{mag}X MAGNIFICATION, A PREMIUM UPGRADE: Most mouth mirrors are 1X. ILLUCO {mag}X enlarges margins, "
            "caries and calculus for precise inspection with the same high-definition clarity. Magnified mirrors "
            "show a smaller area and focus best close to the tooth.")


def mag_sentence(mag):
    if mag == 1:
        return "This is the 1X version for a life-size view; 2X and 3X magnifying versions are also available. "
    return f"This is the {mag}X magnifying version: most mouth mirrors stop at 1X. "


KW_CORE = "high definition hd magnifying magnification 2x 3x quick autoclave"


def kit(mag, color, sku_model, asin, rating, note=''):
    magtxt = '1X' if mag == 1 else f'{mag}X magnifying'
    title = (f"ILLUCO UHD Dental Mirrors, Size 4 (22mm), 1X, 5 Pack, {color}" if mag == 1 else
             f"ILLUCO UHD {mag}X Magnifying Dental Mirrors, Size 4 (22mm), 5 Pack, {color}")
    return dict(
        family='5-Pack with Handles', parent='B0FDCGG69J', asin=asin, mag=mag, color=color,
        model_suggested=sku_model, rating=rating, title=title,
        highlight="Ultra High Definition, 99% Reflectance, No Ghost Image, With 5 Handles, 5-Minute Autoclave, 100+ Cycles",
        bullets=[B_HD, mag_bullet(mag), B_AUTO, HANDLE,
                 f"5 PACK WITH HANDLES: 5 Size 4 (22mm) mirror heads ({magtxt}), 5 ergonomic handles ({color}) and "
                 "an autoclave care guide with the 5-minute setting. Built for general dentists, hygienists, "
                 "orthodontists and dental students."],
        description=(INTRO + mag_sentence(mag) + "Each kit pairs standard Size 4 (22mm) cone socket heads with "
                     "ergonomic anti-rotation handles that stay steady in a light or firm grip. " + CARE +
                     f"Each kit includes 5 mirror heads, 5 handles ({color}) and an autoclave sterilization and care guide."),
        keywords=("mouth mirror dentist tools dental instruments tooth teeth oral exam intraoral hygienist "
                  "orthodontist front surface number 4 professional set kit " + KW_CORE),
        size='Size 4 (22mm)', items=5,
        included="5 Size 4 Mirror Heads, 5 Ergonomic Handles, Autoclave Sterilization & Care Guide",
        note=note)


def heads(mag, asin, model, rating, note=''):
    magtxt = '1X' if mag == 1 else f'{mag}X magnifying'
    title = ("ILLUCO UHD Dental Mirror Heads, Size 4 (22mm), 1X, 5 Pack, Cone Socket" if mag == 1 else
             f"ILLUCO UHD {mag}X Magnifying Dental Mirror Heads, Size 4 (22mm), 5 Pack")
    title = title.replace(", 5 Pack, Cone Socket", ", 5 Pack")
    return dict(
        family='Replacement Heads 5-Pack', parent='B0FCNL53JN', asin=asin, mag=mag, color='',
        model_suggested=model, rating=rating, title=title,
        highlight="Ultra High Definition, 99% Reflectance, Cone Socket, Handles Not Included, 5-Minute Autoclave, 100+ Cycles",
        bullets=[B_HD, mag_bullet(mag),
                 "CONE SOCKET FIT, HANDLES NOT INCLUDED: Threads onto standard cone socket mirror handles, including "
                 "ILLUCO ergonomic anti-rotation handles. Not for simple stem or European-thread handles. Check your "
                 "handle before ordering.",
                 B_AUTO,
                 f"5 REPLACEMENT HEADS: 5 single-sided Size 4 (22mm) mirror heads ({magtxt}) with the same "
                 "high-definition view. Need handles too? Choose the ILLUCO 5 Pack with Handles."],
        description=(INTRO + mag_sentence(mag) + "These Size 4 (22mm) replacement heads thread onto standard cone "
                     "socket mirror handles, including ILLUCO ergonomic handles (sold separately); they do not fit "
                     "simple stem or European-thread handles. " + CARE + "Each pack includes 5 mirror heads. "
                     "Handles are not included."),
        keywords=("mouth mirror heads replacement refill tops screw on cone socket dentist dental instruments tooth "
                  "teeth oral exam hygienist front surface number 4 professional " + KW_CORE),
        size='Size 4 (22mm)', items=5, included='5 Size 4 Mirror Heads',
        note=note)


def single(mag, color, asin, model, rating, note=''):
    magtxt = '1X' if mag == 1 else f'{mag}X magnifying'
    title = (f"ILLUCO UHD Dental Mirror, Size 4 (22mm), 1X, 1 Pack, {color}" if mag == 1 else
             f"ILLUCO UHD {mag}X Magnifying Dental Mirror, Size 4 (22mm), 1 Pack, {color}")
    return dict(
        family='Single Mirror with Handle', parent='B0GGD9DVP9', asin=asin, mag=mag, color=color,
        model_suggested=model, rating=rating, title=title,
        highlight="Ultra High Definition, 99% Reflectance, No Ghost Image, With Handle, 5-Minute Autoclave, 100+ Cycles",
        bullets=[B_HD, mag_bullet(mag), B_AUTO, HANDLE,
                 f"1 MIRROR WITH HANDLE: 1 Size 4 (22mm) mirror head ({magtxt}) on 1 ergonomic handle ({color}). "
                 "Ideal for dental students, a spare for the operatory or a first try of ILLUCO. Equipping a "
                 "practice? Choose the 5 Pack."],
        description=(INTRO + mag_sentence(mag) + "This single mirror puts that view on a standard Size 4 (22mm) "
                     "cone socket head mounted on an ergonomic anti-rotation handle. " + CARE +
                     f"Includes 1 mirror and 1 handle ({color}). Also available in 5 packs and as replacement heads."),
        keywords=("mouth mirror dentist tools dental instruments tooth teeth oral exam intraoral hygienist student "
                  "front surface number 4 professional single " + KW_CORE),
        size='Size 4 (22mm)', items=1, included='1 Size 4 Mirror Head, 1 Ergonomic Handle',
        note=note)


SHAPES = {
    'Occlusal Large': ('B0F86DNNSV', 'IDM-1OL', 'full-arch occlusal views in adults with ample space',
                       '137.22 x 76.10 mm, 44 mm handle'),
    'Occlusal Medium': ('B0FCNG7T9P', '', 'occlusal arch views for most adult patients',
                        '138.47 x 69.00 mm, 44 mm handle'),
    'Occlusal Small': ('B0F86CJ7R6', '', 'occlusal views in smaller mouths, teens and children', ''),
    'Lingual': ('B0FCNRP7NF', '', 'tongue-side (lingual) views of the arch', ''),
    'Buccal': ('B0FCN9V5G4', '', 'cheek-side (buccal) views of the posterior teeth', ''),
}


def photo(shape):
    asin, model, use, dims = SHAPES[shape]
    dimtxt = f" Mirror size: {dims}." if dims else ''
    return dict(
        family='Dental Photo Mirror', parent='B0FCPD1KKN', asin=asin, mag=1, color='',
        model_suggested=model, rating='No ratings',
        title=f"ILLUCO UHD Dental Photography Mirror, Double-Sided, {shape}",
        highlight=("Intraoral Photo Mirror, Front Surface, 99% Reflectance Both Sides, Fog-Resistant, "
                   "Autoclavable, Silicone Sleeve"),
        bullets=[
            "PHOTOS THAT MATCH WHAT YOU SEE: Most photo mirrors lose light and add a ghost image. ILLUCO's "
            "front surface dielectric coating on German optical glass reflects 99% on both sides, for bright, "
            "single-image, true-color intraoral photos.",
            f"{shape.upper()} SHAPE: Designed for {use}.{dimtxt} Also available in Occlusal Large, Medium "
            "and Small, Lingual and Buccal shapes.",
            "DOUBLE-SIDED: Both faces carry the same 99% coating, so you can flip orientation for upper and "
            "lower arches without losing brightness.",
            "FOG-RESISTANT AND AUTOCLAVABLE: Water-repellent coating helps manage moisture during the shot "
            "(warm the mirror or use air to keep it clear). Rated for 100+ autoclave cycles up to 134°C "
            "(273°F). Package mirrors individually and avoid abrasive wiping.",
            "PROTECTIVE SILICONE SLEEVE: Each mirror comes with a silicone sleeve for a secure gloved grip "
            "and safer handling. Built for cosmetic, orthodontic, implant and general dentists who document "
            "every case."],
        description=("ILLUCO Double-Sided Dental Photography Mirrors are made for clinicians who rely on "
                     "intraoral photography for case documentation, treatment planning and patient "
                     "communication. A front surface dielectric coating on German optical glass reflects 99% "
                     "of light on both faces, so images are bright, sharp and free of the ghosting seen with "
                     f"rear-surface mirrors. The {shape} shape is designed for {use}. The water-repellent "
                     "surface helps manage moisture during the shot, and each mirror is rated for 100+ "
                     "autoclave cycles up to 134°C (273°F). Each mirror includes a protective silicone sleeve."),
        keywords=("intraoral photo mirror dental photography reflector occlusal buccal lingual orthodontic "
                  "cosmetic dentistry camera case documentation anti fog fog free two sided front surface "
                  "glass dentist clinical photo"),
        size=shape, items=1, included='1 Double-Sided Photo Mirror, 1 Silicone Sleeve',
        note=('Model number on Amazon is the placeholder "IDMXXX" - replace with the real model. '
              'Confirm whether the Amazon box also includes the travel pouch listed on illuco.com.'))


# Photo mirrors stay as they are (owner decision 2026-11-20), so they are not in ROWS.
# model = illuco.com variant SKU (public product feed, 2026-11-20); price = illuco.com regular price.
ROWS = [
    kit(1, 'Dark Blue', 'IDM-2C41DB', 'B0FCZBD1KY', '3.4 (5 ratings, family)'),
    kit(1, 'Light Blue', 'IDM-2C41LB', 'B0F84VWGG5', 'family 3.4'),
    kit(2, 'Dark Blue', 'IDM-2C42DB', 'B0F84TKGLS', 'family 3.4'),
    kit(2, 'Light Blue', 'IDM-2C42LB', 'B0FCMVZH31', 'family 3.4'),
    kit(3, 'Dark Blue', 'IDM-2C43DB', 'B0F85B5BDC', 'family 3.4; 1-star: "not anti-fog or water-resistant"'),
    kit(3, 'Light Blue', 'IDM-2C43LB', 'B0F857HKBG', 'family 3.4'),
    heads(1, 'B0FBPG5CS9', 'IDM-3C41NA', '2.0 (family)'),
    heads(2, 'B0FCHH2SQB', 'IDM-3C42NA', '2.0 (family)'),
    heads(3, 'B0FCJY3H9H', 'IDM-3C43NA', '2.0 (family)'),
    single(1, 'Light Blue', 'B0G2DYRY7T', 'IDM-2C41LB-1X', '3.4 (3 ratings); best seller: 68 units, 16.8% conversion',
           'Becomes the 1X Light Blue child of the merged family (keeps its sales history). Confirm it ships the '
           'current product (its photos show a black shank) and replace its photos and A+ (A+ describes photo mirrors).'),
    single(1, 'Dark Blue', 'B0GGF37FSB', 'IDM-2C41DB-1X', '5.0 (family)'),
    single(2, 'Light Blue', 'B0GGDV4J6B', 'IDM-2C41LB-2X', '5.0 (family)', 'Variation value "Blue" -> "Light Blue".'),
    single(2, 'Dark Blue', 'B0GGD95T8Z', 'IDM-2C41DB-2X', '5.0 (family)'),
    single(3, 'Light Blue', 'B0GGDS9MVF', 'IDM-2C41LB-3X', '5.0 (family)', 'Variation value "Blue" -> "Light Blue".'),
    single(3, 'Dark Blue', 'B0GGDGRHRR', 'IDM-2C41DB-3X', '1.0 (1 rating): "water shedding last for 1-2 sterilization cycles"; NCX 20%',
           'Detached from family B0GGD9DVP9; re-attached here as 3X Dark Blue. Answer the NCX flag in Voice of the Customer.'),
    single(1, 'Light Blue', 'B0GGDQ15DD', 'IDM-2C41LB-1X', '5.0 (1 rating)',
           'DUPLICATE of B0G2DYRY7T (same 1X Light Blue single). Not re-parented: open a Seller Support case to merge '
           'this ASIN into B0G2DYRY7T so the two review histories combine, then close this offer.'),
]

# Seller SKUs per ASIN. Verified = from ILLUCO's Listing Summary, FBA returns or reimbursement reports.
# Inferred = FBA SKU follows the verified pattern but did not appear in any report: check in Manage All Inventory.
SKUS = {
    'B0FCZBD1KY': [('IDM2C41DB', 'verified')],
    'B0F84VWGG5': [('IDM2C41LB', 'verified')],
    'B0F84TKGLS': [('IDM2C42DB', 'verified')],
    'B0FCMVZH31': [('IDM2C42LB', 'verified')],
    'B0F85B5BDC': [('IDM2C43DB', 'verified')],
    'B0F857HKBG': [('IDM2C43LB', 'inferred'), ('IDM2C43LB-FBM', 'verified')],
    'B0FBPG5CS9': [('IDM3C41NA', 'verified')],
    'B0FCHH2SQB': [('IDM3C42NA', 'inferred')],
    'B0FCJY3H9H': [('IDM3C43NA', 'inferred')],
    'B0G2DYRY7T': [('A2-3YBP-WRV7', 'verified')],
    'B0GGF37FSB': [('IDM-2C41DB-1X', 'verified')],
    'B0GGDV4J6B': [('IDM2C41LB-2X-FBA', 'verified'), ('IDM-2C41LB-2X', 'verified')],
    'B0GGD95T8Z': [('IDM2C41DB-2X-FBA', 'verified'), ('IDM-2C41DB-2X', 'verified')],
    'B0GGDS9MVF': [('IDM2C41LB-3X-FBA', 'verified'), ('IDM-2C41LB-3X', 'verified')],
    'B0GGDGRHRR': [('IDM-2C41DB-3X-FBA', 'verified'), ('IDM-2C41DB-3X', 'verified')],
    'B0GGDQ15DD': [('IDM2C41LB-1X-FBA', 'verified'), ('IDM-2C41LB-1X', 'verified')],
}

# illuco.com regular prices (no compare-at / promotion on 2026-11-20) and current Amazon prices.
PRICE_DTC = {'IDM-2C41': 85.00, 'IDM-2C42': 115.00, 'IDM-2C43': 130.00,
             'IDM-3C41NA': 69.00, 'IDM-3C42NA': 95.00, 'IDM-3C43NA': 105.00, 'IDM-3CD41H': 139.00,
             'single-1': 17.99, 'single-2': 24.00, 'single-3': 27.00}


def dtc_price(r):
    if r['family'] == '5-Pack with Handles':
        return PRICE_DTC[f"IDM-2C4{r['mag']}"]
    if r['family'] == 'Replacement Heads 5-Pack':
        return PRICE_DTC[r['model_suggested']]
    return PRICE_DTC[f"single-{r['mag']}"]


SIZE_A = {1: 'Size 4 (22mm) 1X', 2: 'Size 4 (22mm) 2X', 3: 'Size 4 (22mm) 3X'}
SIZE_B = {1: 'Size 4 (22mm) Single-Sided 1X', 2: 'Size 4 (22mm) Single-Sided 2X', 3: 'Size 4 (22mm) Single-Sided 3X'}
for r in ROWS:
    r['skus'] = SKUS[r['asin']]
    r['price_new'] = dtc_price(r)
    if r['family'] == 'Replacement Heads 5-Pack':
        r['new_family'], r['var_size'] = 'B', SIZE_B[r['mag']]
    else:
        r['new_family'], r['var_size'] = 'A', SIZE_A[r['mag']]

ATTRIBUTE_FIXES = [
    ('B0F7YPNMWK', 'IDS-1100 Dermatoscope', 'Browse node is Home & Kitchen > Home Decor Accents; Unit Count "16 Ounce"',
     'Request re-classification to the professional medical diagnostic node via Seller Support; set Unit Count = 1 Count'),
    ('B0F81HQMD2', 'IDS-1000 Dermatoscope', 'Browse node is Home & Kitchen > Home Decorative Accessories',
     'Request re-classification to the professional medical diagnostic node'),
    ('B0F7Z2TP29', 'IDS-3100 Dermatoscope', 'Model Number field says IDS-1100; no BSR (unclassified)',
     'Set Model Number = IDS-3100; request browse classification'),
    ('B0FSM14R8P', 'IDS-9100 Dermatoscope', 'Ranked in Automotive (#2,986,869) and Lab Scopes',
     'Request re-classification to the professional medical diagnostic node'),
    ('B0FDCGG69J family', '5-Pack with Handles', 'Model number holds the variant name ("1X Magnification Dark Blue Handle"); '
     'Item Weight 2 lb and 10x1x1 in look wrong', 'Set Model/Part Number to IDM codes; re-measure and correct weight and dimensions'),
    ('B0FCNL53JN family', 'Replacement Heads', 'Model number holds the variant name; item dimensions 1x1x1 in',
     'Set Model/Part Number to IDM codes; correct dimensions'),
    ('All dental mirrors', 'Brand name', 'Existing listings show brand "Illuco"; new upload uses "ILLUCO"',
     'Use the exact Brand Registry spelling on every new listing; do not change brand on live ASINs via upload'),
]

CONFIRM = [
    'SKU for each ASIN (All Listings Report) - required for the partial-update upload',
    'Product type of the live listings is PROFESSIONAL_HEALTHCARE (same as the Grand file); if not, use that product type\'s template',
    'B0G2DYRY7T is the same product as the 1X single mirror (its photos show a black shank)',
    'Photo-mirror dimensions for Occlusal Small, Lingual and Buccal; whether the Amazon box includes the travel pouch',
    'Double-Sided head (IDM-3CD41H) pack size = 5, cone socket, price, images and package dimensions',
]


for _r in ROWS:
    _r['bullets'] = [lead_case(b) for b in _r['bullets']]
B_HD, B_AUTO, HANDLE = lead_case(B_HD), lead_case(B_AUTO), lead_case(HANDLE)
