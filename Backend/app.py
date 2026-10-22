import os
import time
import uuid
from collections import defaultdict
from pathlib import Path
from threading import Lock

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)

import functions


load_dotenv(Path(__file__).resolve().parent / ".env")

RATE_LIMIT_MAX_REQUESTS = 15
RATE_LIMIT_WINDOW_SECONDS = 60
MAX_MESSAGE_LENGTH = 500
MAX_HISTORY_MESSAGES = 20
CONVERSATION_TTL_SECONDS = 60 * 60 * 6

_rate_limit_store = defaultdict(list)
_conversations = {}
_conversation_lock = Lock()


def is_rate_limited(ip: str) -> bool:
    """Return True when an IP has exceeded the rolling request limit."""
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW_SECONDS
    timestamps = [timestamp for timestamp in _rate_limit_store[ip] if timestamp > window_start]
    _rate_limit_store[ip] = timestamps
    if len(timestamps) >= RATE_LIMIT_MAX_REQUESTS:
        return True
    timestamps.append(now)
    return False


def _remove_expired_conversations(now: float) -> None:
    expired_ids = [
        conversation_id
        for conversation_id, conversation in _conversations.items()
        if now - conversation["updated_at"] > CONVERSATION_TTL_SECONDS
    ]
    for conversation_id in expired_ids:
        del _conversations[conversation_id]


def create_conversation() -> str:
    now = time.time()
    conversation_id = str(uuid.uuid4())
    with _conversation_lock:
        _remove_expired_conversations(now)
        _conversations[conversation_id] = {"messages": [], "updated_at": now}
    return conversation_id


def get_conversation_with_user_message(conversation_id: str, user_input: str):
    """Return history including the pending user message, or None for an unknown ID."""
    now = time.time()
    with _conversation_lock:
        _remove_expired_conversations(now)
        conversation = _conversations.get(conversation_id)
        if conversation is None:
            return None
        history = list(conversation["messages"])
        history.append({"role": "user", "content": user_input})
        return history


def save_exchange(conversation_id: str, user_input: str, assistant_response: str) -> None:
    with _conversation_lock:
        conversation = _conversations.get(conversation_id)
        if conversation is None:
            return
        conversation["messages"].extend(
            [
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": assistant_response},
            ]
        )
        conversation["messages"] = conversation["messages"][-MAX_HISTORY_MESSAGES:]
        conversation["updated_at"] = time.time()


app = Flask(__name__)
CORS(
    app,
    origins=[
        "https://mywaterwarehouse.com",
        "https://wordpress-984626-5694127.cloudwaysapps.com",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not configured")

client = OpenAI(api_key=api_key)


@app.route("/", methods=["GET"])
def health_check():
    return jsonify(
        {
            "status": "healthy",
            "message": "Water Warehouse Chatbot API is running",
            "api": "responses",
        }
    )


@app.route("/start", methods=["GET"])
def start_conversation():
    conversation_id = create_conversation()
    print(f"Created conversation: {conversation_id}")
    # Preserve the existing field name for compatibility with the website.
    return jsonify({"thread_id": conversation_id})


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    conversation_id = data.get("thread_id")
    user_input = data.get("message")

    if not isinstance(conversation_id, str) or not conversation_id.strip():
        return jsonify({"error": "Missing thread_id"}), 400
    if not isinstance(user_input, str) or not user_input.strip():
        return jsonify({"error": "Missing message"}), 400

    conversation_id = conversation_id.strip()
    user_input = user_input.strip()

    if len(user_input) > MAX_MESSAGE_LENGTH:
        return jsonify(
            {"error": f"Message too long. Please keep messages under {MAX_MESSAGE_LENGTH} characters."}
        ), 400

    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown")
    client_ip = client_ip.split(",")[0].strip()
    if is_rate_limited(client_ip):
        return jsonify(
            {"error": "Too many messages. Please wait a moment before sending another."}
        ), 429

    conversation = get_conversation_with_user_message(conversation_id, user_input)
    if conversation is None:
        return jsonify(
            {"error": "Conversation expired or was not found. Please start a new conversation."}
        ), 404

    try:
        response_text = functions.create_response(client, conversation)
        save_exchange(conversation_id, user_input, response_text)
        return jsonify({"response": response_text})
    except AuthenticationError as exc:
        print(f"OpenAI authentication error: {exc}")
        return jsonify({"error": "The chatbot is temporarily unavailable."}), 503
    except RateLimitError as exc:
        print(f"OpenAI rate limit error: {exc}")
        return jsonify({"error": "The chatbot is busy. Please try again shortly."}), 503
    except APITimeoutError as exc:
        print(f"OpenAI timeout: {exc}")
        return jsonify({"error": "The chatbot took too long to respond. Please try again."}), 504
    except APIConnectionError as exc:
        print(f"OpenAI connection error: {exc}")
        return jsonify({"error": "Unable to reach the chatbot service. Please try again."}), 502
    except Exception as exc:
        print(f"Unexpected chat error ({type(exc).__name__}): {exc}")
        return jsonify({"error": "The chatbot could not answer right now. Please try again."}), 502


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    debug_mode = os.environ.get("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
