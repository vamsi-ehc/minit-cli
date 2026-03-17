"""Tests for the CLI entry point."""

from __future__ import annotations

import json

import pytest
from click.testing import CliRunner

from minit_cli.cli import main


@pytest.fixture
def runner():
    return CliRunner()


class TestCliVersion:
    def test_version(self, runner):
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output


class TestCliHelp:
    def test_main_help(self, runner):
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "dashboard" in result.output
        assert "serve" in result.output
        assert "stats" in result.output

    def test_dashboard_help(self, runner):
        result = runner.invoke(main, ["dashboard", "--help"])
        assert result.exit_code == 0

    def test_serve_help(self, runner):
        result = runner.invoke(main, ["serve", "--help"])
        assert result.exit_code == 0

    def test_stats_help(self, runner):
        result = runner.invoke(main, ["stats", "--help"])
        assert result.exit_code == 0


class TestCliStatsCommand:
    def test_stats_outputs_json(self, runner):
        result = runner.invoke(main, ["stats"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "timestamp" in data
        assert "cpu" in data
        assert "memory" in data
        assert "disk" in data
        assert "network" in data
        assert "processes" in data

    def test_stats_pretty_flag(self, runner):
        result = runner.invoke(main, ["stats", "--pretty"])
        assert result.exit_code == 0
        # Pretty JSON should be multi-line and parse correctly
        data = json.loads(result.output)
        assert "cpu" in data
        assert "\n" in result.output
