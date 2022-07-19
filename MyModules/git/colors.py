from typing import Set
import colorama, os, psutil

# Init colorama if windows #
if ("cmd" in str(psutil.Process(os.getpid()).parent().name)):
    colorama.init(autoreset=True)


stdcolors : Set[str] = {
    "red" : colorama.Fore.RED,
    "green" : colorama.Fore.GREEN,
    "yellow" : colorama.Fore.YELLOW,
    "blue" : colorama.Fore.BLUE,
    "magenta" : colorama.Fore.MAGENTA,
    "cyan" : colorama.Fore.CYAN,
    "brightgreen" : colorama.Style.BRIGHT + colorama.Fore.GREEN,
    "brightyellow" : colorama.Style.BRIGHT + colorama.Fore.YELLOW,
    "brightred" : colorama.Style.BRIGHT + colorama.Fore.RED,
    
    "reset" : colorama.Style.RESET_ALL,
}


def printColor(
    text : str,
    color : str,
    endcolor : str = colorama.Style.RESET_ALL,
    flush:bool=True,
    **kwargs
) -> None:
    print(f"{color}{text}{endcolor}", **kwargs, flush=flush)


def exitOnError(text : str, **kwargs):
    printColor(text, stdcolors["brightred"], **kwargs)
    exit(1)
