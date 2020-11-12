from rl_interaction.ExplorationAlgorithm import ExplorationAlgorithm


class TestApp(ExplorationAlgorithm):

    @staticmethod
    def explore(app, emulator, appium, timesteps, timer, **kwargs):
        try:
            app.reset()
            if app.bug:
                with open('error.txt', 'a+') as f:
                    f.write(f'{app.package}\n')
            else:
                with open('success.txt', 'a+') as f:
                    f.write(f'{app.package}\n')
            return True

        except Exception:
            with open('error.txt', 'a+') as f:
                f.write(f'{app.package}\n')
            return True
