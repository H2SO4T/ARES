import time
from stable_baselines import DDPG
from stable_baselines.ddpg.policies import MlpPolicy
from rl_interaction.ExplorationAlgorithm import ExplorationAlgorithm
from rl_interaction.utils.TimerCallback import TimerCallback
from rl_interaction.utils.wrapper import TimeFeatureWrapper


class DDPGAlgorithm(ExplorationAlgorithm):

    @staticmethod
    def explore(app, emulator, appium, timesteps, timer, nb_train_steps=10, random_exploration=0.7):
        try:
            env = TimeFeatureWrapper(app)
            model = DDPG(MlpPolicy, env, verbose=1, random_exploration=random_exploration,
                         nb_train_steps=nb_train_steps)
            callback = TimerCallback(timer=timer)
            model.learn(total_timesteps=timesteps, callback=callback)
            return True
        except Exception:
            appium.restart_appium()
            emulator.restart_emulator()
            return False
