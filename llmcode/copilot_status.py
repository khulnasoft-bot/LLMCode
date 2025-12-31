import json
from pathlib import Path


class CopilotStatus:
    def __init__(self, repo_root="."):
        self.repo_root = Path(repo_root)
        self.module_map = {
            "CLI Scaffolding": "tui.py",
            "Config Management": "context_expansion.py",
            "Git Integration": "git_utils.py",
            "Prompt Pipeline": "prompts.py",
            "Vector DB Index": "vector_db.py",
            "Cross-file Awareness": "cross_file.py",
            "LSP Bridge": "lsp_bridge.py",
            "Inline Editing": "inline_edit.py",
            "Test & Diagnostics Loop": "test_loop.py",
            "Automation & Retry Loop": None,  # Phase 3
            "GUI/TUI Experience": None,  # Phase 3
            "Team/Collaboration Features": None,  # Phase 3
        }
        self.phases = {
            "Phase 1: Developer Essentials": [
                "CLI Scaffolding",
                "Config Management",
                "Git Integration",
                "Prompt Pipeline",
            ],
            "Phase 2: Code Intelligence": [
                "Vector DB Index",
                "Cross-file Awareness",
                "LSP Bridge",
                "Inline Editing",
                "Test & Diagnostics Loop",
            ],
            "Phase 3: (Upcoming)": [
                "Automation & Retry Loop",
                "GUI/TUI Experience",
                "Team/Collaboration Features",
            ],
        }

    def feature_status(self, feature):
        mod = self.module_map.get(feature)
        if mod is None:
            return False
        return (self.repo_root / "llmcode" / mod).exists()

    def summary(self):
        lines = []
        for phase, features in self.phases.items():
            lines.append(f"\n{phase}")
            for feat in features:
                check = "✔" if self.feature_status(feat) else "✘"
                lines.append(f"  {check} {feat}")
        return "\n".join(lines)

    def save(self):
        status_dict = {}
        for phase, features in self.phases.items():
            status_dict[phase] = {feat: self.feature_status(feat) for feat in features}
        out = self.repo_root / ".copilot_status.json"
        out.write_text(json.dumps(status_dict, indent=2))
        return out


# Usage example:
# status = CopilotStatus()
# print(status.summary())
# status.save()
