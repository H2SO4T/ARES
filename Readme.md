[![MacOS Build Status](https://github.com/H2SO4T/ARES/workflows/MacOS/badge.svg)](https://github.com/H2SO4T/ARES/actions?query=workflow%3AMacOS)
[![Ubuntu Build Status](https://github.com/H2SO4T/ARES/workflows/Ubuntu/badge.svg)](https://github.com/H2SO4T/ARES/actions?query=workflow%3AUbuntu)
[![Windows Build Status](https://github.com/H2SO4T/ARES/workflows/Windows/badge.svg)](https://github.com/H2SO4T/ARES/actions?query=workflow%3AWindows)
[![Android Version](https://img.shields.io/badge/Android-6.0%2B-brightgreen.svg?logo=android&logoColor=white)](https://developer.android.com/)
[![Python Version](https://img.shields.io/badge/Python-3.7%2B-green.svg?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-AGPL%20&%20Commercial-blue.svg)](https://github.com/H2SO4T/ARES/blob/master/LICENSE.COMMERCIAL)

# ARES

ARES is a black-box tool that uses Deep Reinforcement Learning to test and explore Android applications.

# Publication

More details about **ARES** can be found in the TOSEM paper "[Deep Reinforcement Learning for Black-Box Testing of Android Apps](https://dl.acm.org/doi/abs/10.1145/3502868)"
Please use the following bibtex entry to cite our work:


```BibTex
@article{10.1145/3502868, 
author = {Romdhana, Andrea and Merlo, Alessio and Ceccato, Mariano and Tonella, Paolo}, 
title = {Deep Reinforcement Learning for Black-Box Testing of Android Apps}, year = {2021}, publisher = {Association for Computing Machinery}, 
issn = {1049-331X}, 
url = {https://doi.org/10.1145/3502868}, doi = {10.1145/3502868}, 
journal = {ACM Trans. Softw. Eng. Methodol.},
keywords = {Deep reinforcement learning, Android testing}}
```

# Demo

![video](docs/ares.gif)

# Requirements

* Android emulator or Android smartphone (more stable)
* MacOS or Ubuntu or Windows
* Python 3.7+

# Compatibility

* Android from 6.0 to 12.0
* OpenAI Gym 

# Installation and Setup

* Install Appium from http://appium.io/docs/en/about-appium/getting-started/; please make sure to set up the 
  environment variables. $ANDROID_HOME and $JAVA_HOME
* Use appium-doctor to check that everything is working correctly
* Create a virtualenv named `venv` in folder ARES (not in rl_interaction):
`virtualenv -p python3 venv` and source it `source venv/bin/activate`
* Go to rl_interaction: `cd rl_interaction`
* Install the requirements `requirements.txt` using the command `pip3 install -r requirements.txt`

# Using the testing Tool (Quick Guide)

* Export PYTHONPATH: ``export PYTHONPATH="path/to/ares"``
* Move yourself to `ares/rl_interaction`
* Generate a folder for the apks, and put them inside
* Activate the venv 
* Start testing

## Testing with emulated devices

* Create one or more Android emulators.
* Run the tests using `parallel_exec.py`:
`python3 parallel_exec.py --instr_jacoco --list_devices "avd-name0 avd-name1 ..." --appium_ports "4270 4277 ..." 
  --android_ports "5554 5556 ..." --path "apps" --timer 60 --rotation --internet --emu headless --platform_version 8.1 
  --iterations 10 --algo SAC --timesteps 4000 --trials_per_app 3`
  
The flag `--instr_jacoco`  is not useful if you are not interested in code coverage.
You don't need to boot the emulators; ARES will do it for you.
To see the avd names of your emulators, you can run `emulator -list-avds`.
There is no need to specify `udids` using emulated devices since ARES will manage them automatically.
Read `Available Flags` for more information.


## Testing with real devices

* Buy one or more Android devices.
* Activate ADB and usb debug.
* Run the testing using `parallel_exec.py`:
`python3 parallel_exec.py --instr_jacoco --real_device --udids "HG*****9 PO********NA" --list_device "lenovo1 levecchio2" 
  --appium_ports "4270 4290" --android_ports "5554 5556" --path "apps" --timer 70 --rotation --internet  
  --platform_version 7.0 --iterations 2 --algo SAC --timesteps 5000 --trials_per_app 3`

With real devices the flag `--list_devices` can contain arbitrary names, while the flag `--udids` must contain 
the real udids of your devices.
You can find the udids using the command `adb devices`
Flag `--real_device` is required.
  
# Available Flags:

* `--instr_emma`,  If you want to collect code coverage with EMMA.
* `--instr_jacoco`,  If you want to collect code coverage using JaCoCo.
  `--save_policy`, You can save an exploration policy of your app and use it in new explorations.
  `--reload_policy`, Tell ARES to reload a previous policy.
* `--real_device`, If you are using a real device you must specify it.
* `--timer: [time_in_minutes]`, You can specify the time to test the app, required=True.
* `--platform_version [android_version]`, You have to specify the android version, default = 10.0 . 
* `--iterations [number_of_iterations]`, How many times you want to repeat the test, default=10 .
* `--algo [algo]`, Choose one between SAC random and Q-Learning (SAC is the algorithm used in the paper).
* `--timesteps`, Number of time steps of each testing, (`--timer` has higher priority ), required=True.
* `--rotation`, If you want to enable rotation.
* `--internet`, If you want to toggle data during testing.
* `--emu`, If you are using an emulator, you need to specify in what mode (normal or headless).
* `--max_timesteps`, You can specify the duration of an episode, default = 250 .
* `--pool_strings`, Name of the file to pick the strings from, default = strings.txt .
* `--list_devices [emulators]`, A list of the device_names (avd_names), required = True.
* `--appium_ports [ports]`, A list of the ports you want to use, required = True.
* `--android_ports [ports]`, A list  of the adb-ports you want to use, required = True.
* `--udids [strings]`, A list of the udids of the real devices, in case you are using 
emulators don't use this flag (ARES will assign udids for you).
* `--trials_per_app`, How many times ARES attempts to launch an app.
* `--path [folders]`,The folder containing all apks, ARES will equally subdivide the apps between the devices available.  

# Testing Phase, Coverage Reports and Logs

During the testing phase several files are generated:
* In a folder named `coverage` you will find all .ec files associated to each app tested organized by algorithm and 
  number of executions.
* In a folder named `logs` you will find the trace of the entire execution (the time, 
  the activity and the operation generated), it is useful to recreate a bug or a specific set of actions. 
  You will also find all the stack traces associated to the generated bugs.
* In a folder named `policies` you will find the policies saved by ARES of your apps.

To automatically instrument apps from source code, you can use COSMO: https://github.com/H2SO4T/COSMO

FATE: https://github.com/H2SO4T/FATE

# Troubleshooting

### Generic Errors:
We strongly suggest using Android 8.1 (to the best of our knowledge, the most stable).
Google emulators are not meant to run for multiple days, and they can have unexpected behaviors due to this. 
ARES integrates many protection systems that save the current session and restart the emulators. However, sometimes the 
emulators are irremediably broken, and you need to delete and recreate them.

### In case of connection errors:
Connection errors usually depend on the emulator, using a real devices can reduce these errors
* At first try to delete and recreate the emulator
* If it does not work, try to reinstall the packages `selenium` and `Appium-Python-Client`

# How To Contribute

If you are interested in the project, please feel free to suggest new features!


# Working with Apple Silicon (M1 SoCs)

Using ARES on Apple Silicon is possible, but the configuration is a bit longer. The configuration steps are identical, except for the Python part.

We have tested this procedure on a Mac Mini 16Gb, Python3.9 and a real device.

## Install Miniconda and Setup
* At first install `miniconda` from https://github.com/conda-forge/miniforge.
* Create a venv using `conda create --name venv` and activate it `conda activate venv`.
* Run `conda install pandas`, `conda install numpy` and `conda install scipy`, and `conda install pyyaml`, `conda install typing_extensions`.

## Installing Pytorch on Apple Silicon

* Run `brew install openblas`
* Then clone pytorch: `git clone --recursive https://github.com/pytorch/pytorch`
* `cd pytorch`
* run `python setup.py build`
* run `python setup.py develop`
* Install the missing packages using pip: `stable_baselines3`, `loguru==0.5.0`, `androguard==3.3.5`, `Appium-Python-Client==1.0.2`, `cloudpickle==1.2.2`, `future==0.18.2` and `gym==0.18.0`
* At last, modify il `parallel_exec.py` at line 99: insert a string with the path to the venv python (use `which python` when the venv is activated)

Now the environt is ready!

# *New* Saving and Reloading Policies

* Use the flags `save-policy` and `reload-policy` to save or reload previous policies in SAC. The policies are saved under the 
  folder `policies` with the same name of the apk file in apps folder. WARNING: If `save-policy` is True, 
  then at the end of the testing the previous policy will be overwritten.
