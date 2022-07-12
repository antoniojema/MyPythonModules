from typing import List, Set
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
    "reset" : colorama.Style.RESET_ALL
}


def printColor(
    text : str,
    color : str,
    endcolor : str = colorama.Style.RESET_ALL,
    flush:bool=True,
    **kwargs) -> None:
    print(f"{color}{text}{endcolor}", **kwargs, flush=flush)


def git_check(dir_list : List[Path], status:bool=True, commit:bool=False, push:bool=False, pull:bool=False) -> None:
    for dir in dir_list:
        msg : str = "-- Checking directory: " + str(dir) + " --"
        print("\n" + "-" * len(msg))
        print(msg)
        print("-" * len(msg), flush=True)
        
        try:
            # Fetch #
            output : str = Popen(
                ['git', 'fetch', '-avp'],
                cwd=dir,
                encoding='utf-8',
                stdout=PIPE, stderr=PIPE
            ).communicate()
            
            fetch_error : bool = False
            if "fatal" in output[1]:
                fetch_error = True
                if "Could not read from remote repository" in output[1]:
                    printColor("    -- ERROR: Remote repository could not be reached.", stdcolors["red"])
                
                elif "not a git repository" in output[1]:
                    printColor("    -- ERROR: Directory is not a git repository.", stdcolors["red"])
                    continue

                else:
                    printColor("    -- ERROR: Unknown error in fetch:", stdcolors["red"])
                    printColor(output[1], stdcolors["red"])
                    continue

            if not fetch_error:
                all_up_to_date : bool = True
                for out in output:
                    for line in out.split("\n")[2:-1]:
                        if not "[up to date]" in line:
                            all_up_to_date = False
                            printColor(f"    {line}", stdcolors["red"])
                if (all_up_to_date):
                    printColor("    - REMOTE UP TO DATE -", stdcolors["green"])
            
            # Status #
            if status or commit or push or pull:
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
                    printColor("    - BRANCH CLEAN -", stdcolors["green"])
                else:
                    printColor("    -- BRANCH NOT CLEAN:", stdcolors["red"])
                    for out in output:
                        for line in out.split("\n"):
                            printColor(f"    {line}", stdcolors["red"])
                
                if branch_ahead:
                    printColor("    -- BRANCH IS AHEAD REMOTE", stdcolors["red"])
                elif branch_behind:
                    printColor("    -- BRANCH IS BEHIND REMOTE", stdcolors["red"])
                elif branch_diverged:
                    printColor("    -- BRANCH DIVERGED FROM REMOTE", stdcolors["red"])

                
                # Commit #
                if (not branch_clean) and (commit or push or pull):
                    proc : Popen = Popen(
                        ['git', 'add', '.'],
                        cwd=dir,
                        encoding='utf-8',
                        stdout=PIPE, stderr=PIPE
                    )
                    output = proc.communicate()
                    ret_code : int = proc.returncode
                    if ret_code != 0:
                        printColor("    -- ERROR: Error in add:", stdcolors["red"])
                        for out in output:
                            for line in out.split("\n"):
                                printColor(f"    {line}", stdcolors["red"])
                        continue

                    proc : Popen = Popen(
                        ['git', 'commit', '-m', '[Automatic commit]'],
                        cwd=dir,
                        encoding='utf-8',
                        stdout=PIPE, stderr=PIPE
                    )
                    output = proc.communicate()
                    ret_code : int = proc.returncode
                    if ret_code != 0:
                        printColor("    -- ERROR: Error in commit:", stdcolors["red"])
                        for out in output:
                            for line in out.split("\n"):
                                printColor(f"    {line}", stdcolors["red"])
                        continue

                    printColor("    - COMMIT MADE -", stdcolors["green"])
                    branch_clean = True
                    if not (branch_ahead or branch_behind or branch_diverged):
                        branch_ahead = True
                    if branch_behind:
                        branch_behind = False
                        branch_diverged = True
                        printColor("    -- WARNING: COMMIT MADE BRANCHE DIVERGE FROM REMOTE", stdcolors["red"])
                
                # Pull & push #
                if not (branch_diverged or fetch_error):
                    # Push #
                    if push and branch_clean and branch_ahead:
                        proc : Popen = Popen(
                            ['git', 'push'],
                            cwd=dir,
                            encoding='utf-8',
                            stdout=PIPE, stderr=PIPE
                        )
                        output = proc.communicate()
                        ret_code : int = proc.returncode
                        if ret_code != 0:
                            printColor("    -- ERROR: Error in push:", stdcolors["red"])
                            for out in output:
                                for line in out.split("\n"):
                                    printColor(f"    {line}", stdcolors["red"])
                            continue
                        
                        printColor("    - PUSH MADE -", stdcolors["green"])
                    
                    # Pull #
                    if pull and branch_clean and branch_behind:
                        proc : Popen = Popen(
                            ['git', 'pull'],
                            cwd=dir,
                            encoding='utf-8',
                            stdout=PIPE, stderr=PIPE
                        )
                        output = proc.communicate()
                        ret_code : int = proc.returncode
                        if ret_code != 0:
                            printColor("    -- ERROR: Error in pull:", stdcolors["red"])
                            for out in output:
                                for line in out.split("\n"):
                                    printColor(f"    {line}", stdcolors["red"])
                            continue
                        
                        printColor("    - PULL MADE -", stdcolors["green"])
        
        except KeyboardInterrupt:
            print("Keyboard Interrupt")
            exit()
        
        except:
            printColor("    - ERROR: Directory probably does not exist.", stdcolors["red"])


def printHelp(options: List[str], default_options: List[str]) -> None:
        print("Usage: python <git.py> <args>\n\nPossible arguments are:\n")
        print(f"    --help, -h (prints this)")
        for arg in options:
            print(f"    --{arg}, --no-{arg}")
        print(f"    --repo/-r [default/<directory>] (specifies)")
        print("\nDefault options are: ", end="")
        for arg in default_options:
            print(f"{arg} " , end="")
        print("")


def printHelpAndExit(options: List[str], default_options: List[str], exit_code: int = 0) -> None:
    printHelp(options, default_options)
    exit(exit_code)


def git_check_main(dir_list:List[str] = []) -> None:
    # Read flags #
    options : List[str] = ["status", "commit", "push", "pull"]
    default_options : List[str] = ["--status", "--no-commit", "--no-push", "--no-pull"]
    status : bool = True
    commit : bool = False
    push   : bool = False
    pull   : bool = False
    arg_i = 1
    real_dir_list : List[str] = []
    while(arg_i < len(sys.argv)):
        arg : str = sys.argv[arg_i]
        if arg in default_options:
            pass
        elif arg == "--no-status":
            status = False
        elif arg == "--commit":
            commit = True
        elif arg == "--push":
            push = True
        elif arg == "--pull":
            pull = True
        elif arg in ["--repo", "-r"]:
            flag : str = arg
            arg_i += 1
            if arg_i == len(sys.argv):
                printColor(f"ERROR: Missing argument for {flag}\n", stdcolors["red"])
                printHelpAndExit(options, default_options, 1)
            else:
                arg = sys.argv[arg_i]
                if arg == "default":
                    real_dir_list.extend(dir_list)
                else:
                    real_dir_list.append(arg)
        elif arg in ["--help", "-h"]:
            printHelpAndExit(options, default_options)
            exit()
        else:
            printColor(f"ERROR: Unknown argument: {arg}\n", stdcolors["red"])
            printHelpAndExit(options, default_options, 1)
        arg_i += 1
    del arg_i
    
    # Set directory list (default if none specified) #
    if len(real_dir_list) == 0:
        if len(dir_list) == 0:
            printColor("ERROR: No directories to check\n", stdcolors["red"])
            printHelpAndExit(options, default_options, 1)
        else:
            real_dir_list = dir_list
            del dir_list
    
    # Run #
    print("Executing git_check with options: " +
        "--" + ("" if status else "no-") + "status " +
        "--" + ("" if commit else "no-") + "commit " +
        "--" + ("" if push   else "no-") + "push "   +
        "--" + ("" if pull   else "no-") + "pull "
    )
    
    dir_set : Set[Path] = set()
    for dir in real_dir_list:
        path = Path(dir).absolute()
        if not path.is_dir():
            printColor(f"ERROR: {dir} is not a directory\n", stdcolors["red"])
            printHelpAndExit(options, default_options, 1)
        else:
            dir_set.add(path)
    
    real_dir_list = sorted(dir_set)
    del dir_set

    print("Directories to ckeck:")
    for dir in real_dir_list:
        print(f"    {dir}")
    
    git_check(real_dir_list, status=status, commit=commit, push=push, pull=pull)


__all__ = ["git_check", "git_check_main"]