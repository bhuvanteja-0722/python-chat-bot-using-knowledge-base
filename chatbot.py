"""A small command-line Python question-answering chatbot."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class KnowledgeEntry:
    question: str
    answer: str
    keywords: tuple[str, ...]
    aliases: tuple[str, ...] = ()


KNOWLEDGE_BASE = (
    KnowledgeEntry(
        "What is Python?",
        "Python is a high-level, general-purpose programming language known for readable syntax and a large standard library.",
        ("python", "language", "programming"), ("what is python", "about python"),
    ),
    KnowledgeEntry(
        "How do I define a function?",
        "Use `def`, followed by the function name, parentheses, and a colon. Indent the function body:\n\n```python\ndef greet(name):\n    return f\"Hello, {name}!\"\n```",
        ("function", "define", "def", "parameter", "return"), ("create a function", "write a function"),
    ),
    KnowledgeEntry(
        "What are Python lists?",
        "A list is an ordered, mutable collection. Create one with square brackets, such as `numbers = [1, 2, 3]`. Use `append()` to add an item and indexing like `numbers[0]` to access one.",
        ("list", "lists", "append", "mutable", "collection"), ("python array", "add to a list"),
    ),
    KnowledgeEntry(
        "What is a dictionary?",
        "A dictionary stores key-value pairs. For example, `person = {\"name\": \"Ada\"}` and `person[\"name\"]` returns `\"Ada\"`. Use `person.get(\"age\")` when a key may be missing.",
        ("dictionary", "dict", "key", "value", "mapping"), ("key value", "hash map"),
    ),
    KnowledgeEntry(
        "How do for loops work?",
        "A `for` loop iterates over items in an iterable:\n\n```python\nfor item in [\"a\", \"b\"]:\n    print(item)\n```\nUse `range(n)` when you need a sequence of numbers.",
        ("for", "loop", "iterate", "iteration", "range"), ("repeat code", "iterate over"),
    ),
    KnowledgeEntry(
        "How do while loops work?",
        "A `while` loop repeats as long as its condition is true:\n\n```python\ncount = 0\nwhile count < 3:\n    print(count)\n    count += 1\n```\nMake sure the condition eventually becomes false to avoid an infinite loop.",
        ("while", "loop", "condition", "repeat"), ("while loop", "infinite loop"),
    ),
    KnowledgeEntry(
        "How do I handle exceptions?",
        "Use `try` and `except` to handle expected errors. Catch a specific exception when possible:\n\n```python\ntry:\n    number = int(text)\nexcept ValueError:\n    print(\"Please enter a whole number.\")\n```",
        ("exception", "error", "try", "except", "handling"), ("catch an error", "error handling"),
    ),
    KnowledgeEntry(
        "What are Python modules and imports?",
        "A module is a Python file that can be reused in another file. Load it with `import`, for example `import math` or `from pathlib import Path`.",
        ("module", "import", "package", "library"), ("use a library", "importing"),
    ),
    KnowledgeEntry(
        "How do I create a class?",
        "Define a class with `class`. The `__init__` method initializes each instance, and `self` refers to that instance:\n\n```python\nclass Dog:\n    def __init__(self, name):\n        self.name = name\n```",
        ("class", "object", "oop", "init", "self", "instance"), ("object oriented", "create an object"),
    ),
    KnowledgeEntry(
        "What is a tuple?",
        "A tuple is an ordered, immutable collection. Write one with parentheses, for example `point = (3, 4)`. Tuples are useful for fixed groups of values.",
        ("tuple", "immutable", "parentheses"), ("tuples",),
    ),
    KnowledgeEntry(
        "How do I use a set?",
        "A set holds unique values and is useful for removing duplicates or checking membership. Create one with `colors = {\"red\", \"blue\"}`; use `set()` for an empty set.",
        ("set", "unique", "duplicate", "membership"), ("remove duplicates",),
    ),
    KnowledgeEntry(
        "How do I read a file?",
        "Use `open()` with a context manager so the file closes automatically:\n\n```python\nfrom pathlib import Path\ntext = Path(\"notes.txt\").read_text(encoding=\"utf-8\")\n```\nFor line-by-line processing, iterate over the opened file.",
        ("file", "read", "open", "path", "text"), ("read a file", "load a file"),
    ),
    KnowledgeEntry(
        "What is a list comprehension?",
        "A list comprehension builds a list from an iterable in a compact way. For example, `[n * n for n in range(5)]` produces `[0, 1, 4, 9, 16]`.",
        ("comprehension", "list", "compact", "square"), ("list comprehension",),
    ),
    KnowledgeEntry(
        "How do I install a Python package?",
        "Install packages with pip, preferably inside a virtual environment: `python -m venv .venv`, activate it, then run `python -m pip install package-name`.",
        ("install", "package", "pip", "venv", "virtual", "environment"), ("pip install", "add a library"),
    ),
    KnowledgeEntry(
        "How do I check a Python value's type?",
        "Call `type(value)` to inspect its type. For type checks in conditional code, `isinstance(value, SomeType)` is usually more flexible.",
        ("type", "typeof", "isinstance", "data type"), ("check the type",),
    ),
)

STOP_WORDS = {"a", "an", "and", "are", "can", "do", "does", "for", "how", "i", "in", "is", "it", "of", "the", "to", "what", "with", "you", "your"}


def normalize(text: str) -> list[str]:
    """Return lowercase words, treating common Python terms consistently."""
    return re.findall(r"[a-z0-9_]+", text.lower())


def find_answer(question: str) -> str:
    """Find the best matching knowledge entry using phrase and keyword scoring."""
    words = set(normalize(question)) - STOP_WORDS
    if not words:
        return "Please ask a Python question, such as ‘How do I define a function?’"

    question_normalized = " ".join(normalize(question))
    best_entry: KnowledgeEntry | None = None
    best_score = 0.0

    for entry in KNOWLEDGE_BASE:
        keywords = set(entry.keywords)
        overlap = words & keywords
        score = len(overlap) / max(1, len(words))
        for phrase in entry.aliases:
            phrase_words = " ".join(normalize(phrase))
            if phrase_words and phrase_words in question_normalized:
                score += 1.0
        if score > best_score:
            best_score = score
            best_entry = entry

    if best_entry is None or best_score < 0.25:
        return ("I don't have a confident answer for that yet. I can help with Python functions, collections, loops, "
                "exceptions, modules, classes, files, packages, and types. Try asking about one of those topics.")
    return best_entry.answer


def main() -> None:
    print("Python Q&A Chatbot")
    print("Ask a Python question, or type 'quit' to exit.\n")
    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBot: Goodbye!")
            break
        if question.lower() in {"quit", "exit", "q"}:
            print("Bot: Goodbye!")
            break
        print(f"Bot: {find_answer(question)}\n")


if __name__ == "__main__":
    main()
