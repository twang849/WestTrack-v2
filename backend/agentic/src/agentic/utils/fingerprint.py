import hashlib
import unicodedata
import re

def generate_fingerprint(content: str) -> str:
    """Create hash based on normalized content"""
    # Normalize Unicode and whitespace
    normalized = unicodedata.normalize('NFKC', content)
    cleaned = re.sub(r'\s+', ' ', normalized).strip()
    return hashlib.sha256(cleaned.encode('utf-8')).hexdigest() 