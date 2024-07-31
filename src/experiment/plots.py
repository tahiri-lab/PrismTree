""" Plotting functions for the performance analysis. 
"""
from statistics import fmean
import seaborn as sns
from matplotlib.axes import Axes


def plot_data_points(data: dict, alg: str, metric: str, x_axis: str, ax: Axes, color: str) -> None:
    """ Plot data points and mean curve for a given algorithm and metric.

    Args:
        data (dict): the data from the experiments
        alg (str): the algorithm to plot
        metric (str): the metric to plot
        x_axis (str): the value to use as x axis (k or n)
        ax (Axes): the axis to plot on
        color (str): the color to use for the plot
    """
    points = []
    for inst in data.values():
        inst_points = [(inst[x_axis], v) for v in inst[alg][metric]]
        points += inst_points

    points = sorted(points, key=lambda x: x[0])
    x_ticks = sorted(list(set([x for x, _ in points])))
    mean_points = [(x, fmean([y for x_val, y in points if x_val == x])) for x in x_ticks]
    x_values, y_values = zip(*points)
    x_ticks, y_means = zip(*mean_points)

    sns.scatterplot(ax=ax, x=x_values, y=y_values, color=color, label=alg)
    ax.plot(x_ticks, y_means, marker='o', linestyle='-', color=color, label= alg + ' mean')
    ax.set_xticks(x_ticks)


def plot_metric(data: dict, algs: dict[str, str], metric: str, ax1: Axes, ax2: Axes, ax3: Axes) -> None:
    """ Plot the data points and mean curves for a given metric. Plot on one subplot
        for k (number of trees) and one for n (number of leaves).

    Args:
        data (dict): the data from the experiments
        algs (dict[str, str]): 
        metric (str): the metric to plot
        ax1 (Axes): subplot for k
        ax2 (Axes): subplot for n
        ax3 (Axes): subplot for c
    """
    for alg, color in algs.items():
        plot_data_points(data, alg, metric, "k", ax1, color)
        plot_data_points(data, alg, metric, "n", ax2, color)
        plot_data_points(data, alg, metric, "c", ax3, color)
