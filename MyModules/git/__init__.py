from email.policy import default
from typing import List
from pathlib import Path
from subprocess import Popen, PIPE
import sys

colors : dict = {
    "red"    : "\033[91m",
    "green"  : "\033[92m",
    "usual"  : "\033[0m",
}

def printColor(text : str, color : str, endcolor : str = "usual", flush:bool=True, **kwargs) -> None:
    print(f"{colors[color]}{text}{colors[endcolor]}", **kwargs, flush=flush)


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
            
            if "fatal" in output[1]:
                if "Could not read from remote repository" in output[1]:
                    printColor("    -- ERROR: Remote repository could not be reached.", "red")
                
                elif "not a git repository" in output[1]:
                    printColor("    -- ERROR: Directory is not a git repository.", "red")
                
                else:
                    printColor("    -- ERROR: Unknown error in fetch:", "red")
                    printColor(output[1], "red")
                
                continue

            all_up_to_date : bool = True
            for out in output:
                for line in out.split("\n")[2:-1]:
                    if not "[up to date]" in line:
                        all_up_to_date = False
                        printColor(f"    {line}", "red")
            if (all_up_to_date):
                printColor("    - REMOTE UP TO DATE -", "green")
            
            # Status #
            if status:
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
                    printColor("    - BRANCH CLEAN -", "green")
                else:
                    printColor("    -- BRANCH NOT CLEAN:", "red")
                    for out in output:
                        for line in out.split("\n"):
                            printColor(f"    {line}", "red")
                
                if branch_ahead:
                    printColor("    -- BRANCH IS AHEAD REMOTE", color="red")
                elif branch_behind:
                    printColor("    -- BRANCH IS BEHIND REMOTE", color="red")
                elif branch_diverged:
                    printColor("    -- BRANCH DIVERGED FROM REMOTE", color="red")

                
                # Commit #
                if (not branch_clean) and commit:
                    proc : Popen = Popen(
                        ['git', 'add', '.'],
                        cwd=dir,
                        encoding='utf-8',
                        stdout=PIPE, stderr=PIPE
                    )
                    output = proc.communicate()
                    ret_code : int = proc.returncode
                    if ret_code != 0:
                        printColor("    -- ERROR: Error in add:", "red")
                        for out in output:
                            for line in out.split("\n"):
                                printColor(f"    {line}", "red")
                        continue

                    proc : Popen = Popen(
                        ['git', 'commit', '-m', '"Automated commit"'],
                        cwd=dir,
                        encoding='utf-8',
                        stdout=PIPE, stderr=PIPE
                    )
                    output = proc.communicate()
                    ret_code : int = proc.returncode
                    if ret_code != 0:
                        printColor("    -- ERROR: Error in commit:", "red")
                        for out in output:
                            for line in out.split("\n"):
                                printColor(f"    {line}", "red")
                        continue

                    printColor("    - COMMIT MADE -", "green")
                    branch_clean = True
                    if not (branch_ahead or branch_behind or branch_diverged):
                        branch_ahead = True
                    if branch_behind:
                        branch_behind = False
                        branch_diverged = True
                
                if not branch_diverged:
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
                            printColor("    -- ERROR: Error in push:", "red")
                            for out in output:
                                for line in out.split("\n"):
                                    printColor(f"    {line}", "red")
                            continue
                        
                        printColor("    - PUSH MADE -", "green")
                    
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
                            printColor("    -- ERROR: Error in pull:", "red")
                            for out in output:
                                for line in out.split("\n"):
                                    printColor(f"    {line}", "red")
                            continue
                        
                        printColor("    - PULL MADE -", "green")
        
        except KeyboardInterrupt:
            print("Keyboard Interrupt", "usual")
            exit()
        
        except:
            printColor("    - ERROR: Directory probably does not exist.", "red")


def git_check_main(dir_list:List[str]) -> None:
    options : List[str] = ["status", "commit", "push", "pull"]
    default_options : List[str] = ["--status", "--no-commit", "--no-push", "--no-pull"]
    status : bool = True
    commit : bool = False
    push   : bool = False
    pull   : bool = False
    print_help : bool  = False
    for arg in sys.argv[1:]:
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
        elif arg in ["--help", "-h"]:
            print_help = True
        else:
            printColor(f"Unknown argument: {arg}\n", "red")
            print_help = True
    
    if print_help:
        print("Usage: python <git.py> <args>\n\nPossible arguments are:\n")
        print(f"    --help, -h (prints this)")
        for arg in options:
            print(f"    --{arg}, --no-{arg}")
        print("\nDefault options are: ", end="")
        for arg in default_options:
            print(f"{arg} " , end="")
        print("")
    
    else:
        print("Executing git_check with options: " +
            "--" + ("" if status else "no-") + "status " +
            "--" + ("" if commit else "no-") + "commit " +
            "--" + ("" if push   else "no-") + "push "   +
            "--" + ("" if pull   else "no-") + "pull "
        )
        git_check(dir_list, status=status, commit=commit, push=push, pull=pull)


__all__ = ["git_check", "git_check_main"]