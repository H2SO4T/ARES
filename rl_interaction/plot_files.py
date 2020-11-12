import os
from utils.plotter import Plotter

algo_list = ['TD3_bank_app', 'Random_bank_app']
steps = 4000
title = 'TD3 Bank App'
path = 'pickle_files'
Plotter.plot_data(algo_list=algo_list, N=5, steps=steps, title=title, path=path)
