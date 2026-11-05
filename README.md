# Personal Python Question-Answering Chatbot

A polished, responsive local web chatbot that answers Python and data-structures questions from a predefined knowledge base. Browse and search all 2,000 entries in the built-in knowledge-base viewer, including their answers and visual guides. The catalog includes 1,300 additional built-in and standard-library API references. Some APIs require newer Python versions than 3.10; check your installed version before using them. Relevant answers include accessible diagrams and charts drawn as local SVG, alongside concise explanations and Python examples. It uses only the Python standard library, so no API key or package installation is needed.

## Requirements

- Python 3.10 or newer

## Run the web app

```bash
python3 server.py
```

Open [http://127.0.0.1:8765](http://127.0.0.1:8765) in your browser. Ask questions in the chat box, use a suggested prompt, choose a topic from the sidebar, or open **Knowledge base** in the header to search all entries, read answers, view diagrams, and ask a selected question. Press Enter to send and Shift+Enter for a new line. Stop the server with Ctrl+C.

The original terminal interface remains available with `python3 chatbot.py`.

## Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/bhuvanteja-0722/python-chat-bot-using-knowledge-base)

The Render Blueprint configures a free Python web service, binds to Render's assigned `PORT`, and checks `/healthz`. Review and approve the service creation in Render. To redeploy future GitHub pushes automatically, turn on **Auto-Deploy** in the Render service settings.

## Topics covered

The curated knowledge base contains 2,000 entries covering Python syntax and control flow, including structural pattern matching and assignment expressions; built-in types and collections such as Counter, defaultdict, and bisect; arrays, queues, circular queues, stacks, hash tables, linked lists, heaps, trees, tries, range trees, union-find, probabilistic structures and graphs; algorithms such as BFS/DFS, Dijkstra, Bellman-Ford, Floyd-Warshall, A*, topological sort, string search, binary search, two pointers, sliding windows, greedy methods, divide and conquer, dynamic programming and backtracking; Big O, time and space complexity; problem-solving workflows, correctness reasoning, and worked patterns such as Two Sum, prefix sums, interval merging, cycle detection, interval scheduling, longest common subsequence, knapsack, subsets, and shortest paths, edit distance, longest increasing subsequence, rotated-array search and minimum-window substring; implementation guides for binary search, Dijkstra, topological sorting, union-find, tries, LRU caches, heaps, merge sort, quickselect, BFS path reconstruction and prefix-sum queries, k-way merge and sorted-list search; functions, arguments, scope, iterators, generators and decorators; object-oriented programming, dataclasses and type hints; exceptions, logging, files, paths, JSON, CSV, dates and regular expressions; standard-library tools such as `collections`, `itertools`, `argparse`, `sqlite3` and `asyncio`; HTTP, concurrency and the GIL, testing, debugging, profiling, virtual environments, dependencies, style, memory and common security pitfalls.

The chatbot uses keyword and phrase matching against its local knowledge base. It does not call an AI model or the internet; unsupported or ambiguous questions receive a suggestion to ask about a covered topic.

## How answers are selected

The browser sends each question to the Python server at `/api/answer`. The matcher normalizes case, punctuation, and common plurals; checks exact titles and special cases; then scores topic keywords, title overlap, and phrase aliases. It returns the strongest match above a confidence threshold, or a fallback when it cannot find one. The answers are curated entries, not generated text, so the chatbot is designed for questions covered by its knowledge base rather than every possible question.

The 2,506 built-in entries are demo/reference content bundled with the project. They include curated Python answers and natural-language question variants that reuse those answers. The app does not store chat history. A local run processes questions on your machine; the hosted Render version sends question text to the PyPal service so it can return the answer.
