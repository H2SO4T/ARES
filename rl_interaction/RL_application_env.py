import re
from gym import Env
import os
import numpy
import time
import subprocess
from loguru import logger
import xml.etree.ElementTree as ET
from gym import spaces
from hashlib import md5
from selenium.common.exceptions import InvalidElementStateException, WebDriverException, \
    StaleElementReferenceException, InvalidSessionIdException, NoSuchElementException, ElementNotVisibleException
from appium.webdriver.common.touch_action import TouchAction
from rl_interaction.utils.utils import Utils
from multiprocessing import Process, Queue
from appium import webdriver
from collections import deque


def search_package_and_setprop(folder):
    '''
    result = subprocess.run(
        ["adb", "shell", "su", "0", "find", "/data/data/", "-type", "d", "-name", f'"{package}*"'],
        capture_output=True)
    folder = result.stdout.decode('utf-8').strip('\n')
    '''
    command = f'adb shell "su 0 setprop jacoco.destfile /data/data/{folder}/jacoco.exec"'
    os.popen(command).read()


def collect_coverage_emma(udid, package, coverage_dir, coverage_count):
    os.system(f'adb -s {udid} shell am broadcast -p {package}  -a edu.gatech.m3.emma.COLLECT_COVERAGE')
    os.system(f'adb -s {udid} pull /mnt/sdcard/coverage.ec {os.path.join(".", coverage_dir, str(coverage_count))}.ec')


def collect_coverage_jacoco(udid, package, coverage_dir, coverage_count):
    os.system(f'adb -s {udid} shell am broadcast -p {package} -a intent.END_COVERAGE')
    os.system(f'adb -s {udid} pull /sdcard/Android/data/{package}/files/coverage.ec '
              f'{os.path.join(".", coverage_dir, str(coverage_count))}.ec')


def bug_handler(bug_queue, udid):
    os.system(f'adb -s {udid} logcat -c')
    proc = subprocess.Popen(['adb', '-s', udid, 'logcat'], stdout=subprocess.PIPE)
    while True:
        dump_bug = ''
        try:
            temp = proc.stdout.readline().decode('utf-8')
        except UnicodeDecodeError:
            temp = ''
        if temp.find('FATAL EXCEPTION') > 0:
            dump_bug += temp[temp.find('FATAL EXCEPTION'):]
            try:
                temp = proc.stdout.readline().decode('utf-8')
            except UnicodeDecodeError:
                temp = ''
            while temp.find('E AndroidRuntime:') > 0:
                dump_bug += temp[temp.find('E AndroidRuntime:'):]
                temp = proc.stdout.readline().decode('utf-8')
            bug_queue.put(dump_bug)


class RLApplicationEnv(Env):

    def __init__(self, coverage_dict, app_path, list_activities,
                 widget_list, bug_set, coverage_dir, log_dir, rotation, internet, merdoso_button_menu, platform_name,
                 platform_version, udid, instr_emma, instr_jacoco,
                 device_name, exported_activities, services, receivers,
                 is_headless, appium, emulator, package, pool_strings, visited_activities: list, clicked_buttons: list,
                 number_bugs: list, appium_port, max_episode_len=250, string_activities='',
                 instr=False, OBSERVATION_SPACE=2000, ACTION_SPACE=30):

        self.OBSERVATION_SPACE = OBSERVATION_SPACE
        self.ACTION_SPACE = ACTION_SPACE
        self.instr = instr
        self.emulator = emulator
        self.appium = appium
        self.exported_activities = deque(exported_activities)
        self.coverage_dir = coverage_dir
        self.log_dir = log_dir
        self.app_path = app_path
        self.appium_port = appium_port
        if instr_emma:
            self.instr = True
            self.instr_funct = collect_coverage_emma
        elif instr_jacoco:
            self.instr = True
            self.instr_funct = collect_coverage_jacoco

        self.rotation = rotation
        self.internet = internet
        self.merdoso_button_menu = merdoso_button_menu
        self.intents = services + receivers
        self.intent_flag = bool(len(self.intents))

        self.shift = self.internet + self.rotation + self.merdoso_button_menu + self.intent_flag
        self.modify_internet_connection = int(self.internet) - 1
        self.do_rotation = self.internet + self.rotation - 1
        self.click_menu_button = self.internet + self.rotation + self.merdoso_button_menu - 1
        self.intent_action = self.internet + self.rotation + self.merdoso_button_menu + self.intent_flag - 1

        self.jacoco_package = package
        self.visited_activities = visited_activities
        self.clicked_buttons = clicked_buttons
        self.number_bugs = number_bugs
        self.bug_set = bug_set
        self.connection = False
        self.bug_queue = Queue()
        self.strings = []
        self.coverage_count = 0
        self.observation = numpy.array([0] * self.OBSERVATION_SPACE)
        self._max_episode_steps = max_episode_len
        self.timesteps = 0
        self.bug = False
        self.outside = False
        # Obtaining reference to external dictionary
        self.coverage_dict = coverage_dict
        self.widget_list = widget_list
        self.views = {}

        self.logger_id = logger.add(os.path.join(self.log_dir, 'action_logger.log'), format="{time} {level} {message}",
                                    level='DEBUG')

        self.bug_logger_id = logger.add(os.path.join(self.log_dir, 'bug_logger.log'), format="{time} {level} {message}",
                                        filter=lambda record: record["level"].name == "CRITICAL")

        logger.debug(self.app_path + ' START')

        self.list_activities = list_activities
        self.udid = udid

        if float(platform_version) >= 5.0:
            automation_name = 'uiautomator2'
        else:
            automation_name = 'uiautomator1'

        self.desired_caps = {'platformName': platform_name,
                             'platformVersion': platform_version,
                             'udid': udid,
                             'deviceName': device_name,
                             'app': self.app_path,
                             'autoGrantPermissions': True,
                             'fullReset': False,
                             'unicodeKeyboard': True,
                             'resetKeyboard': True,
                             'androidInstallTimeout': 30000,
                             'isHeadless': is_headless,
                             'automationName': automation_name,
                             'adbExecTimeout': 30000,
                             'appWaitActivity': string_activities,
                             'newCommandTimeout': 200}

        # search_package_and_setprop(self.jacoco_package)
        self.driver = webdriver.Remote(f'http://127.0.0.1:{self.appium_port}/wd/hub', self.desired_caps)
        # First initialization
        self.package = self.driver.current_package
        self.current_activity = self.rename_activity(self.driver.current_activity)
        self.old_activity = self.current_activity

        # Finding all clickable elements, it updates self.views
        self._md5 = ''
        self.get_all_views()
        # Used to get the reward during an episode
        self.set_activities_episode = {self.current_activity}
        # Adding each button in self.views into the dictionary
        self.update_buttons_in_coverage_dict()
        self.driver.implicitly_wait(0.3)
        # Opening String input
        with open(pool_strings, 'r+') as f:
            self.strings = f.read().split('\n')
        self.bug_proc_pid = self.start_bug_handler()
        # Defining Gym Spaces
        self.action_space = spaces.Box(low=numpy.array([0, 0, 0]),
                                       high=numpy.array([self.ACTION_SPACE, len(self.strings) - 1, 1]),
                                       dtype=numpy.int64)
        self.observation_space = spaces.Box(low=0, high=1, shape=(self.OBSERVATION_SPACE,), dtype=numpy.int32)
        self.dims = self.driver.get_window_size()
        self.check_activity()

    @logger.catch()
    def step(self, action_number):
        try:
            action_number = action_number.astype(int)
            if action_number[0] >= self.get_action_space()[0]:
                return self.observation, numpy.array([-50.0]), numpy.array(False), {}
            else:
                self.timesteps += 1
                return self.step2(action_number)
        except StaleElementReferenceException:
            self.check_activity()
            return self.observation, numpy.array([0.0]), numpy.array(False), {}
        except NoSuchElementException:
            self.check_activity()
            return self.observation, numpy.array([0.0]), numpy.array(False), {}
        except ElementNotVisibleException:
            self.check_activity()
            return self.observation, numpy.array([-50.0]), numpy.array(False), {}
        except WebDriverException as e:
            return self.manager(e)

    def step2(self, action_number):
        # We do a system action
        if self.internet and (action_number[0] == self.modify_internet_connection):
            logger.debug('set connection to ' + str(self.connection))
            self.connection_action()
        # We do a system action
        elif self.rotation and (action_number[0] == self.do_rotation):
            logger.debug('set orientation, original was ' + self.driver.orientation)
            self.orientation()
            time.sleep(0.2)
            try:
                self.dims = self.driver.get_window_size()
            except:
                pass
        elif self.merdoso_button_menu and (action_number[0] == self.click_menu_button):
            logger.debug('pressed menu button')
            self.driver.press_keycode(82)
        elif self.intent_flag and (action_number[0] == self.intent_action):
            mod = action_number[1] % len(self.intents)
            self.generate_intent(mod)
        else:
            action_number[0] = action_number[0] - self.shift
            if len(self.views) == 0:
                self.perform_touch_action(action_number)
                time.sleep(0.05)
            else:
                current_view = self.views[action_number[0]]

                identifier = current_view['identifier']
                self.update_button_in_coverage_dict(identifier)

                # We save the action in queue
                logger.debug(f'action: {identifier} Activity: {self.current_activity}')

                # Do Action
                self.action(current_view, action_number)
                time.sleep(0.2)
        self.bug, self.outside = self.check_activity()
        if self.outside:
            self.outside = False
            # We need to reset the application
            if self.driver.current_activity is None:
                return self.observation, numpy.array([-100.0]), numpy.array(True), {}
            # You should not use an activity named launcher ( ಠ ʖ̯ ಠ)
            elif 'launcher' in self.driver.current_activity.lower():
                return self.observation, numpy.array([-100.0]), numpy.array(True), {}
            # We are in another app, let's go back
            else:
                self.driver.back()
                self.update_views()
                return self.observation, numpy.array([-100.0]), numpy.array(False), {}
        self.get_observation()
        reward = self.compute_reward()
        # self.append_visited_activities_coverage()
        done = self._termination()
        return self.observation, numpy.array([reward]), numpy.array(done), {}

    def action(self, current_view, action_number):
        # If element is android.widget.EditText
        if current_view['class_name'] == 'android.widget.EditText':
            try:
                current_view['view'].clear()
                current_view['view'].click()
                current_string = self.strings[action_number[1]]
                current_view['view'].send_keys(current_string)
                logger.debug('put string: ' + current_string)
            except InvalidElementStateException:
                logger.debug('Impossible to insert string')
                pass

        else:
            # If element is CLICKABLE
            if current_view['clickable'] == 'true' and current_view['long-clickable'] == 'false':
                current_view['view'].click()

            # If element is both CLICKABLE and LONG-CLICKABLE
            elif current_view['clickable'] == 'true' and current_view['long-clickable'] == 'true':
                if action_number[2] == 0:
                    current_view['view'].click()
                else:
                    actions = TouchAction(self.driver)
                    actions.long_press(current_view['view'], duration=1000).release().perform()

            # If element is LONG-CLICKABLE
            elif current_view['clickable'] == 'false' and current_view['long-clickable'] == 'true':
                actions = TouchAction(self.driver)
                actions.long_press(current_view['view'], duration=1000).release().perform()

            # If element is SCROLLABLE
            elif current_view['scrollable'] == 'true':
                bounds = re.findall(r'\d+', current_view['view'].get_attribute('bounds'))
                bounds = [int(i) for i in bounds]
                if (bounds[2] - bounds[0] > 20) and (bounds[3] - bounds[1] > 40):
                    self.scroll_action(action_number, bounds)
                else:
                    pass

    def compute_reward(self):
        # if editText return reward 0, counter on activity
        MAX_REWARD = 1000.0
        if self.bug:
            return MAX_REWARD
        if self.old_activity != self.current_activity:
            if self.current_activity not in self.set_activities_episode:
                self.set_activities_episode.add(self.current_activity)
                return MAX_REWARD
            else:
                return 0.0
        else:
            return -1.0

    def reset(self):
        logger.debug('<--- EPISODE RESET --->')
        self._md5 = ''
        self.timesteps = 0
        '''
        if len(self.exported_activities) > 1:
            try:
                self.driver.quit()
                time.sleep(0.1)
            except:
                pass
            i = 0
            while True:
                try:
                    self.desired_caps['appActivity'] = self.exported_activities[0]
                    self.exported_activities.rotate(1)
                    self.driver = webdriver.Remote(f'http://127.0.0.1:{self.appium_port}/wd/hub', self.desired_caps)
                    break
                except Exception as e:
                    i += 1
                    if i <= len(self.exported_activities):
                        try:
                            self.driver.quit()
                        except:
                            pass
                    else:
                        logger.critical(e)
                        self.manager(e)
        else:
        '''
        try:
            self.driver.reset()
        except Exception as e:
            logger.critical(e)
            self.manager(e)
        self.current_activity = self.rename_activity(self.driver.current_activity)
        self.old_activity = self.current_activity
        self.set_activities_episode = {self.current_activity}
        self.bug, self.outside = self.check_activity()
        self.get_observation()
        return self.observation

    def get_observation(self):
        if self.bug:
            self.observation = numpy.array([0] * self.OBSERVATION_SPACE)
        else:
            observation_0 = self.one_hot_encoding_activities()
            observation_1 = self.one_hot_encoding_widgets()
            self.observation = numpy.array(observation_0 + observation_1)

    def one_hot_encoding_activities(self):
        activity_observation = [0] * len(self.list_activities)
        if self.current_activity in self.list_activities:
            index = self.list_activities.index(self.current_activity)
            activity_observation[index] = 1
        return activity_observation

    def one_hot_encoding_widgets(self):
        widget_observation = [0] * (self.OBSERVATION_SPACE - len(self.list_activities))
        for k, item in self.views.items():
            identifier = item['identifier']
            if identifier in self.widget_list:
                index = self.widget_list.index(identifier)
                widget_observation[index] = 1
        return widget_observation

    def check_activity(self):

        temp_activity = self.rename_activity(self.driver.current_activity)

        # At first I need to check whether it is a bug
        if not self.bug_queue.empty():
            # If the bug is new we add it
            new_bug = self.bug_queue.get()
            self.bug_set.add(new_bug)
            logger.error('A bug occurred, relaunching application')
            logger.critical(new_bug)
            return True, False

        # If it is not a bug we could be outside the application
        elif (self.package != self.driver.current_package) or (temp_activity is None) or \
                (temp_activity.find('com.facebook.FacebookActivity') >= 0):
            return False, True

        # If we have changed the activity:
        elif self.current_activity != temp_activity:
            self.old_activity = self.current_activity
            self.current_activity = temp_activity

        # Updating buttons
        self.update_views()
        return False, False

    def update_views(self):
        i = 0
        while i < 15:
            try:
                self.get_all_views()
                break
            except StaleElementReferenceException as e:
                time.sleep(0.05)
                i += 1
                if i == 15:
                    logger.error('Too Many times tried')
                    self.manager(e)
            except WebDriverException as e:
                self.manager(e)
        if len(self.views) == 0:
            self.action_space.high[0] = self.ACTION_SPACE
        else:
            self.action_space.high[0] = len(self.views) + self.shift

    def get_all_views(self):
        # Searching for clickable elements in XML/HTML source page
        page = self.driver.page_source
        tree = ET.fromstring(page)
        page = page.replace('enabled="true"', '').replace('enabled="false"', '').replace('checked="false"', '') \
            .replace('checked="true"', '')
        temp_md5 = md5(page.encode()).hexdigest()
        if temp_md5 != self._md5:
            self._md5 = temp_md5
            elements = tree.findall(".//*[@clickable='true']") + tree.findall(".//*[@scrollable='true']") + \
                       tree.findall(".//*[@long-clickable='true']")
            self.views = {}
            tags = set([element.tag for element in elements])
            i = 0
            for tag in tags:
                elements = self.driver.find_elements_by_class_name(tag)
                for e in elements:
                    clickable = e.get_attribute('clickable')
                    scrollable = e.get_attribute('scrollable')
                    long_clickable = e.get_attribute('long-clickable')
                    if (clickable == 'true') or (scrollable == 'true') or (long_clickable == 'true'):
                        identifier = self.return_attribute(e)
                        self.views.update({i: {'view': e, 'identifier': identifier, 'class_name': tag,
                                               'clickable': clickable, 'scrollable': scrollable,
                                               'long-clickable': long_clickable}})
                        i += 1
            self.update_buttons_in_coverage_dict()

    def update_button_in_coverage_dict(self, attribute):
        self.coverage_dict[self.current_activity].update({attribute: True})

    def update_buttons_in_coverage_dict(self):
        # Updating activity coverage
        if self.current_activity in self.coverage_dict.keys():
            self.coverage_dict[self.current_activity].update({'visited': True})
        else:
            self.coverage_dict.update(
                {self.current_activity: {'visited': True}})

        # Updating views coverage
        for k, item in self.views.items():
            identifier = item['identifier']
            if identifier not in self.coverage_dict[self.current_activity].keys():
                self.coverage_dict[self.current_activity].update({identifier: False})
            if identifier not in self.widget_list:
                self.widget_list.append(identifier)

    def get_action_space(self):
        return list(self.action_space.high)

    def get_observation_space(self):
        return list(self.observation_space.shape)

    def append_visited_activities_coverage(self):
        visited_activities, pressed_buttons = Utils.compute_coverage(self.coverage_dict)
        self.visited_activities.append(visited_activities)
        self.clicked_buttons.append(pressed_buttons)
        self.number_bugs.append(len(self.bug_set))

    def _termination(self):
        if (self.timesteps >= self._max_episode_steps) or self.bug or self.outside:
            self.bug = False
            self.outside = False
            return True
        else:
            return False

    def manager(self, e):
        if str(e).find('DOM') > -1:
            return self.observation, numpy.array([0.0]), numpy.array(False), {}
        else:
            logger.error(f'E: {e} in app {self.app_path}')
            try:
                self.driver.quit()
            except WebDriverException:
                pass
            self.appium.restart_appium()
            try:
                self.driver = webdriver.Remote(f'http://127.0.0.1:{self.appium_port}/wd/hub', self.desired_caps)
            except Exception:
                if self.emulator is not None:
                    self.emulator.restart_emulator()
                self.driver = webdriver.Remote(f'http://127.0.0.1:{self.appium_port}/wd/hub', self.desired_caps)
            time.sleep(5)
            return self.observation, numpy.array([0.0]), numpy.array(True), {}

    def return_attribute(self, my_view):
        attribute_fields = ['resource-id', 'content-desc']
        attribute = None
        for attr in attribute_fields:
            attribute = my_view.get_attribute(attr)
            if attribute is not None:
                break
        if attribute is None:
            attribute = self.current_activity + '.' + my_view.get_attribute('class') + '.'
            sub_node = my_view.find_elements_by_class_name('android.widget.TextView')
            if len(sub_node) > 0:
                attribute += sub_node[0].get_attribute('text')
            else:
                attribute += my_view.get_attribute('text')
        return attribute

    def connection_action(self):
        # Activate internet connection
        if self.connection:
            self.connection = False
            self.driver.set_network_connection(4)
        else:
            self.connection = True
            self.driver.set_network_connection(0)

    def orientation(self):
        orientation = self.driver.orientation
        if orientation == 'PORTRAIT':
            try:
                self.driver.orientation = 'LANDSCAPE'
            except InvalidElementStateException:
                pass
        else:
            try:
                self.driver.orientation = 'PORTRAIT'
            except InvalidElementStateException:
                pass

    def start_bug_handler(self):
        bug_proc = Process(name='bug_handler', target=bug_handler, args=(self.bug_queue, self.udid))
        bug_proc.daemon = True
        bug_proc.start()
        return bug_proc.pid

    def scroll_action(self, action_number, bounds):
        y = int((bounds[3] - bounds[1]))
        x = int((bounds[2] - bounds[0]) / 2)
        if action_number[2] == 0:
            try:
                self.driver.swipe(x, int(y * 0.3), x, int(y * 0.5), duration=200)
            except InvalidElementStateException:
                logger.error(f'swipe not performed start_position: ({x}, {y}), end_position: ({x}, {y + 20})')
        else:
            try:
                self.driver.swipe(x, int(y * 0.5), x, int(y * 0.3), duration=200)
            except InvalidElementStateException:
                logger.error(f'swipe not performed start_position: ({x}, {y + 20}), end_position: ({x}, {y})')

    def rename_activity(self, actual_activity):
        if actual_activity is not None:
            for activity in self.list_activities:
                if activity.endswith(actual_activity):
                    return activity
        return None

    def perform_touch_action(self, action):
        try:
            act = TouchAction(self.driver)
            x = (self.dims['width'] - 1) * action[0] / (self.ACTION_SPACE - self.shift)
            y = (self.dims['height'] - 1) * action[1] / (len(self.strings) - 1)
            act.tap(x=x, y=y).perform()
            logger.debug(f'action: Touch Action at coordinates:{int(x)}, {int(y)} Activity: {self.current_activity}')
        except Exception:
            pass

    def generate_intent(self, num):
        if len(self.intents[num]["action"]) > 0:
            if self.intents[num]['type'] == 'service':
                command_string = f'adb -s {self.udid} shell su 0 am startservice -n ' \
                                 f'"{self.package}/{self.intents[num]["name"]}" -a "{self.intents[num]["action"][0]}"'
            else:
                command_string = f'adb -s {self.udid} shell su 0 am broadcast -n ' \
                                 f'"{self.package}/{self.intents[num]["name"]}" -a "{self.intents[num]["action"][0]}"'
            # in case there is more than one action
            self.intents[num]["action"].rotate(1)
        else:
            if self.intents[num]['type'] == 'service':
                command_string = f'adb -s {self.udid} shell su 0 am startservice -n ' \
                                 f'"{self.package}/{self.intents[num]["name"]}"'
            else:
                command_string = f'adb -s {self.udid} shell su 0 am broadcast ' \
                                 f'-n "{self.package}/{self.intents[num]["name"]}"'
        if self.emulator is None:
            command_string = command_string.replace('su 0', '')
        os.system(command_string)
