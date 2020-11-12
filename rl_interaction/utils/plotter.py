import pickle
import matplotlib.pyplot as plt
import matplotlib.colors as color


class Plotter:

    @staticmethod
    def plot_data(algo_list, N, steps, title, path):
        y_activities = []
        y_buttons = []
        y_bugs = []
        for name in algo_list:
            for i in range(N):
                y_activities.append(Plotter.load_pickle(path + '/' + name + '_activities_'
                                                        + str(i) + '.pkl')[0:steps])
                y_buttons.append(Plotter.load_pickle(path + '/' + name + '_buttons_'
                                                     + str(i) + '.pkl')[0:steps])
                y_bugs.append(Plotter.load_pickle(path + '/' + name + '_bugs_'
                                                  + str(i) + '.pkl')[0:steps])
        y_a = []
        y_b = []
        y_bgs = []
        i = 0
        for j in range(len(algo_list)):
            y_a.append([sum(x) / N for x in zip(*y_activities[i:i + N])])
            y_b.append([sum(x) / N for x in zip(*y_buttons[i:i + N])])
            y_bgs.append([sum(x) / N for x in zip(*y_bgs[i:i + N])])
            i += N
        Plotter.matplot(y_a, algo_list, 'Activities Coverage ' + title)
        Plotter.matplot(y_b, algo_list, 'Buttons Coverage ' + title)
        Plotter.matplot(y_bgs, algo_list, 'Bugs Coverage ' + title)

    @staticmethod
    def matplot(y, y_labels, title):
        colors = list(color.BASE_COLORS.keys())
        fig, ax = plt.subplots()
        for i in range(len(y)):
            ax.plot(y[i], colors[i], label=y_labels[i])
        ax.set(xlabel='simulation Steps', title=title)
        ax.legend(loc='lower right')
        ax.grid()
        fig.savefig('figs/' + title + '.png')

    @staticmethod
    def load_pickle(path):
        return pickle.load(open(path, 'rb'))
