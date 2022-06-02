#!/usr/bin/env python3

import os
import shutil
import subprocess


class TestAppium(object):
    def test_appium_valid_command(self):
        appium_path = shutil.which("appium")
        assert os.path.isfile(appium_path)
        output = subprocess.check_output(
            [appium_path, "--help"], stderr=subprocess.STDOUT
        ).decode()
        assert "show this help message and exit" in output.lower()


class TestEmulator(object):
    def test_emulator_valid_command(self):
        emulator_path = shutil.which(
            "emulator", path=os.path.join(os.environ.get("ANDROID_HOME"), "emulator")
        )
        assert os.path.isfile(emulator_path)
        output = subprocess.check_output(
            [emulator_path, "-help"], stderr=subprocess.STDOUT
        ).decode()
        assert "print this help" in output.lower()
