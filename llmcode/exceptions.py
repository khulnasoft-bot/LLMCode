from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from llmcode.dump import dump  # noqa: F401


@dataclass
class ExInfo:
    name: str
    retry: bool
    description: str


EXCEPTIONS = [
    ExInfo("APIConnectionError", True, None),
    ExInfo("APIError", True, None),
    ExInfo("APIResponseValidationError", True, None),
    ExInfo(
        "AuthenticationError",
        False,
        "The API provider is not able to authenticate you. Check your API key.",
    ),
    ExInfo("AzureOpenAIError", True, None),
    ExInfo("BadRequestError", False, None),
    ExInfo("BudgetExceededError", True, None),
    ExInfo(
        "ContentPolicyViolationError",
        True,
        "The API provider has refused the request due to a safety policy about the content.",
    ),
    ExInfo(
        "ContextWindowExceededError", False, None
    ),  # special case handled in base_coder
    ExInfo(
        "InternalServerError",
        True,
        "The API provider's servers are down or overloaded.",
    ),
    ExInfo("InvalidRequestError", True, None),
    ExInfo("JSONSchemaValidationError", True, None),
    ExInfo("NotFoundError", False, None),
    ExInfo("OpenAIError", True, None),
    ExInfo(
        "RateLimitError",
        True,
        "The API provider has rate limited you. Try again later or check your quotas.",
    ),
    ExInfo("RouterRateLimitError", True, None),
    ExInfo(
        "ServiceUnavailableError",
        True,
        "The API provider's servers are down or overloaded.",
    ),
    ExInfo("UnprocessableEntityError", True, None),
    ExInfo("UnsupportedParamsError", True, None),
    ExInfo(
        "Timeout",
        True,
        "The API provider timed out without returning a response. They may be down or overloaded.",
    ),
]


class LlmcodeError(Exception):
    """
    Base exception class for all llmcode-specific errors.

    This serves as the root exception for all application-specific errors
    that are not related to external API provider issues.
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the LlmcodeError.

        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error context
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConfigurationError(LlmcodeError):
    """
    Raised when there's an issue with llmcode configuration.

    This includes problems with config files, environment variables,
    API keys, model settings, and other configuration-related issues.
    """

    def __init__(
        self, message: str, config_key: Optional[str] = None, **kwargs: Any
    ) -> None:
        """
        Initialize the ConfigurationError.

        Args:
            message: Human-readable error message
            config_key: The configuration key that caused the issue
            **kwargs: Additional context information
        """
        super().__init__(message, kwargs)
        self.config_key = config_key
        if config_key:
            self.details["config_key"] = config_key


class ModelError(LlmcodeError):
    """
    Raised when there's an issue with model configuration or usage.

    This includes problems with model selection, model settings,
    model compatibility, and model-specific operations.
    """

    def __init__(
        self, message: str, model_name: Optional[str] = None, **kwargs: Any
    ) -> None:
        """
        Initialize the ModelError.

        Args:
            message: Human-readable error message
            model_name: The model that caused the issue
            **kwargs: Additional context information
        """
        super().__init__(message, kwargs)
        self.model_name = model_name
        if model_name:
            self.details["model_name"] = model_name


class RepositoryError(LlmcodeError):
    """
    Raised when there's an issue with git repository operations.

    This includes problems with repository initialization, file tracking,
    git operations, and repository state management.
    """

    def __init__(
        self, message: str, repo_path: Optional[str] = None, **kwargs: Any
    ) -> None:
        """
        Initialize the RepositoryError.

        Args:
            message: Human-readable error message
            repo_path: Path to the repository that caused the issue
            **kwargs: Additional context information
        """
        super().__init__(message, kwargs)
        self.repo_path = repo_path
        if repo_path:
            self.details["repo_path"] = repo_path


class FileOperationError(LlmcodeError):
    """
    Raised when there's an issue with file operations.

    This includes problems with reading, writing, creating, or
    manipulating files in the project.
    """

    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the FileOperationError.

        Args:
            message: Human-readable error message
            file_path: Path to the file that caused the issue
            operation: The operation that was being performed
            **kwargs: Additional context information
        """
        super().__init__(message, kwargs)
        self.file_path = file_path
        self.operation = operation
        if file_path:
            self.details["file_path"] = file_path
        if operation:
            self.details["operation"] = operation


class ValidationError(LlmcodeError):
    """
    Raised when input validation fails.

    This includes problems with argument validation, data validation,
    and other forms of input checking.
    """

    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        value: Any = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the ValidationError.

        Args:
            message: Human-readable error message
            field_name: The field that failed validation
            value: The invalid value that was provided
            **kwargs: Additional context information
        """
        super().__init__(message, kwargs)
        self.field_name = field_name
        self.value = value
        if field_name:
            self.details["field_name"] = field_name
        if value is not None:
            self.details["value"] = str(value)


class DependencyError(LlmcodeError):
    """
    Raised when there's an issue with required dependencies.

    This includes problems with missing packages, incompatible versions,
    and dependency installation failures.
    """

    def __init__(
        self,
        message: str,
        package_name: Optional[str] = None,
        required_version: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the DependencyError.

        Args:
            message: Human-readable error message
            package_name: The package that caused the issue
            required_version: The minimum required version
            **kwargs: Additional context information
        """
        super().__init__(message, kwargs)
        self.package_name = package_name
        self.required_version = required_version
        if package_name:
            self.details["package_name"] = package_name
        if required_version:
            self.details["required_version"] = required_version


class NetworkError(LlmcodeError):
    """
    Raised when there's a network-related issue.

    This includes problems with network connectivity, SSL/TLS issues,
    and network timeout problems.
    """

    def __init__(self, message: str, url: Optional[str] = None, **kwargs: Any) -> None:
        """
        Initialize the NetworkError.

        Args:
            message: Human-readable error message
            url: The URL that was being accessed
            **kwargs: Additional context information
        """
        super().__init__(message, kwargs)
        self.url = url
        if url:
            self.details["url"] = url


class ProjectPermissionError(LlmcodeError):
    """
    Raised when there's a permission issue related to a project in Vertex AI.

    This includes problems with authentication, authorization, or
    insufficient permissions for the specified project.
    """

    def __init__(
        self,
        message: str,
        project_id: Optional[str] = None,
        permission: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the ProjectPermissionError.

        Args:
            message: Human-readable error message
            project_id: The project ID that caused the permission issue
            permission: The specific permission that was missing
            **kwargs: Additional context information
        """
        super().__init__(message, kwargs)
        self.project_id = project_id
        self.permission = permission
        if project_id:
            self.details["project_id"] = project_id
        if permission:
            self.details["permission"] = permission


class LiteLLMExceptions:
    exceptions = dict()
    exception_info = {exi.name: exi for exi in EXCEPTIONS}

    def __init__(self):
        self._load()

    def _load(self, strict=False):
        import litellm

        for var in dir(litellm):
            if var.endswith("Error"):
                if var not in self.exception_info:
                    raise ValueError(
                        f"{var} is in litellm but not in llmcode's exceptions list"
                    )

        for var in self.exception_info:
            ex = getattr(litellm, var)
            self.exceptions[ex] = self.exception_info[var]

    def exceptions_tuple(self):
        return tuple(self.exceptions)

    def get_ex_info(self, ex):
        """Return the ExInfo for a given exception instance"""
        import litellm

        if ex.__class__ is litellm.APIConnectionError:
            if "google.auth" in str(ex):
                return ExInfo(
                    "APIConnectionError",
                    False,
                    "You need to: pip install google-generativeai",
                )
            if "boto3" in str(ex):
                return ExInfo(
                    "APIConnectionError", False, "You need to: pip install boto3"
                )
            if "OpenrouterException" in str(ex) and "'choices'" in str(ex):
                return ExInfo(
                    "APIConnectionError",
                    True,
                    (
                        "OpenRouter or the upstream API provider is down, overloaded or rate"
                        " limiting your requests."
                    ),
                )

        # Check for specific non-retryable APIError cases like insufficient credits
        if ex.__class__ is litellm.APIError:
            err_str = str(ex).lower()
            if "insufficient credits" in err_str and '"code":402' in err_str:
                return ExInfo(
                    "APIError",
                    False,
                    "Insufficient credits with the API provider. Please add credits.",
                )
            # Fall through to default APIError handling if not the specific credits error

        return self.exceptions.get(ex.__class__, ExInfo(None, None, None))
