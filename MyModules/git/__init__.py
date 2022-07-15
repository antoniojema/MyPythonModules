from tabnanny import check
from typing import List, Set, Optional, Union
from pathlib import Path
from subprocess import Popen, PIPE
import sys, colorama, os, psutil
import json


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


class GitOptions:
    list = ["status", "commit", "push", "pull"]
    
    def __init__(self, status:bool, commit:bool, push:bool, pull:bool) -> None:
        args = list(locals().keys())
        args.remove("self")
        assert args == GitOptions.list, \
            "Arguments in GitOptions.__init__() do not match possible options."

        self.status = status
        self.commit = commit
        self.push = push
        self.pull = pull


def printBasicHelp(options: List[str], default_options: List[str]) -> None:
    print("")
    with open(Path(__file__).parent / "basic_help.txt", "r") as fin:
        for line in fin:
            print(line, end="")


def printHelp(options: List[str], default_options: List[str]) -> None:
    printBasicHelp(options, default_options)
    print("")
    with open(Path(__file__).parent / "more_help.txt", "r") as fin:
        for line in fin:
            print(line, end="")


def printHelpAndExit(options: List[str], default_options: List[str], only_basic : bool = False, exit_code: int = 0) -> None:
    if only_basic:
        printBasicHelp(options, default_options)
        print(f"\nFor more detailed information, use flag --help/-h")
    else:
        printHelp(options, default_options)
    exit(exit_code)


def createIfNotExists(path : Path, dir_error : bool = True) -> None:
    json_path = Path(__file__).parent / "config.json"
    if not json_path.exists():
        with open(json_path, "w") as fout:
            json.dump(dict(), fout)
    elif dir_error and json_path.is_dir():
        exitOnError(f"YOU SHOULD NEVER SEE THIS: {path} is a directory.")


def listOneConfig(config_list : dict, label : str) -> None:
    error : bool = True
    config = config_list[label]
    if not type(config) is dict:
        exitOnError(f"YOU SHOULD NEVER SEE THIS: Configuration {label} is not a dictionary.")
    types : dict = {"repos" : "Repositories", "search" : "Search directories", "ignore" : "Ignore directories"}
    for t in types:
        if t in config:
         if len(config[t]) > 0:
            if not type(config[t]) is list:
                exitOnError(f"YOU SHOULD NEVER SEE THIS: A type in the config {label} is not a list.")
            error = False
            print(f"\n        {types[t]}:")
            for dir in config[t]:
                if not type(dir) is str:
                    exitOnError(f"YOU SHOULD NEVER SEE THIS: A directory in the config {label} is not a string.")
                print(f"            {dir}")
    
    if error:
        exitOnError(f"Error: configuration {label} is empty.")


def listConfigsAndExit(specific : List[str] = [], verbose : bool = False) -> None:
    json_path : Path = Path(__file__).parent / "config.json"
    createIfNotExists(json_path)
    
    with json_path.open() as fin:
        data = json.load(fin)
    if not type(data) is dict:
        exitOnError("YOU SHOULD NEVER SEE THIS: json.load() did not return dictionary.")
    
    if len(specific) == 0:
        if len(data) == 0:
            print("\nThere are no saved configurations.")
        else:
            print("\nConfigurations:")    
            for key in data:
                print(('\n' if verbose else '') + f"    {key}")
                if (verbose):
                    listOneConfig(data, key)
    else:
        print("\nConfigurations:")
        for key in specific:
            if key not in data:
                exitOnError(f"ERROR: Configuration {key} does not exist.")
        print("\nConfigurations:")
        for key in specific:
            print(f"\n    {key}")
            listOneConfig(data, key)
    
    exit(0)


def readJSON(
    use_config_list : List[str],
    dir_list        : List[str],
    search_list     : List[str],
    ignore_list     : List[str]
) -> None:
    json_path : Path = Path(__file__).parent / "config.json"
    createIfNotExists(json_path)
    
    with json_path.open() as fin:
        data = json.load(fin)
    if not type(data) is dict:
        exitOnError("YOU SHOULD NEVER SEE THIS: json.load() did not return dictionary.")
    
    for label in use_config_list:
        if label not in data:
            exitOnError(f"ERROR: Configuration {label} does not exist.")
    
    for label in use_config_list:
        config = data[label]
        if not type(config) is dict:
            exitOnError(f"YOU SHOULD NEVER SEE THIS: Configuration {label} is not a dictionary.")
        
        for t in config:
            if t not in ["repos", "search", "ignore"]:
                exitOnError(f"YOU SHOULD NEVER SEE THIS: Type {t} in the config {label} is not a valid type.")
            if len(config[t]) > 0:
                if not type(config[t]) is list:
                    exitOnError(f"YOU SHOULD NEVER SEE THIS: A type in the config {label} is not a list.")
                for dir in config[t]:
                    if not type(dir) is str:
                        exitOnError(f"YOU SHOULD NEVER SEE THIS: A directory in the config {label} is not a string.")
                    (dir_list if t =="repos" else (search_list if t == "search" else ignore_list)).append(dir)


def writeJSON(
    set_config_list : List[str],
    dir_list        : List[str],
    search_list     : List[str],
    ignore_set      : Set [str]
) -> None:
    json_path : Path = Path(__file__).parent / "config.json"
    createIfNotExists(json_path)
    
    with json_path.open() as fin:
        data = json.load(fin)
    if not type(data) is dict:
        exitOnError("YOU SHOULD NEVER SEE THIS: json.load() did not return dictionary.")
    
    ignore_list = sorted(ignore_set)
    for label in set_config_list:
        if label in data:
            inp = ""
            while inp not in ["y", "n"]:
                printColor(f"WARNING: Configuration {label} already exists. Overwrite? [y/n]", stdcolors["yellow"])
                inp = input().lower()
            if inp == "n":
                continue
        
        data[label] = dict()
        config = data[label]

        if len(dir_list) > 0:
            config["repos"] = list()
            for dir in dir_list:
                config["repos"].append(str(dir))
        
        if len(search_list) > 0:
            config["search"] = list()
            for dir in search_list:
                config["search"].append(str(dir))

        if len(ignore_list) > 0:
            config["ignore"] = list()
            for dir in ignore_list:
                config["ignore"].append(str(dir))

    with json_path.open("w") as fout:
        json.dump(data, fout, indent=4)


def deleteJSON(del_config_list : List[str]) -> None:
    json_path : Path = Path(__file__).parent / "config.json"
    createIfNotExists(json_path)
    
    with json_path.open() as fin:
        data = json.load(fin)
    if not type(data) is dict:
        exitOnError("YOU SHOULD NEVER SEE THIS: json.load() did not return dictionary.")
    
    for label in del_config_list:
        if label not in data:
            exitOnError(f"ERROR: Configuration {label} does not exist.")
    
    printColor("WARNING: The following configurations will be deleted:", stdcolors["yellow"])
    for label in del_config_list:
        printColor(f"    {label}", stdcolors["yellow"])
    inp = ""
    while inp not in ["y", "n"]:
        printColor("Continue? [y/n]", stdcolors["yellow"])
        inp = input().lower()
    
    if inp == "y":
        for label in del_config_list:
            del data[label]
        with json_path.open("w") as fout:
            json.dump(data, fout, indent=4)

    exit(0)


# Used to delete any directory in the JSON that does not exist anymore #
def purgeJSON() -> None:
    json_path : Path = Path(__file__).parent / "config.json"
    createIfNotExists(json_path)
    
    with json_path.open() as fin:
        data = json.load(fin)
    if not type(data) is dict:
        exitOnError("YOU SHOULD NEVER SEE THIS: json.load() did not return dictionary.")
    
    print("")
    something_done : bool = False
    for label in data:
        config = data[label]
        if not type(config) is dict:
            exitOnError(f"YOU SHOULD NEVER SEE THIS: Configuration {label} is not a dictionary.")
        for t in config:
            if t not in ["repos", "search", "ignore"]:
                exitOnError(f"YOU SHOULD NEVER SEE THIS: Type {t} in the config {label} is not a valid type.")
            if len(config[t]) > 0:
                if not type(config[t]) is list:
                    exitOnError(f"YOU SHOULD NEVER SEE THIS: A type in the config {label} is not a list.")
                for dir in config[t]:
                    if not type(dir) is str:
                        exitOnError(f"YOU SHOULD NEVER SEE THIS: A directory in the config {label} is not a string.")
                    if not Path(dir).is_dir():
                        something_done = True
                        print(f"Purging: {label} > {t} > {dir}")
                        config[t].remove(dir)

    with json_path.open("w") as fout:
        json.dump(data, fout, indent=4)
    
    if not something_done:
        print("Nothing to purge")
    else:
        printColor("\n-- Purge complete --", stdcolors["green"])
    exit(0)


def git_fetch(dir : Path) -> bool:
    output : str = Popen(
        ['git', 'fetch', '-avp'],
        cwd=dir,
        encoding='utf-8',
        stdout=PIPE, stderr=PIPE
    ).communicate()
    
    is_repo : bool = True
    reached : bool = True
    fetch_error : bool = False
    if "fatal" in output[1]:
        fetch_error = True
        if "Could not read from remote repository" in output[1]:
            printColor("    -- ERROR: Remote repository could not be reached.", stdcolors["brightred"])
            reached = False
        
        elif "not a git repository" in output[1]:
            printColor("    -- ERROR: Directory is not a git repository.", stdcolors["brightred"])
            is_repo = False
            reached = False

        else:
            printColor("    -- ERROR: Unknown error in fetch:", stdcolors["brightred"])
            printColor(output[1], stdcolors["brightred"])
            is_repo = False
            reached = False

    if reached:
        all_up_to_date : bool = True
        for out in output:
            for line in out.split("\n")[2:-1]:
                if not "[up to date]" in line:
                    all_up_to_date = False
                    printColor(f"    {line}", stdcolors["brightred"])
        if (all_up_to_date):
            printColor("    - REMOTE UP TO DATE -", stdcolors["brightgreen"])
    
    return is_repo, fetch_error


def git_check_repo(dir : Path, options : GitOptions) -> bool:

    msg : str = "-- Checking directory: " + str(dir) + " --"
    print("\n" + "-" * len(msg))
    print(msg)
    print("-" * len(msg), flush=True)
    
    try:
        # Fetch #
        is_repo, fetch_error = git_fetch(dir)

        if not is_repo:
            return False
        
        # Status #
        if options.status or options.commit or options.push or options.pull:
            output = Popen(
                ['git', 'status'],
                cwd=dir,
                encoding='utf-8',
                stdout=PIPE, stderr=PIPE
            ).communicate()
            total_output = output[0] + output[1]

            branch_clean : bool = False
            branch_ahead : bool = False
            branch_behind : bool = False
            branch_diverged : bool = False
            if "nothing to commit" in total_output:
                branch_clean = True
            if "Your branch is behind" in total_output:
                branch_behind = True
            elif "Your branch is ahead" in total_output:
                branch_ahead = True
            elif "have diverged" in total_output:
                branch_diverged = True
            
            if branch_clean:
                printColor("    - BRANCH CLEAN -", stdcolors["brightgreen"])
            else:
                printColor("    -- BRANCH NOT CLEAN:", stdcolors["brightred"])
                for out in output:
                    for line in out.split("\n"):
                        printColor(f"    {line}", stdcolors["brightred"])
            
            if branch_ahead:
                printColor("    -- BRANCH IS AHEAD REMOTE", stdcolors["brightred"])
            elif branch_behind:
                printColor("    -- BRANCH IS BEHIND REMOTE", stdcolors["brightred"])
            elif branch_diverged:
                printColor("    -- BRANCH DIVERGED FROM REMOTE", stdcolors["brightred"])

            
            # Commit #
            if (not branch_clean) and (options.commit or options.push or options.pull):
                proc : Popen = Popen(
                    ['git', 'add', '.'],
                    cwd=dir,
                    encoding='utf-8',
                    stdout=PIPE, stderr=PIPE
                )
                output = proc.communicate()
                ret_code : int = proc.returncode
                if ret_code != 0:
                    printColor("    -- ERROR: Error in add:", stdcolors["brightred"])
                    for out in output:
                        for line in out.split("\n"):
                            printColor(f"    {line}", stdcolors["brightred"])
                    return

                proc : Popen = Popen(
                    ['git', 'commit', '-m', '[Automatic commit]'],
                    cwd=dir,
                    encoding='utf-8',
                    stdout=PIPE, stderr=PIPE
                )
                output = proc.communicate()
                ret_code : int = proc.returncode
                if ret_code != 0:
                    printColor("    -- ERROR: Error in commit:", stdcolors["brightred"])
                    for out in output:
                        for line in out.split("\n"):
                            printColor(f"    {line}", stdcolors["brightred"])
                    return

                printColor("    - COMMIT MADE -", stdcolors["brightgreen"])
                branch_clean = True
                if not (branch_ahead or branch_behind or branch_diverged):
                    branch_ahead = True
                if branch_behind:
                    branch_behind = False
                    branch_diverged = True
                    printColor("    -- WARNING: COMMIT MADE BRANCHE DIVERGE FROM REMOTE", stdcolors["brightyellow"])
            
            # Pull & push #
            if not (branch_diverged or fetch_error):
                # Push #
                if options.push and branch_clean and branch_ahead:
                    proc : Popen = Popen(
                        ['git', 'push'],
                        cwd=dir,
                        encoding='utf-8',
                        stdout=PIPE, stderr=PIPE
                    )
                    output = proc.communicate()
                    ret_code : int = proc.returncode
                    if ret_code != 0:
                        printColor("    -- ERROR: Error in push:", stdcolors["brightred"])
                        for out in output:
                            for line in out.split("\n"):
                                printColor(f"    {line}", stdcolors["brightred"])
                        return
                    
                    printColor("    - PUSH MADE -", stdcolors["brightgreen"])
                
                # Pull #
                if options.pull and branch_clean and branch_behind:
                    proc : Popen = Popen(
                        ['git', 'pull'],
                        cwd=dir,
                        encoding='utf-8',
                        stdout=PIPE, stderr=PIPE
                    )
                    output = proc.communicate()
                    ret_code : int = proc.returncode
                    if ret_code != 0:
                        printColor("    -- ERROR: Error in pull:", stdcolors["brightred"])
                        for out in output:
                            for line in out.split("\n"):
                                printColor(f"    {line}", stdcolors["brightred"])
                        return
                    
                    printColor("    - PULL MADE -", stdcolors["brightgreen"])
    
    except KeyboardInterrupt:
        print("Keyboard Interrupt")
        exit()
    
    except Exception as e:
        printColor("    - ERROR: Directory probably does not exist.", stdcolors["brightred"])
        printColor(f"{e}", stdcolors["brightred"])
    
    return True


def git_check_repos(
    dir_list : List[Path],
    ignore_set : Set[Path],
    options : GitOptions,
    checked_dirs : Set[Path],
) -> None:
    for dir in dir_list:
        if dir not in ignore_set:
            if dir not in checked_dirs:
                git_check_repo(dir, options)
                checked_dirs.add(dir)


def git_check_directories(
    dir_list : List[Path],
    ignore_set : Set[Path],
    options : GitOptions,
    recursive : bool,
    level : int,
    recursive_max_level : Optional[int],
    checked_dirs : Set[Path] = set(),
) -> None:
    for dir in dir_list:
        if dir not in ignore_set:
            subdir_list = [dir/d for d in os.listdir(dir) if os.path.isdir(dir/d)]
            for d in subdir_list:
                if d not in ignore_set:
                    if d not in checked_dirs:
                        is_repo = git_check_repo(d, options)
                        checked_dirs.add(d)
                    if recursive and not is_repo:
                        do_check : bool = False
                        if recursive_max_level is None:
                            do_check = True
                        elif level < recursive_max_level:
                            do_check = True
                        if do_check:
                            git_check_directories([d], ignore_set, options, recursive, level+1, recursive_max_level, checked_dirs)


def git_check(
    dir_list : List[Path],
    search_list : List[Path],
    ignore_set : Set[Path],
    options : GitOptions,
    recursive : bool,
    recursive_max_level : Optional[int]
) -> None:
    checked_dirs : Set[Path] = set()
    git_check_repos(dir_list, ignore_set, options, checked_dirs)
    git_check_directories(search_list, ignore_set, options, recursive, 0, recursive_max_level, checked_dirs)


def git_check_main(
    dir_list    : List[Union[str,Path]] = [],
    search_list : List[Union[str,Path]] = [],
    ignore_list : List[Union[str,Path]] = []
) -> None:
    # Read flags #
    default_options : List[str] = ["--status", "--no-commit", "--no-push", "--no-pull"]
    
    options = GitOptions(status = True, commit=False, push=False, pull=False)
    arg_i = 1
    real_dir_list : List[str] = []
    real_search_list : List[str] = []
    recursive_max_level : int = 0
    recursive : bool = False
    real_ignore_list : List[str] = []
    real_ignore_list.extend(ignore_list)
    use_config_list : List[str] = []
    set_config_list : List[str] = []
    del_config_list : List[str] = []
    while(arg_i < len(sys.argv)):
        arg : str = sys.argv[arg_i]
        if arg in default_options:
            pass
        elif arg == "--no-status":
            options.status = False
        elif arg == "--commit":
            options.commit = True
        elif arg == "--push":
            options.push = True
        elif arg == "--pull":
            options.pull = True
        elif arg in ["--repo", "-r"]:
            flag : str = arg

            print_help : bool = False
            if arg_i+1 == len(sys.argv):
                print_help = True
            elif sys.argv[arg_i+1][0] == "-":
                print_help = True
            if print_help:
                printColor(f"ERROR: Missing argument for {flag}", stdcolors["brightred"])
                printHelpAndExit(options.list, default_options, True, 1)

            arg_i += 1
            while arg_i < len(sys.argv):
                arg = sys.argv[arg_i]
                if arg == "default":
                    real_dir_list.extend(dir_list)
                elif arg[0] != "-":
                    real_dir_list.append(arg)
                else:
                    break
                arg_i += 1
            arg_i -= 1
        elif arg in ["--search", "-s"]:
            flag : str = arg

            print_help : bool = False
            if arg_i+1 == len(sys.argv):
                print_help = True
            elif sys.argv[arg_i+1][0] == "-":
                print_help = True
            if print_help:
                printColor(f"ERROR: Missing argument for {flag}", stdcolors["brightred"])
                printHelpAndExit(options.list, default_options, True, 1)
            
            arg_i += 1
            while arg_i < len(sys.argv):
                arg = sys.argv[arg_i]
                if arg == "default":
                    real_search_list.extend(search_list)
                elif arg[0] != "-":
                    real_search_list.append(arg)
                else:
                    break
                arg_i += 1
            arg_i -= 1
        elif arg in ["--ignore", "-i"]:
            flag : str = arg

            print_help : bool = False
            if arg_i+1 == len(sys.argv):
                print_help = True
            elif sys.argv[arg_i+1][0] == "-":
                print_help = True
            if print_help:
                printColor(f"ERROR: Missing argument for {flag}", stdcolors["brightred"])
                printHelpAndExit(options.list, default_options, True, 1)
            
            arg_i += 1
            while arg_i < len(sys.argv):
                arg = sys.argv[arg_i]
                if arg == "none":
                    real_ignore_list = []
                elif arg[0] != "-":
                    real_ignore_list.append(arg)
                else:
                    break
                arg_i += 1
            arg_i -= 1
                
        elif arg == "--recursive":
            recursive = True
            flag : str = arg
            arg_i += 1
            if arg_i == len(sys.argv):
                printColor(f"ERROR: Missing argument for {flag}", stdcolors["brightred"])
                printHelpAndExit(options.list, default_options, True, 1)
            else:
                arg = sys.argv[arg_i]
                if arg == "all":
                    recursive_max_level = None
                else:
                    if not arg.isdigit():
                        printColor(f"ERROR: Argument for {flag} must be an unsigned integer or 'all'", stdcolors["brightred"])
                        printHelpAndExit(options.list, default_options, True, 1)
                    recursive_max_level = int(arg)

        elif arg == "--use-config":
            flag : str = arg

            print_help : bool = False
            if arg_i+1 == len(sys.argv):
                print_help = True
            elif sys.argv[arg_i+1][0] == "-":
                print_help = True
            if print_help:
                printColor(f"ERROR: Missing argument for {flag}", stdcolors["brightred"])
                printHelpAndExit(options.list, default_options, True, 1)

            arg_i += 1
            while arg_i < len(sys.argv):
                arg = sys.argv[arg_i]
                if arg[0] != "-":
                    use_config_list.append(arg)
                else:
                    break
                arg_i += 1
            arg_i -= 1

        elif arg == "--set-config":
            flag : str = arg

            print_help : bool = False
            if arg_i+1 == len(sys.argv):
                print_help = True
            elif sys.argv[arg_i+1][0] == "-":
                print_help = True
            if print_help:
                printColor(f"ERROR: Missing argument for {flag}", stdcolors["brightred"])
                printHelpAndExit(options.list, default_options, True, 1)

            arg_i += 1
            while arg_i < len(sys.argv):
                arg = sys.argv[arg_i]
                if arg[0] != "-":
                    set_config_list.append(arg)
                else:
                    break
                arg_i += 1
            arg_i -= 1

        elif arg == "--del-config":
            flag : str = arg

            print_help : bool = False
            if arg_i+1 == len(sys.argv):
                print_help = True
            elif sys.argv[arg_i+1][0] == "-":
                print_help = True
            if print_help:
                printColor(f"ERROR: Missing argument for {flag}", stdcolors["brightred"])
                printHelpAndExit(options.list, default_options, True, 1)

            arg_i += 1
            while arg_i < len(sys.argv):
                arg = sys.argv[arg_i]
                if arg[0] != "-":
                    del_config_list.append(arg)
                else:
                    break
                arg_i += 1
            arg_i -= 1

        elif arg == "--purge-configs":
            purgeJSON()
        
        elif arg == "--list-config":
            flag : str = arg
            
            print_help : bool = False
            if arg_i+1 == len(sys.argv):
                print_help = True
            elif sys.argv[arg_i+1][0] == "-":
                print_help = True
            if print_help:
                printColor(f"ERROR: Missing argument for {flag}", stdcolors["brightred"])
                printHelpAndExit(options.list, default_options, True, 1)

            configs_list = []
            arg_i += 1
            while arg_i < len(sys.argv):
                arg = sys.argv[arg_i]
                if arg[0] != "-":
                    configs_list.append(arg)
                else:
                    break
                arg_i += 1
            
            listConfigsAndExit(configs_list, verbose = False)

        elif arg == "--list-configs":
            listConfigsAndExit(verbose = False)
        
        elif arg == "--list-configs-verbose":
            listConfigsAndExit(verbose=True)
        
        elif arg in ["--help", "-h"]:
            printHelpAndExit(options.list, default_options)
        else:
            printColor(f"ERROR: Unknown argument: {arg}", stdcolors["brightred"])
            printHelpAndExit(options.list, default_options, True, 1)
        arg_i += 1
    del arg_i
    
    # Read from JSON if specified #
    if len(use_config_list) > 0:
        readJSON(use_config_list, real_dir_list, real_search_list, real_ignore_list)
    
    # Delete JSON configurations if specified #
    if len(del_config_list) > 0:
        deleteJSON(del_config_list)
    
    # Set directory and search lists (default if none specified) #
    if len(real_dir_list) == 0 and len(real_search_list) == 0:
        if len(dir_list) == 0 and len(search_list) == 0:
            printColor("ERROR: No directories specified", stdcolors["brightred"])
            printHelpAndExit(options.list, default_options, True, 1)
        real_dir_list = dir_list
        real_search_list = search_list
    
    # Run #
    print("Executing git_check with options: " +
        "--" + ("" if options.status else "no-") + "status " +
        "--" + ("" if options.commit else "no-") + "commit " +
        "--" + ("" if options.push   else "no-") + "push "   +
        "--" + ("" if options.pull   else "no-") + "pull "
    )

    recursive_warning : bool = False
    if recursive and recursive_max_level is None:
        recursive_warning = True    
    elif recursive and recursive_max_level > 0:
        recursive_warning = True
    if recursive_warning:
        rec_str : str = "ALL" if recursive_max_level is None else str(recursive_max_level)
        printColor(f"\nWARNING: Recursive search set to {rec_str}. This can be dangerous.", stdcolors["brightyellow"])

    # Repositories directories #
    dir_set : Set[Path] = set()
    for dir in real_dir_list:
        path = Path(dir).absolute()
        if not path.is_dir():
            printColor(f"ERROR: {dir} is not a directory", stdcolors["brightred"])
            printHelpAndExit(options.list, default_options, True, 1)
        else:
            dir_set.add(path)
    
    # Search directories #
    search_set : Set[Path] = set()
    for dir in real_search_list:
        path = Path(dir).absolute()
        if not path.is_dir():
            printColor(f"ERROR: {dir} is not a directory", stdcolors["brightred"])
            printHelpAndExit(options.list, default_options, True, 1)
        else:
            search_set.add(path)

    # Ignore directories #
    ignore_set : Set[Path] = set()
    for dir in real_ignore_list:
        path = Path(dir).absolute()
        if not path.is_dir():
            printColor(f"ERROR: {dir} is not a directory", stdcolors["brightred"])
            printHelpAndExit(options.list, default_options, True, 1)
        else:
            ignore_set.add(path)
    
    # Create sets
    real_dir_list = sorted(dir_set)
    real_search_list = sorted(search_set)
    real_ignore_list = sorted(ignore_set)
    del dir_set, search_set

    if len(real_dir_list) > 0:
        print("\nRepos to check:")
        for dir in real_dir_list:
            print(f"    {dir}")

    if len(real_search_list) > 0:
        print("\nRoot directories to check:")
        for dir in real_search_list:
            print(f"    {dir}")
    
    if len(real_ignore_list) > 0:
        print("\nDirectories to ignore:")
        for dir in real_ignore_list:
            print(f"    {dir}")
    del real_ignore_list

    if len(set_config_list) > 0:
        writeJSON(set_config_list, real_dir_list, real_search_list, ignore_set)
    else:
        git_check(real_dir_list, real_search_list, ignore_set, options, recursive, recursive_max_level)


__all__ = ["git_check", "git_check_main"]
