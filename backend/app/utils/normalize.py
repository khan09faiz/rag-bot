import re

_whitespace_re = re.compile(r"\s+")

def normalize_text(text: str) -> str:
    text = text.replace('\u00A0', ' ')
    text = _whitespace_re.sub(' ', text)
    return text.strip()
