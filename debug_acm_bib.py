# debug_acm_bib.py
from src.normalize.text_cleaner import clean_acm_url, SCRAPER, HEADERS

# change this to the same DOI you used earlier
TEST_URL = "https://dl.acm.org/doi/abs/10.1145/3677057?mi=19n0l1t"

clean = clean_acm_url(TEST_URL)
print("CLEAN URL:", clean)

# extract DOI string from canonical URL
doi = clean.split("/doi/")[-1]
print("DOI:", doi)

bib_url = f"https://dl.acm.org/action/downloadCitation?doi={doi}&format=bibtex"
print("BIB URL:", bib_url)

r = SCRAPER.get(bib_url, headers=HEADERS, timeout=15)
print("HTTP status:", r.status_code)
print("Response length (chars):", len(r.text or ""))
print("First 800 chars of response:\n")
print((r.text or "")[:800])
