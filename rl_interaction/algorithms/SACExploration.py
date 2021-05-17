import os

import numpy
from gym import spaces
from stable_baselines3.sac.policies import MlpPolicy
from stable_baselines3 import SAC
from rl_interaction.algorithms.ExplorationAlgorithm import ExplorationAlgorithm
from rl_interaction.utils.TimerCallback import TimerCallback
from rl_interaction.utils.wrapper import TimeFeatureWrapper


class SACAlgorithm(ExplorationAlgorithm):

    @staticmethod
    def explore(app, emulator, appium, timesteps, timer, save_policy=False, app_name='', reload_policy=False,
                policy_dir='.', cycle=0, train_freq=5, target_update_interval=10):
        try:
            env = TimeFeatureWrapper(app)
            # Loading a previous policy and checking file existence
            if reload_policy and (os.path.isfile(f'{policy_dir}{os.sep}{app_name}.zip')):
                temp_dim = env.action_space.high[0]
                env.action_space.high[0] = env.env.ACTION_SPACE
                print(f'Reloading Policy {app_name}.zip')
                model = SAC.load(f'{policy_dir}{os.sep}{app_name}', env)
                env.action_space.high[0] = temp_dim
            else:
                print('Starting training from zero')
                model = SAC(MlpPolicy, env, verbose=1, train_freq=train_freq, target_update_interval=target_update_interval)
            callback = TimerCallback(timer=timer, app=app)
            model.learn(total_timesteps=timesteps, callback=callback)
            # It will overwrite the previous policy
            if save_policy:
                print('Saving Policy...')
                model.action_space.high[0] = model.env.envs[0].ACTION_SPACE
                model.save(f'{policy_dir}{os.sep}{app_name}')
            return True
        except Exception as e:
            print(e)
            appium.restart_appium()
            if emulator is not None:
                emulator.restart_emulator()
            return False

