import json
import os
from typing import Dict, List, Optional

from pygls.client import JsonRpcClient
from pygls.lsp.types import (Diagnostic, Hover, Location, Position,
                             TextDocumentIdentifier)

from llmcode.cross_file import find_symbol

CACHE_FILE = ".lsp_cache.json"


class LspBridge:
    def __init__(self, server_cmd: List[str]):
        self.client = JsonRpcClient(server_cmd)
        self.client.start()
        self.cache = self._load_cache()

    def _load_cache(self) -> Dict:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        return {}

    def _save_cache(self):
        with open(CACHE_FILE, "w") as f:
            json.dump(self.cache, f, indent=2)

    def go_to_definition(
        self, file_path: str, line: int, character: int
    ) -> Optional[Location]:
        key = f"def:{file_path}:{line}:{character}"
        if key in self.cache:
            return self.cache[key]
        doc = TextDocumentIdentifier(uri=f"file://{os.path.abspath(file_path)}")
        pos = Position(line=line, character=character)
        result = self.client.lsp.send_request(
            "textDocument/definition", {"textDocument": doc, "position": pos}
        )
        if result and result.result:
            self.cache[key] = result.result
            self._save_cache()
            return result.result
        # Fallback to cross-file index
        symbol = self._extract_symbol_at(file_path, line)
        cross = find_symbol(symbol) if symbol else None
        if cross:
            self.cache[key] = cross
            self._save_cache()
        return cross

    def get_diagnostics(self, file_path: str) -> List[Diagnostic]:
        key = f"diag:{file_path}"
        if key in self.cache:
            return self.cache[key]
        doc = TextDocumentIdentifier(uri=f"file://{os.path.abspath(file_path)}")
        result = self.client.lsp.send_request(
            "textDocument/publishDiagnostics", {"textDocument": doc}
        )
        if result and result.result:
            self.cache[key] = result.result
            self._save_cache()
            return result.result
        return []

    def hover(self, file_path: str, line: int, character: int) -> Optional[Hover]:
        key = f"hover:{file_path}:{line}:{character}"
        if key in self.cache:
            return self.cache[key]
        doc = TextDocumentIdentifier(uri=f"file://{os.path.abspath(file_path)}")
        pos = Position(line=line, character=character)
        result = self.client.lsp.send_request(
            "textDocument/hover", {"textDocument": doc, "position": pos}
        )
        if result and result.result:
            self.cache[key] = result.result
            self._save_cache()
            return result.result
        return None

    def _extract_symbol_at(self, file_path: str, line: int) -> Optional[str]:
        # Simple static extraction: get symbol at line (improve with AST/Tree-sitter)
        try:
            with open(file_path, "r") as f:
                lines = f.readlines()
            code_line = lines[line].strip()
            # Naive: get first word (function/class name)
            return code_line.split()[1] if len(code_line.split()) > 1 else None
        except Exception:
            return None


# Example usage:
# lsp = LspBridge(["pylsp"])
# loc = lsp.go_to_definition("llmcode/main.py", 10, 5)
# diags = lsp.get_diagnostics("llmcode/main.py")
# hover = lsp.hover("llmcode/main.py", 10, 5)
