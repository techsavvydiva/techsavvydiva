import os
from pathlib import Path
from dotenv import load_dotenv

AGENT_ENV_FILES = {
    "synthesized_future": Path("configs/synthesized_future.env"),
    "techsavvydiva": Path("configs/techsavvydiva.env"),
    "snobos": Path("configs/snobos.env"),
}

def load_agent_config(agent_name: str) -> None:
    env_path = AGENT_ENV_FILES.get(agent_name)

    if env_path is None or not env_path.exists():
        raise ValueError(f"No environment configuration found for agent: {agent_name}")

    # Clear any inherited key so agents cannot accidentally share credentials.
    os.environ.pop("ANTHROPIC_API_KEY", None)

    load_dotenv(dotenv_path=env_path, override=True)

    if not os.getenv("ANTHROPIC_API_KEY"):
        raise ValueError(f"ANTHROPIC_API_KEY is missing in {env_path}")