import requests
from readability import Document
from lxml import html

def normalize_text(content: str) -> str:
    """
    Normalize encoding issues (like Â® symbols) and clean whitespace.
    """
    if not content:
        return ""
    try:
        # Try fixing common UTF-8 / Latin-1 mismatches
        content = content.encode("latin-1", "ignore").decode("utf-8", "ignore")
    except Exception:
        # Fallback to utf-8 only
        content = content.encode("utf-8", "ignore").decode("utf-8", "ignore")

    return content.strip()

def clean_article(url: str) -> dict:
    """
    Fetch a URL and return cleaned article content using readability-lxml.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        doc = Document(response.text)

        # Extract HTML summary
        content_html = doc.summary()

        # Convert HTML to plain text
        tree = html.fromstring(content_html)
        content_text = tree.text_content()

        # Normalize encoding problems
        content_text = normalize_text(content_text)

        return {
            "title": doc.short_title(),
            "content": content_text
        }
    except Exception as e:
        print(f"⚠️ Failed to clean {url}: {e}")
        return {"title": None, "content": None}

if __name__ == "__main__":
    test_url = "https://huggingface.co/blog/embeddinggemma"
    result = clean_article(test_url)
    print("Title:", result["title"])
    if result["content"]:
        print("Preview:", result["content"][:300])
    else:
        print("No content extracted")
