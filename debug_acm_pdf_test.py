from src.normalize.text_cleaner import clean_acm_url, SCRAPER, HEADERS
from PyPDF2 import PdfReader
import io

url = "https://dl.acm.org/doi/abs/10.1145/3677057?mi=19n0l1t"
clean = clean_acm_url(url)
print("CLEAN:", clean)

resp = SCRAPER.get(clean, headers=HEADERS, timeout=20)
print("Status:", resp.status_code)
print("Content-Type:", resp.headers.get("Content-Type"))

# Save PDF so we can inspect if needed
with open("debug_pdf.pdf", "wb") as f:
    f.write(resp.content)

print("Saved debug_pdf.pdf (size bytes):", len(resp.content))

# Try reading the PDF
try:
    reader = PdfReader(io.BytesIO(resp.content))
    text = reader.pages[0].extract_text()
    print("First 500 chars of PDF text:")
    print(text[:500])
except Exception as e:
    print("PDF parse error:", e)
