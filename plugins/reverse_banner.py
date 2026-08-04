"""
Example Plugin: reverse_banner
==============================
A simple demo plugin that reverses the characters on each line of the ASCII art.

Each plugin must expose a top-level `render(text, **kwargs)` function that
returns the rendered string.
"""

import pyfiglet


def render(text: str, font: str = "banner3", **kwargs) -> str:
    """
    Render text as ASCII art with each line reversed.

    Args:
        text: The text to render.
        font: pyfiglet font name.

    Returns:
        ASCII art string with each line reversed.
    """
    art = pyfiglet.figlet_format(text, font=font)
    reversed_lines = [line[::-1] for line in art.splitlines()]
    return "\n".join(reversed_lines)
