import os
import shutil
import subprocess
import time

from appium.webdriver.appium_service import AppiumService


class Utils:

    @staticmethod
    def get_adb_executable_path() -> str:
        adb_path = shutil.which("adb")
        if not os.path.isfile(adb_path):
            raise FileNotFoundError(
                "Appium executable is not available! "
                "Please check your Appium installation."
            )
        return adb_path

    @staticmethod
    def get_appium_executable_path() -> str:
        appium_path = shutil.which("appium")
        if not os.path.isfile(appium_path):
            raise FileNotFoundError(
                "Adb executable is not available! Make sure to have adb (Android "
                "Debug Bridge) installed and added to the PATH environment variable."
            )
        return appium_path

    @staticmethod
    def get_emulator_executable_path() -> str:
        emulator_path = shutil.which(
            "emulator", path=os.path.join(os.environ.get("ANDROID_HOME"), "emulator")
        )
        if not os.path.isfile(emulator_path):
            raise FileNotFoundError(
                "Emulator executable is not available! "
                "Please check your Android SDK installation."
            )
        return emulator_path

    @staticmethod
    def compute_coverage(coverage_dict):
        visited_activities = 0
        pressed_buttons = 0
        for key in coverage_dict.keys():
            for small_key in coverage_dict[key].keys():
                if small_key == 'visited':
                    if coverage_dict[key][small_key]:
                        visited_activities += 1
                else:
                    if coverage_dict[key][small_key]:
                        pressed_buttons += 1
        return visited_activities, pressed_buttons


class AppiumLauncher:

    def __init__(self, port: int):
        self.port: int = port
        self.appium_service: AppiumService = AppiumService()
        self.adb_path: str = Utils.get_adb_executable_path()
        self.start_appium()

    def terminate(self):
        self.appium_service.stop()
        time.sleep(4.0)

    def start_appium(self):
        self.appium_service.start(args=["-p", str(self.port)])
        os.system(f"{self.adb_path} start-server")
        time.sleep(4.0)

    def restart_appium(self):
        self.terminate()
        self.start_appium()


class EmulatorLauncher:

    def __init__(self, emu, device_name, android_port, speedup=False):
        self.device_name: str = '@'+device_name.replace(' ', '_')
        self.emu: str = emu
        self.android_port: int = android_port
        self.speedup: bool = speedup
        self.adb_path: str = Utils.get_adb_executable_path()
        self.emulator_path: str = Utils.get_emulator_executable_path()
        self.start_emulator()

    def terminate(self):
        os.system(f'{self.adb_path} -s emulator-{self.android_port} emu kill')
        time.sleep(5.0)

    def start_emulator(self):
        if self.emu == 'normal':
            if self.speedup:
                subprocess.Popen([self.emulator_path, self.device_name,
                                  '-port', str(self.android_port)])
                time.sleep(40)
            else:
                subprocess.Popen([self.emulator_path, self.device_name,
                                  '-port', str(self.android_port),
                                  '-no-snapshot', '-no-boot-anim', '-wipe-data'])
                time.sleep(50.0)
        else:
            # Headless emulator.
            subprocess.Popen([self.emulator_path, self.device_name,
                              '-port', str(self.android_port), '-no-window',
                              '-no-snapshot', '-no-audio', '-no-boot-anim', '-wipe-data'])
            time.sleep(50.0)

        os.system(f'{self.adb_path} -s emulator-{self.android_port} shell settings put global window_animation_scale 0')
        os.system(f'{self.adb_path} -s emulator-{self.android_port} shell settings put global transition_animation_scale 0')
        os.system(f'{self.adb_path} -s emulator-{self.android_port} shell settings put global animator_duration_scale 0')

    def restart_emulator(self):
        self.terminate()
        self.start_emulator()


class Timer:

    # timer expressed in minutes
    def __init__(self, timer=30):
        self.start = time.perf_counter()
        self.timer = timer

    def time_elapsed_seconds(self):
        return time.perf_counter() - self.start

    def time_elapsed_minutes(self):
        return int((time.perf_counter() - self.start) / 60.0)

    def timer_expired(self):
        return True if (int((time.perf_counter() - self.start) / 60.0) >= self.timer) else False
