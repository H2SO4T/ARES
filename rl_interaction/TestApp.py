from rl_interaction.ExplorationAlgorithm import ExplorationAlgorithm


class TestApp(ExplorationAlgorithm):

    @staticmethod
    def explore(app, emulator, appium, timesteps, timer, **kwargs):
        try:
            app.reset()
            if app.bug:
                return False
            else:
                return True
        except Exception:
            return False
