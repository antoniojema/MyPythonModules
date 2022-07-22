from pathlib import Path
from typing import List, Union
import sys

from git_check import git_check, GitOptions
from colors import printColor, stdcolors
from console import main as console_main
from json_readwrite import readJSON


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
        if arg == "--console":
            console_main()
            exit(0)
        elif arg in default_options:
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
        try:
            git_check(real_dir_list, real_search_list, ignore_set, options, recursive, recursive_max_level)
        except KeyboardInterrupt:
            print("\nKeyboard interrupt")
            exit(1)
