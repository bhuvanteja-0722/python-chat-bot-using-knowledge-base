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

Python basics, functions, lists, dictionaries, tuples, sets, `for` and `while` loops, exceptions, modules and imports, classes, files, list comprehensions, package installation, and types.

The chatbot uses keyword and phrase matching against its local knowledge base. It does not call an AI model or the internet; unsupported or ambiguous questions receive a suggestion to ask about a covered topic.
