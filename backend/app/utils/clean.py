import re

_STOPWORDS = {
    'the','a','an','and','or','but','if','then','else','for','on','in','at','to','from','by','of','with','is','are','was','were','be','been','it','this','that','these','those','as','so','we','you','i'
}

def clean_for_embedding(text: str) -> str:
    # lower, remove non-alphanum (keep spaces), collapse spaces, strip stopwords
    t = text.lower()
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    tokens = [w for w in t.split() if w not in _STOPWORDS and len(w) > 1]
    return " ".join(tokens)[:10000]
