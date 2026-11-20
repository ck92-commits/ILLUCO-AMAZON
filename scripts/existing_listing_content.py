"""Rewritten content for every live ILLUCO dental-mirror ASIN on amazon.com.

House style follows ILLUCO's own Grand / Double-Sided upload file: a title under 75
characters (so Amazon shows the Item Highlight in search), a feature-led Item Highlight,
five CAPS-led bullets, a description paragraph and backend generic keywords.

Facts used here come from the live Amazon listings and illuco.com (scraped 2026-11-20).
Anything not verified is marked in CONFIRM and must be checked before upload.
"""

INTRO = ("The first thing dental professionals notice about an ILLUCO mirror is the view. "
         "Most dental mirrors reflect only 60-70% of available light. ILLUCO's UHD front surface "
         "dielectric coating on German optical glass reflects 99%, so the image is over 40% brighter, "
         "sharp, true to color and free of the ghost images that cause visual fatigue. ")
STERIL = ("Sterilize at 273°F (134°C) for 5 minutes or 250°F (121°C) for 20 minutes; "
          "do not exceed 277°F (136°C).")
B_LOOK = ("SEE THE DIFFERENCE AT FIRST LOOK: Most dental mirrors reflect only 60-70% of light. "
          "ILLUCO's UHD front surface dielectric coating on German optical glass reflects 99%, for an "
          "image over 40% brighter, crisp, true to color and free of ghosting. Look into it once and "
          "you will notice it.")
B_FOG = ("FOG-RESISTANT, AUTOCLAVE-RATED FOR 100 CYCLES: Water-repellent coating sheds saliva and "
         "spray mid-procedure. Glass and coating are rated for 100 autoclave cycles. " + STERIL +
         " Avoid abrasive wiping to protect the coating.")


def mag_bullet(mag):
    if mag == 1:
        return ("TRUE 1X VIEW: Life-size, distortion-free reflection for routine exams, restorative "
                "checks and indirect vision. Need more detail? Also available in 2X and 3X magnification.")
    return (f"{mag}X MAGNIFICATION FOR FINE DETAIL: Enlarges margins, caries and calculus for close "
            "inspection. Magnifying mirrors show a smaller area and focus best close to the tooth; "
            "choose 1X for general exams and wide views.")


HANDLE = ("ERGONOMIC ANTI-ROTATION HANDLE: The textured, finger-indented handle keeps the head steady "
          "in a light or firm grip and is easy to turn with wet gloves. The Size 4 head uses a standard "
          "cone socket, so ILLUCO replacement heads thread straight on.")


def kit(mag, color, sku_model, asin, rating, note=''):
    magtxt = '1X' if mag == 1 else f'{mag}X Magnifying'
    title = f"ILLUCO UHD Dental Mirror Kit, Size 4 (22mm), {mag}X, 5 Pack, {color}"
    return dict(
        family='5-Pack with Handles', parent='B0FDCGG69J', asin=asin, mag=mag, color=color,
        model_suggested=sku_model, rating=rating,
        title=title,
        highlight=("With Handles, Front Surface, Cone Socket, 99% Reflectance, Fog-Resistant, "
                   "Autoclave-Rated 100 Cycles, No Ghost Image"),
        bullets=[B_LOOK, mag_bullet(mag), HANDLE, B_FOG,
                 f"5 PACK WITH HANDLES: 5 Size 4 (22mm) front surface mirror heads ({magtxt}), 5 ergonomic "
                 f"anti-rotation handles ({color}) and an autoclave sterilization and care guide. Built "
                 "for general dentists, hygienists, orthodontists and dental students."],
        description=(INTRO + "Each kit puts that view on a standard Size 4 (22mm) cone socket head "
                     f"in {magtxt.lower()} and pairs it with an ergonomic anti-rotation handle that "
                     "stays steady in a light or firm grip. A water-repellent coating keeps the view "
                     "clear mid-procedure, and the glass and coating are rated for 100 autoclave cycles. "
                     + STERIL + " Each kit includes 5 Size 4 mirror heads, 5 ergonomic handles and an "
                     "autoclave sterilization and care guide. Available in 1X, 2X and 3X magnification "
                     "with Light Blue or Dark Blue handles."),
        keywords=("mouth mirror dentist tools dental instruments tooth teeth oral exam intraoral hygienist "
                  "orthodontist anti fog front surface number 4 professional dentist mirror for inside mouth "
                  "hd high definition magnifying concave set kit"),
        size='Size 4 (22mm)', items=5,
        included=f"5 Size 4 Mirror Heads, 5 Ergonomic Handles, Autoclave Sterilization & Care Guide",
        note=note)


def heads(mag, asin, model, rating, note=''):
    magtxt = '1X' if mag == 1 else f'{mag}X Magnifying'
    return dict(
        family='Replacement Heads 5-Pack', parent='B0FCNL53JN', asin=asin, mag=mag, color='',
        model_suggested=model, rating=rating,
        title=f"ILLUCO UHD Dental Mirror Heads, Size 4 (22mm), {mag}X, 5 Pack, Cone Socket",
        highlight=("Replacement Heads, Handles Not Included, Front Surface, 99% Reflectance, "
                   "Fog-Resistant, Autoclave-Rated 100 Cycles"),
        bullets=[B_LOOK,
                 "CONE SOCKET FIT, HANDLES NOT INCLUDED: Threads onto standard cone socket mirror handles, "
                 "including ILLUCO ergonomic anti-rotation handles. Not for simple stem or European-thread "
                 "handles. Check your handle before ordering.",
                 mag_bullet(mag), B_FOG,
                 f"5 REPLACEMENT HEADS: 5 single-sided Size 4 (22mm) front surface mirror heads ({magtxt}). "
                 "Restock every operatory with the same bright, ghost-free view. Need handles too? Choose "
                 "the ILLUCO 5 Pack with Handles."],
        description=(INTRO + f"These replacement heads bring that view to the handles you already use: "
                     f"standard Size 4 (22mm), {magtxt.lower()}, with a cone socket thread that fits cone "
                     "socket mirror handles including ILLUCO ergonomic handles (sold separately). They do "
                     "not fit simple stem or European-thread handles. A water-repellent coating keeps the "
                     "view clear, and the glass and coating are rated for 100 autoclave cycles. " + STERIL +
                     " Each pack includes 5 mirror heads. Handles are not included."),
        keywords=("mouth mirror heads replacement refill tops screw on dentist dental instruments tooth teeth "
                  "oral exam intraoral hygienist anti fog front surface number 4 professional dentist mirror "
                  "hd high definition magnifying concave"),
        size='Size 4 (22mm)', items=5, included='5 Size 4 Mirror Heads',
        note=note)


def single(mag, color, asin, model, rating, note=''):
    magtxt = '1X' if mag == 1 else f'{mag}X Magnifying'
    return dict(
        family='Single Mirror with Handle', parent='B0GGD9DVP9', asin=asin, mag=mag, color=color,
        model_suggested=model, rating=rating,
        title=f"ILLUCO UHD Dental Mirror, Size 4 (22mm), {mag}X, 1 Pack, {color}",
        highlight=("With Handle, Single Mirror, Front Surface, Cone Socket, 99% Reflectance, "
                   "Fog-Resistant, Autoclave-Rated 100 Cycles"),
        bullets=[B_LOOK, mag_bullet(mag), HANDLE, B_FOG,
                 f"1 MIRROR WITH HANDLE: Includes 1 Size 4 (22mm) front surface mirror head ({magtxt}) on 1 "
                 f"ergonomic anti-rotation handle ({color}). Ideal for dental students, a spare for the "
                 "operatory or a first try of ILLUCO. Equipping a practice? Choose the 5 Pack."],
        description=(INTRO + "This single mirror puts that view on a standard Size 4 (22mm) cone socket "
                     f"head in {magtxt.lower()}, mounted on an ergonomic anti-rotation handle. A "
                     "water-repellent coating keeps the view clear mid-procedure, and the glass and coating "
                     "are rated for 100 autoclave cycles. " + STERIL + " Includes 1 mirror and 1 handle. "
                     "Also available in 5 packs and as replacement heads."),
        keywords=("mouth mirror dentist tools dental instruments tooth teeth oral exam intraoral hygienist "
                  "student anti fog front surface number 4 professional dentist mirror for inside mouth hd "
                  "high definition magnifying concave single"),
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


ROWS = [
    kit(1, 'Dark Blue', 'IDM-2C41DB', 'B0FCZBD1KY', '3.4 (5 ratings, family)'),
    kit(1, 'Light Blue', 'IDM-2C41LB', 'B0F84VWGG5', 'family 3.4'),
    kit(2, 'Dark Blue', 'IDM-2C42DB', 'B0F84TKGLS', 'family 3.4'),
    kit(2, 'Light Blue', 'IDM-2C42LB', 'B0FCMVZH31', 'family 3.4'),
    kit(3, 'Dark Blue', 'IDM-2C43DB', 'B0F85B5BDC', 'family 3.4 (this variant shows a 1-star)'),
    kit(3, 'Light Blue', 'IDM-2C43LB', 'B0F857HKBG', 'family 3.4'),
    heads(1, 'B0FBPG5CS9', 'IDM-3C41NA', '2.0 (2 reviews, family)'),
    heads(2, 'B0FCHH2SQB', 'IDM-3C42NA', 'family 2.0'),
    heads(3, 'B0FCJY3H9H', 'IDM-3C43NA', 'family 2.0'),
    single(1, 'Light Blue', 'B0GGDQ15DD', '', '5.0 (1 rating, family)',
           'Variation value "Blue" -> rename to "Light Blue" to match the 5-pack and new Grand listings.'),
    single(1, 'Dark Blue', 'B0GGF37FSB', '', 'family 5.0'),
    single(2, 'Light Blue', 'B0GGDV4J6B', '', 'family 5.0', 'Rename "Blue" -> "Light Blue".'),
    single(2, 'Dark Blue', 'B0GGD95T8Z', '', 'family 5.0'),
    single(3, 'Light Blue', 'B0GGDS9MVF', '', 'family 5.0', 'Rename "Blue" -> "Light Blue".'),
    single(3, 'Dark Blue', 'B0GGDGRHRR', '', '1.0 (1 rating) - ORPHAN',
           'ORPHAN: not in family B0GGD9DVP9. Add as the missing "3X / Dark Blue" child so it shares the family rating.'),
    single(1, 'Light Blue', 'B0G2DYRY7T', '', '3.4 (3 ratings) - ORPHAN, best BSR (#30 Dental Mirrors)',
           'ORPHAN DUPLICATE of the 1X single mirror. Photos show a black shank. Confirm the product, then either '
           'ask Seller Support to merge it into B0GGDQ15DD, or make it the 1X child and close B0GGDQ15DD. Its A+ '
           'currently uses photo-mirror copy ("intraoral photos") - replace.'),
    photo('Occlusal Large'), photo('Occlusal Medium'), photo('Occlusal Small'),
    photo('Lingual'), photo('Buccal'),
]

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
    'Suggested model numbers follow the illuco.com pattern (IDM-2C41DB = 5-pack 1X Dark Blue; IDM-3C41NA = heads 1X); confirm 2X/3X codes',
    'B0G2DYRY7T is the same product as the 1X single mirror (its photos show a black shank)',
    'Photo-mirror dimensions for Occlusal Small, Lingual and Buccal; whether the Amazon box includes the travel pouch',
    'Double-Sided head (IDM-3CD41H) pack size = 5, cone socket, price, images and package dimensions',
]
