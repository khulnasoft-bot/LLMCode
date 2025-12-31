import os

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Footer, Header, Input
from textual.widgets import RichLog as TextLog
from textual.widgets import Static, Tree


class LlmcodeTUI(App):
    CSS_PATH = "tui.css"

    def compose(self) -> ComposeResult:
        yield Header()
        # File tree navigation (dynamic)
        file_tree = Tree("File Tree")
        for folder in ["llmcode", "benchmark", "tests"]:
            node = file_tree.root.add(folder + "/")
            folder_path = os.path.join(os.getcwd(), folder)
            if os.path.isdir(folder_path):
                for fname in os.listdir(folder_path):
                    node.add(fname)
        # Chat area (TextLog for scrollback)
        chat_area = TextLog(highlight=True, markup=True, id="chatlog")
        chat_area.write("Welcome to Llmcode chat!")
        # Diff viewer placeholder
        diff_viewer = Static("Diff Viewer: Select a file to view changes.")
        yield Horizontal(
            Container(file_tree, id="filetree"),
            Container(chat_area, id="chat"),
            Container(diff_viewer, id="diff"),
        )
        # Command palette / scrollback
        yield Input(placeholder="Type a command or message...")
        yield Footer()


if __name__ == "__main__":
    LlmcodeTUI().run()
