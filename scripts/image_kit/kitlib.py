"""Shared helpers for the ILLUCO Amazon image kit (fonts, colours, text, shapes, cutouts, saving).

Only real ILLUCO photos are used. Image operations here are limited to cropping, masking
(background removal), scaling, rotation, compositing, background clean-up, layout and text.
"""
import io
import os
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageCms, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'image_kit' / '_sources'
OUT = ROOT / 'image_kit'
W = H = 2000

# ---------------------------------------------------------------- colours (match ILLUCO infographics)
NAVY = (0, 48, 96)            # existing infographic background #003060
NAVY_TEXT = (11, 42, 91)      # #0B2A5B
BLUE = (21, 101, 192)         # ILLUCO blue #1565C0
BLUE_HEADER = (0, 91, 172)    # header gradient end used in dsdm-03 / grand-03 (#005BAC)
CARD_TEXT = (2, 75, 147)      # card copy colour in grand-01 / dsdm-01 (#024B93)
SKY = (120, 180, 245)         # light accent on navy
PALE = (235, 242, 251)        # pale blue panel
LIGHT_BG = (246, 248, 252)
DIVIDER = (214, 224, 237)
GREY_TEXT = (84, 98, 120)
WHITE = (255, 255, 255)
RED = (198, 40, 40)
GREEN = (27, 128, 72)

# ---------------------------------------------------------------- copy guard
# Claims customer reviews / returns contradict, typos, and unsupported specs. A revision request relayed on
# 2026-11-20 reports that ILLUCO's sales lead approved "100+ autoclave cycles" WITH the plus and the 5-minute
# qualifier, so the guard lets that exact form through ("100 autoclave cycles" without the plus and "100X"
# stay rejected). No image uses it yet: it waits for the owner's direct confirmation (see README).
FORBIDDEN = [
    r'\bfog', r'anti-?fog', r'stays? dry', r'40%\s*clearer', r'rhodium', r'quandrant',
    r'minimi[sz]ing light(?!\s+loss)', r'moisture', r'spot-free',
    r'\b100(?!\+)\s*(?:autoclave|cycles)',      # "100 autoclave cycles" / "100 cycles" without the plus
    r'\b100\s*x\b',                             # "100X" (reads as magnification)
]
# "100+ ... cycles" must say which setting it applies to
REQUIRE_WITH = [(r'100\+', r'5-minute|5 min|on this setting')]


def check_copy(text, context=None):
    """Reject forbidden claims. `context` (e.g. the whole card or image copy) is used for the
    "100+ cycles needs the 5-minute qualifier" rule; defaults to the text itself."""
    t = text.lower()
    for pat in FORBIDDEN:
        if re.search(pat, t):
            raise ValueError(f'forbidden/unsupported claim in copy: {pat!r} in {text!r}')
    ctx = (context or text).lower()
    for pat, need in REQUIRE_WITH:
        if re.search(pat, t) and not re.search(need, ctx):
            raise ValueError(f'claim {pat!r} needs a qualifier ({need!r}) in {text!r}')
    return text


# ---------------------------------------------------------------- fonts
WEIGHTS = {'regular': 400, 'medium': 500, 'semibold': 600, 'bold': 700, 'extrabold': 800, 'black': 900}
OUTFIT = SRC / 'fonts' / 'Outfit-Variable.ttf'
INTER_DIR = Path('/usr/share/fonts/opentype/inter')
INTER = {'regular': 'Inter-Regular.otf', 'medium': 'Inter-Medium.otf', 'semibold': 'Inter-SemiBold.otf',
         'bold': 'Inter-Bold.otf', 'extrabold': 'Inter-ExtraBold.otf', 'black': 'Inter-Black.otf'}
INTER_DISPLAY = {'regular': 'InterDisplay-Regular.otf', 'medium': 'InterDisplay-Medium.otf',
                 'semibold': 'InterDisplay-SemiBold.otf', 'bold': 'InterDisplay-Bold.otf',
                 'extrabold': 'InterDisplay-ExtraBold.otf', 'black': 'InterDisplay-Black.otf'}
DEJAVU = {'regular': '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
          'bold': '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'}
_font_cache = {}


def font_family():
    if OUTFIT.exists() and OUTFIT.stat().st_size > 10000:
        return 'Outfit'
    if (INTER_DIR / INTER['regular']).exists():
        return 'Inter'
    return 'DejaVu Sans'


def font(size, weight='regular', display=False):
    """Outfit (if downloaded) -> Inter / Inter Display (installed) -> DejaVu Sans."""
    key = (int(size), weight, display)
    if key in _font_cache:
        return _font_cache[key]
    fam = font_family()
    if fam == 'Outfit':
        f = ImageFont.truetype(str(OUTFIT), int(size))
        try:
            f.set_variation_by_axes([WEIGHTS[weight]])
        except Exception:
            pass
    elif fam == 'Inter':
        table = INTER_DISPLAY if display else INTER
        f = ImageFont.truetype(str(INTER_DIR / table[weight]), int(size))
    else:
        f = ImageFont.truetype(DEJAVU['bold' if WEIGHTS[weight] >= 600 else 'regular'], int(size))
    _font_cache[key] = f
    return f


# ---------------------------------------------------------------- text layout
def text_w(s, f):
    return f.getlength(s)


def wrap(text, f, max_w):
    lines = []
    for para in text.split('\n'):
        words = para.split(' ')
        cur = ''
        for wd in words:
            trial = (cur + ' ' + wd).strip()
            if not cur or text_w(trial, f) <= max_w:
                cur = trial
            else:
                lines.append(cur)
                cur = wd
        lines.append(cur)
    return lines


class Overflow(Exception):
    pass


def text_block(draw, xy, text, size, weight='regular', fill=NAVY_TEXT, max_w=1800, line_h=1.22,
               align='left', display=False, max_lines=None, min_size=None, dry=False, tracking=0, context=None):
    """Draw wrapped text with its top at xy. Shrinks (not below min_size) to respect max_lines.
    Returns (height, size_used, n_lines)."""
    check_copy(text, context)
    size_used = size
    while True:
        f = font(size_used, weight, display)
        lines = wrap(text, f, max_w)
        too_wide = any(text_w(ln, f) > max_w + 1 for ln in lines)
        if (max_lines is None or len(lines) <= max_lines) and not too_wide:
            break
        if min_size is None or size_used - 2 < min_size:
            raise Overflow(f'text does not fit: {text!r} size={size_used} lines={len(lines)} max={max_lines}')
        size_used -= 2
    x, y = xy
    lh = round(size_used * line_h)
    if not dry:
        for i, ln in enumerate(lines):
            lw = text_w(ln, f)
            if align == 'center':
                lx = x + (max_w - lw) / 2
            elif align == 'right':
                lx = x + max_w - lw
            else:
                lx = x
            draw.text((lx, y + i * lh), ln, font=f, fill=fill, anchor='la')
    # visual height: (n-1) line steps + cap/ascender height of one line
    asc, desc = f.getmetrics()
    height = (len(lines) - 1) * lh + asc
    return height, size_used, len(lines)


def text_line(draw, xy, text, size, weight='regular', fill=NAVY_TEXT, anchor='la', display=False, context=None):
    check_copy(text, context)
    f = font(size, weight, display)
    draw.text(xy, text, font=f, fill=fill, anchor=anchor)
    return text_w(text, f)


def rich_line(draw, xy, parts, size, fill=WHITE, anchor_center_w=None, display=True):
    """parts: [(text, weight)] drawn on one line; if anchor_center_w given, centre within that width."""
    for t, _ in parts:
        check_copy(t)
    fonts = [font(size, wgt, display) for _, wgt in parts]
    total = sum(text_w(t, f) for (t, _), f in zip(parts, fonts))
    x, y = xy
    if anchor_center_w is not None:
        x = x + (anchor_center_w - total) / 2
    for (t, _), f in zip(parts, fonts):
        draw.text((x, y), t, font=f, fill=fill, anchor='la')
        x += text_w(t, f)
    return total


# ---------------------------------------------------------------- shapes
def gradient(size, c1, c2, direction='h'):
    w, h = size
    if direction == 'h':
        t = np.linspace(0, 1, w)[None, :, None]
        t = np.repeat(t, h, axis=0)
    elif direction == 'v':
        t = np.linspace(0, 1, h)[:, None, None]
        t = np.repeat(t, w, axis=1)
    else:  # diagonal
        tx = np.linspace(0, 1, w)[None, :]
        ty = np.linspace(0, 1, h)[:, None]
        t = ((tx + ty) / 2)[..., None]
    a = np.array(c1, float)[None, None, :] * (1 - t) + np.array(c2, float)[None, None, :] * t
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGB')


def rrect(draw, box, r, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def check_icon(img, center, d, bg=BLUE, fg=WHITE, ss=4):
    """Filled circle with a check mark (vector, supersampled)."""
    cx, cy = center
    big = Image.new('RGBA', (d * ss, d * ss), (0, 0, 0, 0))
    g = ImageDraw.Draw(big)
    g.ellipse((0, 0, d * ss - 1, d * ss - 1), fill=bg)
    s = d * ss
    pts = [(0.27 * s, 0.53 * s), (0.44 * s, 0.69 * s), (0.75 * s, 0.35 * s)]
    g.line(pts, fill=fg, width=int(0.11 * s), joint='curve')
    for p in (pts[0], pts[2]):
        r = 0.055 * s
        g.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=fg)
    small = big.resize((d, d), Image.LANCZOS)
    img.paste(small, (int(cx - d / 2), int(cy - d / 2)), small)


def cross_icon(img, center, d, bg=RED, fg=WHITE, ss=4):
    cx, cy = center
    big = Image.new('RGBA', (d * ss, d * ss), (0, 0, 0, 0))
    g = ImageDraw.Draw(big)
    g.ellipse((0, 0, d * ss - 1, d * ss - 1), fill=bg)
    s = d * ss
    w = int(0.11 * s)
    g.line([(0.32 * s, 0.32 * s), (0.68 * s, 0.68 * s)], fill=fg, width=w)
    g.line([(0.68 * s, 0.32 * s), (0.32 * s, 0.68 * s)], fill=fg, width=w)
    for p in [(0.32, 0.32), (0.68, 0.68), (0.68, 0.32), (0.32, 0.68)]:
        r = w / 2
        g.ellipse((p[0] * s - r, p[1] * s - r, p[0] * s + r, p[1] * s + r), fill=fg)
    small = big.resize((d, d), Image.LANCZOS)
    img.paste(small, (int(cx - d / 2), int(cy - d / 2)), small)


def aa_draw(img, fn, ss=3):
    """Run fn(draw, scale) on a supersampled RGBA layer and composite it onto img (anti-aliased shapes)."""
    layer = Image.new('RGBA', (img.width * ss, img.height * ss), (0, 0, 0, 0))
    fn(ImageDraw.Draw(layer), ss)
    layer = layer.resize(img.size, Image.LANCZOS)
    img.paste(layer, (0, 0), layer)


def leader(img, p0, p1, color=BLUE, width=6, dot=16):
    """Callout leader line from p0 (text side) to p1 (product point) with a dot at p1."""
    def fn(g, s):
        g.line([(p0[0] * s, p0[1] * s), (p1[0] * s, p1[1] * s)], fill=color + (255,), width=width * s)
        r = dot * s / 2
        g.ellipse((p1[0] * s - r, p1[1] * s - r, p1[0] * s + r, p1[1] * s + r), fill=color + (255,))
        r2 = r * 0.45
        g.ellipse((p1[0] * s - r2, p1[1] * s - r2, p1[0] * s + r2, p1[1] * s + r2), fill=(255, 255, 255, 255))
    aa_draw(img, fn)


def dim_line(img, x0, x1, y, color=NAVY_TEXT, width=5, tick=36):
    """Horizontal dimension line with end ticks and arrow heads."""
    def fn(g, s):
        c = color + (255,)
        g.line([(x0 * s, y * s), (x1 * s, y * s)], fill=c, width=width * s)
        for x in (x0, x1):
            g.line([(x * s, (y - tick / 2) * s), (x * s, (y + tick / 2) * s)], fill=c, width=width * s)
        a = 22
        g.polygon([(x0 * s, y * s), ((x0 + a) * s, (y - a * 0.55) * s), ((x0 + a) * s, (y + a * 0.55) * s)], fill=c)
        g.polygon([(x1 * s, y * s), ((x1 - a) * s, (y - a * 0.55) * s), ((x1 - a) * s, (y + a * 0.55) * s)], fill=c)
    aa_draw(img, fn)


# ---------------------------------------------------------------- image loading
_SRGB = ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB'))
SRGB_BYTES = _SRGB.tobytes()


def load(rel):
    """Load a source image (path relative to image_kit/_sources) as sRGB RGB."""
    p = SRC / rel
    im = Image.open(p)
    icc = im.info.get('icc_profile')
    im = im.convert('RGB')
    if icc:
        try:
            src = ImageCms.ImageCmsProfile(io.BytesIO(icc))
            im = ImageCms.profileToProfile(im, src, _SRGB, outputMode='RGB')
        except Exception:
            pass
    return im


# ---------------------------------------------------------------- masks / cutouts
def _dilate(m):
    o = m.copy()
    o[1:, :] |= m[:-1, :]
    o[:-1, :] |= m[1:, :]
    o[:, 1:] |= m[:, :-1]
    o[:, :-1] |= m[:, 1:]
    return o


def _erode(m):
    return ~_dilate(~m)


def border_connected(cand, scale=4, close=0):
    """True where `cand` pixels connect to the image border (4-connectivity).
    Flood runs on a block-reduced grid (a block is passable only if all its pixels are) and is
    refined at full resolution. `close` (in reduced pixels) closes small gaps in the blocking set."""
    Hh, Ww = cand.shape
    h, w = Hh // scale, Ww // scale
    c = cand[:h * scale, :w * scale].reshape(h, scale, w, scale).all(axis=(1, 3))
    if close:
        blk = ~c
        for _ in range(close):
            blk = _dilate(blk)
        for _ in range(close):
            blk = _erode(blk)
        c = ~blk
    cur = np.zeros_like(c)
    cur[0, :] = c[0, :]
    cur[-1, :] = c[-1, :]
    cur[:, 0] = c[:, 0]
    cur[:, -1] = c[:, -1]
    n = cur.sum()
    while True:
        for _ in range(8):
            cur = _dilate(cur) & c
        m = cur.sum()
        if m == n:
            break
        n = m
    up = np.zeros((Hh, Ww), bool)
    up[:h * scale, :w * scale] = np.repeat(np.repeat(cur, scale, 0), scale, 1)
    up[h * scale:, :] = cand[h * scale:, :]
    up[:, w * scale:] = cand[:, w * scale:]
    up &= cand
    for _ in range(scale * 3):
        up = _dilate(up) & cand
    return up


def alpha_white_bg(img, lo=6, hi=34, scale=4, close=0):
    """Alpha for a product shot on a white background. Background = near-white pixels connected
    to the border; enclosed near-white areas (mirror faces) stay opaque. Soft edge between lo..hi."""
    a = np.asarray(img, dtype=np.float32)
    d = 255.0 - a.min(axis=2)
    bg = border_connected(d <= hi, scale=scale, close=close)
    soft = np.clip((d - lo) / float(hi - lo), 0, 1)
    return np.where(bg, soft, 1.0).astype(np.float32)


def alpha_dark_bg(img, bg_rgb, lo=10, hi=40, scale=4):
    """Alpha for a bright product on a dark (navy) background; foreground-ness = how much brighter /
    bluer the pixel is than the background."""
    a = np.asarray(img, dtype=np.float32)
    bgc = np.array(bg_rgb, np.float32)
    lum = a @ np.array([0.299, 0.587, 0.114], np.float32)
    lum_bg = float(bgc @ np.array([0.299, 0.587, 0.114], np.float32))
    d = np.maximum(lum - lum_bg, (a[..., 2] - bgc[2]) * 0.8)
    bg = border_connected(d <= hi, scale=scale)
    soft = np.clip((d - lo) / float(hi - lo), 0, 1)
    return np.where(bg, soft, 1.0).astype(np.float32)


def cutout(img, alpha, bg_rgb=(255, 255, 255), erode_px=0):
    """RGBA cutout; edge colours are un-mixed from the original background colour."""
    a = np.asarray(img, dtype=np.float32)
    al = alpha.copy()
    if erode_px:
        m = Image.fromarray((al * 255).astype(np.uint8), 'L').filter(ImageFilter.MinFilter(erode_px * 2 + 1))
        al = np.minimum(al, np.asarray(m, np.float32) / 255.0)
    bgc = np.array(bg_rgb, np.float32)
    safe = np.maximum(al, 0.05)[..., None]
    f = (a - (1 - al[..., None]) * bgc) / safe
    f = np.where(al[..., None] > 0.02, f, a)
    f = np.clip(f, 0, 255)
    rgba = np.dstack([f, al * 255]).astype(np.uint8)
    return Image.fromarray(rgba, 'RGBA')


def trim(rgba, pad=0, thresh=8):
    al = np.asarray(rgba.getchannel('A'))
    ys, xs = np.where(al > thresh)
    box = (max(xs.min() - pad, 0), max(ys.min() - pad, 0), min(xs.max() + 1 + pad, rgba.width),
           min(ys.max() + 1 + pad, rgba.height))
    return rgba.crop(box)


def fit(im, max_w, max_h, upscale=True):
    s = min(max_w / im.width, max_h / im.height)
    if not upscale:
        s = min(s, 1.0)
    return im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)


def scale(im, s):
    return im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)


def rotate_rgba(rgba, deg):
    """Rotate an RGBA cutout without dark fringes (premultiplied rotation)."""
    a = np.asarray(rgba, np.float32) / 255.0
    pm = a[..., :3] * a[..., 3:4]
    big = np.dstack([pm, a[..., 3:4]])
    chans = [Image.fromarray((big[..., i] * 255).astype(np.uint8), 'L').rotate(
        deg, resample=Image.BICUBIC, expand=True) for i in range(4)]
    arr = np.dstack([np.asarray(c, np.float32) / 255.0 for c in chans])
    al = arr[..., 3:4]
    rgb = np.where(al > 0.004, arr[..., :3] / np.maximum(al, 1e-4), 0)
    out = np.dstack([np.clip(rgb, 0, 1), al]) * 255
    return Image.fromarray(out.astype(np.uint8), 'RGBA')


def shadow_of(rgba, blur=18, opacity=0.18, color=(20, 30, 50)):
    al = rgba.getchannel('A').filter(ImageFilter.GaussianBlur(blur))
    al = al.point(lambda v: int(v * opacity))
    sh = Image.new('RGBA', rgba.size, color + (0,))
    sh.putalpha(al)
    return sh


def paste(canvas, rgba, xy, shadow=None):
    """Paste RGBA onto canvas at xy (top-left). shadow=(dx, dy, blur, opacity)."""
    x, y = int(round(xy[0])), int(round(xy[1]))
    if shadow:
        dx, dy, blur, op = shadow
        pad = blur * 3
        padded = Image.new('RGBA', (rgba.width + 2 * pad, rgba.height + 2 * pad), (0, 0, 0, 0))
        padded.paste(rgba, (pad, pad))
        sh = shadow_of(padded, blur, op)
        canvas.paste(sh, (x - pad + dx, y - pad + dy), sh)
    canvas.paste(rgba, (x, y), rgba)


def circle_crop(img, center, radius, out_d, ring=0, ring_color=WHITE, ss=3):
    """Circular crop (radius in source px) resized to out_d, optional ring; returns RGBA."""
    cx, cy = center
    box = (int(cx - radius), int(cy - radius), int(cx + radius), int(cy + radius))
    sq = img.crop(box).resize((out_d, out_d), Image.LANCZOS).convert('RGBA')
    m = Image.new('L', (out_d * ss, out_d * ss), 0)
    ImageDraw.Draw(m).ellipse((0, 0, out_d * ss - 1, out_d * ss - 1), fill=255)
    m = m.resize((out_d, out_d), Image.LANCZOS)
    sq.putalpha(m)
    if ring:
        r = Image.new('RGBA', (out_d * ss, out_d * ss), (0, 0, 0, 0))
        g = ImageDraw.Draw(r)
        g.ellipse((ring * ss / 2, ring * ss / 2, out_d * ss - ring * ss / 2, out_d * ss - ring * ss / 2),
                  outline=ring_color + (255,), width=ring * ss)
        r = r.resize((out_d, out_d), Image.LANCZOS)
        sq.alpha_composite(r)
    return sq


def rounded_photo(img, size, radius, ss=3):
    """Cover-crop img to size and round the corners; returns RGBA."""
    tw, th = size
    s = max(tw / img.width, th / img.height)
    im = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x0 = (im.width - tw) // 2
    y0 = (im.height - th) // 2
    im = im.crop((x0, y0, x0 + tw, y0 + th)).convert('RGBA')
    m = Image.new('L', (tw * ss, th * ss), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, tw * ss - 1, th * ss - 1), radius=radius * ss, fill=255)
    im.putalpha(m.resize((tw, th), Image.LANCZOS))
    return im


def round_corners(im, radius, ss=3):
    im = im.convert('RGBA')
    m = Image.new('L', (im.width * ss, im.height * ss), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width * ss - 1, im.height * ss - 1), radius=radius * ss, fill=255)
    im.putalpha(m.resize(im.size, Image.LANCZOS))
    return im


# ---------------------------------------------------------------- saving / checks
def save_jpg(img, path, quality=90):
    img = img.convert('RGB')
    if img.size != (W, H):
        img = img.resize((W, H), Image.LANCZOS)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, 'JPEG', quality=quality, optimize=True, icc_profile=SRGB_BYTES, subsampling=0)
    size = path.stat().st_size
    if size >= 5 * 1024 * 1024:
        img.save(path, 'JPEG', quality=quality, optimize=True, icc_profile=SRGB_BYTES, subsampling=2)
        size = path.stat().st_size
    assert size < 5 * 1024 * 1024, f'{path} is {size} bytes'
    return size


def white_border_ok(img, band=6):
    a = np.asarray(img.convert('RGB'))
    b = np.concatenate([a[:band].reshape(-1, 3), a[-band:].reshape(-1, 3),
                        a[:, :band].reshape(-1, 3), a[:, -band:].reshape(-1, 3)])
    return int(b.min()) >= 254


def product_fill(img, thresh=245):
    a = np.asarray(img.convert('RGB'))
    ys, xs = np.where(a.min(axis=2) < thresh)
    if len(xs) == 0:
        return 0, 0
    return (xs.max() - xs.min() + 1) / a.shape[1], (ys.max() - ys.min() + 1) / a.shape[0]
