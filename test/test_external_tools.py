#!/usr/bin/env python3

import os
import subprocess

from rl_interaction.utils.utils import AppiumLauncher, Utils


class TestAppium(object):
    def test_appium_valid_command(self):
        appium_path = Utils.get_appium_executable_path()
        assert os.path.isfile(appium_path)
        output = subprocess.check_output(
            [appium_path, "--help"], stderr=subprocess.STDOUT
        ).decode()
        assert "show this help message and exit" in output.lower()

    def test_appium_launcher(self):
        appium = AppiumLauncher(4270)
        appium.restart_appium()
        appium.terminate()


class TestAdb(object):
    def test_adb_valid_command(self):
        adb_path = Utils.get_adb_executable_path()
        assert os.path.isfile(adb_path)
        output = subprocess.check_output(
            [adb_path, "--help"], stderr=subprocess.STDOUT
        ).decode()
        assert "show this help message" in output.lower()


class TestEmulator(object):
    def test_emulator_valid_command(self):
        emulator_path = Utils.get_emulator_executable_path()
        assert os.path.isfile(emulator_path)
        output = subprocess.check_output(
            [emulator_path, "-help"], stderr=subprocess.STDOUT
        ).decode()
        assert "print this help" in output.lower()
