from __future__ import annotations


def word_count(text: str) -> int:
    """Count whitespace-separated words in text. Non-string input returns 0."""
    if not isinstance(text, str):
        return 0
    return len(text.split())


def clean_ids(items: list) -> list[str]:
    """Return sorted unique non-empty string items after stripping whitespace.
    Non-strings and empty strings are skipped. Non-list input returns [].
    """
    if not isinstance(items, list):
        return []
    result = set()
    for item in items:
        if isinstance(item, str):
            stripped = item.strip()
            if stripped:
                result.add(stripped)
    return sorted(result)
