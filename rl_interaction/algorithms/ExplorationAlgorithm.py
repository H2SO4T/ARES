import abc


class ExplorationAlgorithm:
    __metaclass__ = abc.ABCMeta

    @staticmethod
    @abc.abstractmethod
    def explore(app, emulator, appium, timesteps, timer, save_policy, policy_dir, cycle,  **kwargs):
        return "Explore"
