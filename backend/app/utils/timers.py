import time
from contextlib import contextmanager
from typing import Generator, Dict, Any

@contextmanager
def timer() -> Generator[Dict[str, Any], None, None]:
    start = time.perf_counter()
    data: Dict[str, Any] = {}
    try:
        yield data
    finally:
        data['ms'] = int((time.perf_counter() - start) * 1000)
