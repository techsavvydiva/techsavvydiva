"""Construct the direct Anthropic client used by agent workflows.

Callers load the agent-specific secret and pass it explicitly, preventing the
client from inheriting another agent's key from process-wide environment state.
"""

from anthropic import Anthropic


def get_anthropic_client(api_key: str) -> Anthropic:
    """Create an Anthropic client with an explicitly selected agent key.

    Args:
        api_key: Secret loaded from the selected agent's private env file.

    Returns:
        An Anthropic SDK client; creating it does not make a network request.

    Raises:
        ValueError: If the provided key is empty.
    """
    if not api_key:
        raise ValueError("An Anthropic API key is required to create the client.")

    return Anthropic(api_key=api_key)