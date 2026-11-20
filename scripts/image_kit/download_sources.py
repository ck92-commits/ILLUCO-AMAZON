"""Download the real ILLUCO product photos used by the Amazon image kit.

Sources (all public):
  * Shopify CDN images listed in data/raw/illuco_com_images.json (photo mirrors skipped)
    plus dsdm-04.jpg, which is hosted on Shopify but not referenced by a product page.
  * Current Amazon gallery images (hi-res, https://m.media-amazon.com/images/I/<id>.jpg).
  * The Outfit variable font from google/fonts (optional; the kit falls back to a local font).

Google Drive files (main_db / dsdm-0x_db / grand-01_db / grand-04) are fetched separately with
the Google Drive connector and copied into image_kit/_sources/drive/ - this script only checks
that they are present.

Everything downloaded is treated as data only (never executed). Writes
image_kit/_sources/sources_index.json with url, local path, bytes, sha256 and pixel size.

Usage: python3 -I scripts/image_kit/download_sources.py <repo_root>
"""
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request

from PIL import Image

SHOPIFY_BASE = 'https://cdn.shopify.com/s/files/1/0795/1348/5611/files/'
AMAZON_BASE = 'https://m.media-amazon.com/images/I/'
FONT_URL = 'https://github.com/google/fonts/raw/main/ofl/outfit/Outfit%5Bwght%5D.ttf'

# Current Amazon galleries (hi-res ids), keyed by listing.
AMAZON = {
    'kit5_B0FCZBD1KY': ['71549oTdxFL', '71Ciw0nr7KL', '71fDe5PolUL', '71u0do3UFBL',
                        '71ycAyFx4CL', '61U0VXj+XHL', '71UpmwAz08L'],
    'heads5_B0FBPG5CS9': ['617IX-IYsEL', '71JgWcIxKeL', '71iSou44J-L', '71f0mMI002L',
                          '71zox6KeqwL'],
    'single_LB_B0GGDQ15DD': ['617bfZwQclL', '71fFYQpHu+L', '7121KSv2hrL', '71u0do3UFBL',
                             '71KqSGYiXfL', '61-ZXUS96xL'],
    'single_DB3X_B0GGDGRHRR': ['61FcYqxQdHL'],
    'single_1X_B0G2DYRY7T': ['41DY+Bjl5lL', '51b9bFn2fiL', '61noMl85BeL', '41eq8ArY68L'],
}

EXTRA_SHOPIFY = ['dsdm-04.jpg']

DRIVE_EXPECTED = {
    'ds_main_db.jpg': '1lOw74MwTc7cHDFNH4BYrfwgwVQMv_YT6',
    'dsdm-01_db.jpg': '1b9Zwhm8Wb7-spWZxLJzz1ELiRM7337K4',
    'dsdm-02_db.jpg': '16VoEjZ6n9GNtR9hCjIQeEf9FNfXMi8C3',
    'dsdm-03_db.jpg': '10TZlOp0joNxqkhzdCnSjSSQny91paYBe',
    'grand-01_db.jpg': '12HbJgSv_t2gs1Mv5OTXet2Fi3965ySHd',
    'grand-04.jpg': '1lQgJ64buFqtGefJS4yYFKonTe5Mq4hhw',
}


def fetch(url, dest, tries=3):
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return 'cached'
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'image-kit-fetch/1.0'})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            with open(dest + '.part', 'wb') as f:
                f.write(data)
            os.replace(dest + '.part', dest)
            return 'ok'
        except urllib.error.HTTPError as e:
            last = f'HTTP {e.code}'
            if e.code in (403, 404, 407):
                break
        except Exception as e:  # network hiccup: retry
            last = repr(e)
        time.sleep(2 * (i + 1))
    return 'failed: ' + str(last)


def describe(path, url, origin):
    rec = {'origin': origin, 'url': url, 'path': path}
    if os.path.exists(path):
        with open(path, 'rb') as f:
            b = f.read()
        rec['bytes'] = len(b)
        rec['sha256'] = hashlib.sha256(b).hexdigest()
        try:
            with Image.open(path) as im:
                rec['size'] = list(im.size)
                rec['mode'] = im.mode
        except Exception:
            pass
    return rec


def main(root):
    src = os.path.join(root, 'image_kit', '_sources')
    for sub in ('shopify', 'amazon', 'drive', 'fonts'):
        os.makedirs(os.path.join(src, sub), exist_ok=True)
    index = []

    with open(os.path.join(root, 'data', 'raw', 'illuco_com_images.json')) as f:
        shop = json.load(f)
    names = []
    for item in shop:
        if item['product'] == 'illuco-dental-photo-mirror':
            continue  # photo mirrors are out of scope
        names.append((item['product'], item['url'].rsplit('/', 1)[-1], item['url']))
    for n in EXTRA_SHOPIFY:
        names.append(('double-sided-dental-mirror', n, SHOPIFY_BASE + n))
    for product, name, url in names:
        # main.jpg / main_db.jpg are ambiguous names -> prefix with product handle
        local = f'{product}__{name}'
        dest = os.path.join(src, 'shopify', local)
        status = fetch(url, dest)
        print('shopify', local, status)
        rec = describe(dest, url, 'shopify')
        rec['product'] = product
        rec['status'] = status
        index.append(rec)

    seen = set()
    for listing, ids in AMAZON.items():
        for pos, iid in enumerate(ids, 1):
            url = AMAZON_BASE + iid + '.jpg'
            dest = os.path.join(src, 'amazon', iid.replace('+', 'PLUS') + '.jpg')
            status = fetch(url, dest) if iid not in seen else 'cached'
            seen.add(iid)
            print('amazon', listing, pos, iid, status)
            rec = describe(dest, url, 'amazon')
            rec['listing'] = listing
            rec['position'] = pos
            rec['status'] = status
            index.append(rec)

    font_dest = os.path.join(src, 'fonts', 'Outfit-Variable.ttf')
    status = fetch(FONT_URL, font_dest, tries=1)
    print('font Outfit', status)
    index.append({'origin': 'font', 'url': FONT_URL, 'path': font_dest, 'status': status})

    for name, fid in DRIVE_EXPECTED.items():
        dest = os.path.join(src, 'drive', name)
        rec = describe(dest, f'https://drive.google.com/file/d/{fid}', 'google-drive')
        rec['status'] = 'present' if os.path.exists(dest) else 'missing (fetch with Drive connector)'
        print('drive', name, rec['status'])
        index.append(rec)

    for rec in index:
        rec['path'] = os.path.relpath(rec['path'], root)
    with open(os.path.join(src, 'sources_index.json'), 'w') as f:
        json.dump(index, f, indent=1)


if __name__ == '__main__':
    main(os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.'))
