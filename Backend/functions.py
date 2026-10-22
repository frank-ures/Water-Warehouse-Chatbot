import os
from pathlib import Path
from typing import Dict, List, Optional


DEFAULT_MODEL = "gpt-4o-mini"
KNOWLEDGE_FILE = Path(__file__).resolve().parent / "knowledge.txt"


def load_knowledge() -> str:
    """Load the local Water Warehouse knowledge base."""
    try:
        return KNOWLEDGE_FILE.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Warning: unable to read {KNOWLEDGE_FILE}: {exc}")
        return ""


def build_instructions(knowledge_content: str) -> str:
    return f"""
You are the Water Warehouse Customer Support Assistant.
Help customers with questions about Water Warehouse products, pricing, and services.
Keep responses concise and include only necessary information.

Water Warehouse knowledge base:

{knowledge_content}

Use the knowledge base to answer accurately. If requested product, pricing, or
service information is absent, say that you do not have that specific information
and offer general water-treatment guidance. Do not invent business information.
""".strip()


SYSTEM_INSTRUCTIONS = build_instructions(load_knowledge())


def create_response(
    client,
    conversation: List[Dict[str, str]],
    model: Optional[str] = None,
) -> str:
    """Generate one assistant response using OpenAI's supported Responses API."""
    response = client.responses.create(
        model=model or os.environ.get("OPENAI_MODEL", DEFAULT_MODEL),
        instructions=SYSTEM_INSTRUCTIONS,
        input=conversation,
    )

    text = (response.output_text or "").strip()
    if not text:
        raise ValueError("OpenAI returned an empty response")
    return text
