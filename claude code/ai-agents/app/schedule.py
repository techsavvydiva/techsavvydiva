"""Calculate show dates, reporting windows, episodes, and producer rotation.

These deterministic calendar helpers are called by the CLI before any agent
work. Keeping them separate makes the same date and rotation logic reusable by
other agents without a model call.
"""

from dataclasses import dataclass
from datetime import date, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


@dataclass(frozen=True)
class ShowWindow:
    """Represent an inclusive local-date range for gathering stories.

    Attributes:
        start_date: First included local calendar date.
        end_date: Show date and final included local calendar date.
        timezone: IANA timezone used to interpret publication dates.
    """

    start_date: date
    end_date: date
    timezone: str


def calculate_episode_number(
    show_date: date,
    anchor_date: date,
    anchor_number: int,
    skipped_show_dates: frozenset[date],
) -> int:
    """Calculate the episode number for an occurring Wednesday show.

    Args:
        show_date: Wednesday being prepared.
        anchor_date: Wednesday assigned to the known anchor episode.
        anchor_number: Episode number assigned to the anchor date.
        skipped_show_dates: Wednesdays after the anchor when no show occurred.

    Returns:
        The episode number after excluding skipped weeks.

    Raises:
        ValueError: If dates are not Wednesdays, the show precedes the anchor,
            the anchor number is invalid, or the requested show is skipped.

    Example:
        >>> calculate_episode_number(date(2026, 10, 28), date(2026, 10, 14), 383, frozenset())
        385
    """
    if anchor_number < 1:
        raise ValueError("anchor_number must be positive")
    if anchor_date.weekday() != 2 or show_date.weekday() != 2:
        raise ValueError("The anchor date and show date must be Wednesdays")
    if show_date < anchor_date:
        raise ValueError("show_date cannot precede the configured episode anchor")
    if show_date in skipped_show_dates:
        raise ValueError(f"No episode is scheduled for skipped show date {show_date}")
    if any(day.weekday() != 2 or day <= anchor_date for day in skipped_show_dates):
        raise ValueError("Skipped show dates must be Wednesdays after the episode anchor")

    show_count = (show_date - anchor_date).days // 7 + 1
    skipped_count = sum(anchor_date < skipped_date <= show_date for skipped_date in skipped_show_dates)
    return anchor_number + show_count - skipped_count - 1


def is_user_produced_episode(episode_number: int, first_user_episode: int, interval: int) -> bool:
    """Determine whether an episode falls on the user's production rotation.

    Args:
        episode_number: Calculated or explicitly overridden episode number.
        first_user_episode: First episode in the known user-produced rotation.
        interval: Number of occurring episodes between user-produced episodes.

    Returns:
        True when the episode is on or after the anchor and matches the cadence.

    Raises:
        ValueError: If the episode or interval is not positive.
    """
    if episode_number < 1 or first_user_episode < 1 or interval < 1:
        raise ValueError("Episode numbers and rotation interval must be positive")
    return episode_number >= first_user_episode and (episode_number - first_user_episode) % interval == 0


def get_show_window(
    show_date: date,
    window_days: int,
    timezone: str,
    skipped_show_dates: frozenset[date] = frozenset(),
) -> ShowWindow:
    """Build an inclusive window from the previous occurring show to show day.

    Args:
        show_date: Wednesday that ends the reporting window.
        window_days: Day interval between normally scheduled weekly shows.
        timezone: IANA timezone used when assigning stories to local dates.
        skipped_show_dates: Wednesdays when no show occurred.

    Returns:
        The previous occurring Wednesday through show day, inclusive, and timezone.

    Raises:
        ValueError: If dates are not Wednesdays, the interval is invalid, or the
            timezone is unknown.

    Example:
        >>> get_show_window(date(2026, 10, 14), 7, "America/New_York")
        ShowWindow(start_date=date(2026, 10, 7), end_date=date(2026, 10, 14), timezone='America/New_York')
    """
    if window_days < 1:
        raise ValueError("window_days must be positive")
    if show_date.weekday() != 2 or any(day.weekday() != 2 for day in skipped_show_dates):
        raise ValueError("The show date and skipped show dates must be Wednesdays")
    try:
        ZoneInfo(timezone)
    except ZoneInfoNotFoundError as error:
        raise ValueError(f"Unknown IANA timezone: {timezone}") from error

    start_date = show_date - timedelta(days=window_days)
    while start_date in skipped_show_dates:
        start_date -= timedelta(days=window_days)
    return ShowWindow(
        start_date=start_date,
        end_date=show_date,
        timezone=timezone,
    )