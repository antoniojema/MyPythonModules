from typing import List, Set, Optional
from pathlib import Path
from subprocess import Popen, PIPE
import sys, colorama, os, psutil


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
    **kwargs) -> None:
    print(f"{color}{text}{endcolor}", **kwargs, flush=flush)


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


def git_check_repos(dir_list : List[Path], options : GitOptions) -> None:
    for dir in dir_list:
        git_check_repo(dir, options)


def git_check_directories(
    dir_list : List[Path],
    options : GitOptions,
    recursive : bool,
    level : int,
    recursive_max_level : Optional[int],
) -> None:
    for dir in dir_list:
        subdir_list = [dir/d for d in os.listdir(dir) if os.path.isdir(dir/d)]
        for d in subdir_list:
            is_repo = git_check_repo(d, options)
            if recursive and not is_repo:
                if recursive_max_level is None:
                    git_check_directories([d], options, recursive, level+1, recursive_max_level)
                elif level < recursive_max_level:
                    git_check_directories([d], options, recursive, level+1, recursive_max_level)


def git_check(
    dir_list : List[Path],
    search_list : List[Path],
    options : GitOptions,
    recursive : bool,
    recursive_max_level : Optional[int]
) -> None:
    git_check_repos(dir_list, options)
    git_check_directories(search_list, options, recursive, 0, recursive_max_level)


def printHelp(options: List[str], default_options: List[str]) -> None:
        print("Usage: python <git.py> <args>\n\nPossible arguments are:\n")
        print(f"    --help, -h (Prints this)")
        for arg in options:
            print(f"    --{arg}, --no-{arg}")
        print("\nDefault options are: ", end="")
        for arg in default_options:
            print(f"{arg} " , end="")

        print("\n\nOther possible flags are:\n")
        print(f"    --repo/-r [default/<directory>]")
        print(f"        Specifies a repository directory.\n")

        print(f"    --search/-s [default/<directory>]")
        print(f"        Specifies root directory for subdirectories search.\n")
        
        print(f"    --recursive [all/<n>]")
        print(f"        Enables recursive search for --search subdirectories specifing the recursivity level. Disabled by default.\n")


def printHelpAndExit(options: List[str], default_options: List[str], exit_code: int = 0) -> None:
    printHelp(options, default_options)
    exit(exit_code)


def git_check_main(dir_list:List[str] = [], search_list : List[str] = []) -> None:
    # Read flags #
    default_options : List[str] = ["--status", "--no-commit", "--no-push", "--no-pull"]
    
    options = GitOptions(status = True, commit=False, push=False, pull=False)
    arg_i = 1
    real_dir_list : List[str] = []
    real_search_list : List[str] = []
    recursive_max_level : int = 0
    recursive : bool = False
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
            arg_i += 1
            if arg_i == len(sys.argv):
                printColor(f"ERROR: Missing argument for {flag}\n", stdcolors["brightred"])
                printHelpAndExit(options.list, default_options, 1)
            else:
                arg = sys.argv[arg_i]
                if arg == "default":
                    real_dir_list.extend(dir_list)
                else:
                    real_dir_list.append(arg)
        elif arg in ["--search", "-s"]:
            flag : str = arg
            arg_i += 1
            if arg_i == len(sys.argv):
                printColor(f"ERROR: Missing argument for {flag}\n", stdcolors["brightred"])
                printHelpAndExit(options.list, default_options, 1)
            else:
                arg = sys.argv[arg_i]
                if arg == "default":
                    real_search_list.extend(search_list)
                else:
                    real_search_list.append(arg)
        elif arg == "--recursive":
            recursive = True
            flag : str = arg
            arg_i += 1
            if arg_i == len(sys.argv):
                printColor(f"ERROR: Missing argument for {flag}\n", stdcolors["brightred"])
                printHelpAndExit(options.list, default_options, 1)
            else:
                arg = sys.argv[arg_i]
                if arg == "all":
                    recursive_max_level = None
                else:
                    if not arg.isdigit():
                        printColor(f"ERROR: Argument for {flag} must be an unsigned integer\n", stdcolors["brightred"])
                        printHelpAndExit(options.list, default_options, 1)
                    recursive_max_level = int(arg)
        elif arg in ["--help", "-h"]:
            printHelpAndExit(options.list, default_options)
            exit()
        else:
            printColor(f"ERROR: Unknown argument: {arg}\n", stdcolors["brightred"])
            printHelpAndExit(options.list, default_options, 1)
        arg_i += 1
    del arg_i
    
    # Set directory and search lists (default if none specified) #
    if len(real_dir_list) == 0 and len(real_search_list) == 0:
        if len(dir_list) == 0 and len(search_list) == 0:
            printColor("ERROR: No directories specified\n", stdcolors["brightred"])
            printHelpAndExit(options.list, default_options, 1)
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
        printColor("\nWARNING: Recursive search enabled. This can be dangerous.\n", stdcolors["brightyellow"])

    dir_set : Set[Path] = set()
    for dir in real_dir_list:
        path = Path(dir).absolute()
        if not path.is_dir():
            printColor(f"ERROR: {dir} is not a directory\n", stdcolors["brightred"])
            printHelpAndExit(options.list, default_options, 1)
        else:
            dir_set.add(path)
    
    search_set : Set[Path] = set()
    for dir in real_search_list:
        path = Path(dir).absolute()
        if not path.is_dir():
            printColor(f"ERROR: {dir} is not a directory\n", stdcolors["brightred"])
            printHelpAndExit(options.list, default_options, 1)
        else:
            search_set.add(path)
    
    real_dir_list = sorted(dir_set)
    real_search_list = sorted(search_set)
    del dir_set, search_set

    if len(real_dir_list) > 0:
        print("\nRepos to check:")
        for dir in real_dir_list:
            print(f"    {dir}")

    if len(real_search_list) > 0:
        print("\nDirectories to ckeck:")
        for dir in real_search_list:
            print(f"    {dir}")
    
    git_check(real_dir_list, real_search_list, options, recursive, recursive_max_level)


__all__ = ["git_check", "git_check_main"]
