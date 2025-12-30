# Coder Reference: AskCoder

The `AskCoder` is the simplest possible implementation of a `Coder`. Its purpose is not to edit code, but to answer questions about the code provided in the chat context. It's a useful example for understanding the minimal requirements for creating a new coder.

## How it Works

The `AskCoder` is defined in `llmcode/coders/ask_coder.py`:

```python
from .ask_prompts import AskPrompts
from .base_coder import Coder


class AskCoder(Coder):
    """Ask questions about code without making any changes."""

    edit_format = "ask"
    gpt_prompts = AskPrompts()
```

This class does only two things:

1.  It sets the `edit_format` to `"ask"`.
2.  It assigns a custom prompt container, `AskPrompts`, to `gpt_prompts`.

### `edit_format`

The `edit_format` is a string that uniquely identifies the coder. When the user runs `llmcode` with `/coder ask` or has `edit_format: ask` in their `.llmcode.yaml` config file, the `Coder.create()` factory method will find and instantiate `AskCoder`.

### `gpt_prompts`

This property holds an instance of a class that inherits from `CoderPrompts`. It contains all the prompt snippets that will be used to construct the final system prompt sent to the LLM.

For `AskCoder`, the prompts are defined in `llmcode/coders/ask_prompts.py`:

```python
from .base_prompts import CoderPrompts

class AskPrompts(CoderPrompts):
    main_system = """Act as an expert code analyst.
Answer questions about the supplied code.
Always reply to the user in {language}.

If you need to describe code changes, do so *briefly*.
"""
    # ... other prompt snippets
```

The `main_system` prompt is the most important one. As you can see, it instructs the model to "Act as an expert code analyst" and "Answer questions about the supplied code". It does *not* include any instructions for how to format or apply edits, which is why this coder won't try to change your files.

## Creating Your Own Coder

To create your own coder, you can follow the `AskCoder` example:

1.  Create a new `your_coder_prompts.py` file and define a class that inherits from `CoderPrompts`. Customize the `main_system` prompt and other snippets for your needs.
2.  Create a new `your_coder.py` file.
3.  In `your_coder.py`, define a class that inherits from `Coder`.
4.  Set a unique `edit_format` string.
5.  Set the `gpt_prompts` property to an instance of your new prompts class.
6.  If your coder needs to parse LLM output or apply changes in a unique way, you can override methods from `BaseCoder` like `get_edits()` or `apply_edits()`. For a simple conversational coder, this is not necessary.
7.  Make sure your new coder is imported in `llmcode/coders/__init__.py`.
