import subprocess
from typing import Optional


def create_auto_branch(session_name: Optional[str] = None) -> str:
    """
    Create a new git branch for the current session.
    If session_name is not provided, use a timestamp.
    Returns the branch name.
    """
    import datetime

    branch = (
        session_name
        or f"llmcode-session-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
    )
    subprocess.run(["git", "checkout", "-b", branch], check=True)
    return branch


def generate_commit_message(diff: str) -> str:
    """
    Generate an AI-powered commit message from a diff.
    Placeholder: returns a generic message. Integrate with LLM later.
    """
    # TODO: Integrate with LLM for commit message generation
    return "Update code based on recent changes"


def commit_changes(message: str) -> None:
    """
    Commit staged changes with the given message.
    """
    subprocess.run(["git", "commit", "-m", message], check=True)
