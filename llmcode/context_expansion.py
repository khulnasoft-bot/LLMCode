import os
from typing import List, Optional, Tuple


def list_files_by_size(
    root: str, min_size: int = 0, max_size: Optional[int] = None
) -> List[Tuple[str, int]]:
    """
    List files in the repo, sorted by size, optionally filtered by min/max size.
    Returns a list of (filepath, size) tuples.
    """
    files = []
    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:
            fpath = os.path.join(dirpath, fname)
            try:
                size = os.path.getsize(fpath)
                if (min_size is None or size >= min_size) and (
                    max_size is None or size <= max_size
                ):
                    files.append((fpath, size))
            except Exception:
                continue
    return sorted(files, key=lambda x: x[1], reverse=True)


def select_scope(
    paths: List[str],
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
) -> List[str]:
    """
    Select a subset of files/folders for context expansion.
    Can filter by include/exclude lists.
    """
    selected = paths
    if include:
        selected = [p for p in selected if any(inc in p for inc in include)]
    if exclude:
        selected = [p for p in selected if not any(exc in p for exc in exclude)]
    return selected
