"""Language table for the fallback syntax highlighter (py/js/c/md + more)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Language:
    name: str
    extensions: tuple
    keywords: tuple
    line_comments: tuple = ("#",)
    block_comments: tuple = ()
    strings: tuple = ('"', "'")
    tab_width: int = 4


LANGUAGES = {
    "python": Language(
        name="Python",
        extensions=(".py", ".pyi"),
        keywords=(
            "and", "as", "assert", "async", "await", "break", "class", "continue",
            "def", "del", "elif", "else", "except", "finally", "for", "from",
            "global", "if", "import", "in", "is", "lambda", "nonlocal", "not",
            "or", "pass", "raise", "return", "try", "while", "with", "yield",
            "True", "False", "None", "self",
        ),
        line_comments=("#",),
    ),
    "javascript": Language(
        name="JavaScript",
        extensions=(".js", ".mjs", ".cjs", ".ts", ".jsx", ".tsx"),
        keywords=(
            "async", "await", "break", "case", "catch", "class", "const",
            "continue", "debugger", "default", "delete", "do", "else", "export",
            "extends", "finally", "for", "function", "if", "import", "in",
            "instanceof", "let", "new", "of", "return", "static", "super",
            "switch", "this", "throw", "try", "typeof", "var", "void", "while",
            "yield", "true", "false", "null", "undefined",
        ),
        line_comments=("//",),
        block_comments=(("/*", "*/"),),
    ),
    "c": Language(
        name="C",
        extensions=(".c", ".h", ".cpp", ".cc", ".hpp", ".cxx"),
        keywords=(
            "auto", "break", "case", "char", "const", "continue", "default",
            "do", "double", "else", "enum", "extern", "float", "for", "goto",
            "if", "inline", "int", "long", "register", "restrict", "return",
            "short", "signed", "sizeof", "static", "struct", "switch", "typedef",
            "union", "unsigned", "void", "volatile", "while", "NULL",
        ),
        line_comments=("//",),
        block_comments=(("/*", "*/"),),
    ),
    "markdown": Language(
        name="Markdown",
        extensions=(".md", ".markdown"),
        keywords=(),
        line_comments=(),
        strings=(),
    ),
    "shell": Language(
        name="Shell",
        extensions=(".sh", ".bash"),
        keywords=(
            "if", "then", "else", "elif", "fi", "for", "while", "do", "done",
            "case", "esac", "function", "return", "local", "export", "source",
            "echo", "exit", "set", "unset", "trap",
        ),
        line_comments=("#",),
    ),
    "json": Language(
        name="JSON",
        extensions=(".json",),
        keywords=("true", "false", "null"),
        line_comments=(),
        strings=('"',),
    ),
}

EXTENSION_MAP = {
    ext: lang for lang in LANGUAGES.values() for ext in lang.extensions
}


def language_for_path(path) -> Language | None:
    from pathlib import Path

    return EXTENSION_MAP.get(Path(path).suffix.lower())


@dataclass
class HighlightPalette:
    """Colors derived from the Aether theme for dark code backgrounds."""

    keyword: str = "#e29163"
    string: str = "#a5c3a5"
    comment: str = "#8f8a80"
    number: str = "#9db8d6"
    heading: str = "#ffffff"
    default_fg: str = "#e9e3d9"
    tag_names: tuple = field(default=("keyword", "string", "comment", "number", "heading"))
