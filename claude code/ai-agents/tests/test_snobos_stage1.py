"""Test deterministic Snobos setup, configuration, and calendar behavior."""

from datetime import date
from pathlib import Path

import pytest
from _pytest.capture import CaptureFixture
from _pytest.monkeypatch import MonkeyPatch

from app.config import ConfigurationError, load_snobos_api_key, load_snobos_settings
from app.main import main
from app.schedule import (
    ShowWindow,
    calculate_episode_number,
    get_show_window,
    is_user_produced_episode,
)


def test_load_snobos_settings_reads_episode_and_search_settings() -> None:
    """Snobos YAML supplies the anchor, local window, search cap, and rotation."""
    settings = load_snobos_settings()

    assert settings.episode_anchor_date == date(2026, 10, 14)
    assert settings.episode_anchor_number == 383
    assert settings.window_days == 7
    assert settings.timezone == "America/New_York"
    assert settings.max_web_searches_per_run == 10
    assert settings.user_anchor_episode == 385


def test_load_snobos_api_key_reads_only_the_requested_file(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    """The selected Snobos env file provides its key without ambient env state."""
    env_file = tmp_path / "snobos.env"
    env_file.write_text("ANTHROPIC_API_KEY=test-key-only\n", encoding="utf-8")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "different-process-key")

    assert load_snobos_api_key(env_file) == "test-key-only"


def test_load_snobos_api_key_rejects_missing_key(tmp_path: Path) -> None:
    """A secret file without the Anthropic key fails with a safe error."""
    env_file = tmp_path / "snobos.env"
    env_file.write_text("UNRELATED_SETTING=value\n", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="ANTHROPIC_API_KEY is missing"):
        load_snobos_api_key(env_file)


def test_load_snobos_api_key_does_not_interpolate_process_environment(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    """The selected secret file cannot indirectly inherit another env variable."""
    env_file = tmp_path / "snobos.env"
    env_file.write_text("ANTHROPIC_API_KEY=${SHARED_KEY}\n", encoding="utf-8")
    monkeypatch.setenv("SHARED_KEY", "ambient-key")

    assert load_snobos_api_key(env_file) == "${SHARED_KEY}"


def test_window_for_october_14_spans_previous_show_through_show_day() -> None:
    """Window for the Oct 14, 2026 show spans Oct 7 through Oct 14."""
    window = get_show_window(date(2026, 10, 14), 7, "America/New_York")

    assert window == ShowWindow(
        start_date=date(2026, 10, 7),
        end_date=date(2026, 10, 14),
        timezone="America/New_York",
    )


def test_window_for_november_18_spans_november_11_through_november_18() -> None:
    """Window for the Nov 18, 2026 show spans Nov 11 through Nov 18."""
    window = get_show_window(date(2026, 11, 18), 7, "America/New_York")

    assert window == ShowWindow(
        start_date=date(2026, 11, 11),
        end_date=date(2026, 11, 18),
        timezone="America/New_York",
    )


def test_window_starts_at_previous_show_before_a_skipped_wednesday() -> None:
    """A skipped prior Wednesday extends the window to the last occurring show."""
    window = get_show_window(
        date(2026, 11, 4),
        7,
        "America/New_York",
        frozenset({date(2026, 10, 28)}),
    )

    assert window.start_date == date(2026, 10, 21)
    assert window.end_date == date(2026, 11, 4)


def test_episode_number_increments_for_each_wednesday() -> None:
    """Episodes 383 on Oct 14 and 385 on Oct 28 follow weekly show numbering."""
    episode = calculate_episode_number(
        date(2026, 10, 28),
        date(2026, 10, 14),
        383,
        frozenset(),
    )

    assert episode == 385


def test_skipped_wednesday_does_not_consume_episode_number() -> None:
    """Skipping Oct 21 assigns episode 384 to Oct 28 and 385 to Nov 4."""
    skipped_dates = frozenset({date(2026, 10, 21)})

    assert calculate_episode_number(
        date(2026, 10, 28), date(2026, 10, 14), 383, skipped_dates
    ) == 384
    assert calculate_episode_number(
        date(2026, 11, 4), date(2026, 10, 14), 383, skipped_dates
    ) == 385


def test_episode_override_is_printed_without_exposing_the_key(
    monkeypatch: MonkeyPatch,
    capsys: CaptureFixture[str],
) -> None:
    """CLI override changes the displayed number while never printing credentials."""
    monkeypatch.setattr("app.main.load_snobos_api_key", lambda: "test-secret")
    monkeypatch.setattr("app.main.get_anthropic_client", lambda api_key: object())

    exit_code = main(["--show-date", "2026-10-14", "--episode-number", "900"])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "episode 900" in output
    assert "test-secret" not in output
    assert "window 2026-10-07 through 2026-10-14" in output


def test_user_rotation_starts_at_episode_385() -> None:
    """User rotation marks 385 and 387 as user-produced, but not 383 or 386."""
    assert is_user_produced_episode(383, 385, 2) is False
    assert is_user_produced_episode(385, 385, 2) is True
    assert is_user_produced_episode(386, 385, 2) is False
    assert is_user_produced_episode(387, 385, 2) is True


def test_episode_calculation_rejects_non_wednesday() -> None:
    """Only Wednesday show dates can receive a calculated episode number."""
    with pytest.raises(ValueError, match="must be Wednesdays"):
        calculate_episode_number(
            date(2026, 10, 15), date(2026, 10, 14), 383, frozenset()
        )


def test_episode_calculation_rejects_skipped_date() -> None:
    """A skipped Wednesday cannot be run as a show, even with separate overrides."""
    with pytest.raises(ValueError, match="No episode is scheduled"):
        calculate_episode_number(
            date(2026, 10, 21),
            date(2026, 10, 14),
            383,
            frozenset({date(2026, 10, 21)}),
        )


def test_cli_rejects_non_positive_episode_override(
    monkeypatch: MonkeyPatch,
    capsys: CaptureFixture[str],
) -> None:
    """An explicit zero episode override is rejected instead of ignored."""
    monkeypatch.setattr("app.main.load_snobos_api_key", lambda: "test-secret")
    monkeypatch.setattr("app.main.get_anthropic_client", lambda api_key: object())

    exit_code = main(["--show-date", "2026-10-14", "--episode-number", "0"])

    assert exit_code == 2
    assert "--episode-number must be positive" in capsys.readouterr().err