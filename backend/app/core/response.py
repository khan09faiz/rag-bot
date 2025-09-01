from typing import Any, Iterable

def success(data: Any = None, meta: dict | None = None):
    resp = {"status": "success"}
    if data is not None:
        resp["data"] = data
    if meta:
        resp["meta"] = meta
    return resp

def paginate(items: Iterable[Any], total: int, page: int, page_size: int):
    return {
        "items": list(items),
        "meta": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size if page_size else 1,
        }
    }
