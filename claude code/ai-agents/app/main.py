"""Resolve a Snobos run's configuration before source collection begins.

The Step 1 CLI validates settings, secrets, episode numbering, and the reporting
window. Later pipeline steps will add adapters and output generation after this
deterministic setup has passed.
"""

import argparse
from datetime import date
import sys
from collections.abc import Sequence

from app.config import ConfigurationError, load_snobos_api_key, load_snobos_settings
from app.llm import get_anthropic_client
from app.schedule import calculate_episode_number, get_show_window, is_user_produced_episode


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser for a Snobos show run.

    Returns:
        Parser requiring the show date and accepting an episode override.
    """
    parser = argparse.ArgumentParser(description="Prepare a Snobos Stage 1 run.")
    parser.add_argument(
        "--show-date",
        required=True,
        type=date.fromisoformat,
        help="Wednesday show date in YYYY-MM-DD format",
    )
    parser.add_argument(
        "--episode-number",
        type=int,
        help="Override the episode number calculated from the configured anchor",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Validate a Snobos run and print its resolved schedule without sourcing.

    Args:
        argv: Optional argument list; defaults to the process command line.

    Returns:
        Process exit code, with zero for a valid setup and two for invalid input.

    Example:
        >>> main(["--show-date", "2026-10-14"])
        0
    """
    args = build_parser().parse_args(argv)
    try:
        settings = load_snobos_settings()
        api_key = load_snobos_api_key()
        _client = get_anthropic_client(api_key)
        calculated_episode = calculate_episode_number(
            show_date=args.show_date,
            anchor_date=settings.episode_anchor_date,
            anchor_number=settings.episode_anchor_number,
            skipped_show_dates=settings.skipped_show_dates,
        )
        episode_number = (
            calculated_episode if args.episode_number is None else args.episode_number
        )
        if episode_number < 1:
            raise ValueError("--episode-number must be positive")
        window = get_show_window(
            args.show_date,
            settings.window_days,
            settings.timezone,
            settings.skipped_show_dates,
        )
        user_show = is_user_produced_episode(
            episode_number,
            settings.user_anchor_episode,
            settings.producer_rotation_interval,
        )
    except (ConfigurationError, ValueError) as error:
        print(f"Snobos setup failed: {error}", file=sys.stderr)
        return 2

    producer = "user" if user_show else "other co-host"
    print(
        f"Snobos setup ready: episode {episode_number}, show date {args.show_date}, "
        f"window {window.start_date} through {window.end_date} ({window.timezone}), "
        f"producer rotation: {producer}. No sources were queried."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())