from typing import Tuple
import matplotlib.pyplot as plt
import numpy as np
from typing import Optional, Tuple, List, Callable, Sequence, Union

def plotFromFile(
    file_name:str,
    delimiter:Union[str, int, Sequence]=None,
    cols:Tuple[int,int]=(0,1),
    skip_header:int=0,
    logscale:Optional[str]=None,
    func_x:Callable[[List[float]],List[float]]=lambda x: x,
    func_y:Callable[[List[float]],List[float]]=lambda x: x,
    show:bool=True,
    **kwargs
) -> None:
    data : List[List[float]] = np.genfromtxt(file_name, skip_header=skip_header,dtype=float,delimiter=delimiter)
    
    if logscale is None:
        plt.plot    (func_x(data[:,cols[0]]), func_y(data[:,cols[1]]), **kwargs)
    elif logscale == 'x':
        plt.semilogx(func_x(data[:,cols[0]]), func_y(data[:,cols[1]]), **kwargs)
    elif logscale == 'y':
        plt.semilogy(func_x(data[:,cols[0]]), func_y(data[:,cols[1]]), **kwargs)
    elif logscale == 'xy':
        plt.loglog  (func_x(data[:,cols[0]]), func_y(data[:,cols[1]]), **kwargs)
    else:
        raise Exception("logscale must be None, 'x', 'y', or 'xy'")
    
    if show:
        plt.show()

__all__:List[str] = ['plotFromFile']
