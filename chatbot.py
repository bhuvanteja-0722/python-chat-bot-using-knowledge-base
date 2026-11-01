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
    KnowledgeEntry(
        "What is an integer in Python?",
        "An integer (`int`) is a whole number with no fractional part, such as `7`, `0`, or `-12`. Python integers can grow beyond fixed machine sizes. Convert compatible text with `int(\"42\")`.",
        ("int", "integer", "integers", "whole", "number", "numbers"), ("what is int", "python int", "integer type"),
    ),
    KnowledgeEntry(
        "What is a string in Python?",
        "A string (`str`) is text. Write it inside single or double quotes, for example `name = \"Ada\"`. Strings are immutable; use methods such as `name.upper()` to create a changed result. Convert a value to text with `str(value)`.",
        ("str", "string", "strings", "text", "character", "characters"), ("what is str", "python str", "string type"),
    ),
    KnowledgeEntry(
        "What is a float in Python?",
        "A float (`float`) represents a number with a decimal part, such as `3.14` or `-0.5`. For exact decimal arithmetic such as money, consider Python's `decimal.Decimal` instead.",
        ("float", "floats", "decimal", "fractional"), ("what is float", "floating point", "float type"),
    ),
    KnowledgeEntry(
        "What is a boolean in Python?",
        "A boolean (`bool`) represents a truth value: `True` or `False`. Comparisons such as `age >= 18` produce booleans, which are commonly used in `if` statements.",
        ("bool", "boolean", "booleans", "true", "false", "truth"), ("what is bool", "boolean type"),
    ),
    KnowledgeEntry(
        "What does None mean in Python?",
        "`None` represents the absence of a value. A function that reaches the end without a `return` statement returns `None`. Check it with `value is None`.",
        ("none", "null", "absence", "nothing"), ("what is none", "none type", "python null"),
    ),
    KnowledgeEntry("What is a variable?", "A variable is a name bound to a value. Assign with `=`: `score = 10`. Python is dynamically typed, so a name can later refer to a value of another type.", ("variable", "variables", "assignment", "assign", "name"), ("create a variable", "declare a variable")),
    KnowledgeEntry("How do comments work?", "Use `#` for a one-line comment. A docstring is a string at the start of a module, class, or function that documents its behavior.", ("comment", "comments", "docstring", "documentation"), ("write a comment", "document a function")),
    KnowledgeEntry("How do if, elif, and else work?", "Use `if` to run code conditionally, `elif` for another condition, and `else` as the fallback. Indent each block:\n\n```python\nif score >= 90:\n    grade = \"A\"\nelif score >= 80:\n    grade = \"B\"\nelse:\n    grade = \"Keep practicing\"\n```", ("if", "elif", "else", "conditional", "condition"), ("if statement", "conditional statement")),
    KnowledgeEntry("What do break and continue do?", "`break` exits the nearest loop. `continue` skips to the next iteration. Use them when they make loop logic clearer; a helper function can sometimes be easier to read.", ("break", "continue", "skip", "exit", "loop"), ("break a loop", "continue a loop")),
    KnowledgeEntry("How do enumerate and zip work?", "`enumerate(items)` gives each item with its index, and `zip(a, b)` pairs items from iterables:\n\n```python\nfor index, name in enumerate(names, start=1):\n    print(index, name)\n\nfor name, score in zip(names, scores):\n    print(name, score)\n```", ("enumerate", "zip", "index", "pair", "iterable"), ("loop with index", "pair two lists")),
    KnowledgeEntry("How do I unpack values?", "Unpacking assigns items from an iterable to multiple names: `x, y = (3, 4)`. Use `first, *middle, last = values` to capture remaining items in a list.", ("unpack", "unpacking", "starred", "multiple assignment"), ("unpack a list", "unpack a tuple")),
    KnowledgeEntry("What are *args and **kwargs?", "In a function definition, `*args` collects extra positional arguments into a tuple and `**kwargs` collects extra named arguments into a dictionary. Use these when a function truly needs a flexible signature.", ("args", "kwargs", "positional", "keyword", "argument"), ("variable arguments", "arbitrary arguments")),
    KnowledgeEntry("What is a lambda function?", "A `lambda` creates a small anonymous function with one expression, such as `key=lambda item: item[1]`. For logic with multiple steps or a meaningful name, use `def` instead.", ("lambda", "anonymous", "inline", "function"), ("lambda function", "anonymous function")),
    KnowledgeEntry("What is recursion?", "Recursion is when a function calls itself. It needs a base case that stops the calls. For many tasks, a loop is simpler and avoids Python's recursion depth limit.", ("recursion", "recursive", "base case", "stack"), ("recursive function", "function call itself")),
    KnowledgeEntry("What is variable scope?", "A name assigned inside a function is local to that function unless declared `global` or `nonlocal`. Prefer passing values in and returning results instead of changing global state.", ("scope", "local", "global", "nonlocal", "name"), ("variable scope", "local variable", "global variable")),
    KnowledgeEntry("What is a generator?", "A generator produces values lazily, one at a time, which can save memory. Write a generator function with `yield`, or use a generator expression like `(n * n for n in range(10))`.", ("generator", "generators", "yield", "lazy", "iteration"), ("generator expression", "yield keyword")),
    KnowledgeEntry("What is an iterator?", "An iterator yields values one at a time. `iter(value)` gets an iterator and `next(iterator)` retrieves its next value. `for` loops handle this protocol automatically.", ("iterator", "iterators", "iter", "next", "iteration"), ("iteration protocol", "iter function")),
    KnowledgeEntry("What is a decorator?", "A decorator wraps or changes a function or class. The `@decorator` syntax applies it when the function is defined. Decorators are useful for reusable behavior such as logging or authorization.", ("decorator", "decorators", "wrapper", "wrap", "at sign"), ("python decorator", "function decorator")),
    KnowledgeEntry("What is a context manager?", "A context manager handles setup and cleanup around a block. Use `with`, for example `with open(\"notes.txt\") as file:`. It ensures resources are released even if an error occurs.", ("context", "manager", "with", "cleanup", "resource"), ("context manager", "with statement")),
    KnowledgeEntry("What is a dataclass?", "`dataclasses.dataclass` generates common methods such as `__init__` and `__repr__` for a class that mainly stores data:\n\n```python\nfrom dataclasses import dataclass\n\n@dataclass\nclass Point:\n    x: float\n    y: float\n```", ("dataclass", "dataclasses", "boilerplate", "record"), ("data class", "dataclass decorator")),
    KnowledgeEntry("What is inheritance?", "Inheritance lets a class reuse or specialize another class. Put the parent in parentheses, then call `super().__init__(...)` when the child needs the parent's initialization. Prefer composition when objects simply need to work together.", ("inheritance", "subclass", "parent", "super", "child", "object"), ("class inheritance", "inherit from a class")),
    KnowledgeEntry("What is a property?", "`@property` lets an attribute-style access run getter logic. It can be useful for derived values or validation, but ordinary public attributes are simpler when no extra behavior is needed.", ("property", "getter", "setter", "attribute", "property decorator"), ("python property", "property decorator")),
    KnowledgeEntry("What are dunder methods?", "Dunder methods have double underscores, such as `__init__`, `__str__`, and `__len__`. Python calls them to support object setup, display, and built-in operations. Implement them to make custom objects behave naturally.", ("dunder", "magic", "special", "__init__", "__str__", "method"), ("magic methods", "special methods")),
    KnowledgeEntry("What are type hints?", "Type hints document expected types and help editors and static checkers. They do not usually enforce types at runtime:\n\n```python\ndef greet(name: str) -> str:\n    return f\"Hello, {name}\"\n```", ("typing", "hint", "hints", "annotation", "annotations", "type"), ("type annotation", "function annotation")),
    KnowledgeEntry("How do match and case work?", "`match` and `case` compare a value against patterns, available in Python 3.10 and newer. They can make structured branching clearer; use ordinary `if` statements for simple conditions.", ("match", "case", "pattern", "structural"), ("pattern matching", "match case")),
    KnowledgeEntry("How do I raise an exception?", "Use `raise` to signal an error. Choose a specific built-in exception or define a custom one by subclassing `Exception`. Include a message that explains what went wrong.", ("raise", "custom", "exception", "error"), ("raise an error", "custom exception")),
    KnowledgeEntry("How do I use logging?", "Use the standard `logging` module instead of `print()` for application diagnostics. It supports levels such as `DEBUG`, `INFO`, `WARNING`, and `ERROR`, and can send messages to a file or console.", ("logging", "log", "logger", "debug", "diagnostic"), ("logging module", "log an error")),
    KnowledgeEntry("How do I work with JSON?", "Use `json.loads(text)` to parse JSON text and `json.dumps(value)` to produce JSON text. With files, use `json.load(file)` and `json.dump(value, file)`. JSON supports a limited set of data types.", ("json", "serialize", "serialization", "parse", "loads", "dumps"), ("read json", "write json", "json file")),
    KnowledgeEntry("How do I work with CSV files?", "Use Python's `csv` module. `csv.reader` reads rows and `csv.DictReader` maps columns by header. Open files with `newline=\"\"` and a specified encoding to handle CSV consistently.", ("csv", "comma", "spreadsheet", "row", "column"), ("read csv", "write csv", "csv file")),
    KnowledgeEntry("How do I work with paths?", "Use `pathlib.Path` to build and inspect filesystem paths. For example, `Path(\"data\") / \"input.txt\"` joins path parts in a platform-aware way. `Path.read_text()` and `write_text()` handle simple text files.", ("pathlib", "path", "paths", "directory", "filesystem"), ("path object", "join file paths")),
    KnowledgeEntry("How do I use regular expressions?", "The `re` module searches text using patterns. `re.search()` finds a match, `re.findall()` returns matches, and `re.sub()` replaces them. For simple fixed text, ordinary string methods are easier to read.", ("regex", "regular", "expression", "pattern", "re."), ("regular expression", "regex pattern")),
    KnowledgeEntry("How do I work with dates and times?", "Use `datetime.date` and `datetime.datetime` for dates and times, and `datetime.timedelta` for durations. Attach a timezone when representing real-world instants; naive datetimes can be ambiguous.", ("datetime", "date", "time", "timezone", "timedelta"), ("date and time", "python dates")),
    KnowledgeEntry("How do I generate random values?", "Use `random` for simulations and casual selection, such as `random.choice(items)`. For security-sensitive tokens or passwords, use the `secrets` module instead.", ("random", "randomness", "choice", "shuffle", "secure", "secrets"), ("random number", "random values")),
    KnowledgeEntry("What is the collections module?", "`collections` provides useful container types: `Counter` counts items, `defaultdict` supplies missing values, `deque` supports fast operations at both ends, and `namedtuple` creates tuple-like records.", ("collections", "counter", "defaultdict", "deque", "namedtuple"), ("collections module", "count items")),
    KnowledgeEntry("What are itertools and functools?", "`itertools` offers efficient iterator building blocks such as `chain`, `product`, and `islice`. `functools` includes tools such as `lru_cache`, `partial`, and `reduce`. Both are part of the standard library.", ("itertools", "functools", "chain", "product", "lru_cache", "partial"), ("iterator tools", "cache a function")),
    KnowledgeEntry("How do I create a command-line argument parser?", "Use `argparse` to define command-line options, validate input, and generate help text. Create an `ArgumentParser`, add arguments, then call `parse_args()`.", ("argparse", "command", "line", "cli", "argument", "parser"), ("command line arguments", "cli arguments")),
    KnowledgeEntry("How do I use SQLite?", "Python includes the `sqlite3` module for local SQL databases. Use parameterized queries such as `connection.execute(\"SELECT ... WHERE id = ?\", (record_id,))`; never build SQL by concatenating untrusted input.", ("sqlite", "sqlite3", "sql", "database", "query"), ("sqlite database", "python database")),
    KnowledgeEntry("How do I make an HTTP request?", "For simple HTTP requests with no third-party dependencies, use `urllib.request`. For larger applications, popular packages such as `requests` can offer a friendlier interface. Handle timeouts and network errors.", ("http", "https", "request", "urllib", "api", "network"), ("http request", "call an api", "web request")),
    KnowledgeEntry("How do I use threads or processes?", "Threads are useful for I/O-bound work; processes can run CPU-bound Python work in parallel. The `threading` and `multiprocessing` modules provide these tools. Start with a simple sequential solution and measure before adding concurrency.", ("thread", "threading", "process", "multiprocessing", "parallel", "concurrency"), ("run in parallel", "concurrent tasks")),
    KnowledgeEntry("How do I use async and await?", "`async def` defines a coroutine, `await` pauses it until an asynchronous operation completes, and `asyncio` runs coroutines. Async is most useful for programs that wait on many network or other I/O operations.", ("async", "await", "asyncio", "coroutine", "asynchronous"), ("async function", "async programming")),
    KnowledgeEntry("How do I write tests?", "Python's standard library includes `unittest`. Write small tests for expected behavior and edge cases, then run them with `python -m unittest`. `pytest` is a popular third-party alternative with a simpler test syntax.", ("test", "tests", "testing", "unittest", "pytest", "assert"), ("write a test", "run tests", "unit test")),
    KnowledgeEntry("How do I debug Python code?", "Use the traceback to find the line where an error occurred. Add a focused test or inspect values with a debugger such as `pdb`; avoid leaving temporary prints in production code. Reproduce the smallest failing case first.", ("debug", "debugging", "traceback", "pdb", "error"), ("debug a program", "debug code")),
    KnowledgeEntry("How do I use a virtual environment?", "Create an isolated environment with `python -m venv .venv`, activate it for your shell, then install packages using `python -m pip install ...`. This keeps project dependencies separate from other Python projects.", ("venv", "virtual", "environment", "isolate", "activate"), ("virtualenv", "create an environment")),
    KnowledgeEntry("How do I manage Python dependencies?", "Install a package with `python -m pip install package-name`. Record dependencies in a project file such as `requirements.txt` or `pyproject.toml`, and use a virtual environment so installs stay isolated.", ("dependency", "dependencies", "requirements", "pyproject", "pip", "package"), ("requirements file", "manage packages")),
    KnowledgeEntry("What is PEP 8?", "PEP 8 is Python's style guide. It recommends consistent indentation, readable names, and formatting that makes code easy to scan. Many teams automate formatting and lint checks to apply shared conventions.", ("pep", "pep8", "style", "format", "lint", "readability"), ("python style guide", "code style")),
    KnowledgeEntry("What are Python's built-in functions?", "Python includes built-ins such as `len`, `range`, `sum`, `min`, `max`, `sorted`, `enumerate`, and `zip`. They are available without an import. Use `help(name)` or the official docs to explore one.", ("builtin", "builtins", "built-in", "function", "functions", "len", "sum"), ("built in functions", "python builtins")),
    KnowledgeEntry("How do I use map and filter?", "`map(function, values)` transforms each item, while `filter(function, values)` keeps items that pass a condition. List comprehensions are often more readable for simple cases.", ("map", "filter", "transform", "functional"), ("map function", "filter function")),
    KnowledgeEntry("What is a shallow or deep copy?", "Assignment creates another reference to the same object, not a copy. `copy.copy()` makes a shallow copy; `copy.deepcopy()` recursively copies nested objects. Prefer immutable values or explicit construction when that is clearer.", ("copy", "shallow", "deepcopy", "reference", "mutable"), ("deep copy", "shallow copy")),
    KnowledgeEntry("How does Python manage memory?", "Python manages object memory automatically, including reference counting and a garbage collector for reference cycles. Usually you should focus on releasing external resources with context managers rather than manually freeing objects.", ("memory", "garbage", "collector", "reference", "leak"), ("garbage collection", "memory management")),
    KnowledgeEntry("Is eval safe in Python?", "Avoid `eval()` and `exec()` on untrusted input: they can execute arbitrary Python code. Use safer parsers such as `json.loads()` for JSON or validate input against the exact format you expect.", ("eval", "exec", "security", "unsafe", "untrusted"), ("eval security", "execute a string")),
    KnowledgeEntry("How do I use Python's interactive shell?", "Run `python3` in a terminal to open the interactive interpreter, where you can try expressions one at a time. Use `help(str)` or `dir(object)` to explore. Exit with `exit()` or Ctrl+D on macOS/Linux.", ("interactive", "shell", "repl", "interpreter", "help"), ("python repl", "interactive interpreter")),
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
        return ("I don't have a confident answer for that yet. I can help with Python strings and built-in types, "
                "functions, collections, loops, exceptions, modules, classes, files, and packages. Try asking about one of those topics.")
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
