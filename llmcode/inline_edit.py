import difflib
import os
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

from termcolor import colored

from llmcode.lsp_bridge import LspBridge

from .test_loop import TestLoop


class InlineEdit:
    def __init__(self, file_path: str, lsp_server_cmd: Optional[List[str]] = None):
        self.file_path = file_path
        with open(file_path, "r") as f:
            self.original = f.readlines()
        self.working = self.original.copy()
        self.diff = None
        self.preview = None
        self.conflicts = []
        self.lsp = LspBridge(lsp_server_cmd) if lsp_server_cmd else None
        self.repo_root = Path(".")
        self.test_loop = TestLoop(self.repo_root)

    def parse_diff(self, diff_text: str):
        """
        Parse unified diff and store hunks.
        """
        self.diff = list(
            difflib.unified_diff(
                self.original, diff_text.splitlines(keepends=True), lineterm=""
            )
        )

    def apply_patch(self):
        """
        Apply parsed diff to working copy in memory, with fuzzy matching for hunks.
        """
        # Use SequenceMatcher to anchor hunks
        patched = self.original.copy()
        matcher = difflib.SequenceMatcher(
            None,
            self.original,
            [line[1:] for line in self.diff if line.startswith(("-", "+", " "))],
        )
        opcodes = matcher.get_opcodes()
        for tag, i1, i2, j1, j2 in opcodes:
            if tag == "replace" or tag == "delete" or tag == "insert":
                # Fuzzy match failed, mark conflict
                self.conflicts.append((i1, i2, j1, j2))
                patched[i1:i2] = (
                    [f"<<<<<<< CONFLICT\n"]
                    + patched[i1:i2]
                    + [f"=======\n"]
                    + [line for line in self.diff if line.startswith("+")]
                    + [f">>>>>>> AI PATCH\n"]
                )
        self.preview = patched
        return patched

    def show_preview(self):
        """
        Show a preview of changes (additions green, removals red, conflicts yellow).
        """
        for line in self.preview:
            if line.startswith("+"):
                print(f"\033[92m{line}\033[0m", end="")  # green
            elif line.startswith("-"):
                print(f"\033[91m{line}\033[0m", end="")  # red
            elif line.startswith("<") or line.startswith(">") or line.startswith("="):
                print(f"\033[93m{line}\033[0m", end="")  # yellow for conflict
            else:
                print(line, end="")

    def accept(self):
        """
        Write working copy to file and run diagnostics/tests.
        """
        with open(self.file_path, "w") as f:
            f.writelines(self.preview)
        self.run_diagnostics_and_tests()

    def reject(self):
        """
        Discard changes.
        """
        self.working = self.original.copy()
        self.preview = None
        self.conflicts = []

    def auto_commit(self, summary: str):
        os.system(f"git add {self.file_path}")
        os.system(f"git commit -m 'AI edit: {summary}'")

    def run_diagnostics_and_tests(self):
        print("Running diagnostics...")
        if self.lsp:
            diags = self.lsp.get_diagnostics(self.file_path)
            print("LSP Diagnostics:", diags)
        print("Running tests...")
        result = subprocess.run(
            ["pytest", self.file_path], capture_output=True, text=True
        )
        print(result.stdout)
        if result.returncode != 0:
            print("Test failures detected. Feed results back to AI for autofix.")

    def apply_patch(self, file_path, diff_hunks):
        path = self.repo_root / file_path
        original = path.read_text().splitlines()

        # Apply hunks (placeholder: use your diff logic)
        patched = original[:]
        for hunk in diff_hunks:
            patched = self._apply_hunk(patched, hunk)

        # Preview
        self.preview(original, patched)

        # Accept or reject
        choice = input("Apply changes? [y/N] ").strip().lower()
        if choice == "y":
            path.write_text("\n".join(patched) + "\n")
            print(colored(f"✔ Applied changes to {file_path}", "green"))

            # Run feedback loop
            feedback = self.test_loop.feedback(files=[str(path)])
            if feedback["tests"]["status"] == "ok":
                print(colored("✅ Tests passed", "green"))
            else:
                print(colored("❌ Tests failed", "red"))
                print(feedback["tests"]["stdout"])
        else:
            print(colored("✘ Changes discarded", "red"))

    def _apply_hunk(self, lines, hunk):
        # TODO: Implement diff hunk application logic
        return lines

    def preview(self, before, after):
        diff = difflib.unified_diff(before, after, lineterm="")
        for line in diff:
            if line.startswith("+") and not line.startswith("+++"):
                print(colored(line, "green"))
            elif line.startswith("-") and not line.startswith("---"):
                print(colored(line, "red"))
            else:
                print(line)
