import ast
import json
import os
from typing import Dict, List, Tuple

INDEX_FILE = ".cross_file_index.json"


def extract_symbols_from_file(filepath: str) -> List[Tuple[str, str]]:
    """
    Extract function and class names from a Python file.
    Returns list of (symbol, type) tuples.
    """
    symbols = []
    try:
        with open(filepath, "r") as f:
            tree = ast.parse(f.read(), filename=filepath)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                symbols.append((node.name, "function"))
            elif isinstance(node, ast.ClassDef):
                symbols.append((node.name, "class"))
    except Exception:
        pass
    return symbols


def build_symbol_index(root: str) -> Dict[str, Dict]:
    """
    Walk repo, extract symbols, build symbol → file/type mapping.
    Returns dict: symbol -> {type, file}
    """
    index = {}
    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:
            if fname.endswith(".py"):
                fpath = os.path.join(dirpath, fname)
                for name, typ in extract_symbols_from_file(fpath):
                    index[name] = {"type": typ, "file": fpath}
    with open(INDEX_FILE, "w") as f:
        json.dump(index, f, indent=2)
    return index


def load_symbol_index() -> Dict[str, Dict]:
    """
    Load symbol index from disk.
    """
    if not os.path.exists(INDEX_FILE):
        return {}
    with open(INDEX_FILE, "r") as f:
        return json.load(f)


def find_symbol(symbol: str) -> Dict:
    """
    Find where a symbol is defined.
    Returns dict with type and file, or None.
    """
    index = load_symbol_index()
    return index.get(symbol)


# Example usage:
# build_symbol_index("./llmcode")
# print(find_symbol("main"))
