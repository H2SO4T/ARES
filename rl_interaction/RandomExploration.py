from rl_interaction.ExplorationAlgorithm import ExplorationAlgorithm
from rl_interaction.utils.utils import Timer


class RandomAlgorithm(ExplorationAlgorithm):

    @staticmethod
    def explore(app, emulator, appium, timesteps, timer, **kwargs):
        try:
            app.reset()
            t = Timer(timer)
            while not t.timer_expired():
                action = app.action_space.sample()
                o, _, done, _ = app.step(action)
                if done:
                    app.reset()
            return True
        except Exception:
            appium.restart_appium()
            if emulator is not None:
                emulator.restart_emulator()
            return False
