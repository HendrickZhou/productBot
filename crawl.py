from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
import json
from config import sitemap_idx_url, root_url
from product import Product, MetaInfo


#############################
# Step 1. crawl the sitemap idx
#############################
page = requests.get(sitemap_idx_url)
soup = BeautifulSoup(page.text, features="xml")

pdp_map = []
for loc in soup.find_all('loc'):
    url = loc.text
    if "misc" in url:
        continue
    elif "pdp" in url:
        pdp_map.append(url)
    elif "categories" in url:
        continue
    else:
        assert False, "names other than misc, pdp, catetories in sitemap idx"

# record the country meta information
def parse_country_code(url:str)->str:
    o = urlparse(url)
    code = o.path.split('/')[0]
    if len(code) == 2:
        return code
    else:
        return None



#############################
# Step 2. get all pdp infomation!
#############################
print(pdp_map)
pdp_urls = []
for pdp in pdp_map:
    pdp_page = requests.get(pdp)
    cc = parse_country_code(pdp) 
    if cc is not None:
        continue
    pdp_soup = BeautifulSoup(pdp_page.text, features="xml")
    for loc in pdp_soup.find_all('loc'):
        pdp_urls.append(loc.text)

#############################
# Step 3. Save it to the disk
#############################
with open("./pdp_url.json", 'w') as f:
    json.dump(pdp_urls, f)