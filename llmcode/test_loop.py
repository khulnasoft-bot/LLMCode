import json
import subprocess
from pathlib import Path

from .lsp_bridge import LspBridge


class TestLoop:
    def __init__(self, repo_root=".", lsp_server_cmd=None):
        self.repo_root = Path(repo_root)
        self.lsp = LspBridge(lsp_server_cmd) if lsp_server_cmd else None

    def run_tests(self, cmd=["pytest", "-q"]):
        try:
            result = subprocess.run(
                cmd, cwd=self.repo_root, capture_output=True, text=True
            )
            return {
                "status": "ok" if result.returncode == 0 else "fail",
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except FileNotFoundError:
            return {"status": "error", "msg": "pytest not installed"}

    def run_diagnostics(self, files=None):
        files = files or [str(p) for p in self.repo_root.rglob("*.py")]
        diags = {}
        if self.lsp:
            for f in files:
                diags[f] = self.lsp.get_diagnostics(f)
        else:
            for f in files:
                diags[f] = []
        return diags

    def feedback(self, files=None):
        data = {"diagnostics": self.run_diagnostics(files), "tests": self.run_tests()}
        out_file = self.repo_root / ".test_feedback.json"
        out_file.write_text(json.dumps(data, indent=2))
        return data

    def loop_control(self, feedback, auto_commit=False, commit_msg="AI: pass tests"):
        if feedback["tests"]["status"] == "ok" and auto_commit:
            subprocess.run(["git", "add", "."], cwd=self.repo_root)
            subprocess.run(["git", "commit", "-m", commit_msg], cwd=self.repo_root)
        elif feedback["tests"]["status"] != "ok":
            print("Test failures detected. AI should suggest fixes.")


# Usage example:
# from llmcode.test_loop import TestLoop
# loop = TestLoop(repo_root=".", lsp_server_cmd=["pylsp"])
# feedback = loop.feedback()
# print("Feedback:", feedback)
# loop.loop_control(feedback, auto_commit=True)
