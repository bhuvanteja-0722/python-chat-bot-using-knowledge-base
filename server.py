"""Local web server for the Python Q&A chatbot."""

from __future__ import annotations

import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from chatbot import KNOWLEDGE_BASE, VISUALS_BY_QUESTION, find_answer, find_entry

ROOT = Path(__file__).resolve().parent


class ChatHandler(SimpleHTTPRequestHandler):
    """Serve the web UI and a small JSON answer endpoint."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / "static"), **kwargs)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/healthz":
            body = b"ok"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return
        if path == "/api/knowledge":
            entries = [
                {
                    "question": entry.question,
                    "answer": entry.answer,
                    "visual": VISUALS_BY_QUESTION.get(entry.question),
                }
                for entry in KNOWLEDGE_BASE
            ]
            body = json.dumps({"count": len(entries), "entries": entries}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/answer":
            self.send_error(404, "Not found")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 16_384:
                raise ValueError("Please enter a shorter question.")
            payload = json.loads(self.rfile.read(length))
            question = payload.get("question", "")
            if not isinstance(question, str) or not question.strip():
                raise ValueError("Please enter a question first.")
            if len(question) > 2_000:
                raise ValueError("Please keep your question under 2,000 characters.")
            entry = find_entry(question.strip())
            response = {
                "answer": entry.answer if entry else find_answer(question.strip()),
                "visual": VISUALS_BY_QUESTION.get(entry.question) if entry else None,
            }
            body = json.dumps(response).encode("utf-8")
            self.send_response(200)
        except (ValueError, json.JSONDecodeError) as error:
            body = json.dumps({"error": str(error) or "Invalid request."}).encode("utf-8")
            self.send_response(400)
        except Exception:
            body = json.dumps({"error": "Something went wrong. Please try again."}).encode("utf-8")
            self.send_response(500)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        print(f"{self.address_string()} - {format % args}")


def main() -> None:
    default_host = "0.0.0.0" if "PORT" in os.environ else "127.0.0.1"
    host = os.environ.get("HOST", default_host)
    port = int(os.environ.get("PORT", "8765"))
    address = (host, port)
    print(f"Python Q&A is ready at http://{address[0]}:{address[1]}")
    print("Press Ctrl+C to stop the server.")
    try:
        with ThreadingHTTPServer(address, ChatHandler) as server:
            server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    main()
