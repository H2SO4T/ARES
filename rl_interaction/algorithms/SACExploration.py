from stable_baselines.sac.policies import MlpPolicy
from stable_baselines import SAC
from rl_interaction.algorithms.ExplorationAlgorithm import ExplorationAlgorithm
from rl_interaction.utils.TimerCallback import TimerCallback
from rl_interaction.utils.wrapper import TimeFeatureWrapper


class SACAlgorithm(ExplorationAlgorithm):

    @staticmethod
    def explore(app, emulator, appium, timesteps, timer, train_freq=5, target_update_interval=10):
        try:
            env = TimeFeatureWrapper(app)
            model = SAC(MlpPolicy, env, verbose=1, train_freq=train_freq, target_update_interval=target_update_interval)
            callback = TimerCallback(timer=timer, app=app)
            model.learn(total_timesteps=timesteps, callback=callback)
            return True
        except Exception as e:
            print(e)
            appium.restart_appium()
            if emulator is not None:
                emulator.restart_emulator()
            return False

