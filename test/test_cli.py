#!/usr/bin/env python3

import os
import sys

import pytest

from rl_interaction import test_application


@pytest.fixture(scope="session")
def valid_apk_path():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "test_resources",
        "InsecureBankv2.apk",
    )


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

    def test_real_application(self, monkeypatch, valid_apk_path):
        if (
            os.environ.get("GITHUB_ACTIONS", "false").lower() == "true"
            and os.environ.get("RUNNER_OS", "unknown") == "macOS"
        ):
            # Run this test only from GitHub Actions, when running on macOS
            # (since is the only OS providing hardware accelerated Android emulators).
            pass

            # Mock the command line parser.
            with monkeypatch.context() as m:
                m.setattr(
                    sys,
                    "argv",
                    [
                        "program",
                        "--device_name",
                        "test",  # Emulator name.
                        "--algo",
                        "SAC",
                        "--appium_port",
                        "4270",
                        "--timer",
                        "1",  # The test will stop after 1 minute.
                        "--iterations",
                        "1",
                        "--pool_strings",
                        os.path.join(
                            os.path.dirname(os.path.realpath(__file__)),
                            os.path.pardir,
                            "rl_interaction",
                            "strings.txt",
                        ),
                        "--apps",
                        valid_apk_path,
                    ],
                )
                exit_code = test_application.main()
                assert exit_code == 0
