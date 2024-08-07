""" Plotting functions for the performance analysis. 
"""
from statistics import fmean
import seaborn as sns
from matplotlib.axes import Axes
from math import log


def plot_complexity(data: list, alg: str, x_axis: str, ax: Axes, color: str, scale: float):
    """ Plot algorithm theorical complexity for varying n or k

    Args:
        data (list[dict]): result from eval_consensus
        alg (str): the alg to plot the complexity of
        x_axis (str): the x axis of the plot (n or k)
        ax (Axes): the subplot to plot on
        color (str): color of the curve
        scale (float): a scale factor so the curve can be compared to execution time
    """
    points = []
    distinct_k = sorted(list(set(inst["k"] for inst in data)))
    distinct_n = sorted(list(set(inst["n"] for inst in data)))
    mean_k = fmean(distinct_k)
    mean_n = fmean(distinct_n)
    if x_axis == "k":
        distinct_x = distinct_k
    else:
        distinct_x = distinct_n

    for x in distinct_x:
        if alg == "pct":
            label = "nk*log(nk)*scale_factor"
            if x_axis == "k":
                points.append((x, (mean_n*x*log(mean_n*x))*scale))
            elif x_axis == "n":
                points.append((x, (mean_k*x*log(mean_k*x))*scale))
        else:
            raise NotImplementedError()

    points = sorted(points, key=lambda x: x[0])
    x_ticks = sorted(list(set([x for x, _ in points])))
    x_values, y_values = zip(*points)

    ax.plot(x_values, y_values, marker='o', linestyle='-', color=color, label=label)
    ax.set_xticks(x_ticks)


def plot_data_points(data: list, alg: str, metric: str, x_axis: str, ax: Axes, color: str) -> None:
    """ Plot data points and mean curve for a given algorithm and metric.

    Args:
        data (list): the data from the experiments
        alg (str): the algorithm to plot
        metric (str): the metric to plot
        x_axis (str): the value to use as x axis (k or n)
        ax (Axes): the axis to plot on
        color (str): the color to use for the plot
    """
    points = []
    for inst in data:
        points.append((inst[x_axis], inst[alg][metric]))

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
