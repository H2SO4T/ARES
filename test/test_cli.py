#!/usr/bin/env python3

import sys

import pytest

from rl_interaction import test_application


class TestCommandLine(object):
    def test_help_message(self, monkeypatch):
        # Mock the command line parser.
        with monkeypatch.context() as m:
            m.setattr(sys, "argv", ["program", "--help"])
            with pytest.raises(SystemExit) as e:
                test_application.main()
            assert e.value.code == 0

    def test_missing_required_parameters(self, monkeypatch):
        # Mock the command line parser.
        with monkeypatch.context() as m:
            m.setattr(sys, "argv", ["program"])
            with pytest.raises(SystemExit) as e:
                test_application.main()
            assert e.value.code == 2
