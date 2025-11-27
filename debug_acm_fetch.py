# debug_acm_fetch.py

from src.normalize.text_cleaner import SCRAPER, HEADERS, clean_acm_url

# Replace with ANY ACM URL from your DB
url = "https://dl.acm.org/doi/abs/10.1145/3677057?mi=19n0l1t"

clean = clean_acm_url(url)

print("CLEAN URL:", clean)

resp = SCRAPER.get(clean, headers=HEADERS)
print("STATUS:", resp.status_code)

# Save raw HTML so we can inspect what ACM returns
with open("acm_debug.html", "w", encoding="utf-8") as f:
    f.write(resp.text)

print("Saved acm_debug.html")
