
# ARES

ARES is a black-box tool that uses Deep Reinforcement Learning to test and explore Android applications.

# Publication

More details about **ARES** can be found in the pre-print paper "[Deep Reinforcement Learning for Black-Box Testing of Android Apps](https://arxiv.org/abs/2101.02636)"
Please use the following bibtex entry to cite our work:

```BibTex
@misc{romdhana2021deep,
      title={Deep Reinforcement Learning for Black-Box Testing of Android Apps}, 
      author={Andrea Romdhana and Alessio Merlo and Mariano Ceccato and Paolo Tonella},
      year={2021},
      eprint={2101.02636},
      archivePrefix={arXiv},
      primaryClass={cs.SE}
}
```


# Requirements

* Android emulator or Android smartphone (more stable)
* MacOS or Ubuntu or Windows
* python 3.5 to 3.7 (tensorflow limitation)

# Compatibility

* Android from 6.0 to 10.0
* OpenAI Gym 

# Installation and Setup

* Install Appium from http://appium.io/docs/en/about-appium/getting-started/; please make sure to set up the 
  environment variables. $ANDROID_HOME and $JAVA_HOME
* Use appium-doctor to check that everything is working correctly
* Create a virtualenv named `venv` in folder ARES (not in rl_interaction):
`virtualenv -p python3 venv` and source it `source venv/bin/activate`
* Go to rl_interaction: `cd rl_interaction`
* Install the requirements `requirements.txt` using the command `pip3 install -r requirements.txt`
* In case of errors make sure that `tensorflow` and `stable_baselines` are installed, 
  you can also check the package `mpi4py` (see Troubleshooting)

# Using the testing Tool (Quick Guide)

* Export PYTHONPATH: ``export PYTHONPATH="path/to/ares``
* Move yourself to `ares/rl_interaction`
* Generate a folder for apks, and put the apks inside
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
You can find the udids using the command `adb devices``  
Flag `--real_device` is required.
  
# Available Flags:

* `--instr_emma`,  If you want to collect code coverage with EMMA.
* `--instr_jacoco`,  If you want to collect code coverage using JaCoCo.
  `--save_policy`, you can save an exploration policy of your app and use it in new explorations.
* `--real_device`, If you are using a real device you must specify it.
* `--timer: [time_in_minutes]`, you can specify the time to test the app, required=True.
* `--platform_version [android_version]`, you have to specify the android version, default = 10.0 . 
* `--iterations [number_of_iterations]`, how many times you want to repeat the test, default=10 .
* `--algo [algo]`, choose one between TD3, SAC, DDPG, random, Q-Learning (we strongly suggest SAC).
* `--timesteps`, number of time steps of each testing, (`--timer` has higher priority ), required=True.
* `--rotation`, If you want to enable rotation.
* `--internet`, If you want to toggle data during testing.
* `--emu`, if you are using an emulator, you need to specify in what mode (normal or headless).
* `--max_timesteps`, you can specify the duration of an episode, default = 250 .
* `--pool_strings`, name of the file to pick the strings from, default = strings.txt .
* `--list_devices [emulators]`, a list of the device_names (avd_names), required = True.
* `--appium_ports [ports]`, a list of the ports you want to use, required = True.
* `--android_ports [ports]`, a list  of the adb-ports you want to use, required = True.
* `--udids [strings]`, a list of the udids of the real devices, in case you are using 
emulators don't use this flag (ARES will assign udids for you).
* `--trials_per_app`, how many times ARES attempts to launch an app.
* `--path [folders]`,the folder containing all apks, ARES will equally subdivide the apps between the devices available.  

# Testing Phase, Coverage Reports and Logs

During the testing phase several files are generated:
* In a folder named `coverage` you will find all .ec files associated to each app tested organized by algorithm and 
  number of executions.
* In a folder named `logs` you will find the trace of the entire execution (the time, 
  the activity and the operation generated), it is useful to recreate a bug or a specific set of actions. 
  You will also find all the stack traces associated to the generated bugs.
* In a folder named `policies` you will find the policies saved by ARES of your apps.

To automatically instrument apps from source code, you can use COSMO: https://github.com/H2SO4T/COSMO


# Troubleshooting

### Generic Errors:
We strongly suggest using Android 8.1 (to the best of our knowledge, the most stable).
Google emulators are not meant to run for multiple days, and they can have unexpected behaviors due to this. 
ARES integrates many protection systems that save the current session and restart the emulators. However, sometimes the 
emulators are irremediably broken, and you need to delete and recreate them.

### If MPI does not work

ARES works also if MPI does not work, you can comment the references to DDPG from rl_interaction/test_application.py:
line 9:
```python
from rl_interaction.algorithms.DDPGExploration import DDPGAlgorithm
``` 
and lines 191-192:
```python   
elif algo == 'DDPG':
    algorithm = DDPGAlgorithm()
```

### In case of connection errors:
Connection errors usually depend on the emulator, using a real devices can reduce these errors
* At first try to delete and recreate the emulator
* If it does not work, try to reinstall the packages `selenium` and `Appium-Python-Client`
