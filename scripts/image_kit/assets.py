"""Cutouts and source crops of real ILLUCO photos used by build_kit.py.

Every asset is derived from a file in image_kit/_sources by masking (background removal),
cropping, rotating or scaling only.
"""
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import kitlib as K

# source files (relative to image_kit/_sources) and their public URLs
S = {
    'single_lb_main': 'amazon/617bfZwQclL.jpg',
    'single_db_main': 'amazon/61FcYqxQdHL.jpg',
    'kit_db_main': 'amazon/71549oTdxFL.jpg',
    'kit_lb_box': 'shopify/dental-mirror__light_blue.jpg',
    'kit_db_box': 'shopify/dental-mirror__illuco_dental_mirrors_with_box.jpg',
    'heads_main': 'amazon/617IX-IYsEL.jpg',
    'single_head': 'shopify/mouth-mirror-heads__single-head.jpg',
    'double_head': 'shopify/mouth-mirror-heads__double-head_7873821b-dd72-4a9a-8cea-7147a90c92c9.jpg',
    'ds_main_lb': 'shopify/double-sided-dental-mirror__main.jpg',
    'ds_main_db': 'drive/ds_main_db.jpg',
    'dsdm01_lb': 'shopify/double-sided-dental-mirror__dsdm-01.jpg',
    'dsdm01_db': 'drive/dsdm-01_db.jpg',
    'dsdm03_lb': 'shopify/double-sided-dental-mirror__dsdm-03.jpg',
    'dsdm03_db': 'drive/dsdm-03_db.jpg',
    'dsdm04': 'shopify/double-sided-dental-mirror__dsdm-04.jpg',
    'grand01_lb': 'shopify/grand-dental-mirror__grand-01.jpg',
    'grand01_db': 'drive/grand-01_db.jpg',
    'grand04': 'drive/grand-04.jpg',
    'grand_main_lb': 'shopify/grand-dental-mirror__main_1b36fb35-6c34-4a82-81aa-68ef89447d58.jpg',
    'grand_main_db': 'shopify/grand-dental-mirror__main_db.jpg',
    'card_lb': 'amazon/7121KSv2hrL.jpg',
    'card_db': 'amazon/71fDe5PolUL.jpg',
    'card_heads': 'amazon/71f0mMI002L.jpg',
    'mag_art': 'shopify/dental-mirror__1-3x_magnification_dental_mirrors.jpg',
    'life_glove': 'amazon/51b9bFn2fiL.jpg',
    'life_typodont': 'amazon/61noMl85BeL.jpg',
    'life_tray': 'shopify/dental-mouth-mirror__mouth_mirror_light_blue.jpg',
}
SHOP = 'https://cdn.shopify.com/s/files/1/0795/1348/5611/files/'
AMZ = 'https://m.media-amazon.com/images/I/'
DRIVE = 'https://drive.google.com/file/d/'
URL = {
    'single_lb_main': AMZ + '617bfZwQclL.jpg',
    'single_db_main': AMZ + '61FcYqxQdHL.jpg',
    'kit_db_main': AMZ + '71549oTdxFL.jpg',
    'kit_lb_box': SHOP + 'light_blue.jpg',
    'kit_db_box': SHOP + 'illuco_dental_mirrors_with_box.jpg',
    'heads_main': AMZ + '617IX-IYsEL.jpg',
    'single_head': SHOP + 'single-head.jpg',
    'double_head': SHOP + 'double-head_7873821b-dd72-4a9a-8cea-7147a90c92c9.jpg',
    'ds_main_lb': SHOP + 'main.jpg',
    'ds_main_db': DRIVE + '1lOw74MwTc7cHDFNH4BYrfwgwVQMv_YT6 (main_db.jpg, Double-Sided)',
    'dsdm01_lb': SHOP + 'dsdm-01.jpg',
    'dsdm01_db': DRIVE + '1b9Zwhm8Wb7-spWZxLJzz1ELiRM7337K4 (dsdm-01_db.jpg)',
    'dsdm03_lb': SHOP + 'dsdm-03.jpg',
    'dsdm03_db': DRIVE + '10TZlOp0joNxqkhzdCnSjSSQny91paYBe (dsdm-03_db.jpg)',
    'dsdm04': SHOP + 'dsdm-04.jpg',
    'grand01_lb': SHOP + 'grand-01.jpg',
    'grand01_db': DRIVE + '12HbJgSv_t2gs1Mv5OTXet2Fi3965ySHd (grand-01_db.jpg)',
    'grand04': DRIVE + '1lQgJ64buFqtGefJS4yYFKonTe5Mq4hhw (grand-04.jpg)',
    'grand_main_lb': SHOP + 'main_1b36fb35-6c34-4a82-81aa-68ef89447d58.jpg',
    'grand_main_db': SHOP + 'main_db.jpg',
    'card_lb': AMZ + '7121KSv2hrL.jpg',
    'card_db': AMZ + '71fDe5PolUL.jpg',
    'card_heads': AMZ + '71f0mMI002L.jpg',
    'mag_art': SHOP + '1-3x_magnification_dental_mirrors.jpg',
    'life_glove': AMZ + '51b9bFn2fiL.jpg',
    'life_typodont': AMZ + '61noMl85BeL.jpg',
    'life_tray': SHOP + 'mouth_mirror_light_blue.jpg',
}


@lru_cache(maxsize=None)
def img(key):
    return K.load(S[key])


@lru_cache(maxsize=None)
def white_cut(key, lo=6, hi=34, close=0):
    im = img(key)
    al = K.alpha_white_bg(im, lo=lo, hi=hi, close=close)
    return K.trim(K.cutout(im, al))


def single_mirror(color):
    """Full Size 4 mirror with handle (diagonal, head top-left), white-background cutout."""
    return white_cut('single_lb_main' if color == 'lb' else 'single_db_main')


@lru_cache(maxsize=None)
def single_mirror_vertical(color):
    """The same photo rotated so the head is on top and the handle points straight down."""
    rgba = single_mirror(color)
    al = np.asarray(rgba.getchannel('A')) > 128
    ys, xs = np.nonzero(al)
    # principal axis of the mirror
    xm, ym = xs.mean(), ys.mean()
    cov = np.cov(np.vstack([xs - xm, ys - ym]))
    evals, evecs = np.linalg.eigh(cov)
    vx, vy = evecs[:, np.argmax(evals)]
    ang = np.degrees(np.arctan2(vy, vx))  # angle of main axis in image coords
    # rotate so axis is vertical (90 deg); PIL rotates counter-clockwise for positive angles
    rot = ang - 90
    out = K.trim(K.rotate_rgba(rgba, rot))
    # make sure head (wider end) is on top
    a = np.asarray(out.getchannel('A')) > 128
    h = a.shape[0]
    top_w = a[: h // 5].sum()
    bot_w = a[-h // 5:].sum()
    if bot_w > top_w:
        out = out.rotate(180, expand=True)
    return out


@lru_cache(maxsize=None)
def grand_alpha():
    """Alpha of the full Grand mirror in grand-01 (light blue, on navy). The dark-blue grand-01_db
    is a pixel-aligned recolour of the same photo, so the same alpha is used for both."""
    im = img('grand01_lb').crop((1750, 60, 2950, 2990))
    return K.alpha_dark_bg(im, K.NAVY, lo=12, hi=38)


@lru_cache(maxsize=None)
def grand_full(color):
    key = 'grand01_lb' if color == 'lb' else 'grand01_db'
    im = img(key).crop((1750, 60, 2950, 2990))
    return K.trim(K.cutout(im, grand_alpha(), bg_rgb=K.NAVY, erode_px=1))


@lru_cache(maxsize=None)
def ds_pair(color):
    """The two Double-Sided mirrors from the Double-Sided main (white bg; handles run off-frame)."""
    key = 'ds_main_lb' if color == 'lb' else 'ds_main_db'
    im = img(key)
    al = K.alpha_white_bg(im, lo=6, hi=30)
    return K.cutout(im, al)  # untrimmed: keeps the frame-edge crops aligned to canvas edges


@lru_cache(maxsize=None)
def single_head():
    return white_cut('single_head', lo=8, hi=36)


@lru_cache(maxsize=None)
def double_head():
    # higher lo drops the soft floor shadow under the head
    return white_cut('double_head', lo=22, hi=48)


@lru_cache(maxsize=None)
def grand_head_disc():
    """Grand Size 10 head (disc + upper neck) from the white-background Grand main."""
    im = img('grand_main_lb')
    al = K.alpha_white_bg(im, lo=6, hi=34)
    rgba = K.cutout(im, al)
    return rgba


def disc_geometry_photo(photo, dark=45):
    """Mirror-disc geometry in a white-background photo, from the steel rim/neck pixels only
    (darkness > `dark`, which ignores soft shadows). Returns centre, diameter and extents."""
    a = np.asarray(photo.convert('RGB')).astype(np.int32)
    m = (255 - a.min(axis=2)) > dark
    rows = np.nonzero(m.any(axis=1))[0]
    top = rows.min()
    xmin = np.full(m.shape[0], -1)
    xmax = np.full(m.shape[0], -1)
    for y in rows:
        xs = np.nonzero(m[y])[0]
        xmin[y], xmax[y] = xs.min(), xs.max()
    width = np.where(xmin >= 0, xmax - xmin, 0)
    ymax = int(np.argmax(width))
    wmax = int(width[ymax])
    bottom = ymax
    while bottom < m.shape[0] - 1 and width[bottom] >= 0.4 * wmax:
        bottom += 1
    height = bottom - top
    return {'cx': float((xmin[ymax] + xmax[ymax]) / 2), 'cy': float((top + bottom) / 2), 'w': wmax,
            'h': int(height), 'd': float(max(wmax, height)), 'top': int(top), 'bottom': int(bottom),
            'left': int(xmin[ymax]), 'right': int(xmax[ymax])}


def disc_geometry(rgba, y_max_frac=0.6):
    """Disc geometry from an RGBA cutout's alpha (used for the double head / layout anchors)."""
    a = np.asarray(rgba.getchannel('A')) > 128
    hh = int(a.shape[0] * y_max_frac)
    widths = a[:hh].sum(axis=1)
    wmax = widths.max()
    big = np.nonzero(widths > wmax * 0.35)[0]
    top = big.min()
    run_end = top
    for y in big:
        if y - run_end > 2:
            break
        run_end = y
    row = a[int(np.argmax(widths))]
    xs = np.nonzero(row)[0]
    return {'cx': (xs.min() + xs.max()) / 2, 'cy': (top + run_end) / 2, 'w': xs.max() - xs.min(),
            'h': run_end - top, 'top': top, 'bottom': run_end}


@lru_cache(maxsize=None)
def ds_box_main(color):
    """Double-Sided 5-pack kit photo from dsdm-03 / dsdm-03_db with the blue header/footer
    graphics removed (the box lid overlaps the header, so the lid is kept by a polygon traced
    from its straight edges). Returns an RGB image on pure white, cropped to the product."""
    key = 'dsdm03_lb' if color == 'lb' else 'dsdm03_db'
    im = img(key)
    a = np.asarray(im).astype(np.int32)
    Hh, Ww = a.shape[:2]
    col = a[:, Ww - 40]
    white = col.min(axis=1) > 240
    ys = np.nonzero(white)[0]
    y_top, y_bot = ys.min(), ys.max()  # photo band
    # lid pixels inside the header: light pixels connected to the photo band (flood upwards from
    # the last header row, so the separate 'Kit Includes' panel text is never reached)
    hdr = a[:y_top]
    light = (hdr[..., 0] > 150) & (hdr.min(axis=2) > 140)
    # the last few header rows are an anti-aliased transition: seed the flood a little above them
    seed_y = y_top - 6
    comp = np.zeros_like(light)
    comp[seed_y] = light[seed_y]
    comp[seed_y + 1:] = False
    lim = light.copy()
    lim[seed_y + 1:] = False
    n = comp.sum()
    while True:
        for _ in range(8):
            comp = K._dilate(comp) & lim
        m = comp.sum()
        if m == n:
            break
        n = m
    # the lid is convex: fill each row between its leftmost and rightmost lid pixel (keeps print)
    pts_l, pts_r = [], []
    for y in range(seed_y, -1, -1):
        xs = np.nonzero(comp[y])[0]
        if len(xs) < 2:
            break
        pts_l.append((xs.min(), y))
        pts_r.append((xs.max(), y))
    apex_y = pts_l[-1][1] if pts_l else y_top
    # straight lid edges fitted on the rows above the transition, extended down into the photo band
    nfit = min(80, len(pts_l))
    ys_fit = np.array([p[1] for p in pts_l[:nfit]], float)
    fl = np.polyfit(ys_fit, np.array([p[0] for p in pts_l[:nfit]], float), 1)
    fr = np.polyfit(ys_fit, np.array([p[0] for p in pts_r[:nfit]], float), 1)
    yb = y_top + 3
    poly = ([(float(np.polyval(fl, yb)), yb)] + [p for p in pts_l] + [p for p in reversed(pts_r)]
            + [(float(np.polyval(fr, yb)), yb)])
    mask_hdr = Image.new('L', (Ww * 4, (y_top + 4) * 4), 0)
    if len(poly) > 3:
        ImageDraw.Draw(mask_hdr).polygon([(x * 4 + 2, y * 4 + 2) for x, y in poly], fill=255)
    mask_hdr = mask_hdr.resize((Ww, y_top + 4), Image.LANCZOS).filter(ImageFilter.MinFilter(3))
    mh = np.asarray(mask_hdr, np.float32)[:y_top] / 255.0
    out = np.full_like(a, 255)
    # photo band: clean near-white background to pure white
    band = a[y_top:y_bot + 1].astype(np.float32)
    mn = band.min(axis=2)
    sat = band.max(axis=2) - mn
    t = np.clip((mn - 238) / (250 - 238), 0, 1) * (sat < 14)
    # the soft shadow beside the lid starts abruptly where the old header ended: outside the lid,
    # fade near-white pixels to white over the first rows of the band so no seam remains
    fade_rows = 260
    yy = np.arange(fade_rows)[:, None] + y_top
    xx = np.arange(Ww)[None, :]
    outside = (xx > np.polyval(fr, yy) + 10) | (xx < np.polyval(fl, yy) - 10)
    w = (1 - np.arange(fade_rows) / fade_rows)[:, None] * outside
    near_white = np.clip((mn[:fade_rows] - 215) / (238 - 215), 0, 1) * (sat[:fade_rows] < 16)
    t[:fade_rows] = np.maximum(t[:fade_rows], w * near_white)
    band = band * (1 - t[..., None]) + 255 * t[..., None]
    out[y_top:y_bot + 1] = band.astype(np.int32)
    # header: keep lid only
    hdr_out = hdr.astype(np.float32) * mh[..., None] + 255 * (1 - mh[..., None])
    out[:y_top] = hdr_out.astype(np.int32)
    out[y_bot - 2:] = 255  # bottom graphic band
    out[:, :8] = 255
    out[:, -8:] = 255
    res = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), 'RGB')
    # crop to product
    arr = np.asarray(res)
    yy, xx = np.nonzero(arr.min(axis=2) < 236)
    box = (xx.min(), yy.min(), xx.max() + 1, yy.max() + 1)
    return res.crop(box), {'apex_y': int(apex_y), 'y_top': int(y_top), 'y_bot': int(y_bot), 'box': box}


@lru_cache(maxsize=None)
def single_mirror_vertical_angle(color):
    """Rotation (degrees, PIL convention) that stands the diagonal single-mirror photo upright."""
    im = img('single_lb_main' if color == 'lb' else 'single_db_main')
    a = np.asarray(im).astype(np.int32)
    m = (255 - a.min(axis=2)) > 40
    ys, xs = np.nonzero(m)
    xm, ym = xs.mean(), ys.mean()
    cov = np.cov(np.vstack([xs - xm, ys - ym]))
    evals, evecs = np.linalg.eigh(cov)
    vx, vy = evecs[:, np.argmax(evals)]
    ang = np.degrees(np.arctan2(vy, vx))
    # PIL rotate(+deg) turns counter-clockwise; we want the axis vertical with the head (upper-left) on top
    rot = ang + 90 if ang < 0 else ang - 90
    # head is at the upper-left in both photos -> after rotation it must be on top
    return float(rot)
