import importlib
import os
import warnings

from llmcode.dump import dump  # noqa: F401
from llmcode.exceptions import ProjectPermissionError

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

LLMCODE_SITE_URL = "https://llm.khulnasoft.com"
LLMCODE_APP_NAME = "Llmcode"

os.environ["OR_SITE_URL"] = LLMCODE_SITE_URL
os.environ["OR_APP_NAME"] = LLMCODE_APP_NAME
os.environ["LITELLM_MODE"] = "PRODUCTION"

# `import litellm` takes 1.5 seconds, defer it!

VERBOSE = False


class LazyLiteLLM:
    _lazy_module = None
    _vertex_prompt_management = None  # Placeholder for vertex prompt management

    def __getattr__(self, name):
        if name == "_lazy_module":
            return super()
        self._load_litellm()
        return getattr(self._lazy_module, name)

    def _load_litellm(self):
        if self._lazy_module is not None:
            return

        if VERBOSE:
            print("Loading litellm...")

        self._lazy_module = importlib.import_module("litellm")
        # Initialize _vertex_prompt_management here
        self._vertex_prompt_management = self._lazy_module.vertex_prompt_management

        self._lazy_module.suppress_debug_info = True
        self._lazy_module.set_verbose = False
        self._lazy_module.drop_params = True
        self._lazy_module._logging._disable_debugging()


litellm = LazyLiteLLM()

import json


def _handle_list_prompts(
    display_name: str | None = None,
    project_id: str | None = None,
    location_id: str | None = None,
    page_size: int = 10,
) -> list[dict]:
    try:
        response = litellm._vertex_prompt_management.list_prompts(
            display_name=display_name,
            project_id=project_id,
            location_id=location_id,
            page_size=page_size,
        )
        return json.loads(response) if isinstance(response, str) else response
    except Exception as e:
        if "Permission denied" in str(e) and project_id:
            raise ProjectPermissionError(
                f"Permission denied on project '{project_id}'.", project_id=project_id
            ) from e
        raise


def _handle_read_prompt(
    prompt_id: str, project_id: str | None = None, location_id: str | None = None
) -> dict:
    try:
        response = litellm._vertex_prompt_management.read_prompt(
            prompt_id=prompt_id, project_id=project_id, location_id=location_id
        )
        return json.loads(response) if isinstance(response, str) else response
    except Exception as e:
        if "Permission denied" in str(e) and project_id:
            raise ProjectPermissionError(
                f"Permission denied on project '{project_id}'.", project_id=project_id
            ) from e
        raise


def _handle_create_prompt(
    content: str,
    system_instruction: str,
    model: str,
    display_name: str,
    project_id: str | None = None,
    location_id: str | None = None,
) -> dict:
    try:
        response = litellm._vertex_prompt_management.create_prompt(
            content=content,
            system_instruction=system_instruction,
            model=model,
            display_name=display_name,
            project_id=project_id,
            location_id=location_id,
        )
        return json.loads(response) if isinstance(response, str) else response
    except Exception as e:
        if "Permission denied" in str(e) and project_id:
            raise ProjectPermissionError(
                f"Permission denied on project '{project_id}'.", project_id=project_id
            ) from e
        raise


def _handle_update_prompt(
    prompt_id: str,
    content: str | None = None,
    system_instruction: str | None = None,
    model: str | None = None,
    project_id: str | None = None,
    location_id: str | None = None,
) -> dict:
    try:
        response = litellm._vertex_prompt_management.update_prompt(
            prompt_id=prompt_id,
            content=content,
            system_instruction=system_instruction,
            model=model,
            project_id=project_id,
            location_id=location_id,
        )
        return json.loads(response) if isinstance(response, str) else response
    except Exception as e:
        if "Permission denied" in str(e) and project_id:
            raise ProjectPermissionError(
                f"Permission denied on project '{project_id}'.", project_id=project_id
            ) from e
        raise


def _handle_delete_prompt(
    prompt_id: str, project_id: str | None = None, location_id: str | None = None
) -> dict:
    try:
        response = litellm._vertex_prompt_management.delete_prompt(
            prompt_id=prompt_id, project_id=project_id, location_id=location_id
        )
        return json.loads(response) if isinstance(response, str) else response
    except Exception as e:
        if "Permission denied" in str(e) and project_id:
            raise ProjectPermissionError(
                f"Permission denied on project '{project_id}'.", project_id=project_id
            ) from e
        raise


__all__ = [
    litellm,
    _handle_list_prompts,
    _handle_read_prompt,
    _handle_create_prompt,
    _handle_update_prompt,
    _handle_delete_prompt,
]
