from typing import List, Optional
from pathlib import Path
from subprocess import Popen, CalledProcessError, PIPE

colors : dict = {
    "red"    : "\033[91m",
    "green"  : "\033[92m",
    "usual"  : "\033[0m",
}

def printColor(text : str, color : str, endcolor : str = "usual", **kwargs) -> None:
    print(f"{colors[color]}{text}{colors[endcolor]}", **kwargs)


def git_check(dir_list : List[Path], status:bool=True, commit:bool=False, push:bool=False) -> None:
    for dir in dir_list:
        msg : str = "-- Checking directory: " + str(dir) + " --"
        print("\n" + "-" * len(msg))
        print(msg)
        print("-" * len(msg))
        
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
                    printColor("    ERROR: Remote repository could not be reached.", "red")
                
                elif "not a git repository" in output[1]:
                    printColor("    ERROR: Directory is not a git repository.", "red")
                
                else:
                    printColor("    ERROR: Unknown error in fetch:", "red")
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

                branch_clean : bool = False
                if "nothing to commit, working tree clean" in (output[0] + output[1]):
                    printColor("    - BRANCH CLEAN -", "green")
                    branch_clean = True
                else:
                    for out in output:
                        for line in out.split("\n")[2:-1]:
                            printColor(f"    {line}", "red")
                
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
                        printColor("    ERROR: Error in add:", "red")
                        for out in output:
                            for line in out.split("\n")[2:-1]:
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
                        printColor("    ERROR: Error in commit:", "red")
                        for out in output:
                            for line in out.split("\n")[2:-1]:
                                printColor(f"    {line}", "red")
                        continue

                    printColor("    - COMMIT MADE -", "green")
                    branch_clean = True
                
                # Push #
                if branch_clean and push:
                    proc : Popen = Popen(
                        ['git', 'push'],
                        cwd=dir,
                        encoding='utf-8',
                        stdout=PIPE, stderr=PIPE
                    ).communicate()
                    output = proc.communicate()
                    ret_code : int = proc.returncode
                    if ret_code != 0:
                        printColor("    ERROR: Error in push:", "red")
                        for out in output:
                            for line in out.split("\n")[2:-1]:
                                printColor(f"    {line}", "red")
                        continue
                    
                    printColor("    - PUSH MADE -", "green")
        
        except KeyboardInterrupt:
            print("Keyboard Interrupt", "usual")
            exit()
        
        except:
            printColor("    - ERROR: Directory probably does not exist.", "red")


__all__ = ["git_check"]