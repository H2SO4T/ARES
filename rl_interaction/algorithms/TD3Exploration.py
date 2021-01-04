import os

from stable_baselines import TD3
from stable_baselines.td3.policies import MlpPolicy
from rl_interaction.algorithms.ExplorationAlgorithm import ExplorationAlgorithm
from rl_interaction.utils.TimerCallback import TimerCallback
from rl_interaction.utils.wrapper import TimeFeatureWrapper


class TD3Algorithm(ExplorationAlgorithm):

    @staticmethod
    def explore(app, emulator, appium, timesteps, timer, save_policy, policy_dir,
                cycle, train_freq=10, random_exploration=0.8):
        try:
            env = TimeFeatureWrapper(app)
            model = TD3(MlpPolicy, env, verbose=1, train_freq=train_freq, random_exploration=random_exploration)
            callback = TimerCallback(timer=timer)
            model.learn(total_timesteps=timesteps, callback=callback)
            if save_policy:
                model.save(f'{policy_dir}{os.sep}{cycle}')
            return True
        except Exception:
            appium.restart_appium()
            if emulator is not None:
                emulator.restart_emulator()
            return False
