# Personal Python Question-Answering Chatbot

A polished, responsive local web chatbot that answers common Python programming questions from a predefined knowledge base. It uses only the Python standard library, so no API key or package installation is needed.

## Requirements

- Python 3.10 or newer

## Run the web app

```bash
python3 server.py
```

Open [http://127.0.0.1:8765](http://127.0.0.1:8765) in your browser. Ask questions in the chat box, use a suggested prompt, or choose a topic from the sidebar. Press Enter to send and Shift+Enter for a new line. Stop the server with Ctrl+C.

The original terminal interface remains available with `python3 chatbot.py`.

## Topics covered

The curated knowledge base covers Python syntax and control flow; built-in types and collections; queues, circular queues, stacks, hash tables, linked lists, trees and graphs; algorithms such as BFS/DFS, binary search, two pointers, sliding windows, greedy methods, dynamic programming and backtracking; Big O, time and space complexity; functions, arguments, scope, iterators, generators and decorators; object-oriented programming, dataclasses and type hints; exceptions, logging, files, paths, JSON, CSV, dates and regular expressions; standard-library tools such as `collections`, `itertools`, `argparse`, `sqlite3` and `asyncio`; HTTP, concurrency, testing, debugging, virtual environments, dependencies, style, memory and common security pitfalls.

The chatbot uses keyword and phrase matching against its local knowledge base. It does not call an AI model or the internet; unsupported or ambiguous questions receive a suggestion to ask about a covered topic.
