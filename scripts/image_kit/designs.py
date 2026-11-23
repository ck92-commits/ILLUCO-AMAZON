"""Layouts for every slot of the ILLUCO Amazon image kit (2000 x 2000 px).

Each function returns a PIL RGB image. Product imagery is always a real ILLUCO photo (cropped,
masked, rotated, scaled or composited); everything else is layout, vector shapes and text.
"""
from functools import lru_cache

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


def _border_connected(mask):
    """Pixels of a boolean mask that are connected to the image border (4-neighbour flood fill done
    with numpy dilations on a 1/4-scale copy, then refined at full size)."""
    def grow(m, seed):
        reach = seed & m
        while True:
            nxt = reach.copy()
            nxt[1:] |= reach[:-1]; nxt[:-1] |= reach[1:]; nxt[:, 1:] |= reach[:, :-1]; nxt[:, :-1] |= reach[:, 1:]
            nxt &= m
            if nxt.sum() == reach.sum():
                return reach
            reach = nxt
    h, w = mask.shape
    small = mask[::4, ::4]
    seed = np.zeros_like(small); seed[0, :] = seed[-1, :] = True; seed[:, 0] = seed[:, -1] = True
    rs = grow(small, seed)
    coarse = np.repeat(np.repeat(rs, 4, axis=0), 4, axis=1)[:h, :w]
    return grow(mask, coarse & mask)


@lru_cache(maxsize=None)
def single_mirror_vertical_solid(color):
    """Single Size 4 mirror cutout where only the white connected to the photo's edge is removed, so the
    mirror face (often bright white) stays solid; rotated so the head is on top and the blue handle below."""
    im = A.img('single_lb_main' if color == 'lb' else 'single_db_main').convert('RGB')
    arr = np.asarray(im).astype(np.int32)
    bg = _border_connected(arr.min(axis=2) >= 248)
    alpha = Image.fromarray(np.where(bg, 0, 255).astype(np.uint8), 'L').filter(ImageFilter.GaussianBlur(1.0))
    rgba = im.convert('RGBA')
    rgba.putalpha(alpha)
    rgba = K.trim(rgba)
    a = np.asarray(rgba.getchannel('A')) > 128
    ys, xs = np.nonzero(a)
    evals, evecs = np.linalg.eigh(np.cov(np.vstack([xs - xs.mean(), ys - ys.mean()])))
    vx, vy = evecs[:, np.argmax(evals)]
    out = K.trim(K.rotate_rgba(rgba, np.degrees(np.arctan2(vy, vx)) - 90))
    arr2 = np.asarray(out).astype(np.int32)
    blue = (arr2[..., 3] > 128) & (arr2[..., 2] - arr2[..., 0] > 40)
    q = arr2.shape[0] // 4
    if blue[:q].sum() > blue[-q:].sum():
        out = out.rotate(180, expand=True)
    return out


@lru_cache(maxsize=None)
def kit_db_mirror_from_pack():
    """One whole Dark Blue mirror (the right-hand one) lifted from ILLUCO's real Dark Blue 5-pack photo
    (71549oTdxFL). The five heads touch, so the head is taken as its fitted circle (its rim is unbroken where it
    meets the 4th head, i.e. it is the head in front) and joined to its own shank and handle. The Dark Blue
    single-mirror photo shows the face edge-on, so on white it reads as a hook."""
    im = A.img('kit_db_main').convert('RGB')
    arr = np.asarray(im).astype(np.int32)
    g = arr.min(axis=2)
    h, w = g.shape
    # head 5: least-squares circle through its rim pixels
    ys, xs = np.nonzero(g[110:365, 1590:1850] < 200)
    xs = xs + 1590; ys = ys + 110
    cx, cy, c = np.linalg.lstsq(np.c_[2 * xs, 2 * ys, np.ones(len(xs))], xs ** 2 + ys ** 2, rcond=None)[0]
    r = np.sqrt(c + cx ** 2 + cy ** 2)
    yy, xx = np.mgrid[0:h, 0:w]
    disc = (xx - cx) ** 2 + (yy - cy) ** 2 <= (r + 3) ** 2
    # shank + handle: non-white pixels connected to a seed in its handle, kept right of the 4th head
    region = (xx >= 1625) & (yy >= cy)
    m = (g < 235) & region
    reach = np.zeros_like(m); reach[1800, 1712] = True
    while True:
        nxt = reach.copy()
        nxt[1:] |= reach[:-1]; nxt[:-1] |= reach[1:]; nxt[:, 1:] |= reach[:, :-1]; nxt[:, :-1] |= reach[:, 1:]
        nxt &= m | disc
        if nxt.sum() == reach.sum():
            break
        reach = nxt
    solid = ~_border_connected(~(reach | disc))
    ys2, xs2 = np.nonzero(solid)
    assert xs2.max() - xs2.min() < 330, 'cutout spans more than one mirror'
    alpha = Image.fromarray((solid * 255).astype(np.uint8), 'L').filter(ImageFilter.GaussianBlur(1.0))
    rgba = im.convert('RGBA')
    rgba.putalpha(alpha)
    return K.trim(rgba)


def _grow(mask, seed):
    """4-connected part of `mask` reachable from `seed`."""
    reach = seed & mask
    while True:
        nxt = K._dilate(reach) & mask
        if nxt.sum() == reach.sum():
            return reach
        reach = nxt


def _morph(m, r, op):
    for _ in range(r):
        m = op(m)
    return m


def _box_mean(a, r):
    c = np.pad(a, ((r + 1, r), (r + 1, r)), mode='edge').cumsum(0).cumsum(1)
    k = 2 * r + 1
    return (c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]) / k ** 2


def _handle_start(rgba):
    """First row from the top where the blue handle makes up most of the object."""
    arr = np.asarray(rgba).astype(np.int32)
    obj = arr[..., 3] > 128
    blue = obj & (arr[..., 2] - arr[..., 0] > 40)
    n = obj.sum(axis=1)
    frac = blue.sum(axis=1) / np.maximum(n, 1)
    assert (frac > 0.5).any(), 'no handle found'
    return int(np.argmax(frac > 0.5))


def _span(rgba, y):
    xs = np.nonzero(np.asarray(rgba.getchannel('A'))[y] > 128)[0]
    return int(xs.min()), int(xs.max())


def _widest(rgba, rows):
    a = np.asarray(rgba.getchannel('A'))[:rows] > 128
    best = 0
    for row in a:
        xs = np.nonzero(row)[0]
        if len(xs):
            best = max(best, int(xs[-1] - xs[0]))
    return best


@lru_cache(maxsize=None)
def ds_head_on_shank(color):
    """The Double-Sided head and its shank, from ILLUCO's Double-Sided main photo (the left mirror; its handle runs
    off the frame), stood upright and cut where the shank enters the handle."""
    im = A.img('ds_main_lb' if color == 'lb' else 'ds_main_db').convert('RGB')
    arr = np.asarray(im).astype(np.int32)
    g = arr.min(axis=2)
    obj = (g < 228) | (arr[..., 2] - arr[..., 0] > 40)
    obj = _morph(_morph(obj, 3, K._dilate), 3, K._erode)
    seed = np.zeros_like(obj)
    seed[1900, 300] = True  # inside the left mirror's handle
    comp = _grow(~_border_connected(~obj), seed)
    # the photo has a soft drop shadow on the right: peel smooth, neutral, light-grey pixels off the outline
    gf = g.astype(np.float64)
    std = np.sqrt(np.maximum(_box_mean(gf * gf, 3) - _box_mean(gf, 3) ** 2, 0))
    shadowlike = (g >= 205) & (g <= 240) & (std < 3.0) & (arr.max(axis=2) - g < 12)
    for _ in range(80):
        peel = comp & ~K._erode(comp) & shadowlike
        if not peel.any():
            break
        comp &= ~peel
    comp = ~_border_connected(~comp)
    comp = _grow(_morph(_morph(comp, 3, K._erode), 3, K._dilate) & comp, seed)
    alpha = Image.fromarray((comp * 255).astype(np.uint8), 'L').filter(ImageFilter.GaussianBlur(1.0))
    rgba = im.convert('RGBA')
    rgba.putalpha(alpha)
    rgba = K.trim(rgba)
    a = np.asarray(rgba).astype(np.int32)
    by, bx = np.nonzero((a[..., 3] > 128) & (a[..., 2] - a[..., 0] > 40))
    evals, evecs = np.linalg.eigh(np.cov(np.vstack([bx - bx.mean(), by - by.mean()])))
    vx, vy = evecs[:, np.argmax(evals)]
    out = K.trim(K.rotate_rgba(rgba, np.degrees(np.arctan2(vy, vx)) - 90))
    a2 = np.asarray(out).astype(np.int32)
    b2 = (a2[..., 3] > 128) & (a2[..., 2] - a2[..., 0] > 40)
    q = a2.shape[0] // 3
    if b2[:q].sum() > b2[-q:].sum():
        out = out.rotate(180, expand=True)
    return out.crop((0, 0, out.width, _handle_start(out)))


@lru_cache(maxsize=None)
def ds_mirror_full(color):
    """One whole Double-Sided mirror: the real Double-Sided head and shank (ds_head_on_shank) seated on the real
    handle of the same colour, taken from the 5-pack mirror photos (the handle is the same cone-socket handle).
    Both heads are Size 4 (22 mm), so the head is scaled to the single-sided head's width; at that scale the
    shank matches the handle opening (checked below)."""
    top = ds_head_on_shank(color)
    kit = single_mirror_vertical_solid('lb') if color == 'lb' else kit_db_mirror_from_pack()
    yk = _handle_start(kit)
    s = _widest(kit, int(kit.height * 0.2)) / _widest(top, int(top.height * 0.5))
    lo, hi = _span(top, top.height - 12)
    klo, khi = _span(kit, yk - 12)
    assert abs((hi - lo) * s / (khi - klo) - 1) < 0.12, 'shank and handle opening do not match'
    top = K.scale(top, s)
    bot = kit.crop((0, yk, kit.width, kit.height))
    ct = sum(_span(top, top.height - 3)) / 2
    cb = sum(_span(bot, 3)) / 2
    w = 2 * max(top.width, bot.width)
    out = Image.new('RGBA', (w, top.height + bot.height), (255, 255, 255, 0))
    out.alpha_composite(bot, (int(round(w / 2 - cb)), top.height))
    out.alpha_composite(top, (int(round(w / 2 - ct)), 0))
    return K.trim(out)


def _row_of(m, n=5):
    """n copies of an upright mirror cutout in a row, heads on top, pure white, soft contact shadow."""
    a = K.scale(m, int(H * 0.86) / m.height)
    img = white()
    span = int(W * 0.86)
    step = (span - a.width) / (n - 1)
    x0 = (W - span) / 2
    y = (H - a.height) / 2
    for i in range(n):
        K.paste(img, a, (x0 + step * i, y), shadow=(10, 16, 18, 0.14))
    return img


def main_kit_composite(color, n=5):
    """5-pack with handles, product only (owner, 11/23: mains are the product on white, no box, no text):
    five cutouts of ILLUCO's real mirror photo of the same product, heads on top, in a row, pure white
    background with a soft contact shadow."""
    return _row_of(single_mirror_vertical_solid('lb') if color == 'lb' else kit_db_mirror_from_pack(), n)


def main_ds_composite(color, n=5):
    """Double-Sided 5-pack, product only: five whole Double-Sided mirrors (ds_mirror_full) in a row."""
    return _row_of(ds_mirror_full(color), n)


def main_heads_row(n=5):
    """Single-sided heads 5-pack, product only: five cutouts of the real single-head photo side by side,
    slightly overlapping, pure white background, no box."""
    hd = A.single_head()
    a = K.scale(hd, int(H * 0.74) / hd.height)
    img = white()
    span = int(W * 0.88)
    step = (span - a.width) / (n - 1)
    x0 = (W - span) / 2
    y = (H - a.height) / 2
    for i in range(n):
        K.paste(img, a, (x0 + step * i, y), shadow=(8, 12, 14, 0.12))
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
    elif layout == 'diag':
        tx0, tx1 = 1040, W - 100
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
    elif layout == 'diag':
        # large diagonal product from top-left to bottom-right; text sits in the free top-right corner
        px0, py0, px1, py1 = 40, top + 40, 1640, H - 70
        y = top + 110
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
                               max_lines=2, min_size=90, align='center' if layout == 'stack' else 'left')
        y += h + 26
    # accent rule
    if layout in ('side', 'diag'):
        d.rectangle((tx0, y + 14, tx0 + 150, y + 24), fill=K.BLUE)
    else:
        d.rectangle((W / 2 - 75, y + 14, W / 2 + 75, y + 24), fill=K.BLUE)
    y += 60
    if layout in ('side', 'diag'):
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
        bx = tx0 if layout in ('side', 'diag') else (W - bw) / 2
        if layout in ('side', 'diag'):
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


# Card copy (revised 2026-11-20 per ILLUCO's sales lead): lead with Ultra High Definition and add the
# 5-minute autoclave as a time saver. The "100+ autoclave cycles" line is NOT used until the owner
# confirms it directly (the original brief lists cycle-count claims as contradicted by reviews).
ITEM_UHD = ('Ultra High Definition', '99% reflectance, true color and no ghost image.')
ITEM_UHD_DS = ('Ultra High Definition', '99% reflectance on both faces, true color and no ghost image.')
ITEM_BRIGHT = ('Over 40% Brighter', 'Than standard dental mirrors, which reflect 60–70%.')
ITEM_FS = ('Front-Surface Dielectric Coating', 'Maximizes reflectivity while minimizing light loss.')
ITEM_FS_LONG = ('Front-Surface Dielectric Coating',
                'Maximizes reflectivity while minimizing light loss for a consistently sharp image.')
ITEM_AUTO = ('5-Minute Autoclave', '273°F (134°C) for just 5 minutes, faster than a standard 20-minute cycle.')
ITEM_ERGO = ('Ergonomic, Anti-Rotation Design', 'Comfortable grip with stable positioning during use.')
ITEM_CONE = ('Cone Socket Fit', 'Threads onto cone socket handles. Not for simple stem or European-thread handles.')


def key_benefit_size4(color):
    base = A.img('card_lb' if color == 'lb' else 'card_db')
    return card_redraw(base, (96, 96, 1107, 1903), [ITEM_UHD, ITEM_BRIGHT, ITEM_FS, ITEM_AUTO, ITEM_ERGO])


def key_benefit_heads():
    return card_redraw(A.img('card_heads'), (96, 96, 1107, 1903),
                       [ITEM_UHD, ITEM_BRIGHT, ITEM_FS, ITEM_AUTO, ITEM_CONE])


def key_benefit_grand(color):
    base = A.img('grand01_lb' if color == 'lb' else 'grand01_db')
    items = [ITEM_UHD,
             ('Expansive Field of View',
              'Instantly view an entire quadrant or multiple teeth, reducing the need to pan or tilt.'),
             ITEM_BRIGHT, ITEM_FS_LONG, ITEM_AUTO]
    return card_redraw(base, (96, 72, 1290, 1939), items)


def key_benefit_ds(color):
    base = A.img('dsdm01_lb' if color == 'lb' else 'dsdm01_db')
    items = [ITEM_UHD_DS,
             ('Dual-Sided Viewing', 'Two-sided reflection minimizes mirror changing during procedures.'),
             ITEM_FS_LONG, ITEM_AUTO]
    return card_redraw(base, (96, 72, 1068, 1939), items)


def key_benefit_ds_heads():
    """New: double-sided head on navy, led by Ultra High Definition, with four benefit cards."""
    img = Image.new('RGB', (W, H), K.NAVY)
    img.paste(K.gradient((W, H), (0, 40, 84), (0, 70, 140), 'd'), (0, 0))
    d = ImageDraw.Draw(img)
    K.text_block(d, (90, 110), 'ULTRA HIGH DEFINITION', 120, 'extrabold', K.WHITE, max_w=W - 180, display=True,
                 max_lines=1, min_size=90, align='center')
    K.text_block(d, (90, 268), '99% reflectance on both faces of every head', 64, 'medium', (190, 215, 245),
                 max_w=W - 180, max_lines=1, min_size=56, align='center')
    hd = A.double_head()
    ph = K.fit(hd, 1700, 520)
    K.paste(img, ph, ((W - ph.width) / 2, 410), shadow=(0, 24, 30, 0.35))
    items = [('Front-surface dielectric coating', 'on German optical glass'),
             ('No ghost image', 'one sharp, true-color reflection'),
             ('Over 40% brighter', 'than standard 60–70% dental mirrors'),
             ('5-minute autoclave', '273°F (134°C) for just 5 minutes')]
    cw, ch, gx, gy = 880, 400, 40, 36
    x0 = (W - (2 * cw + gx)) / 2
    y0 = 1010
    for i, (t, b) in enumerate(items):
        x = x0 + (i % 2) * (cw + gx)
        y = y0 + (i // 2) * (ch + gy)
        K.aa_draw(img, lambda g, s, x=x, y=y: g.rounded_rectangle((x * s, y * s, (x + cw) * s, (y + ch) * s),
                                                                  radius=26 * s, fill=(255, 255, 255, 255)))
        K.check_icon(img, (x + 90, y + ch / 2), 100)
        tw = cw - 200
        th, _, _ = K.text_block(d, (0, 0), t, 62, 'bold', max_w=tw, max_lines=2, min_size=56, dry=True)
        bh, _, _ = K.text_block(d, (0, 0), b, 56, 'regular', max_w=tw, max_lines=3, min_size=56, dry=True)
        ty = y + (ch - (th + 22 + bh)) / 2
        K.text_block(d, (x + 170, ty), t, 62, 'bold', K.CARD_TEXT, max_w=tw, max_lines=2, min_size=56)
        K.text_block(d, (x + 170, ty + th + 22), b, 56, 'regular', K.NAVY_TEXT, max_w=tw, max_lines=3,
                     min_size=56)
    return img


# ================================================================ 04 MAGNIFICATION / SIZE / BOTH FACES
def magnification_guide():
    img = white()
    top = header(img, '2X & 3X: SEE FINE DETAIL LARGER', 'Premium magnification · most mouth mirrors are 1X')
    footer_band(img)
    d = ImageDraw.Draw(img)
    art = A.img('mag_art')  # ILLUCO's 1x / 2x / 3x view circles
    centers = [(468, 1157), (1021, 1157), (1574, 1157)]
    r_src = 246
    cols = [(W / 6) * (1 + 2 * i) for i in range(3)]
    diam = 520
    labels = [('1X', 'STANDARD', 'True size', 'Widest area', 'General exams'),
              ('2X', 'PREMIUM', 'Detail 2× larger', 'Smaller area', 'Work closer'),
              ('3X', 'PREMIUM', 'Detail 3× larger', 'Smallest area', 'Work closest')]
    y_c = top + 95
    # premium panel behind the 2X and 3X columns
    pnl = (cols[1] - 310, top + 45, cols[2] + 300, y_c + diam + 605)
    K.aa_draw(img, lambda g, s: g.rounded_rectangle([v * s for v in pnl], radius=36 * s, fill=K.PALE + (255,),
                                                    outline=(170, 200, 240, 255), width=4 * s))
    f_tag = K.font(56, 'bold')
    for (cx_src, cy_src), cx, lab in zip(centers, cols, labels):
        premium = lab[1] == 'PREMIUM'
        c = K.circle_crop(art, (cx_src, cy_src), r_src, diam, ring=14,
                          ring_color=K.BLUE if premium else (200, 222, 248))
        K.paste(img, c, (cx - diam / 2, y_c), shadow=(0, 14, 20, 0.22))
        K.text_line(d, (cx, y_c + diam + 26), lab[0], 150, 'extrabold', K.BLUE if premium else K.NAVY_TEXT,
                    anchor='ma', display=True)
        tag_w = K.text_w(lab[1], f_tag) + 80
        ty = y_c + diam + 210
        tag = (cx - tag_w / 2, ty, cx + tag_w / 2, ty + 88)
        tag_fill = K.BLUE if premium else (226, 231, 238)
        K.aa_draw(img, lambda g, s, tag=tag, tag_fill=tag_fill: g.rounded_rectangle(
            [v * s for v in tag], radius=44 * s, fill=tag_fill + (255,)))
        d.text((cx, ty + 44), lab[1], font=f_tag, fill=K.WHITE if premium else K.GREY_TEXT, anchor='mm')
        yy = ty + 120
        K.text_line(d, (cx, yy), lab[2], 60, 'bold', K.BLUE if premium else K.NAVY_TEXT, anchor='ma')
        K.text_line(d, (cx, yy + 82), lab[3], 58, 'regular', K.NAVY_TEXT, anchor='ma')
        K.text_line(d, (cx, yy + 164), lab[4], 58, 'regular', K.NAVY_TEXT, anchor='ma')
    # honest trade-off note
    ya = y_c + diam + 665
    bar = K.gradient((1640, 22), (150, 190, 235), K.NAVY, 'h')
    img.paste(bar, (180, ya))
    K.aa_draw(img, lambda g, s: g.polygon([(1820 * s, (ya - 26) * s), (1880 * s, (ya + 11) * s),
                                           (1820 * s, (ya + 48) * s)], fill=K.NAVY + (255,)))
    K.text_line(d, (180, ya + 50), 'Wider view', 56, 'semibold', K.GREY_TEXT, anchor='la')
    K.text_line(d, (1880, ya + 50), 'More detail', 56, 'semibold', K.NAVY_TEXT, anchor='ra')
    K.text_block(d, (130, ya + 160), 'Magnified mirrors show a smaller area and work best held close to the '
                 'tooth. Choose 1X for wide views.', 56, 'regular', K.NAVY_TEXT, max_w=W - 260, max_lines=2,
                 min_size=56, align='center')
    return img


def _head_photo_with_fade(photo, crop_box, fade_px, fade_right=0):
    """Crop a white-background photo and fade its bottom (and optionally right) edge to white."""
    c = photo.crop(crop_box).convert('RGB')
    a = np.asarray(c, np.float32)
    h, w = a.shape[:2]
    t = np.ones((h, w), np.float32)
    t[h - fade_px:, :] *= np.linspace(1, 0, fade_px)[:, None]
    if fade_right:
        t[:, w - fade_right:] *= np.linspace(1, 0, fade_right)[None, :]
    a = a * t[..., None] + 255 * (1 - t[..., None])
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
    items = ['Ultra high definition on both faces',
             'Same front-surface dielectric coating on each side',
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


# ================================================================ 05 COMPARISON CHARTS
def _fit_in_box(img, item, box, rgba=False, shadow=None):
    x0, y0, x1, y1 = box
    if rgba:
        ph = K.fit(item, x1 - x0, y1 - y0)
        K.paste(img, ph, (x0 + (x1 - x0 - ph.width) / 2, y0 + (y1 - y0 - ph.height) / 2), shadow=shadow)
    else:
        ph = K.fit(tight(item, pad=6), x1 - x0, y1 - y0)
        multiply_paste(img, ph, (x0 + (x1 - x0 - ph.width) / 2, y0 + (y1 - y0 - ph.height) / 2))


def grand_diag_rgba(color='lb'):
    m = A.grand_full(color)
    return K.trim(K.rotate_rgba(m, 45))


def chart_family_a():
    img = white()
    top = header(img, 'ILLUCO ULTRA HIGH DEFINITION', 'Compare the line · every handle in Light Blue or Dark Blue',
                 band_h=290)
    footer_band(img)
    d = ImageDraw.Draw(img)
    cols = ['Single', '5-Pack Kit', 'Double-Sided', 'Grand']
    x0, x1 = 50, W - 50
    cw = (x1 - x0) / 4
    pb_top, pb_h = top + 22, 240
    photos = [(A.img('single_lb_main'), False), (A.img('kit_lb_box'), False),
              (A.ds_box_main('lb')[0], False), (K.trim(K.rotate_rgba(grand_pair_rgba('lb'), 45)), True)]
    for i, (ph, rgba) in enumerate(photos):
        cx0 = x0 + i * cw
        _fit_in_box(img, ph, (cx0 + 40, pb_top, cx0 + cw - 40, pb_top + pb_h), rgba=rgba)
        K.text_line(d, (cx0 + cw / 2, pb_top + pb_h + 20), cols[i], 66, 'bold', K.NAVY_TEXT, anchor='ma',
                    display=True)
    # a str value spans all four columns (same for every model)
    rows = [('HEAD SIZE', ['Size 4 · 22 mm', 'Size 4 · 22 mm', 'Size 4 · 22 mm', 'Size 10 · 34 mm']),
            ('MIRROR FACES', ['1', '1', '2', '1']),
            ('MAGNIFICATION', ['1X · 2X · 3X', '1X · 2X · 3X', '1X', '1X · 2X']),
            ('HANDLES INCLUDED', ['1', '5', '5', '2']),
            ('MIRRORS PER PACK', ['1', '5', '5', '2']),
            ('AUTOCLAVE', '5 min at 273°F (134°C) for every model'),
            ('BEST FOR', ['Trying ILLUCO\nor a spare', 'Stocking the\noperatory', 'Two mirror\nfaces in one',
                          'Whole-quadrant\nviews'])]
    y = pb_top + pb_h + 104
    band_h, lh, padv = 72, 64, 22
    f_val = K.font(56, 'medium')
    seps = []
    for label, vals in rows:
        K.aa_draw(img, lambda g, s, y=y: g.rounded_rectangle((x0 * s, y * s, x1 * s, (y + band_h) * s),
                                                             radius=16 * s, fill=K.PALE + (255,)))
        K.text_line(d, (x0 + 34, y + band_h / 2), label, 56, 'bold', K.BLUE, anchor='lm')
        y += band_h
        if isinstance(vals, str):
            K.check_copy(vals)
            d.text((W / 2, y + padv), vals, font=K.font(58, 'semibold'), fill=K.NAVY_TEXT, anchor='ma')
            y += padv * 2 + lh - 10
            continue
        nl = max(v.count('\n') + 1 for v in vals)
        for i, v in enumerate(vals):
            cxm = x0 + i * cw + cw / 2
            for j, ln in enumerate(v.split('\n')):
                K.check_copy(ln)
                if K.text_w(ln, f_val) > cw - 20:
                    raise K.Overflow(ln)
                d.text((cxm, y + padv + j * lh), ln, font=f_val, fill=K.NAVY_TEXT, anchor='ma')
        seps.append((y, y + padv * 2 + nl * lh - 10))
        y += padv * 2 + nl * lh - 10
    if y > H - 60:
        raise K.Overflow(f'chart A overflow {y}')
    # column separators through the per-model value rows
    for ya, yb in seps:
        for i in range(1, 4):
            xx = x0 + i * cw
            d.line((xx, ya, xx, yb), fill=K.DIVIDER, width=2)
    return img


def chart_family_b():
    img = white()
    top = header(img, 'ULTRA HIGH DEFINITION HEADS', 'Single- or double-sided · handles not included', band_h=290)
    footer_band(img)
    d = ImageDraw.Draw(img)
    lab_w = 560
    x0, x1 = 60, W - 60
    cw = (x1 - x0 - lab_w) / 2
    cols = ['Single-Sided', 'Double-Sided']
    pb_top, pb_h = top + 36, 290
    _fit_in_box(img, A.single_head(), (x0 + lab_w + 60, pb_top, x0 + lab_w + cw - 60, pb_top + pb_h), rgba=True,
                shadow=(6, 10, 10, 0.12))
    _fit_in_box(img, A.double_head(), (x0 + lab_w + cw + 30, pb_top + 40, x1 - 30, pb_top + pb_h - 30),
                rgba=True, shadow=(6, 10, 10, 0.12))
    for i, c in enumerate(cols):
        K.text_line(d, (x0 + lab_w + i * cw + cw / 2, pb_top + pb_h + 26), c, 70, 'bold', K.NAVY_TEXT,
                    anchor='ma', display=True)
    rows = [('Head size', ['Size 4 (22 mm)', 'Size 4 (22 mm)']),
            ('Mirror faces', ['1', '2']),
            ('Magnification', ['1X · 2X · 3X', '1X']),
            ('Thread', ['Cone socket', 'Cone socket']),
            ('Handles included', ['No', 'No']),
            ('Heads per pack', ['5', '5']),
            ('Autoclave', '5 min at 273°F (134°C) for both'),
            ('Best for', ['Replacing worn heads', 'Two faces per head'])]
    y = pb_top + pb_h + 130
    rh = 134
    f_val = K.font(58, 'medium')
    for k, (label, vals) in enumerate(rows):
        if k % 2 == 0:
            K.aa_draw(img, lambda g, s, y=y: g.rounded_rectangle((x0 * s, y * s, x1 * s, (y + rh) * s),
                                                                 radius=18 * s, fill=K.PALE + (255,)))
        K.text_line(d, (x0 + 40, y + rh / 2), label, 58, 'bold', K.BLUE, anchor='lm')
        if isinstance(vals, str):  # same for both heads: one value centred across both columns
            K.check_copy(vals)
            d.text((x0 + lab_w + cw, y + rh / 2), vals, font=K.font(58, 'semibold'), fill=K.NAVY_TEXT, anchor='mm')
            y += rh
            continue
        for i, v in enumerate(vals):
            K.check_copy(v)
            if K.text_w(v, f_val) > cw - 30:
                raise K.Overflow(v)
            col = K.RED if v == 'No' else K.NAVY_TEXT
            d.text((x0 + lab_w + i * cw + cw / 2, y + rh / 2), v, font=f_val, fill=col, anchor='mm')
        y += rh
    if y > H - 70:
        raise K.Overflow(f'chart B overflow {y}')
    return img


# ================================================================ 06 HANDLE / COMPATIBILITY
def _blue_top(photo_rgb, x_range=None):
    """Topmost row containing handle-blue pixels (the steel/handle junction). Handle blue is
    strongly blue with a low red channel; the pale blue tint of mirror faces is excluded."""
    a = np.asarray(photo_rgb.convert('RGB')).astype(np.int32)
    blue = (a[..., 2] - a[..., 0] > 45) & (a[..., 0] < 110)
    if x_range:
        blue[:, :x_range[0]] = False
        blue[:, x_range[1]:] = False
    rows = np.nonzero(blue.sum(axis=1) > 6)[0]
    y = rows.min()
    xs = np.nonzero(blue[y + 4])[0]
    return y, (xs.min() + xs.max()) / 2 if len(xs) else None


def _callouts(img, d, items, x_text, w_text):
    """items: [(title, body, target_xy, text_top_y)] -> text at x_text with leader to target."""
    for title, body, (tx, ty), y in items:
        th, _, _ = K.text_block(d, (x_text, y), title, 66, 'bold', K.NAVY_TEXT, max_w=w_text, max_lines=2,
                                min_size=58, display=True)
        bh, _, _ = K.text_block(d, (x_text, y + th + 18), body, 56, 'regular', K.GREY_TEXT, max_w=w_text,
                                max_lines=3, min_size=56)
        K.leader(img, (x_text - 30, y + th / 2 + 6), (tx, ty), color=K.BLUE)


def _fits_heads_note(img, d, text, x0=820):
    by = H - 46 - 230
    K.aa_draw(img, lambda g, s: g.rounded_rectangle((x0 * s, by * s, (W - 90) * s, (by + 170) * s),
                                                    radius=28 * s, fill=K.PALE + (255,)))
    K.text_block(d, (x0 + 50, by + 24), text, 56, 'medium', K.NAVY_TEXT, max_w=W - 90 - x0 - 100, max_lines=2,
                 min_size=56)


def handle_size4(color):
    img = white()
    cname = COLOR_NAME[color]
    top = header(img, 'ERGONOMIC ANTI-ROTATION HANDLE', f'{cname} handle with cone socket thread')
    footer_band(img)
    d = ImageDraw.Draw(img)
    photo = A.img('single_lb_main' if color == 'lb' else 'single_db_main')
    # rotate the diagonal photo so the mirror stands vertical (head on top)
    geo = A.single_mirror_vertical_angle(color)
    vert = tight(rotate_white(photo, geo), pad=4)
    ph = K.fit(vert, 520, H - top - 150)
    px, py = 300 - ph.width / 2 + 60, top + 70
    multiply_paste(img, ph, (px, py))
    # anchors
    jy, jx = _blue_top(ph)
    # the head is the widest part of the upright mirror: its centre sits ~half a width below the top
    head_c = (ph.width - 8, ph.width * 0.5)
    targets = [(px + head_c[0], py + head_c[1]), (px + jx + 18, py + jy + 4),
               (px + ph.width * 0.62, py + jy + (ph.height - jy) * 0.32)]
    x_text, w_text = 820, W - 820 - 90
    items = [('Size 4 (22 mm) UHD head', 'Ultra high definition, 99% reflectance', targets[0], targets[0][1] - 70),
             ('Cone socket thread', 'Replace the head, keep the handle', targets[1], py + jy - 60),
             ('Anti-rotation grip', f'Ergonomic shape, {cname}', targets[2], targets[2][1] - 60)]
    _callouts(img, d, items, x_text, w_text)
    _fits_heads_note(img, d, 'Takes ILLUCO UHD Size 4 replacement heads (cone socket)')
    return img


def handle_grand(color):
    img = white()
    cname = COLOR_NAME[color]
    top = header(img, 'ERGONOMIC ANTI-ROTATION HANDLE', f'{cname} handle with cone socket thread')
    footer_band(img)
    d = ImageDraw.Draw(img)
    m = A.grand_full(color)
    ph = K.fit(m, 560, H - top - 140)
    px, py = 330 - ph.width / 2 + 40, top + 60
    K.paste(img, ph, (px, py), shadow=(14, 18, 20, 0.15))
    # anchors measured on the Light Blue photo: the Dark Blue file is a pixel-aligned recolour, and
    # its dark handle / steel reflections are too close in colour to separate reliably
    ref = K.fit(A.grand_full('lb'), 560, H - top - 140)
    al = np.asarray(ref.getchannel('A')) > 128
    rgb = Image.new('RGB', ref.size, (255, 255, 255))
    rgb.paste(ref, (0, 0), ref)
    a = np.asarray(rgb).astype(np.int32)
    handle = (a[..., 2] > 150) & (a[..., 0] < 90) & (a[..., 1] > 60)
    rows = np.nonzero(handle.sum(axis=1) > 6)[0]
    jy = int(rows.min())
    xs = np.nonzero(handle[jy + 4])[0]
    jx = (xs.min() + xs.max()) / 2
    widths = al.sum(axis=1)
    hy = int(np.argmax(widths[: jy]))
    hx = np.nonzero(al[hy])[0].max()
    targets = [(px + hx - 4, py + hy), (px + jx + 22, py + jy + 4),
               (px + ph.width * 0.62, py + jy + (ph.height - jy) * 0.35)]
    x_text, w_text = 820, W - 820 - 90
    items = [('Grand Size 10 (34 mm) head', 'Ultra high definition, 99% reflectance', targets[0], py + hy - 70),
             ('Cone socket thread', 'The head threads into the handle', targets[1], py + jy - 60),
             ('Anti-rotation grip', f'Ergonomic shape, {cname}', targets[2], targets[2][1] - 60)]
    _callouts(img, d, items, x_text, w_text)
    return img


def handle_ds(color):
    img = white()
    cname = COLOR_NAME[color]
    top = header(img, 'ERGONOMIC ANTI-ROTATION HANDLE', f'{cname} handle with cone socket thread')
    d = ImageDraw.Draw(img)
    photo = A.img('ds_main_lb' if color == 'lb' else 'ds_main_db')
    s = (H - top) / photo.height
    ph = K.scale(photo, s)
    ox, oy = W - ph.width, top
    multiply_paste(img, ph, (ox, oy))
    footer_band(img)
    T = lambda x, y: (ox + x * s, oy + y * s)
    disc_left = T(705, 650)
    junction = T(598, 1372)
    grip = T(560, 1690)

    def callout(x, y, title, body, target, w, leader_from='right'):
        th, _, _ = K.text_block(d, (x, y), title, 66, 'bold', K.NAVY_TEXT, max_w=w, max_lines=1, min_size=58,
                                display=True)
        K.text_block(d, (x, y + th + 18), body, 56, 'regular', K.GREY_TEXT, max_w=w, max_lines=2, min_size=56)
        if leader_from == 'right':
            tw = K.text_w(title, K.font(66, 'bold', True))
            K.leader(img, (x + tw + 30, y + th / 2 + 6), target, color=K.BLUE)
        else:
            K.leader(img, (x - 30, y + th / 2 + 6), target, color=K.BLUE)

    callout(80, disc_left[1] - 120, 'Double-sided head', 'Ultra high definition on both faces', disc_left, 720)
    callout(80, junction[1] - 300, 'Cone socket thread', 'Replace the head, keep the handle', junction, 620)
    callout(1150, H - 330, 'Anti-rotation grip', f'Ergonomic shape, {cname}', (grip[0] + 70, grip[1]),
            W - 1150 - 80, leader_from='left')
    return img


def _thread_zoom(photo_rgb, center, radius, out_d):
    return K.circle_crop(photo_rgb, center, radius, out_d, ring=10, ring_color=K.BLUE)


def compatibility(head='single'):
    img = white()
    top = header(img, 'FITS CONE SOCKET HANDLES', 'Replacement heads only, handles not included')
    footer_band(img)
    d = ImageDraw.Draw(img)
    if head == 'single':
        photo = A.img('single_head')
        ph = K.fit(tight(photo, pad=6), 520, 1180)
        px, py = 150, top + 70
        multiply_paste(img, ph, (px, py))
        # thread = bottom 9% of the head
        bx = photo_bbox(photo, pad=6)
        thread_c = ((bx[0] + bx[2]) / 2 + 12, bx[3] - 70)
        zoom = _thread_zoom(photo, thread_c, 95, 360)
        zx, zy = 560, top + 900
        sc = ph.width / (bx[2] - bx[0])
        t_canvas = (px + (thread_c[0] - bx[0]) * sc, py + (thread_c[1] - bx[1]) * sc)
        K.leader(img, (zx + 60, zy + 120), t_canvas, color=K.BLUE, width=5, dot=14)
        K.paste(img, zoom, (zx, zy), shadow=(0, 10, 14, 0.2))
        K.text_line(d, (zx + 180, zy + 380), 'Cone socket thread', 56, 'bold', K.BLUE, anchor='ma')
        lx = 1020
        ly = top + 160
    else:
        photo = A.img('double_head')
        ph = K.fit(tight(photo, pad=6), 1500, 420)
        px, py = (W - ph.width) / 2, top + 70
        multiply_paste(img, ph, (px, py))
        bx = photo_bbox(photo, pad=6)
        # thread at the left end of the head
        thread_c = (bx[0] + 120, bx[3] - 70)
        zoom = _thread_zoom(photo, thread_c, 105, 330)
        sc = ph.width / (bx[2] - bx[0])
        t_canvas = (px + (thread_c[0] - bx[0]) * sc, py + (thread_c[1] - bx[1]) * sc)
        zx, zy = 110, py + ph.height + 40
        K.leader(img, (zx + 165, zy + 10), t_canvas, color=K.BLUE, width=5, dot=14)
        K.paste(img, zoom, (zx, zy), shadow=(0, 10, 14, 0.2))
        K.text_line(d, (zx + 165, zy + 350), 'Cone socket thread', 56, 'bold', K.BLUE, anchor='ma')
        lx = 600
        ly = py + ph.height + 90
    rows = [(True, 'Cone socket handles', 'including ILLUCO handles'),
            (False, 'Simple stem handles', None),
            (False, 'European-thread handles', None)]
    y = ly
    for ok, t, sub in rows:
        (K.check_icon if ok else K.cross_icon)(img, (lx + 50, y + 44), 100, bg=K.GREEN if ok else K.RED)
        K.text_line(d, (lx + 140, y + 4), t, 66, 'bold', K.NAVY_TEXT, display=True)
        if sub:
            K.text_line(d, (lx + 140, y + 92), sub, 56, 'regular', K.GREY_TEXT)
            y += 250
        else:
            y += 190
    # bottom note
    note = "Check your handle's thread before ordering."
    by = H - 46 - 250
    K.aa_draw(img, lambda g, s: g.rounded_rectangle((90 * s, by * s, (W - 90) * s, (by + 150) * s),
                                                    radius=28 * s, fill=K.PALE + (255,)))
    K.text_block(d, (150, by + 44), note, 60, 'semibold', K.NAVY_TEXT, max_w=W - 300, max_lines=1, min_size=56,
                 align='center')
    return img


# ================================================================ 07 CARE & STERILIZATION
def _thermo(img, cx, cy, h, color):
    def fn(g, s):
        w = h * 0.30
        g.rounded_rectangle(((cx - w / 2) * s, (cy - h / 2) * s, (cx + w / 2) * s, (cy + h * 0.25) * s),
                            radius=w / 2 * s, outline=color + (255,), width=int(h * 0.07 * s))
        r = h * 0.21
        g.ellipse(((cx - r) * s, (cy + h * 0.18) * s, (cx + r) * s, (cy + h * 0.18 + 2 * r) * s), fill=color + (255,))
        g.rectangle(((cx - w * 0.17) * s, (cy - h * 0.12) * s, (cx + w * 0.17) * s, (cy + h * 0.3) * s),
                    fill=color + (255,))
    K.aa_draw(img, fn)


def _clock(img, cx, cy, r, color):
    def fn(g, s):
        g.ellipse(((cx - r) * s, (cy - r) * s, (cx + r) * s, (cy + r) * s), outline=color + (255,),
                  width=int(r * 0.16 * s))
        g.line([(cx * s, cy * s), (cx * s, (cy - r * 0.6) * s)], fill=color + (255,), width=int(r * 0.14 * s))
        g.line([(cx * s, cy * s), ((cx + r * 0.45) * s, (cy + r * 0.2) * s)], fill=color + (255,),
               width=int(r * 0.14 * s))
    K.aa_draw(img, fn)


def _warn(img, cx, cy, size, color):
    def fn(g, s):
        h = size
        pts = [(cx * s, (cy - h / 2) * s), ((cx + h * 0.58) * s, (cy + h / 2) * s), ((cx - h * 0.58) * s, (cy + h / 2) * s)]
        g.polygon(pts, fill=color + (255,))
        g.rounded_rectangle(((cx - h * 0.06) * s, (cy - h * 0.18) * s, (cx + h * 0.06) * s, (cy + h * 0.2) * s),
                            radius=h * 0.05 * s, fill=(255, 255, 255, 255))
        g.ellipse(((cx - h * 0.065) * s, (cy + h * 0.27) * s, (cx + h * 0.065) * s, (cy + h * 0.4) * s),
                  fill=(255, 255, 255, 255))
    K.aa_draw(img, fn)


def _no_scrub(img, cx, cy, r, color):
    def fn(g, s):
        # sponge
        g.rounded_rectangle(((cx - r * 0.62) * s, (cy - r * 0.32) * s, (cx + r * 0.62) * s, (cy + r * 0.32) * s),
                            radius=r * 0.12 * s, fill=(150, 170, 200, 255))
        for i in range(-2, 3):
            for j in (-1, 1):
                rr = r * 0.06
                x, y = cx + i * r * 0.22, cy + j * r * 0.13
                g.ellipse(((x - rr) * s, (y - rr) * s, (x + rr) * s, (y + rr) * s), fill=(110, 130, 165, 255))
        g.ellipse(((cx - r) * s, (cy - r) * s, (cx + r) * s, (cy + r) * s), outline=color + (255,),
                  width=int(r * 0.15 * s))
        g.line([((cx - r * 0.7) * s, (cy + r * 0.7) * s), ((cx + r * 0.7) * s, (cy - r * 0.7) * s)],
               fill=color + (255,), width=int(r * 0.15 * s))
    K.aa_draw(img, fn)


def care_card():
    """Revised 2026-11-20 per ILLUCO's sales lead: the 5-minute cycle is the hero (time saver), and
    longer cycles / higher heat strip the coating (the cause of the bad reviews). "100+ autoclave cycles on the
    5-minute setting" confirmed by the owner on 2026-11-20."""
    img = white()
    top = header(img, 'CARE & STERILIZATION', 'Protect the high-definition coating')
    footer_band(img)
    d = ImageDraw.Draw(img)
    x0, x1 = 90, W - 90
    y = top + 50
    # hero: 5-minute autoclave
    hero_h = 560
    hero = K.round_corners(K.gradient((x1 - x0, hero_h), K.NAVY, K.BLUE_HEADER, 'h'), 34)
    img.paste(hero, (x0, y), hero)
    _clock(img, x0 + 175, y + hero_h / 2, 110, K.WHITE)
    tx = x0 + 340
    K.text_line(d, (tx, y + 62), '5-MINUTE AUTOCLAVE', 112, 'extrabold', K.WHITE, display=True)
    K.text_line(d, (tx, y + 215), '273°F (134°C) for just 5 minutes', 78, 'bold', K.WHITE, display=True)
    K.text_block(d, (tx, y + 330), 'Faster than a standard 20-minute instrument cycle', 58, 'medium',
                 (190, 215, 245), max_w=x1 - tx - 40, max_lines=1, min_size=50)
    cyc = K.check_copy('100+ autoclave cycles on the 5-minute setting')
    K.text_block(d, (tx, y + 430), cyc, 62, 'bold', K.WHITE, max_w=x1 - tx - 40, max_lines=1, min_size=50)
    y += hero_h + 50
    # secondary option
    sec_h = 190
    K.aa_draw(img, lambda g, s: g.rounded_rectangle((x0 * s, y * s, x1 * s, (y + sec_h) * s), radius=30 * s,
                                                    fill=K.PALE + (255,)))
    _thermo(img, x0 + 115, y + sec_h / 2 - 8, 130, K.NAVY_TEXT)
    K.text_line(d, (x0 + 230, y + sec_h / 2), 'or 20 minutes at 250°F (121°C)', 80, 'bold', K.NAVY_TEXT,
                anchor='lm', display=True)
    y += sec_h + 50
    # limit
    warn_h = 340
    K.aa_draw(img, lambda g, s: g.rounded_rectangle((x0 * s, y * s, x1 * s, (y + warn_h) * s), radius=30 * s,
                                                    fill=(253, 236, 236, 255)))
    _warn(img, x0 + 115, y + warn_h / 2, 130, K.RED)
    w_title, w_sub = 'No 20-minute cycle at 273°F\nNever above 277°F (136°C)', 'Extra heat strips the high-definition coating'
    th, _, _ = K.text_block(d, (0, 0), w_title, 72, 'bold', max_w=x1 - x0 - 280, max_lines=2, min_size=60,
                            display=True, dry=True)
    sh, _, _ = K.text_block(d, (0, 0), w_sub, 58, 'regular', max_w=x1 - x0 - 280, max_lines=1, min_size=56, dry=True)
    ty = y + (warn_h - (th + 30 + sh + 14)) / 2
    K.text_block(d, (x0 + 230, ty), w_title, 72, 'bold', K.RED, max_w=x1 - x0 - 280, max_lines=2, min_size=60,
                 display=True)
    K.text_block(d, (x0 + 230, ty + th + 30), w_sub, 58, 'regular', (150, 30, 30), max_w=x1 - x0 - 280,
                 max_lines=1, min_size=56)
    y += warn_h + 50
    # abrasive wiping
    _no_scrub(img, x0 + 115, y + 105, 88, K.RED)
    K.text_line(d, (x0 + 240, y + 25), 'Avoid abrasive wiping', 86, 'bold', K.NAVY_TEXT, display=True)
    K.text_line(d, (x0 + 240, y + 140), 'Protects the front-surface coating', 60, 'regular', K.GREY_TEXT)
    y += 250
    K.text_block(d, (x0, y), "Follow your autoclave manufacturer's instructions.", 58, 'medium',
                 K.GREY_TEXT, max_w=x1 - x0, max_lines=1, min_size=56, align='center')
    if y + 80 > H - 46:
        raise K.Overflow(f'care overflow {y}')
    return img


# ================================================================ 08 APPLICATIONS / SIZE SPEC
def applications_reuse(key):
    im = A.img(key)
    return im.resize((W, H), Image.LANCZOS) if im.size != (W, H) else im


def lifestyle_lb():
    """New lifestyle collage from ILLUCO's own light-blue product photos."""
    img = white()
    top = header(img, 'MADE FOR DAILY CLINICAL USE')
    footer_band(img)
    d = ImageDraw.Draw(img)
    gap = 40
    x0, y0 = 70, top + 50
    big_w, big_h = 1050, H - 46 - 60 - y0 - 150
    typ = A.img('life_typodont')
    big = K.rounded_photo(typ.crop((150, 0, 2048, 2048)), (big_w, big_h), 30)
    K.paste(img, big, (x0, y0))
    K.text_block(d, (x0, y0 + big_h + 40), 'Ultra high definition view', 62, 'bold', K.NAVY_TEXT, max_w=big_w,
                 max_lines=1, min_size=56, align='center')
    rx = x0 + big_w + gap
    rw = W - 70 - rx
    rh = (big_h + 150 - gap) // 2 - 150
    glove = A.img('life_glove')
    tray = A.img('life_tray')
    p1 = K.rounded_photo(glove.crop((100, 150, 1900, 1800)), (rw, rh), 30)
    p2 = K.rounded_photo(tray.crop((250, 250, 1950, 1700)), (rw, rh), 30)
    K.paste(img, p1, (rx, y0))
    K.text_block(d, (rx, y0 + rh + 22), 'Ergonomic anti-rotation grip', 58, 'bold', K.NAVY_TEXT, max_w=rw,
                 max_lines=2, min_size=56, align='center')
    y2 = y0 + rh + 150 + gap
    K.paste(img, p2, (rx, y2))
    K.text_block(d, (rx, y2 + rh + 22), '5-minute autoclave at 273°F (134°C)', 58, 'bold', K.NAVY_TEXT, max_w=rw,
                 max_lines=2, min_size=56, align='center')
    return img


def _chips(img, d, labels, cx, y, h=120, gap=30, size=64):
    f = K.font(size, 'bold', True)
    ws = [K.text_w(t, f) + 90 for t in labels]
    x = cx - (sum(ws) + gap * (len(ws) - 1)) / 2
    for t, w in zip(labels, ws):
        box = (x, y, x + w, y + h)
        K.aa_draw(img, lambda g, s, box=box: g.rounded_rectangle([v * s for v in box], radius=h / 2 * s,
                                                                 fill=K.PALE + (255,), outline=K.BLUE + (255,),
                                                                 width=4 * s))
        K.check_copy(t)
        d.text((x + w / 2, y + h / 2), t, font=f, fill=K.NAVY_TEXT, anchor='mm')
        x += w + gap


def size_spec_single_head():
    img = white()
    top = header(img, 'SIZE 4 · 22 mm HEAD', 'Single-sided · 1X, 2X or 3X magnification')
    footer_band(img)
    d = ImageDraw.Draw(img)
    photo = A.img('single_head')
    t = tight(photo, pad=6)
    ph = K.fit(t, 900, H - top - 330)
    px, py = 420 - ph.width / 2 + 120, top + 230
    multiply_paste(img, ph, (px, py))
    geo = A.disc_geometry_photo(ph)
    dl, dr = px + geo['left'], px + geo['right']
    K.dim_line(img, dl, dr, py - 50, color=K.BLUE)
    K.text_line(d, ((dl + dr) / 2, py - 96), '22 mm', 84, 'bold', K.NAVY_TEXT, anchor='md', display=True)
    x_text, w_text = 1080, W - 1080 - 90
    bb = photo_bbox(ph)
    items = [('Ultra high definition', 'Front-surface, 99% reflectance', (dr - 10, py + geo['cy']),
              py + geo['cy'] - 80),
             ('Cone socket thread', 'Fits cone socket handles', (px + (bb[0] + bb[2]) / 2 + 30, py + bb[3] - 60),
              py + bb[3] - 170)]
    _callouts(img, d, items, x_text, w_text)
    my = py + geo['cy'] + 330
    K.text_line(d, (x_text + w_text / 2, my), 'Magnification options', 60, 'bold', K.NAVY_TEXT, anchor='ma',
                display=True)
    _chips(img, d, ['1X', '2X', '3X'], x_text + w_text / 2, my + 110)
    return img


def size_spec_double_head():
    img = white()
    top = header(img, 'SIZE 4 · 22 mm HEAD', 'Double-sided · 1X magnification')
    footer_band(img)
    d = ImageDraw.Draw(img)
    # face view: head and neck of the double-sided mirror from the Double-Sided photo (handle excluded)
    photo = A.img('ds_main_lb')
    crop = (600, 395, 1160, 1085)  # stops above the second mirror in the photo
    face = _head_photo_with_fade(photo, crop, 170, fade_right=90)
    fp = K.fit(face, 860, 1180)
    fx, fy = 110, top + 250
    multiply_paste(img, fp, (fx, fy))
    sc = fp.width / (crop[2] - crop[0])
    dl, dr = fx + (694 - crop[0]) * sc, fx + (1096 - crop[0]) * sc
    K.dim_line(img, dl, dr, fy - 40, color=K.BLUE)
    K.text_line(d, ((dl + dr) / 2, fy - 86), '22 mm', 84, 'bold', K.NAVY_TEXT, anchor='md', display=True)
    K.text_line(d, (fx + fp.width / 2, fy + fp.height + 10), 'Face view', 58, 'semibold', K.GREY_TEXT,
                anchor='ma')
    # side view
    hd = A.double_head()
    ph = K.fit(hd, 960, 300)
    ex, ey = W - 80 - ph.width, top + 300
    K.paste(img, ph, (ex, ey), shadow=(8, 12, 14, 0.14))
    K.text_line(d, (ex + ph.width / 2, ey + ph.height + 30), 'Side view', 58, 'semibold', K.GREY_TEXT,
                anchor='ma')
    items = ['Mirror on both faces', 'Ultra high definition', 'No ghost image', 'Cone socket thread']
    y = ey + ph.height + 190
    for t in items:
        K.check_icon(img, (ex + 60, y + 32), 76)
        K.text_block(d, (ex + 130, y), t, 64, 'semibold', K.NAVY_TEXT, max_w=W - ex - 210, max_lines=1,
                     min_size=56)
        y += 150
    _chips(img, d, ['1X'], ex + ph.width / 2, y + 40)
    return img
