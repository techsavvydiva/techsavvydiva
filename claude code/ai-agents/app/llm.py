import os
from anthropic import Anthropic

def get_anthropic_client() -> Anthropic:
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY is not set for the selected agent.")

    return Anthropic(api_key=api_key)