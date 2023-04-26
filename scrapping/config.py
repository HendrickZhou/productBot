import json
sitemap_idx_url=None
root_url=None

with open('./config.json','r') as f:
    jo = json.load(f)
    sitemap_idx_url = jo['sitemap_idx_url']
    root_url = jo['root_url']
