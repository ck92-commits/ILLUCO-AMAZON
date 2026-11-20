"""Layouts for every slot of the ILLUCO Amazon image kit (2000 x 2000 px).

Each function returns a PIL RGB image. Product imagery is always a real ILLUCO photo (cropped,
masked, rotated, scaled or composited); everything else is layout, vector shapes and text.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import assets as A
import kitlib as K
from kitlib import W, H

COLOR_NAME = {'lb': 'Light Blue', 'db': 'Dark Blue'}


# ================================================================ helpers
def white():
    return Image.new('RGB', (W, H), K.WHITE)


def multiply_paste(canvas, photo, xy):
    """Paste a white-background photo with a multiply blend: white disappears into the canvas,
    product and its natural shadow stay. Works on any light canvas."""
    x, y = int(round(xy[0])), int(round(xy[1]))
    x0, y0 = max(x, 0), max(y, 0)
    x1, y1 = min(x + photo.width, canvas.width), min(y + photo.height, canvas.height)
    if x1 <= x0 or y1 <= y0:
        return
    region = np.asarray(canvas.crop((x0, y0, x1, y1)), np.float32)
    ph = np.asarray(photo.convert('RGB').crop((x0 - x, y0 - y, x1 - x, y1 - y)), np.float32)
    out = region * ph / 255.0
    canvas.paste(Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), 'RGB'), (x0, y0))


def photo_bbox(photo, thresh=244, pad=0):
    a = np.asarray(photo.convert('RGB'))
    ys, xs = np.nonzero(a.min(axis=2) < thresh)
    return (max(xs.min() - pad, 0), max(ys.min() - pad, 0), min(xs.max() + 1 + pad, photo.width),
            min(ys.max() + 1 + pad, photo.height))


def tight(photo, pad=0, thresh=244):
    return photo.crop(photo_bbox(photo, thresh, pad))


def rotate_white(photo, deg):
    return photo.convert('RGB').rotate(deg, resample=Image.BICUBIC, expand=True, fillcolor=(255, 255, 255))


def header(img, title, subtitle=None, band_h=300, title_size=96, sub_size=56):
    """Navy gradient header band with white headline (ILLUCO dsdm-03 / grand-03 style)."""
    band = K.gradient((W, band_h), K.NAVY, K.BLUE_HEADER, 'h')
    img.paste(band, (0, 0))
    d = ImageDraw.Draw(img)
    if subtitle:
        th, _, _ = K.text_block(d, (110, 0), title, title_size, 'bold', K.WHITE, max_w=W - 220,
                                display=True, max_lines=1, min_size=90, dry=True)
        sh, _, _ = K.text_block(d, (110, 0), subtitle, sub_size, 'medium', K.WHITE, max_w=W - 220,
                                max_lines=1, min_size=56, dry=True)
        gap = 34
        y0 = (band_h - (th + gap + sh)) / 2
        K.text_block(d, (110, y0), title, title_size, 'bold', K.WHITE, max_w=W - 220, display=True,
                     max_lines=1, min_size=90, align='center')
        K.text_block(d, (110, y0 + th + gap), subtitle, sub_size, 'medium', (205, 225, 250),
                     max_w=W - 220, max_lines=1, min_size=56, align='center')
    else:
        th, _, n = K.text_block(d, (110, 0), title, title_size, 'bold', K.WHITE, max_w=W - 220,
                                display=True, max_lines=2, min_size=90, dry=True)
        K.text_block(d, (110, (band_h - th) / 2), title, title_size, 'bold', K.WHITE, max_w=W - 220,
                     display=True, max_lines=2, min_size=90, align='center')
    return band_h


def footer_band(img, h=46):
    img.paste(K.gradient((W, h), K.NAVY, K.BLUE_HEADER, 'h'), (0, H - h))


def pill(img, box, text, size=56, fill=K.BLUE, fg=K.WHITE, weight='semibold'):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    K.aa_draw(img, lambda g, s: g.rounded_rectangle((x0 * s, y0 * s, x1 * s, y1 * s),
                                                    radius=(y1 - y0) / 2 * s, fill=fill + (255,)))
    f = K.font(size, weight)
    K.check_copy(text)
    d.text(((x0 + x1) / 2, (y0 + y1) / 2), text, font=f, fill=fg, anchor='mm')


# ================================================================ 01 MAIN
def main_reuse(key):
    """Existing clean main: re-encoded on a 2000 px pure-white canvas, framing unchanged
    (or scaled down from 2560 px)."""
    im = A.img(key)
    if im.size != (W, H):
        im = im.resize((W, H), Image.LANCZOS)
    return im


def main_ds_box(color):
    """Double-Sided 5-pack: real kit photo (5 mirrors + 5 handles in the box) from dsdm-03 with the
    graphic header removed, placed on pure white."""
    photo, _ = A.ds_box_main(color)
    img = white()
    ph = K.fit(photo, int(W * 0.90), int(H * 0.90))
    img.paste(ph, ((W - ph.width) // 2, (H - ph.height) // 2))
    return img


def main_grand_pair(color):
    """Grand 2-pack: two cutouts of the full Grand mirror photo (grand-01 / grand-01_db),
    slightly fanned, on pure white with a soft contact shadow."""
    m = A.grand_full(color)
    target_h = int(H * 0.86)
    s = target_h / m.height
    a = K.scale(m, s)
    left = K.trim(K.rotate_rgba(a, 4))
    right = K.trim(K.rotate_rgba(a, -4))
    img = white()
    gap = 120
    total_w = left.width + right.width + gap
    x0 = (W - total_w) // 2
    yl = (H - left.height) // 2 + 30
    yr = (H - right.height) // 2 - 30
    sh = (14, 18, 22, 0.16)
    K.paste(img, left, (x0, yl), shadow=sh)
    K.paste(img, right, (x0 + left.width + gap, yr), shadow=sh)
    return img


def main_ds_heads():
    """Double-Sided heads 5-pack: five cutouts of the real IDM-3CD41H head photo, stacked."""
    hd = A.double_head()
    s = (W * 0.80) / hd.width
    a = K.scale(hd, s)
    img = white()
    n = 5
    dy = 250
    dx = 34
    total_h = a.height + dy * (n - 1)
    total_w = a.width + dx * (n - 1)
    x0 = (W - total_w) // 2
    y0 = (H - total_h) // 2
    for i in range(n):
        K.paste(img, a, (x0 + dx * i, y0 + dy * i), shadow=(10, 16, 16, 0.14))
    return img


# ================================================================ 02 WHAT'S IN THE BOX
def in_the_box(photo, count_lines, items, warning=None, layout='side', photo_is_rgba=False,
               title="WHAT'S IN THE BOX"):
    """photo: white-background RGB photo (multiply-pasted) or RGBA cutout.
    count_lines: big count statement lines; items: list of item strings (check icons)."""
    img = white()
    top = header(img, title)
    footer_band(img)
    d = ImageDraw.Draw(img)
    if layout == 'side':
        tx0, tx1 = 1060, W - 90
    else:
        tx0, tx1 = 150, W - 150
    tw = tx1 - tx0
    # measure the text column first
    cnt_h = 0
    for ln in count_lines:
        h, _, _ = K.text_block(d, (0, 0), ln, 104, 'extrabold', max_w=tw, display=True, max_lines=2,
                               min_size=90, dry=True)
        cnt_h += h + 26
    item_h = []
    for it in items:
        h, _, _ = K.text_block(d, (0, 0), it, 58, 'medium', max_w=tw - 110, max_lines=3, min_size=56, dry=True)
        item_h.append(h)
    warn_h = 116 if warning else 0
    total = cnt_h + 60 + sum(item_h) + 54 * (len(items) - 1) + (70 + warn_h if warning else 0)
    if layout == 'side':
        px0, py0, px1, py1 = 70, top + 60, 1010, H - 110
        y = top + (H - 46 - top - total) / 2
    else:  # stack: photo on top, text below
        y = H - 46 - 70 - total
        px0, py0, px1, py1 = 120, top + 50, W - 120, y - 60
        if py1 - py0 < 600:
            raise K.Overflow('in_the_box: photo area too small')
    # photo
    if photo_is_rgba:
        ph = K.fit(photo, px1 - px0, py1 - py0)
        K.paste(img, ph, (px0 + (px1 - px0 - ph.width) / 2, py0 + (py1 - py0 - ph.height) / 2),
                shadow=(12, 16, 18, 0.14))
    else:
        ph = K.fit(tight(photo, pad=10), px1 - px0, py1 - py0)
        multiply_paste(img, ph, (px0 + (px1 - px0 - ph.width) / 2, py0 + (py1 - py0 - ph.height) / 2))
    for ln in count_lines:
        h, _, _ = K.text_block(d, (tx0, y), ln, 104, 'extrabold', K.NAVY_TEXT, max_w=tw, display=True,
                               max_lines=2, min_size=90, align='left' if layout == 'side' else 'center')
        y += h + 26
    # accent rule
    if layout == 'side':
        d.rectangle((tx0, y + 14, tx0 + 150, y + 24), fill=K.BLUE)
    else:
        d.rectangle((W / 2 - 75, y + 14, W / 2 + 75, y + 24), fill=K.BLUE)
    y += 60
    if layout == 'side':
        for it, h in zip(items, item_h):
            K.check_icon(img, (tx0 + 38, y + 30), 70)
            K.text_block(d, (tx0 + 100, y), it, 58, 'medium', K.NAVY_TEXT, max_w=tw - 110, max_lines=3,
                         min_size=56)
            y += h + 54
    else:
        # items centred as a block
        widths = [min(tw - 110, K.text_w(it, K.font(58, 'medium'))) for it in items]
        bw = max(widths) + 100
        bx = (W - bw) / 2
        for it, h in zip(items, item_h):
            K.check_icon(img, (bx + 38, y + 30), 70)
            K.text_block(d, (bx + 100, y), it, 58, 'medium', K.NAVY_TEXT, max_w=tw - 110, max_lines=3,
                         min_size=56)
            y += h + 54
    if warning:
        y += 16
        f = K.font(60, 'bold')
        K.check_copy(warning)
        wtxt = K.text_w(warning, f)
        bw = wtxt + 200
        bx = tx0 if layout == 'side' else (W - bw) / 2
        if layout == 'side':
            bw = min(bw, tw)
        box = (bx, y, bx + bw, y + 116)
        K.aa_draw(img, lambda g, s: g.rounded_rectangle([v * s for v in box], radius=58 * s,
                                                        fill=(253, 236, 236, 255), outline=K.RED + (255,),
                                                        width=5 * s))
        K.cross_icon(img, (bx + 70, y + 58), 64)
        d.text((bx + 120, y + 58), warning, font=f, fill=K.RED, anchor='lm')
    return img


def heads_row(n=5):
    """n copies of the real single-sided head photo side by side (white background)."""
    hd = A.single_head()
    s = 1500 / hd.height
    a = K.scale(hd, s)
    gap = -40
    canvas = Image.new('RGBA', (a.width * n + gap * (n - 1) + 40, a.height + 40), (255, 255, 255, 0))
    for i in range(n):
        K.paste(canvas, a, (20 + i * (a.width + gap), 20), shadow=(8, 12, 12, 0.12))
    return canvas


def heads_stack_rgba(n=5):
    hd = A.double_head()
    s = 1400 / hd.width
    a = K.scale(hd, s)
    dy, dx = 230, 30
    canvas = Image.new('RGBA', (a.width + dx * (n - 1) + 40, a.height + dy * (n - 1) + 40), (255, 255, 255, 0))
    for i in range(n):
        K.paste(canvas, a, (20 + dx * i, 20 + dy * i), shadow=(8, 12, 12, 0.12))
    return canvas


def grand_pair_rgba(color):
    m = A.grand_full(color)
    a = K.scale(m, 1500 / m.height)
    left = K.trim(K.rotate_rgba(a, 4))
    right = K.trim(K.rotate_rgba(a, -4))
    gap = 90
    canvas = Image.new('RGBA', (left.width + right.width + gap + 40, max(left.height, right.height) + 100),
                       (255, 255, 255, 0))
    K.paste(canvas, left, (20, 70))
    K.paste(canvas, right, (20 + left.width + gap, 10))
    return canvas


# ================================================================ 03 KEY BENEFIT (corrected cards)
def card_redraw(base, card_box, items, title_size=60, body_size=56, pad_x=72, pad_y=76, radius=14,
                max_sep=150):
    """Redraw the white copy card of an existing ILLUCO infographic with corrected copy.
    The new card fully covers the old one; the photo side is untouched."""
    img = base.copy()
    if img.size != (W, H):
        img = img.resize((W, H), Image.LANCZOS)
    x0, y0, x1, y1 = card_box
    K.aa_draw(img, lambda g, s: g.rounded_rectangle((x0 * s, y0 * s, x1 * s, y1 * s), radius=radius * s,
                                                    fill=(255, 255, 255, 255)))
    d = ImageDraw.Draw(img)
    tw = x1 - x0 - 2 * pad_x
    gap_tb = 20
    meas = []
    for t, b in items:
        th, _, _ = K.text_block(d, (0, 0), t, title_size, 'bold', max_w=tw, max_lines=2, min_size=56, dry=True)
        bh, _, _ = K.text_block(d, (0, 0), b, body_size, 'regular', max_w=tw, max_lines=4, min_size=56, dry=True)
        meas.append((th, bh))
    content = sum(th + gap_tb + bh for th, bh in meas)
    n = len(items)
    avail = (y1 - y0) - 2 * pad_y
    slack = avail - content
    if slack < (n - 1) * 56:
        raise K.Overflow(f'card overflow: content {content} avail {avail}')
    sep = min(slack / (n - 1), max_sep)
    used = content + sep * (n - 1)
    y = y0 + pad_y + (avail - used) / 2
    for i, ((t, b), (th, bh)) in enumerate(zip(items, meas)):
        K.text_block(d, (x0 + pad_x, y), t, title_size, 'bold', K.CARD_TEXT, max_w=tw, max_lines=2, min_size=56)
        K.text_block(d, (x0 + pad_x, y + th + gap_tb), b, body_size, 'regular', K.CARD_TEXT, max_w=tw,
                     max_lines=4, min_size=56)
        y += th + gap_tb + bh
        if i < n - 1:
            ly = y + sep / 2 + 6
            d.line((x0, ly, x1, ly), fill=K.DIVIDER, width=3)
            y += sep
    return img


ITEM_99 = ('99% Reflectance', 'Over 40% brighter than standard dental mirrors, which reflect 60–70%.')
ITEM_FS = ('Front-Surface Dielectric Coating', 'Maximizes reflectivity while minimizing light loss.')
ITEM_FS_LONG = ('Front-Surface Dielectric Coating',
                'Maximizes reflectivity while minimizing light loss for a consistently sharp image.')
ITEM_GHOST = ('No Ghost Image', 'A single, sharp reflection with no double image.')
ITEM_DUR = ('Built for Long-Term Durability',
            'Engineered to withstand repeated clinical use and sterilization cycles.')
ITEM_ERGO = ('Ergonomic, Anti-Rotation Design', 'Comfortable grip with stable positioning during use.')
ITEM_CONE = ('Cone Socket Fit', 'Threads onto cone socket handles. Not for simple stem or European-thread handles.')


def key_benefit_size4(color):
    base = A.img('card_lb' if color == 'lb' else 'card_db')
    return card_redraw(base, (96, 96, 1107, 1903), [ITEM_99, ITEM_FS, ITEM_GHOST, ITEM_DUR, ITEM_ERGO])


def key_benefit_heads():
    return card_redraw(A.img('card_heads'), (96, 96, 1107, 1903), [ITEM_99, ITEM_FS, ITEM_GHOST, ITEM_DUR, ITEM_CONE])


def key_benefit_grand(color):
    base = A.img('grand01_lb' if color == 'lb' else 'grand01_db')
    items = [('Expansive Field of View',
              'Instantly view an entire quadrant or multiple teeth, reducing the need to pan or tilt.'),
             ITEM_99, ITEM_FS_LONG, ITEM_GHOST, ITEM_DUR]
    return card_redraw(base, (96, 72, 1290, 1939), items)


def key_benefit_ds(color):
    base = A.img('dsdm01_lb' if color == 'lb' else 'dsdm01_db')
    items = [('Dual-Sided Viewing', 'Two-sided reflection minimizes mirror changing during procedures.'),
             ('99% Reflectance on Both Faces',
              'Over 40% brighter than standard dental mirrors, which reflect 60–70%.'),
             ITEM_FS_LONG, ITEM_GHOST]
    return card_redraw(base, (96, 72, 1068, 1939), items)


def key_benefit_ds_heads():
    """New: double-sided head on navy with the three core optical benefits."""
    img = Image.new('RGB', (W, H), K.NAVY)
    img.paste(K.gradient((W, H), (0, 40, 84), (0, 70, 140), 'd'), (0, 0))
    d = ImageDraw.Draw(img)
    K.text_block(d, (110, 120), '99% REFLECTANCE', 120, 'extrabold', K.WHITE, max_w=W - 220, display=True,
                 max_lines=1, min_size=90, align='center')
    K.text_block(d, (110, 280), 'on both faces of every head', 64, 'medium', (190, 215, 245), max_w=W - 220,
                 max_lines=1, min_size=56, align='center')
    hd = A.double_head()
    ph = K.fit(hd, 1640, 520)
    K.paste(img, ph, ((W - ph.width) / 2, 470), shadow=(0, 24, 30, 0.35))
    # three benefit cards
    items = [('Front-surface dielectric coating', 'on German optical glass'),
             ('No ghost image', 'one sharp reflection, no double image'),
             ('Over 40% brighter', 'than standard 60–70% dental mirrors')]
    cw, ch, gap = 560, 640, 50
    x = (W - (3 * cw + 2 * gap)) / 2
    y = 1150
    for t, b in items:
        K.aa_draw(img, lambda g, s, x=x: g.rounded_rectangle((x * s, y * s, (x + cw) * s, (y + ch) * s),
                                                             radius=26 * s, fill=(255, 255, 255, 255)))
        K.check_icon(img, (x + cw / 2, y + 110), 110)
        th, _, _ = K.text_block(d, (x + 50, y + 210), t, 62, 'bold', K.CARD_TEXT, max_w=cw - 100, max_lines=3,
                                min_size=56, align='center')
        K.text_block(d, (x + 50, y + 210 + th + 30), b, 56, 'regular', K.NAVY_TEXT, max_w=cw - 100,
                     max_lines=4, min_size=56, align='center')
        x += cw + gap
    return img


# ================================================================ 04 MAGNIFICATION / SIZE / BOTH FACES
def magnification_guide():
    img = white()
    top = header(img, 'CHOOSE YOUR MAGNIFICATION', 'Same Size 4 (22 mm) head, three views')
    footer_band(img)
    d = ImageDraw.Draw(img)
    art = A.img('mag_art')  # ILLUCO's 1x / 2x / 3x view circles
    centers = [(468, 1157), (1021, 1157), (1574, 1157)]
    r_src = 246
    cols = [(W / 6) * (1 + 2 * i) for i in range(3)]
    diam = 520
    labels = [('1X', 'True size', 'Widest area', 'General exams'),
              ('2X', 'Detail 2× larger', 'Smaller area', 'Work closer'),
              ('3X', 'Detail 3× larger', 'Smallest area', 'Work closest')]
    y_c = top + 70
    for (cx_src, cy_src), cx, lab in zip(centers, cols, labels):
        c = K.circle_crop(art, (cx_src, cy_src), r_src, diam, ring=14, ring_color=(200, 222, 248))
        K.paste(img, c, (cx - diam / 2, y_c), shadow=(0, 14, 20, 0.22))
        K.text_line(d, (cx, y_c + diam + 40), lab[0], 150, 'extrabold', K.NAVY_TEXT, anchor='ma', display=True)
        yy = y_c + diam + 230
        K.text_line(d, (cx, yy), lab[1], 58, 'bold', K.BLUE, anchor='ma')
        K.text_line(d, (cx, yy + 80), lab[2], 56, 'regular', K.NAVY_TEXT, anchor='ma')
        K.text_line(d, (cx, yy + 160), lab[3], 56, 'regular', K.NAVY_TEXT, anchor='ma')
    # arrow bar
    ya = y_c + diam + 520
    bar = K.gradient((1640, 22), (150, 190, 235), K.NAVY, 'h')
    img.paste(bar, (180, ya))
    K.aa_draw(img, lambda g, s: g.polygon([(1820 * s, (ya - 26) * s), (1880 * s, (ya + 11) * s),
                                           (1820 * s, (ya + 48) * s)], fill=K.NAVY + (255,)))
    K.text_line(d, (180, ya + 50), 'Wider view', 56, 'semibold', K.GREY_TEXT, anchor='la')
    K.text_line(d, (1880, ya + 50), 'More detail', 56, 'semibold', K.NAVY_TEXT, anchor='ra')
    K.text_block(d, (150, ya + 170), 'Magnified mirrors enlarge detail but show a smaller area, so they work '
                 'best held close to the tooth.', 56, 'regular', K.NAVY_TEXT, max_w=W - 300, max_lines=2,
                 min_size=56, align='center')
    return img


def _head_photo_with_fade(photo, crop_box, fade_px):
    """Crop a white-background photo and fade its bottom edge to white."""
    c = photo.crop(crop_box).convert('RGB')
    a = np.asarray(c, np.float32)
    h = a.shape[0]
    t = np.ones(h, np.float32)
    t[h - fade_px:] = np.linspace(1, 0, fade_px)
    a = a * t[:, None, None] + 255 * (1 - t[:, None, None])
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGB')


def size_guide_grand():
    img = white()
    top = header(img, 'GRAND SIZE 10 vs. SIZE 4', 'About 2.4× the viewing area of a Size 4 mirror')
    footer_band(img)
    d = ImageDraw.Draw(img)
    # Size 4 head (single-head photo) and Grand head (Grand main photo) at true 22 : 34 scale,
    # measured on the steel rim of each disc (soft shadows ignored)
    s4 = A.img('single_head')
    g10 = A.img('grand_main_lb')
    geo4 = A.disc_geometry_photo(s4)
    geo10 = A.disc_geometry_photo(g10)
    D10 = 800
    D4 = D10 * 22 / 34
    sc4, sc10 = D4 / geo4['w'], D10 / geo10['w']
    disc_top = top + 300
    base_y = H - 360
    fade = 260
    def crop_for(photo, geo, sc):
        cx, ty = geo['cx'], geo['top']
        half = geo['w'] * 0.62
        box = (int(cx - half), int(ty - 30), int(cx + half), int(ty + (base_y - disc_top) / sc))
        return K.scale(_head_photo_with_fade(photo, box, int(fade / sc)), sc), half * sc
    sp, h4 = crop_for(s4, geo4, sc4)
    gp, h10 = crop_for(g10, geo10, sc10)
    cx4, cx10 = 560, 1360
    multiply_paste(img, sp, (cx4 - h4, disc_top - 30 * sc4))
    multiply_paste(img, gp, (cx10 - h10, disc_top - 30 * sc10))
    # dimension lines above the discs (exact disc widths)
    yl = disc_top - 70
    K.dim_line(img, cx4 - D4 / 2, cx4 + D4 / 2, yl, color=K.BLUE)
    K.dim_line(img, cx10 - D10 / 2, cx10 + D10 / 2, yl, color=K.BLUE)
    K.text_line(d, (cx4, yl - 44), '22 mm', 80, 'bold', K.NAVY_TEXT, anchor='md')
    K.text_line(d, (cx10, yl - 44), '34 mm', 80, 'bold', K.NAVY_TEXT, anchor='md')
    # labels
    yb = base_y - 10
    K.text_line(d, (cx4, yb), 'Size 4', 76, 'bold', K.NAVY_TEXT, anchor='ma')
    K.text_line(d, (cx10, yb), 'Grand Size 10', 76, 'bold', K.BLUE, anchor='ma')
    K.text_block(d, (120, yb + 130), 'Grand comes in 1X and 2X. 2X enlarges detail but shows a smaller '
                 'area, so work closer to the tooth.', 56, 'regular', K.NAVY_TEXT, max_w=W - 240, max_lines=2,
                 min_size=56, align='center')
    return img


def both_faces():
    img = white()
    top = header(img, 'MIRROR ON BOTH SIDES', '99% reflectance on each face')
    footer_band(img)
    d = ImageDraw.Draw(img)
    hd = A.double_head()
    ph = K.fit(hd, 1660, 560)
    px, py = 110, top + 330
    K.paste(img, ph, (px, py), shadow=(10, 18, 18, 0.16))
    # locate the disc (right part of the head): its upper and lower surfaces
    al = np.asarray(ph.getchannel('A')) > 128
    x_from = int(ph.width * 0.82)
    cols = np.nonzero(al[:, x_from:].any(axis=0))[0]
    mid = x_from + cols[int(len(cols) * 0.45)]
    colmask = np.nonzero(al[:, mid])[0]
    top_pt = (px + mid, py + colmask.min() + 3)
    bot_pt = (px + mid, py + colmask.max() - 3)
    rx = W - 100
    # Face 1 (above)
    y1 = top + 70
    K.text_line(d, (rx, y1), 'Face 1', 80, 'bold', K.NAVY_TEXT, anchor='ra', display=True)
    K.text_line(d, (rx, y1 + 100), '99% reflectance', 58, 'medium', K.BLUE, anchor='ra')
    K.leader(img, (top_pt[0], y1 + 190), top_pt, color=K.BLUE)
    # Face 2 (below)
    y2 = py + ph.height + 120
    K.leader(img, (bot_pt[0], y2 - 24), bot_pt, color=K.BLUE)
    K.text_line(d, (rx, y2), 'Face 2', 80, 'bold', K.NAVY_TEXT, anchor='ra', display=True)
    K.text_line(d, (rx, y2 + 100), '99% reflectance', 58, 'medium', K.BLUE, anchor='ra')
    # benefit list (centred block)
    items = ['Same front-surface dielectric coating on both faces',
             'No ghost image on either side',
             'Size 4 (22 mm) head, 1X magnification']
    f = K.font(58, 'medium')
    bw = max(K.text_w(t, f) for t in items) + 110
    bx = (W - bw) / 2
    y = y2 + 290
    K.aa_draw(img, lambda g, s: g.rounded_rectangle(((bx - 70) * s, (y - 60) * s, (bx + bw + 60) * s,
                                                      (y + 3 * 118 + 10) * s), radius=30 * s,
                                                     fill=K.PALE + (255,)))
    for it in items:
        K.check_icon(img, (bx + 36, y + 30), 70)
        K.text_block(d, (bx + 100, y), it, 58, 'medium', K.NAVY_TEXT, max_w=W - 300, max_lines=1, min_size=56)
        y += 118
    return img
