# Personal Python Question-Answering Chatbot

A polished, responsive local web chatbot that answers Python and data-structures questions from a predefined knowledge base. Relevant answers include accessible diagrams and charts drawn as local SVG, alongside concise explanations and Python examples. It uses only the Python standard library, so no API key or package installation is needed.

## Requirements

- Python 3.10 or newer

## Run the web app

```bash
python3 server.py
```

Open [http://127.0.0.1:8765](http://127.0.0.1:8765) in your browser. Ask questions in the chat box, use a suggested prompt, or choose a topic from the sidebar. Press Enter to send and Shift+Enter for a new line. Stop the server with Ctrl+C.

The original terminal interface remains available with `python3 chatbot.py`.

## Topics covered

The curated knowledge base contains 197 entries covering Python syntax and control flow; built-in types and collections; arrays, queues, circular queues, stacks, hash tables, linked lists, heaps, trees, tries, range trees, union-find, probabilistic structures and graphs; algorithms such as BFS/DFS, Dijkstra, Bellman-Ford, Floyd-Warshall, A*, topological sort, string search, binary search, two pointers, sliding windows, greedy methods, divide and conquer, dynamic programming and backtracking; Big O, time and space complexity; problem-solving workflows, correctness reasoning, and worked patterns such as Two Sum, prefix sums, interval merging, cycle detection, interval scheduling, longest common subsequence, knapsack, subsets, and shortest paths; implementation guides for binary search, Dijkstra, topological sorting, union-find, tries and LRU caches; functions, arguments, scope, iterators, generators and decorators; object-oriented programming, dataclasses and type hints; exceptions, logging, files, paths, JSON, CSV, dates and regular expressions; standard-library tools such as `collections`, `itertools`, `argparse`, `sqlite3` and `asyncio`; HTTP, concurrency and the GIL, testing, debugging, profiling, virtual environments, dependencies, style, memory and common security pitfalls.

The chatbot uses keyword and phrase matching against its local knowledge base. It does not call an AI model or the internet; unsupported or ambiguous questions receive a suggestion to ask about a covered topic.
