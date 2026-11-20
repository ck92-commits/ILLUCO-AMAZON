"""Clickable links shared by the report builders."""
from openpyxl.styles import Font

def dp(asin):
    return f'https://www.amazon.com/dp/{asin}'

def reviews(asin):
    return f'https://www.amazon.com/product-reviews/{asin}?filterByStar=critical&sortBy=recent'

def drive(file_id):
    return f'https://drive.google.com/file/d/{file_id}/view'

GH = 'https://github.com/ck92-commits/ILLUCO-AMAZON/blob/claude/bold-einstein-yth5jo/'
STORE = 'https://www.amazon.com/stores/ILLUCOUSA/page/190398CE-6848-40BB-9EE3-A506386202F4'
SELLER_STOREFRONT = 'https://www.amazon.com/s?i=merchant-items&me=A1I40WMT1SR62H'
SC = 'https://sellercentral.amazon.com'

DRIVE_IMAGES = [
    ('Double-Sided Dark Blue MAIN image (required)', 'Double-Sided Dental Mirrors/main_db.jpg', '1lOw74MwTc7cHDFNH4BYrfwgwVQMv_YT6'),
    ('Double-Sided Dark Blue infographic 1', 'Double-Sided Dental Mirrors/dsdm-01_db.jpg', '1b9Zwhm8Wb7-spWZxLJzz1ELiRM7337K4'),
    ('Double-Sided Dark Blue infographic 2', 'Double-Sided Dental Mirrors/dsdm-02_db.jpg', '16VoEjZ6n9GNtR9hCjIQeEf9FNfXMi8C3'),
    ('Double-Sided Dark Blue infographic 3', 'Double-Sided Dental Mirrors/dsdm-03_db.jpg', '10TZlOp0joNxqkhzdCnSjSSQny91paYBe'),
    ('Grand Dark Blue infographic 1', 'Grand Dental Mirror/grand-01_db.jpg', '12HbJgSv_t2gs1Mv5OTXet2Fi3965ySHd'),
    ('Grand "Professional Applications"', 'Grand Dental Mirror/grand-04.jpg', '1lQgJ64buFqtGefJS4yYFKonTe5Mq4hhw'),
]

def link(cell, url, text=None, size=9):
    if text is not None:
        cell.value = text
    cell.hyperlink = url
    cell.font = Font(name='Arial', size=size, color='0563C1', underline='single')

# Master list of what is needed to finish the audit and apply the updates.
# (type, what, where in the tool, link, why, needed by)
NEEDS = [
 ('Access', 'Someone with Seller Central access to apply the listing files (I cannot log in from here)', 'Seller Central', SC, 'Updates go live only through Seller Central', 'Today'),
 ('Export', 'All Listings Report (SKU, ASIN, product type)', 'Inventory > Inventory Reports > All Listings Report', SC + '/listing/reports', 'SKUs for the bulk partial-update file', 'Today'),
 ('Export', 'Detail Page Sales & Traffic by Child Item, last 90 days', 'Reports > Business Reports', SC + '/business-reports', 'Sessions, conversion, units, sales per ASIN', 'Today'),
 ('Export', 'Sponsored Products / Brands / Video reports (campaign, targeting, search term), last 60 days + bulk sheet', 'Advertising console > Measurement & Reporting; Bulk operations', 'https://advertising.amazon.com/cm/campaigns', 'PPC audit, wasted spend, new structure', 'Today'),
 ('Export', 'Every 1-3 star review, per ASIN', 'Brand Analytics > Customer Reviews, or the review links in the ASIN Report tab', SC + '/brand-analytics/dashboard', 'Confirm the real complaint causes', 'Today'),
 ('Export', 'FBA Customer Returns report (with reason codes) + Voice of the Customer', 'Reports > Fulfillment > Customer Returns; Performance > Voice of the Customer', SC + '/voice-of-the-customer', 'Product-quality issues', 'Today'),
 ('Export', 'Account Health and Fix Your Products (suppressed / at-risk listings, pricing alerts)', 'Performance > Account Health; Inventory > Fix Your Products', SC + '/performance/dashboard', 'Anything blocking sales now', 'Today'),
 ('Export', 'Search Query Performance + Top Search Terms for our keywords', 'Brand Analytics', SC + '/brand-analytics/dashboard', 'Real keyword volume for SEO and PPC', 'This week'),
 ('Info', 'Status of Brand Registry name spelling, Vine, Amazon Attribution, active coupons/promotions', 'Brand Registry; Advertising > Vine; Advertising console > Attribution', 'https://brandregistry.amazon.com', 'Which programs we can use now', 'Today'),
 ('Info', 'Landed cost per SKU', 'Finance', '', 'Margins and break-even ACoS for budgets', 'This week'),
 ('Info', 'Supplier test reports: 99% reflectance, 100 autoclave cycles, 60-70% standard-mirror figure', 'Product / supplier', '', 'Keep these claims in images and A+', 'This week'),
 ('Image', 'Upload to Shopify Files and send the URL: Double-Sided Dark Blue MAIN image (REQUIRED before upload)', 'Shopify admin > Content > Files', drive('1lOw74MwTc7cHDFNH4BYrfwgwVQMv_YT6'), 'Dark Blue child has no main image', 'Today'),
 ('Image', 'Upload to Shopify Files: dsdm-01_db.jpg', 'Shopify admin > Content > Files', drive('1b9Zwhm8Wb7-spWZxLJzz1ELiRM7337K4'), 'Dark Blue infographic', 'Today'),
 ('Image', 'Upload to Shopify Files: dsdm-02_db.jpg', 'Shopify admin > Content > Files', drive('16VoEjZ6n9GNtR9hCjIQeEf9FNfXMi8C3'), 'Dark Blue infographic', 'Today'),
 ('Image', 'Upload to Shopify Files: dsdm-03_db.jpg', 'Shopify admin > Content > Files', drive('10TZlOp0joNxqkhzdCnSjSSQny91paYBe'), 'Dark Blue infographic', 'Today'),
 ('Image', 'Upload to Shopify Files: grand-01_db.jpg', 'Shopify admin > Content > Files', drive('12HbJgSv_t2gs1Mv5OTXet2Fi3965ySHd'), 'Grand Dark Blue infographic', 'Today'),
 ('Image', 'Upload to Shopify Files: grand-04.jpg', 'Shopify admin > Content > Files', drive('1lQgJ64buFqtGefJS4yYFKonTe5Mq4hhw'), 'Extra Grand image (optional)', 'This week'),
 ('Image', 'Images for the Double-Sided head (IDM-3CD41H) - none in the Drive folder', 'Design team', 'https://drive.google.com/drive/folders/112-y6c3etIb17RGpJH-nvIgKgCBrRnYQ', 'Head listing cannot sell without them', 'This week'),
 ('Image', 'Fix "quandrant" and "minimizing light" (should be "light loss") in grand-01 / dsdm-01 infographics', 'Design team', 'https://cdn.shopify.com/s/files/1/0795/1348/5611/files/grand-01.jpg', 'Typos are live on Amazon-bound and illuco.com images', 'Today'),
 ('Confirm', 'Double-Sided head: pack size 5? cone socket? price? package dimensions?', 'You / product', '', 'Fill the head row', 'Today'),
 ('Confirm', 'Is B0G2DYRY7T (black shank in photos) the same product as the 1X single mirror?', 'You / product', 'https://www.amazon.com/dp/B0G2DYRY7T', 'Before the merge request', 'Today'),
 ('Confirm', 'Model numbers for 2X/3X kits and heads (I used the illuco.com pattern IDM-2C42DB etc.)', 'You / product', '', 'Replace variant names in the model-number field', 'This week'),
 ('Confirm', 'Photo-mirror dimensions (Occlusal Small, Lingual, Buccal) and whether the Amazon box includes the travel pouch', 'You / product', 'https://illuco.com/products/illuco-dental-photo-mirror', 'Complete the photo-mirror copy', 'This week'),
 ('Decision', 'Merge the two orphan single-mirror ASINs into the family', 'Manager', 'https://www.amazon.com/dp/B0GGDGRHRR', 'Pools ratings', 'Today'),
 ('Decision', 'Approve claim wording (fog / autoclave / no "40% clearer", no rhodium figure)', 'Manager', '', 'Copy goes live', 'Today'),
 ('Decision', 'Price parity Amazon vs illuco.com (5-pack $95-140 vs $85; photo $165 vs $155)', 'Manager', 'https://illuco.com/collections/dental-mirrors', 'Buy Box and conversion', 'Nov 24'),
 ('Decision', 'Keep Grand + Double-Sided in one variation family, or split', 'Manager', '', 'Variation-policy risk vs pooled reviews', 'Before upload'),
 ('Decision', 'Black Friday / Cyber Monday coupon (Nov 27-30) and PPC budget (~$53/day proposal)', 'Manager', '', 'No spend increase without approval', 'Nov 24'),
]
