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

# What is still needed (updated 2026-11-20 after ILLUCO shared the research folder).
# (type, what, where in the tool, link, why, needed by)
NEEDS = [
 ('Upload', 'Upload ILLUCO_Dental_Mirrors_MERGE_UPLOAD.xlsx (merges all mirrors into 2 families, new copy, illuco.com prices)', 'Catalog > Add Products via Upload', SC + '/product-search/bulk', 'The merge only happens through this upload', 'Today'),
 ('Confirm', 'Check 3 SKUs I inferred (IDM2C43LB, IDM3C42NA, IDM3C43NA) exist for B0F857HKBG, B0FCHH2SQB, B0FCJY3H9H - yellow cells in column A', 'Catalog > Manage All Inventory', SC + '/myinventory/inventory', 'A wrong SKU makes that row fail', 'Before upload'),
 ('Confirm', 'Brand name spelling for the 2 new parents: file uses "ILLUCO" (live listings show "Illuco")', 'Brand Registry', 'https://brandregistry.amazon.com', 'Parent and children must carry the same brand', 'Before upload'),
 ('Approve', 'Two price INCREASES to match illuco.com: heads 1X $60 -> $69 and heads 2X $90 -> $95 (yellow DI cells). Heads 1X is your top seller at 17.4% conversion', 'You', '', 'Keep, or revert those two cells', 'Before upload'),
 ('Approve', 'Claim wording (sales team): removed "Fog-Resistant", "anti fog" and "100 autoclave cycles"; added an honest care line', 'Sales team', '', 'Reviews and returns contradict the old claims', 'Before upload'),
 ('Case', 'Seller Support case: merge duplicate ASIN B0GGDQ15DD into B0G2DYRY7T (both are the 1X Light Blue single mirror)', 'Help > Get support > Products, listings or inventory', SC + '/help/hub/support', 'Combines the two review histories; no single listings left', 'After upload'),
 ('Confirm', 'B0G2DYRY7T ships the current mirror (its photos show a black shank) - if not, tell me and I will swap the 1X Light Blue child', 'You / warehouse', 'https://www.amazon.com/dp/B0G2DYRY7T', 'It becomes the 1X Light Blue child of the new family', 'Before upload'),
 ('Images', 'Upload the image kit to each child (or host on Shopify Files and send URLs)', 'Catalog > Manage All Inventory > Edit > Images', SC + '/myinventory/inventory', 'Replaces the 5-mirror image on 1-packs and adds missing images', 'After upload'),
 ('Supplier', 'Ask the supplier about the water-repellent top coat: a reviewer says it lasts 1-2 sterilization cycles; request test reports for 99% reflectance and autoclave durability', 'Product / supplier', '', 'Root cause of the 1-star reviews and fog returns', 'This week'),
 ('Respond', 'Answer the NCX flag on IDM-2C41DB-3X-FBA (B0GGDGRHRR, 20% "performance or quality not adequate")', 'Performance > Voice of the Customer', SC + '/voice-of-the-customer', 'CX Health shows "Very poor" for that SKU', 'This week'),
 ('Optional', 'Sponsored Products "Advertised product" report (60 days)', 'Advertising console > Measurement & Reporting', 'https://advertising.amazon.com/cm/campaigns', 'Splits ad spend and sales by ASIN for the report', 'This week'),
 ('Optional', 'Any other 1-3 star review text (I have the 3X Dark Blue ones)', 'Brand Analytics > Customer Reviews', SC + '/brand-analytics/dashboard', 'Confirms there is no second complaint theme', 'This week'),
 ('Case', 'Re-classify the 4 dermatoscopes (Home & Kitchen / Automotive today) and fix IDS-3100 model number', 'Help > Get support', SC + '/help/hub/support', 'Wrong category hides them from buyers', 'This week'),
]

RECEIVED = [
 ('Business Report by child ASIN', 'BusinessReport-11-20-26.csv'),
 ('SKU list per ASIN', 'Listing_Summary_Report.csv + FBA returns/reimbursements'),
 ('Sponsored Products campaign, search-term and targeting reports', 'CHECK-_ILLUCO_1/2/3'),
 ('Search Query Performance (Sep, Oct, Q3)', 'SQP_Brand_*.csv'),
 ('FBA returns with customer comments; reimbursements', '293310020777.csv, 293311020777.csv'),
 ('Account Health (healthy, rating 204)', 'Screenshot'),
 ('Two 1-star review texts', 'Screenshots'),
 ('Model numbers and prices for every variant', 'illuco.com public product feed'),
 ('Double-Sided head: 5-pack, cone socket, $139, main image', 'illuco.com'),
 ('Decisions: you are the approver; merge all singles; photo mirror as is; align prices unless promotion; coupon and PPC budget on hold', 'Your message 11/20'),
]
