from typing import List


def ingest_error_logs(logs: List[str]) -> str:
    """
    Ingest error logs or stack traces and prepare them for AI analysis.
    Returns a formatted string for LLM input.
    """
    # For now, just join logs. Extend with parsing/formatting as needed.
    return "\n".join(logs)


# Example usage:
# logs = ["Traceback (most recent call last): ...", "Error: Something went wrong"]
# formatted = ingest_error_logs(logs)
# send_to_llm(formatted)
