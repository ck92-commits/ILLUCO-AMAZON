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
 ('Upload', 'Step 2, once the step-1 file has processed: upload ILLUCO_Amazon_UPLOAD.xlsx (22 rows, no UPCs, 0 errors): 3 parents (new 5 Pack and 1 Pack families with Color and Size as the choices; the heads family unchanged) and the 19 rows of existing listings; prices unchanged. The 7 new products are in ILLUCO_Amazon_NEW_PRODUCTS.xlsx, for after the GS1 fix', 'Catalog > Add Products via Upload', SC + '/product-search/bulk', 'The families only change through this upload', 'Today'),
 ('Step 1', 'Upload ILLUCO_Amazon_STEP1_delete_parent.xlsx first (1 row). It deletes only IDM-HANDLE-FAMILY-PARENT, the 11/21 family that mixed pack sizes: a parent holds no stock, sales or reviews, and its listings keep their ASINs, reviews and stock. A live family\'s variation theme cannot be changed and a child can belong to one parent only (warning 8032), so it goes before the upload. Afterwards re-point Brand Store tiles and A+ to the new parents', 'Catalog > Add Products via Upload', SC + '/product-search/bulk', 'One pack size per family (your message 11/23)', 'Today'),
 ('GS1', 'Korea: in GS1, change the brand name on the 7 new UPCs (810194860836 to 810194860898) from IDM SERIES to ILLUCO, in English and Korean, and add a product image URL. Verified by GS1 shows them registered to ILLUCO Corporation but with brand IDM SERIES, which is why Amazon rejected them on 11/20. When Verified by GS1 shows ILLUCO, upload ILLUCO_Amazon_UPLOAD.xlsx (again, if you already uploaded it)', 'GS1 account (Korea)', 'https://www.gs1.org/services/verified-by-gs1', 'Amazon compares the listing brand with the GS1 brand', 'Before the 7 new products can go live'),
 ('Approve', 'Claudia OK on the new copy: Ultra High Definition first, 2X / 3X as premium, 5-minute autoclave, 100+ cycles (see Sales Direction tab)', 'Sales team', '', 'Copy follows her direction from Nov 20', 'Before upload'),
 ('Design', 'Bigger in-box instruction card that leads with the 5-minute autoclave at 273°F (134°C)', 'Design team (Ashley)', '', 'Over-autoclaving strips the coating - the cause of the bad reviews', 'This week'),
 ('Optional', 'Host the care card as a PDF and paste its URL in column IK (Instructions for Use) of the upload so it shows under Product guides and documents', 'Shopify > Content > Files', '', 'Makes the care instructions visible on the listing', 'This week'),
 ('Case', 'Seller Support case: merge duplicate ASIN B0GGDQ15DD into B0G2DYRY7T (both are the 1X Light Blue single mirror)', 'Help > Get support > Products, listings or inventory', SC + '/help/hub/support', 'Combines the two review histories; no single listings left', 'After upload'),
 ('Estimate', 'Yellow cells in the upload are my estimates: item thickness 0.4 in (mirrors with handles) and 0.15 in (heads) on the Create rows (parents and the 7 new products); Double-Sided heads box 8.27 x 3.94 x 1.38 in, 0.3 lb (copied from the 5-pack kit box)', 'Upload file, yellow cells', '', 'Amazon requires them on new listings; correct them if you measure different values (FBA re-measures the box anyway)', 'Before upload if you can'),
 ('Privacy', 'Make the GitHub repository private only after Amazon has processed step 1, step 2 and ILLUCO_Amazon_NEW_PRODUCTS.xlsx (after the GS1 fix): each processing downloads the images from links in this repository, so a private repository breaks them. Until then it also shows data/account (order IDs, return comments, sales, PPC and Search Query Performance data) to anyone', 'GitHub > Settings > General > Danger Zone > Change visibility', 'https://github.com/ck92-commits/ILLUCO-AMAZON/settings', 'Amazon has copied the images by then', 'After upload'),
 ('Check', 'Headlight IHL-2000Gray (B0F8CXNTZH) is Inactive with 99 units; 9 flip-up loupes have been out of stock since May 2025 (Fix tab, 11/20)', 'Catalog > Manage All Inventory > Fix', SC + '/myinventory/inventory', 'Sellable stock that is not selling; the store Loupes page has nothing to buy', 'This week'),
 ('Supplier', 'Keep on file the supplier test basis for 99% reflectance and 100+ cycles at 5 min / 273°F', 'Product / supplier', '', 'Backs the claims now in the copy', 'This week'),
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
 ('Sales direction for the copy (Claudia)', 'management-meeting, Nov 20'),
 ('B0G2DYRY7T ships the black-shank version: keep its 4 photos, add 5 related kit images; use every related image (few images, team busy)', 'Your message 11/20'),
 ('3 SKUs confirmed: IDM2C43LB and IDM2C43LB-FBM (B0F857HKBG), IDM3C42NA (B0FCHH2SQB), IDM3C43NA (B0FCJY3H9H)', 'Manage All Inventory screenshots, 11/20'),
 ('Double-Sided head: 5-pack, cone socket, $139, main image', 'illuco.com'),
 ('Decisions: you are the approver; merge all singles; photo mirror as is; keep current Amazon prices; Double-Sided heads at the illuco.com price ($139) for now; brand ILLUCO; one family per pack size with Color and Size as the choices (11/23; heads: Size); main images are the product alone on white, no box, no text (11/23); 100+ cycles on the care card; no fog line; coupon and PPC budget on hold', 'Your messages 11/20-11/23'),
]
