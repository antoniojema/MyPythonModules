from typing import Tuple
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from typing import Optional, Tuple, List, Callable, Sequence, Union, Dict, Any
import os

def formattedFigure(
    subplots_x:int = 1,
    subplots_y:int = 1,
    figsize : Tuple[float,float]=(6.0,4.0),
    font : str = 'serif',
    mathfont : str = 'dejavuserif',
) -> Tuple[plt.figure, Union[plt.Axes, np.ndarray]]:
    # from matplotlib import rc
    # rc('text', usetex=True)

    mpl.rc('font', family=font)
    mpl.rc('mathtext', fontset=mathfont)
    # mpl.rcParams['text.usetex'] = True
    # mpl.rcParams['text.latex.preamble'] = [r'\usepackage{amsmath}'] #for \text command

    fig, ax = plt.subplots(subplots_x, subplots_y, figsize=figsize)

    return fig, ax


# Plots a list of data points
def plot(
    ax:plt.Axes,
    xs:List[float],
    ys:List[float],
    logscale:Optional[str]=None,
    func_x:Callable[[List[float]],List[float]]=lambda x: x,
    func_y:Callable[[List[float]],List[float]]=lambda x: x,
    **kwargs
) -> None:
    if logscale is None:
        ax.plot    (func_x(xs), func_y(ys), **kwargs)
    elif logscale == 'x':
        ax.semilogx(func_x(xs), func_y(ys), **kwargs)
    elif logscale == 'y':
        ax.semilogy(func_x(xs), func_y(ys), **kwargs)
    elif logscale == 'xy':
        ax.loglog  (func_x(xs), func_y(ys), **kwargs)
    else:
        raise Exception("logscale must be None, 'x', 'y', or 'xy'")

def formatPlot(
    ax:plt.Axes,
    title:Optional[str]=None,
    xlabel:Optional[str]=None,
    ylabel:Optional[str]=None,
    title_kwargs:Dict[str, Any]=dict(),
    xlabel_kwargs:Dict[str, Any]=dict(),
    ylabel_kwargs:Dict[str, Any]=dict(),
    xlim:Optional[Tuple[float,float]]=None,
    ylim:Optional[Tuple[float,float]]=None,
    xlim_margin:float=0.02,
    ylim_margin:float=0.02,
    xticks:Optional[Union[List[float], np.ndarray]]=None,
    yticks:Optional[Union[List[float], np.ndarray]]=None,
    xticks_minor:Union[bool, List[float], np.ndarray]=True,
    yticks_minor:Union[bool, List[float], np.ndarray]=True,
    xticks_kwargs:Dict[str, Any]=dict(),
    yticks_kwargs:Dict[str, Any]=dict(),
    grid:bool=True,
    legend:bool=True,
    legend_kwargs:Dict[str, Any]=dict(),
    tight_layout:bool=True,
    savefig:List[str]=[],
    show:bool=True,
) -> None:
    if title is not None:
        ax.set_title(title, **title_kwargs)
    if xlabel is not None:
        ax.set_xlabel(xlabel, **xlabel_kwargs)
    if ylabel is not None:
        ax.set_ylabel(ylabel, **ylabel_kwargs)
    
    if xlim is not None:
        x_extra = xlim_margin * (xlim[1] - xlim[0])
        ax.set_xlim((xlim[0]-x_extra, xlim[1]+x_extra))
    if ylim is not None:
        y_extra = ylim_margin * (ylim[1] - ylim[0])
        ax.set_ylim((ylim[0]-y_extra, ylim[1]+y_extra))

    if xticks is not None:
        ax.set_xticks(xticks)
    if yticks is not None:
        ax.set_yticks(yticks)
    ax.tick_params(axis='x', which='major', **xticks_kwargs)
    ax.tick_params(axis='y', which='major', **yticks_kwargs)

    if type(xticks_minor) is bool:
        if xticks_minor:
            ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    else:
        ax.set_xticks(xticks_minor, minor=True)
    
    if type(yticks_minor) is bool:
        if yticks_minor:
            ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    else:
        ax.set_yticks(xticks_minor, minor=True)

    ax.tick_params(which="major", width=1, length=3)
    ax.tick_params(which="minor", width=1, length=1)

    if legend:
        leg = ax.legend(labelspacing=0.1, borderpad=0, borderaxespad=0.8, **legend_kwargs)
        leg.get_frame().set_edgecolor('black')
        leg.get_frame().set_linewidth(1.0)
        leg.get_frame().set_boxstyle("square")
    if grid:
        ax.grid()
        ax.grid(which='major', color="lightgray", linestyle="-" , linewidth=1)
        ax.grid(which='minor', color="lightgray", linestyle="--", linewidth=1, dashes=(1, 2))
    
    if tight_layout:
        plt.tight_layout()
    
    for save_name in savefig:
        plt.savefig(save_name)

    if show:
        plt.show()


def plotFromFile(
    ax:plt.Axes,
    file_name:os.PathLike,
    delimiter:Union[str, int, Sequence]=None,
    cols:Tuple[int,int]=(0,1),
    skip_header:int=0,
    col1:int=0,
    col2:int=1,
    **kwargs
) -> None:
    data : List[List[float]] = np.genfromtxt(file_name, skip_header=skip_header, dtype=float, delimiter=delimiter)
    plot(ax, data[:,cols[col1]], data[:,col2], **kwargs)

__all__ = ["formattedFigure", "plot", "plotFromFile", "formatPlot"]