import os
import subprocess
import time
import pprint
import platform
from multiprocessing import Process
import signal


class Utils:

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

    def __init__(self, port):
        self.port = port
        self.system = platform.system()
        self.start_appium()

    def terminate(self):
        self.process.terminate()
        time.sleep(4.0)

    def start_appium(self):
        if self.system == 'Windows':
            self.process = subprocess.Popen(['appium', '-p', f'{self.port}', '--log-level', 'error:error'],
                                            creationflags=0x00000008)
        else:
            self.process = subprocess.Popen(['appium', '-p', f'{self.port}', '--log-level', 'error:error'])
        os.system('adb start-server')
        time.sleep(4.0)

    def restart_appium(self):
        self.terminate()
        self.start_appium()


class EmulatorLauncher:

    def __init__(self, emu, device_name, android_port, speedup=True):
        self.device_name = '@'+device_name.replace(' ', '_')
        self.emu = emu
        self.android_port = android_port
        self.speedup = speedup
        self.start_emulator()

    def terminate(self):
        # signal.CTRL_C_EVENT
        self.process.send_signal(signal.SIGINT)
        time.sleep(5.0)

    def start_emulator(self):

        if self.emu == 'normal':
            if self.speedup:
                self.process = subprocess.Popen([f'{os.environ["ANDROID_HOME"]}/emulator/emulator', f'{self.device_name}',
                                                 '-port', f'{self.android_port}'])
                time.sleep(15)
            else:
                self.process = subprocess.Popen([f'{os.environ["ANDROID_HOME"]}/emulator/emulator', f'{self.device_name}',
                                                 '-port', f'{self.android_port}', '-no-snapshot', '-no-boot-anim', '-wipe-data'])
                time.sleep(30.0)
        else:
            self.process = subprocess.Popen([f'{os.environ["ANDROID_HOME"]}/emulator/emulator', f'{self.device_name}',
                                             '-port', f'{self.android_port}', '-no-window', '-no-snapshot', '-no-audio',
                                             '-no-boot-anim', '-wipe-data'])
            # Select the time that your machine needs
            time.sleep(30.0)


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
