# Personal Python Question-Answering Chatbot

A lightweight command-line chatbot that answers common Python programming questions from a predefined knowledge base. It uses only the Python standard library, so no API key or package installation is needed.

## Requirements

- Python 3.10 or newer

## Run

```bash
python3 chatbot.py
```

Type a question at the `You:` prompt. Type `quit`, `exit`, or `q` to end the session. You can also import `find_answer` from `chatbot.py` and call it from another Python program.

## Topics covered

Python basics, functions, lists, dictionaries, tuples, sets, `for` and `while` loops, exceptions, modules and imports, classes, files, list comprehensions, package installation, and types.

The chatbot uses keyword and phrase matching against its local knowledge base. It does not call an AI model or the internet; unsupported or ambiguous questions receive a suggestion to ask about a covered topic.
