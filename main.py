from typing import List
from random import sample

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TABLEAU_COLORS

from core.data_model import DataModel
from core.solver.mock_solver import MockSolver


def plot_results(data_model: DataModel, routes: List[List[int]]):
    print(routes)
    x = [i.x for i in data_model.spots]
    y = [i.y for i in data_model.spots]

    spots = data_model.spots

    fig, ax = plt.subplots()

    # Choose a color for each route
    colors = sample(list(TABLEAU_COLORS), k=len(routes)+1)

    ax.scatter(0, 0, s=100, c=colors[-1])

    for idx, route in enumerate(routes):
        px, py = 0, 0
        for elem in route:
            ax.scatter(spots[elem].x, spots[elem].y, s=100, c=colors[idx])
            ax.plot([px, spots[elem].x], [py, spots[elem].y], c=colors[idx])
            px, py = spots[elem].x, spots[elem].y
        ax.plot([px, 0], [py, 0], c=colors[idx])

    for i in data_model.spots:
        ax.annotate(f"{i.id}", (i.x, i.y), fontsize=10)


if __name__ == '__main__':
    data_model = DataModel.from_json('./data.json')
    s = MockSolver(data_model)

    routes = s.solve()

    plot_results(data_model, routes)
    plt.show()
