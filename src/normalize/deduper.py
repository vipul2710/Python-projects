import hashlib

class Deduper:
    def __init__(self):
        # store seen hashes in memory for now
        self.seen_hashes = set()

    def compute_hash(self, text: str) -> str:
        """
        Compute a SHA256 hash of article text (or URL as fallback).
        """
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def is_duplicate(self, text: str) -> bool:
        """
        Check if an article is a duplicate. Returns True if already seen.
        """
        h = self.compute_hash(text)
        if h in self.seen_hashes:
            return True
        self.seen_hashes.add(h)
        return False

if __name__ == "__main__":
    deduper = Deduper()
    articles = [
        "AI is transforming analytics.",
        "AI is transforming analytics.",  # duplicate
        "Data Mesh adoption is growing."
    ]

    for article in articles:
        if deduper.is_duplicate(article):
            print(f"❌ Duplicate skipped: {article}")
        else:
            print(f"✅ New article: {article}")
