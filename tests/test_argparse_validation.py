"""Tests for CLI numeric option validation."""

import pytest

import SteamGamesScraper


def test_sleep_rejects_negative():
    parser = SteamGamesScraper.create_parser()
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["--sleep", "-1"])
    assert exc_info.value.code == 2


def test_retries_rejects_negative():
    parser = SteamGamesScraper.create_parser()
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["--retries", "-2"])
    assert exc_info.value.code == 2


def test_autosave_rejects_negative():
    parser = SteamGamesScraper.create_parser()
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["--autosave", "-5"])
    assert exc_info.value.code == 2


def test_numeric_options_accept_zero_and_defaults():
    parser = SteamGamesScraper.create_parser()
    args = parser.parse_args(["--sleep", "0", "--retries", "0", "--autosave", "0"])
    assert args.sleep == 0
    assert args.retries == 0
    assert args.autosave == 0
    args = parser.parse_args([])
    assert args.sleep == SteamGamesScraper.DEFAULT_SLEEP
    assert args.retries == SteamGamesScraper.DEFAULT_RETRIES
    assert args.autosave == SteamGamesScraper.DEFAULT_AUTOSAVE
