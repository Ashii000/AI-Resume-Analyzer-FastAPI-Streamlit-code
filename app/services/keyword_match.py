"""Keyword matching utilities"""

def match_keywords(text: str, keywords: list) -> list:
    found = [k for k in keywords if k.lower() in text.lower()]
    return found
