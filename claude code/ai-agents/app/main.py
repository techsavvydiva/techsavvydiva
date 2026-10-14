import argparse
from app.config import load_agent_config

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", required=True, choices=[
        "synthesized_future",
        "techsavvydiva",
        "snobos",
    ])
    parser.add_argument("--task", required=True)
    args = parser.parse_args()

    load_agent_config(args.agent)