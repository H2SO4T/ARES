import os
import platform
import subprocess
import argparse


def close_old_appium_services():
    system = platform.system()
    if system == 'Windows':
        os.system('taskkill /f /im node.exe')
    else:
        os.system('killall node')
        os.system('adb start-server')


def main():
    parser = argparse.ArgumentParser()
    # list of emulators
    parser.add_argument('--list_devices', help='delimited list input', type=str, required=True)
    # put --instr flag in case you want to collect code coverage
    parser.add_argument('--instr', default=False, action='store_true')
    # activate this flag in case you want to run ARES on real devices
    parser.add_argument('--real_device', default=False, action='store_true')
    parser.add_argument('--appium_ports', help='delimited list input', type=str, required=True)
    parser.add_argument('--android_ports', help='android ports e.g. 5554 5556 ...', type=str, required=True)
    parser.add_argument('--udids', type=str, required=False)
    # the folders to pick apks from
    parser.add_argument('--paths', help='list of folders', type=str, required=True)
    # set a timer for testing
    parser.add_argument('--timer', help='timer duration', type=int, required=True)
    # select platform version
    parser.add_argument('--platform_version', type=str, default='10.0')
    # how many times do you want to repeat the test ?
    parser.add_argument('--iterations', type=int, default=10)
    # choose one
    parser.add_argument('--algo', choices=['TD3', 'SAC', 'random', 'Q', 'DDPG', 'test'], type=str, required=True)
    # in case you want to test using timesteps
    parser.add_argument('--timesteps', type=int, required=True)
    # enable if you want to use rotation
    parser.add_argument('--rotation', default=False, action='store_true')
    # enable if you want to toggle internet data
    parser.add_argument('--internet', default=False, action='store_true')
    # in case you are using an emulator you can select between normal or headless (faster)
    parser.add_argument('--emu', choices=['normal', 'headless'], type=str, required=False)
    # Episode duration
    parser.add_argument('--max_timesteps', type=int, default=250)
    # file of strings.txt (one string per line)
    parser.add_argument('--pool_strings', type=str, default='strings.txt')
    parser.add_argument('--trials_per_app', type=str, default=1)

    args = parser.parse_args()
    algo = args.algo
    trials_per_app = args.trials_per_app
    instr = args.instr
    rot = args.rotation
    internet = args.internet
    real_device = args.real_device
    emu = args.emu
    close_old_appium_services()
    # Emulator names
    device_names = args.list_devices.split(" ")
    # Appium ports
    appium_ports = [int(p) for p in args.appium_ports.split(" ")]
    android_ports = [int(a_p) for a_p in args.android_ports.split(" ")]
    app_paths = args.paths.split(" ")
    timer = args.timer
    timesteps = args.timesteps
    max_timesteps = args.max_timesteps
    pool_strings = args.pool_strings
    android_v = args.platform_version
    iterations = args.iterations
    assert len(device_names) == len(appium_ports) == len(android_ports) == len(app_paths)
    udids = []
    # Setting emulator names
    if real_device:
        udids = [str(u) for u in args.udids.split(" ")]
    else:
        for port in android_ports:
            udids.append(f'emulator-{port}')

    # Set app path
    processes = []
    for i in range(len(device_names)):
        # it searches a venv
        py = os.path.join(__file__, os.pardir, os.pardir, 'venv', 'bin', 'python')
        py = os.path.abspath(py)
        script = os.path.abspath(os.path.join(__file__, os.pardir, 'test_application.py'))
        cmd = [py, script, '--algo', algo, '--appium_port',
               str(appium_ports[i]), '--timesteps', str(timesteps), '--iterations', str(iterations),
               '--udid', str(udids[i]), '--android_port', str(android_ports[i]), '--device_name', device_names[i],
               '--app_path', app_paths[i], '--max_timesteps', str(max_timesteps), '--pool_strings', pool_strings,
               '--timer', str(timer), '--platform_version', android_v, '--trials_per_app', str(trials_per_app)]
        if emu is not None:
            cmd = cmd + ['--emu', emu]
        if instr:
            cmd.append('--instr')
        if rot:
            cmd.append('--rotation')
        if internet:
            cmd.append('--internet')
        if real_device:
            cmd.append('--real_device')
        processes.append(subprocess.Popen(cmd))

    exit_codes = [p.wait() for p in processes]


if __name__ == '__main__':
    main()
