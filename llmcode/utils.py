import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import oslex

from llmcode.exceptions import (DependencyError, FileOperationError,
                                NetworkError, ValidationError)

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp", ".pdf"}


class IgnorantTemporaryDirectory:
    """
    A context manager for temporary directories that ignores cleanup errors.

    This class provides a safer alternative to tempfile.TemporaryDirectory,
    especially useful on Windows where cleanup errors can occur frequently.
    """

    def __init__(self) -> None:
        """Initialize the temporary directory context manager."""
        if sys.version_info >= (3, 10):
            self.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        else:
            self.temp_dir = tempfile.TemporaryDirectory()

    def __enter__(self) -> str:
        """Enter the context and return the temporary directory path."""
        return self.temp_dir.__enter__()

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the context and cleanup the temporary directory."""
        self.cleanup()

    def cleanup(self) -> None:
        """Clean up the temporary directory, ignoring errors."""
        try:
            self.temp_dir.cleanup()
        except (OSError, PermissionError, RecursionError):
            pass  # Ignore errors (Windows and potential recursion)

    def __getattr__(self, item: str) -> Any:
        """Delegate attribute access to the underlying temporary directory."""
        return getattr(self.temp_dir, item)


class ChdirTemporaryDirectory(IgnorantTemporaryDirectory):
    """
    A temporary directory context manager that changes the current working directory.

    This extends IgnorantTemporaryDirectory to also change the current working
    directory to the temporary directory for the duration of the context.
    """

    def __init__(self) -> None:
        """Initialize the temporary directory with working directory tracking."""
        try:
            self.cwd = os.getcwd()
        except FileNotFoundError:
            self.cwd = None

        super().__init__()

    def __enter__(self) -> str:
        """Enter the context, create temp dir, and change to it."""
        res = super().__enter__()
        os.chdir(Path(self.temp_dir.name).resolve())
        return res

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the context, restore original directory, and cleanup."""
        if self.cwd:
            try:
                os.chdir(self.cwd)
            except FileNotFoundError:
                pass
        super().__exit__(exc_type, exc_val, exc_tb)


class GitTemporaryDirectory(ChdirTemporaryDirectory):
    """
    A temporary directory context manager with a git repository initialized.

    This extends ChdirTemporaryDirectory to also initialize a git repository
    in the temporary directory.
    """

    def __enter__(self) -> str:
        """Enter the context, create temp dir with git repo."""
        dname = super().__enter__()
        self.repo = make_repo(dname)
        return dname

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the context and cleanup."""
        del self.repo
        super().__exit__(exc_type, exc_val, exc_tb)


def make_repo(path: Optional[str] = None) -> Any:
    """
    Initialize a git repository in the specified path.

    Args:
        path: Directory path where to initialize the repo (default: current directory)

    Returns:
        The initialized git repository object
    """
    import git

    if not path:
        path = "."
    repo = git.Repo.init(path)
    repo.config_writer().set_value("user", "name", "Test User").release()
    repo.config_writer().set_value("user", "email", "testuser@example.com").release()

    return repo


def is_image_file(file_name: Union[str, Path]) -> bool:
    """
    Check if the given file name has an image file extension.

    Args:
        file_name: The name of the file to check

    Returns:
        True if the file is an image, False otherwise
    """
    file_name = str(file_name)  # Convert file_name to string
    return any(file_name.endswith(ext) for ext in IMAGE_EXTENSIONS)


def safe_abs_path(res: Union[str, Path]) -> str:
    """
    Get an absolute path, safely returning a full (not 8.3) Windows path.

    Args:
        res: Path to resolve

    Returns:
        The resolved absolute path as a string
    """
    res = Path(res).resolve()
    return str(res)


def format_content(role: str, content: str) -> str:
    """
    Format message content with role prefix for each line.

    Args:
        role: The role (e.g., "user", "assistant") to prefix each line
        content: The message content to format

    Returns:
        Formatted content with role prefix on each line
    """
    formatted_lines = []
    for line in content.splitlines():
        formatted_lines.append(f"{role} {line}")
    return "\n".join(formatted_lines)


def format_messages(messages: List[Dict[str, Any]], title: Optional[str] = None) -> str:
    """
    Format a list of messages for display.

    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        title: Optional title to display at the top

    Returns:
        Formatted string representation of the messages
    """
    output = []
    if title:
        output.append(f"{title.upper()} {'*' * 50}")

    for msg in messages:
        output.append("-------")
        role = msg["role"].upper()
        content = msg.get("content")
        if isinstance(content, list):  # Handle list content (e.g., image messages)
            for item in content:
                if isinstance(item, dict):
                    for key, value in item.items():
                        if isinstance(value, dict) and "url" in value:
                            output.append(
                                f"{role} {key.capitalize()} URL: {value['url']}"
                            )
                        else:
                            output.append(f"{role} {key}: {value}")
                else:
                    output.append(f"{role} {item}")
        elif isinstance(content, str):  # Handle string content
            output.append(format_content(role, content))
        function_call = msg.get("function_call")
        if function_call:
            output.append(f"{role} Function Call: {function_call}")

    return "\n".join(output)


def show_messages(
    messages: List[Dict[str, Any]],
    title: Optional[str] = None,
    functions: Optional[Any] = None,
) -> None:
    """
    Display formatted messages to stdout.

    Args:
        messages: List of message dictionaries to display
        title: Optional title for the message display
        functions: Optional functions to dump for debugging
    """
    formatted_output = format_messages(messages, title)
    print(formatted_output)

    if functions:
        dump(functions)


def split_chat_history_markdown(
    text: str, include_tool: bool = False
) -> List[Dict[str, str]]:
    """
    Parse markdown-formatted chat history into structured messages.

    Args:
        text: The markdown text to parse
        include_tool: Whether to include tool messages in the output

    Returns:
        List of message dictionaries with 'role' and 'content' keys
    """
    messages = []
    user = []
    assistant = []
    tool = []
    lines = text.splitlines(keepends=True)

    def append_msg(role: str, lines: List[str]) -> None:
        lines = "".join(lines)
        if lines.strip():
            messages.append(dict(role=role, content=lines))

    for line in lines:
        if line.startswith("# "):
            continue
        if line.startswith("> "):
            append_msg("assistant", assistant)
            assistant = []
            append_msg("user", user)
            user = []
            tool.append(line[2:])
            continue

        if line.startswith("#### "):
            append_msg("assistant", assistant)
            assistant = []
            append_msg("tool", tool)
            tool = []

            content = line[5:]
            user.append(content)
            continue

        append_msg("user", user)
        user = []
        append_msg("tool", tool)
        tool = []

        assistant.append(line)

    append_msg("assistant", assistant)
    append_msg("user", user)

    if not include_tool:
        messages = [m for m in messages if m["role"] != "tool"]

    return messages


def get_pip_install(args: List[str]) -> List[str]:
    """
    Generate a pip install command with standard arguments.

    Args:
        args: Additional arguments to pass to pip install

    Returns:
        Complete pip install command as a list of strings
    """
    cmd = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--upgrade",
        "--upgrade-strategy",
        "only-if-needed",
    ]
    cmd += args
    return cmd


def run_install(cmd: List[str]) -> Tuple[bool, str]:
    """
    Run a pip install command with progress indication.

    Args:
        cmd: The pip install command to run

    Returns:
        Tuple of (success: bool, output: str)
    """
    print()
    print("Installing:", printable_shell_command(cmd))

    # First ensure pip is available
    ensurepip_cmd = [sys.executable, "-m", "ensurepip", "--upgrade"]
    try:
        subprocess.run(ensurepip_cmd, capture_output=True, check=False)
    except Exception:
        pass  # Continue even if ensurepip fails

    try:
        output = []
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            encoding=sys.stdout.encoding,
            errors="replace",
        )
        spinner = Spinner("Installing...")

        while True:
            char = process.stdout.read(1)
            if not char:
                break

            output.append(char)
            spinner.step()

        spinner.end()
        return_code = process.wait()
        output = "".join(output)

        if return_code == 0:
            print("Installation complete.")
            print()
            return True, output

    except subprocess.CalledProcessError as e:
        print(f"\nError running pip install: {e}")

    print("\nInstallation failed.\n")

    return False, output


def find_common_root(abs_fnames: List[str]) -> str:
    """
    Find the common root directory of a list of absolute file paths.

    Args:
        abs_fnames: List of absolute file paths

    Returns:
        The common root directory path
    """
    try:
        if len(abs_fnames) == 1:
            return safe_abs_path(os.path.dirname(list(abs_fnames)[0]))
        elif abs_fnames:
            return safe_abs_path(os.path.commonpath(list(abs_fnames)))
    except OSError:
        pass

    try:
        return safe_abs_path(os.getcwd())
    except FileNotFoundError:
        # Fallback if cwd is deleted
        return "."


def format_tokens(count: int) -> str:
    """
    Format a token count for display.

    Args:
        count: Number of tokens

    Returns:
        Formatted string (e.g., "1.5k", "10k")
    """
    if count < 1000:
        return f"{count}"
    elif count < 10000:
        return f"{count / 1000:.1f}k"
    else:
        return f"{round(count / 1000)}k"


def touch_file(fname: Union[str, Path]) -> bool:
    """
    Create a file and its parent directories if they don't exist.

    Args:
        fname: Path to the file to create

    Returns:
        True if successful, False otherwise
    """
    fname = Path(fname)
    try:
        fname.parent.mkdir(parents=True, exist_ok=True)
        fname.touch()
        return True
    except OSError:
        return False


def check_pip_install_extra(
    io,
    module: Optional[str],
    prompt: Optional[str],
    pip_install_cmd: List[str],
    self_update: bool = False,
) -> Optional[bool]:
    """
    Check if a module is installed and offer to install it if not.

    Args:
        io: Input/output interface
        module: Module name to check (None to just run install)
        prompt: Warning message to show before prompting for install
        pip_install_cmd: Command arguments for pip install
        self_update: Whether this is a self-update operation

    Returns:
        True if module is available, False if installation failed, None if user declined

    Raises:
        DependencyError: If dependency installation fails critically
        NetworkError: If pip install fails due to network issues
    """
    if module:
        try:
            __import__(module)
            return True
        except (ImportError, ModuleNotFoundError, RuntimeError):
            pass

    cmd = get_pip_install(pip_install_cmd)

    if prompt:
        io.tool_warning(prompt)

    if self_update and platform.system() == "Windows":
        io.tool_output("Run this command to update:")
        print()
        print(printable_shell_command(cmd))  # plain print so it doesn't line-wrap
        return

    if not io.confirm_ask(
        "Run pip install?", default="y", subject=printable_shell_command(cmd)
    ):
        return

    try:
        success, output = run_install(cmd)
        if success:
            if not module:
                return True
            try:
                __import__(module)
                return True
            except (ImportError, ModuleNotFoundError, RuntimeError) as err:
                io.tool_error(str(err))
                return False
        else:
            io.tool_error(output)
            print()
            print("Install failed, try running this command manually:")
            print(printable_shell_command(cmd))
            return False
    except subprocess.CalledProcessError as e:
        raise NetworkError(
            f"Failed to install dependency: {e}", package_name=module or "unknown"
        ) from e
    except Exception as e:
        raise DependencyError(
            f"Failed to install dependency: {e}", package_name=module or "unknown"
        ) from e


def printable_shell_command(cmd_list: List[str]) -> str:
    """
    Convert a list of command arguments to a properly shell-escaped string.
    Args:
        cmd_list: List of command arguments

    Returns:
        Shell-escaped command string
    """
    return oslex.join(cmd_list)
