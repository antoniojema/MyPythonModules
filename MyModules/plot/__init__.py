from typing import Tuple
import matplotlib.pyplot as plt
import numpy as np
from typing import Optional, Tuple, List, Callable, Sequence, Union

# Plots a list of data points
def plot(
    xs:List[float],
    ys:List[float],
    logscale:Optional[str]=None,
    func_x:Callable[[List[float]],List[float]]=lambda x: x,
    func_y:Callable[[List[float]],List[float]]=lambda x: x,
    xlabel:str="",
    ylabel:str="",
    grid:bool=True,
    show:bool=True,
    **kwargs
) -> None:
    if logscale is None:
        plt.plot    (func_x(xs), func_y(ys), **kwargs)
    elif logscale == 'x':
        plt.semilogx(func_x(xs), func_y(ys), **kwargs)
    elif logscale == 'y':
        plt.semilogy(func_x(xs), func_y(ys), **kwargs)
    elif logscale == 'xy':
        plt.loglog  (func_x(xs), func_y(ys), **kwargs)
    else:
        raise Exception("logscale must be None, 'x', 'y', or 'xy'")
    
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    if grid:
        plt.grid()

    if show:
        plt.show()

# Plots a list of data points from a file
def plotFromFile(
    file_name:str,
    delimiter:Union[str, int, Sequence]=None,
    cols:Tuple[int,int]=(0,1),
    skip_header:int=0,
    **kwargs
) -> None:
    data : List[List[float]] = np.genfromtxt(file_name, skip_header=skip_header,dtype=float,delimiter=delimiter)
    plot(data[:,cols[0]], data[:,cols[1]], **kwargs)

__all__:List[str] = ['plot','plotFromFile']
