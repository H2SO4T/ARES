
# ARES

ARES is a tool based on Appium, it uses Deep Reinforcement Learning to test and explore Android applications.


# Requirements

* python3
* Android emulator or smartphone
* MacOS or Ubuntu or Windows
* python3.5 and above

# Compatible with

* Android from 6.0 to 10.0

# Installation and Setup

* Install Appium, please make sure to setup the environment variables $ANDROID_HOME and $JAVA_HOME, it is a common error to forget them !
* Use appium-doctor to check that everything is working correctly
* Create a virtualenv named `venv` in folder ARES (not in rl_interaction)
* Install the requirements in file `requirements.txt` using the command `pip3 install -r requirements.txt`
* ! In case of errors make sure that `Tensorflow` and `stable_baselines` are correctly installed (check also the package `mpi4py`)


# Using the testing Tool (Quick Guide)

* export PYTHONPATH: ``export PYTHONPATH="path/to/ares``
* move yourself to `ares/rl_interaction`
* Generate a folder for apks, and put the apks inside
* Activate the venv 
* Start testing

## For emulated devices

* Create one or more Android emulators.

* Run the testing using `parallel_exec.py`:

`python3 parallel_exec.py --list_devices "avd-name0 avd-name1 ..." --appium_ports "4273 4276..." --android_ports "5554 5556 ..." --paths "folder0 folder1 ..." --timer 60 --emu headless --platform_version 10.0 --iterations 10 --algo SAC --timesteps 4000`
 
 You don't need to boot the emulators, ARES will do it for you.
 In this case there is no need to specify `udids` since ARES will manage them automatically.
 Read `Detailed Guide` for more information.


## For real devices

* Buy one or more Android device

* Run the testing using `parallel_exec.py`:

`python3 parallel_exec.py --real_device --list_devices "placeholder0 palceholder1 ..." --udids "udid0 udid1 ..." --appium_ports "4273 4276..." --android_ports "5554 5556 ..." --paths "folder0 folder1 ..." --timer 60 --platform_version 10.0 --iterations 10 --algo SAC --timesteps 4000`

Despite what we are doing with emulators `list_devices` is not useful when dealing with real devices. 
`--real_device` is required. 


# Scripts

You can run ARES from two different scripts:
* parallel_exec.py
* test_application.py

The main script is `parallel_exec.py` and allows you to test one or multiple devices at the same time, e.g.:

`python3 parallel_exec.py --list_emulators "test0 test1" --appium_ports "4273 4276" --android_ports "5554 5556" --paths "folder0 folder1" --timer 60 --emu headless --platform_version 10.0 --iterations 10 --algo SAC --timesteps 4000`

In case you want to test a single device you can also use `test_application.py`:

`python3 test_application.py --instr --algo DDPG --emu normal --appium_port 4723 --iterations 10 --max_timesteps 250 --udid emulator-5554 --platform_version 9.0 --timer 10 --app_path folder0`

Once you launch one of the scripts, ARES starts the testing of the apks on your device.
Please be informed that the device-related data will be removed during boot (only if you are using an emulator). 


# Detailed Guide

Available flags (in common):

* `--instr`,  If you want to collect code coverage
* `--real_device`, If you are using a real device you must specify it
* `--timer: [time_in_minutes]`, you can specify the time to test the app, required=True
* `--platform_version [android_version]`, you have to specify the android version, default = 10.0 
* `--iterations [number_of_iterations]`, how many times you want to repeat the test, default=10
* `--algo [algo]`, choose one between TD3, SAC, DDPG, random, Q-Learning
* `--timesteps`, number of time steps of each testing, (`--timer` has higher priority ), required=True
* `--rotation`, If you want to enable rotation
* `--internet`, If you want to toggle data during testing
* `--emu`, if you are using an emulator, you need to specify in what mode (normal or headless)
* `--max_timesteps`, you can specify the duration of an episode, default = 250
* `--pool_strings`, name of the file to pick the strings from, default = strings.txt

`parallel_exec.py` uses the following flags:

* `--list_devices [emulators]`, a list of the device_names (avd_names), required = True
* `--appium_ports [ports]`, a list of the ports you want to use, required = True
* `--android_ports [ports]`, a list  of the adb-ports you want to use, required = True
* `--udids [strings]`, a list of the udids of the real devices, in case you are using 
emulators don't use this flag (ARES will assign udids for you) 
* `--paths [folders]`,a list of the apk paths (one folder per emulator)


`test_application.py` uses flags:
* `--device_name [one_or_more_devices]`, if you are using an emulator `device_name` must specify the `avd-name`of your device, default = test0
* `--appium_port [number]`, you can specify the appium port, required = True
* `--udid [udid_string]`, using the command `adb devices` you can find the udid of you device/emulator, 
default = emulator-5554
*  `--app_path [folder]`, you have to specify the folder name of the apks, default = apps
* `--android_port`, the adb-port to use


# Testing Phase

During the testing phase several files are generated:

* In a folder named `coverage` you will find all .ec files associated to each app tested organized by algorithm and number of run.
* In a folder named `logs` you will find the trace of the entire run, it is useful to recreate a bug or a specific set of actions. You will also find all the stack traces associated to the produced bugs.






