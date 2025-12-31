import json
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Footer, Header, Static, Tree

from .copilot_status import CopilotStatus


class StatusTree(Tree):
    def __init__(self, status_dict):
        super().__init__("Copilot Status")
        for phase, features in status_dict.items():
            phase_node = self.root.add(phase)
            for feat, done in features.items():
                color = "green" if done else "red"
                check = "✔" if done else "✘"
                phase_node.add(f"[{color}]{check} {feat}[/]")


class CopilotTUI(App):
    CSS_PATH = "copilot_tui.css"

    def compose(self) -> ComposeResult:
        yield Header()
        status = CopilotStatus().save().read_text()
        status_dict = json.loads(status)
        yield Container(StatusTree(status_dict), id="status")
        yield Footer()


if __name__ == "__main__":
    CopilotTUI().run()
