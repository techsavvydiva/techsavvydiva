"""Load validated agent settings and secrets for the shared runtime.

This module keeps reviewable YAML configuration separate from secret environment
files. Snobos is the first consumer; the loader can be reused by other agents by
adding their settings schema and secret-file mapping without changing scheduling
logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from dotenv import dotenv_values
import yaml


class ConfigurationError(ValueError):
    """Represent invalid YAML settings or missing required secrets."""


@dataclass(frozen=True)
class SnobosSettings:
    """Hold validated, non-secret Snobos configuration.

    Attributes:
        name: Stable agent identifier.
        description: Human-readable purpose of the agent.
        model: Anthropic model identifier selected by YAML.
        timezone: IANA timezone used for show dates and reporting windows.
        window_days: Number of inclusive local calendar days in a research window.
        max_web_searches_per_run: Configured upper bound for later web-search work.
        episode_anchor_date: Show date associated with the anchor episode number.
        episode_anchor_number: Episode number assigned to the anchor date.
        skipped_show_dates: Wednesdays that do not consume episode numbers.
        producer_rotation_interval: Number of episodes between user-produced shows.
        user_anchor_episode: First episode in the user's configured production rotation.
        allowed_tools: Tool identifiers permitted by the agent configuration.
        approval_required_tools: Tool identifiers requiring human approval.
        output_directory: Base local output directory for this agent.
    """

    name: str
    description: str
    model: str
    timezone: str
    window_days: int
    max_web_searches_per_run: int
    episode_anchor_date: date
    episode_anchor_number: int
    skipped_show_dates: frozenset[date]
    producer_rotation_interval: int
    user_anchor_episode: int
    allowed_tools: tuple[str, ...]
    approval_required_tools: tuple[str, ...]
    output_directory: Path


def _mapping(value: object, field_name: str) -> dict[str, object]:
    """Return a YAML mapping or raise a field-specific configuration error.

    Args:
        value: Parsed YAML value to validate.
        field_name: Configuration path used in any error message.

    Returns:
        The value as a string-keyed dictionary.

    Raises:
        ConfigurationError: If the value is not a mapping.
    """
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise ConfigurationError(f"{field_name} must be a mapping")
    return value


def _string(mapping: dict[str, object], key: str, field_name: str | None = None) -> str:
    """Read a required non-empty string from a mapping.

    Args:
        mapping: Configuration mapping containing the value.
        key: Key to read.
        field_name: Optional full path to use in errors.

    Returns:
        The validated string value.

    Raises:
        ConfigurationError: If the value is absent, empty, or not a string.
    """
    value = mapping.get(key)
    label = field_name or key
    if not isinstance(value, str) or not value.strip():
        raise ConfigurationError(f"{label} must be a non-empty string")
    return value.strip()


def _integer(
    mapping: dict[str, object],
    key: str,
    *,
    minimum: int,
    field_name: str | None = None,
) -> int:
    """Read an integer constrained to a minimum value.

    Args:
        mapping: Configuration mapping containing the value.
        key: Key to read.
        minimum: Smallest accepted integer.
        field_name: Optional full path to use in errors.

    Returns:
        The validated integer value.

    Raises:
        ConfigurationError: If the value is not an integer or is below minimum.
    """
    value = mapping.get(key)
    label = field_name or key
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ConfigurationError(f"{label} must be an integer greater than or equal to {minimum}")
    return value


def _date(value: object, field_name: str) -> date:
    """Parse an ISO date from a value produced by the YAML parser.

    Args:
        value: YAML scalar to parse as a calendar date.
        field_name: Configuration path used in any error message.

    Returns:
        The parsed calendar date.

    Raises:
        ConfigurationError: If the value is not a date or ISO date string.
    """
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError as error:
            raise ConfigurationError(f"{field_name} must use YYYY-MM-DD format") from error
    raise ConfigurationError(f"{field_name} must use YYYY-MM-DD format")


def _string_tuple(value: object, field_name: str) -> tuple[str, ...]:
    """Validate an optional YAML list of non-empty strings.

    Args:
        value: Parsed YAML value to validate.
        field_name: Configuration path used in any error message.

    Returns:
        The values as an immutable tuple.

    Raises:
        ConfigurationError: If the value is not a list of non-empty strings.
    """
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        raise ConfigurationError(f"{field_name} must be a list of non-empty strings")
    return tuple(item.strip() for item in value)


def load_snobos_settings(config_path: Path | None = None) -> SnobosSettings:
    """Load and validate Snobos' non-secret YAML settings.

    Args:
        config_path: Optional YAML path; defaults to the repository's Snobos config.

    Returns:
        Immutable settings ready for CLI and workflow code.

    Raises:
        ConfigurationError: If the file cannot be read or contains invalid settings.

    Example:
        >>> settings = load_snobos_settings()
        >>> settings.episode_anchor_number
        383
    """
    root = Path(__file__).resolve().parents[1]
    path = config_path or root / "agents" / "snobos" / "config.yaml"
    try:
        raw_config = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise ConfigurationError(f"Could not load Snobos settings from {path}") from error

    config = _mapping(raw_config, "root")
    episode = _mapping(config.get("episode"), "episode")
    rotation = _mapping(config.get("producer_rotation"), "producer_rotation")
    anchor_date = _date(episode.get("anchor_date"), "episode.anchor_date")
    anchor_number = _integer(
        episode,
        "anchor_number",
        minimum=1,
        field_name="episode.anchor_number",
    )

    raw_skipped_dates = episode.get("skipped_show_dates", [])
    if not isinstance(raw_skipped_dates, list):
        raise ConfigurationError("episode.skipped_show_dates must be a list of dates")
    skipped_dates = frozenset(
        _date(value, f"episode.skipped_show_dates[{index}]")
        for index, value in enumerate(raw_skipped_dates)
    )
    for skipped_date in skipped_dates:
        if skipped_date.weekday() != 2 or skipped_date <= anchor_date:
            raise ConfigurationError(
                "Skipped show dates must be Wednesdays after episode.anchor_date"
            )

    timezone = _string(config, "timezone")
    try:
        ZoneInfo(timezone)
    except ZoneInfoNotFoundError as error:
        raise ConfigurationError(f"timezone must be a valid IANA timezone: {timezone}") from error

    return SnobosSettings(
        name=_string(config, "name"),
        description=_string(config, "description"),
        model=_string(config, "default_model"),
        timezone=timezone,
        window_days=_integer(config, "window_days", minimum=1),
        max_web_searches_per_run=_integer(config, "max_web_searches_per_run", minimum=0),
        episode_anchor_date=anchor_date,
        episode_anchor_number=anchor_number,
        skipped_show_dates=skipped_dates,
        producer_rotation_interval=_integer(
            rotation,
            "every_n_shows",
            minimum=1,
            field_name="producer_rotation.every_n_shows",
        ),
        user_anchor_episode=_integer(
            rotation,
            "user_anchor_episode",
            minimum=1,
            field_name="producer_rotation.user_anchor_episode",
        ),
        allowed_tools=_string_tuple(config.get("allowed_tools", []), "allowed_tools"),
        approval_required_tools=_string_tuple(
            config.get("approval_required_tools", []), "approval_required_tools"
        ),
        output_directory=Path(_string(config, "output_directory")),
    )


def load_snobos_api_key(env_path: Path | None = None) -> str:
    """Load only the Anthropic key from Snobos' explicitly selected env file.

    Args:
        env_path: Optional env-file path; defaults to `configs/snobos.env`.

    Returns:
        The Anthropic API key, without changing the process environment.

    Raises:
        ConfigurationError: If the selected file is missing or has no API key.

    Example:
        >>> key = load_snobos_api_key()
        >>> bool(key)
        True
    """
    root = Path(__file__).resolve().parents[1]
    path = env_path or root / "configs" / "snobos.env"
    api_key = dotenv_values(path, interpolate=False).get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ConfigurationError(f"ANTHROPIC_API_KEY is missing in {path}")
    return api_key