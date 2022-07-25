from tabnanny import check
from typing import List, Set, Optional, Union
from pathlib import Path
from subprocess import Popen, PIPE
import os, sys

from .colors import *
from .json_readwrite import *


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

def get_remote_branch_name(dir : Path) -> str:
    output = Popen(
        ['git', 'branch', '-vv'],
        cwd=dir,
        encoding='utf-8',
        stdout=PIPE, stderr=PIPE
    ).communicate()
    output = output[0] + "\n" + output[1]

    for line in output.split('\n'):
        if len(line) > 0:
         if line[0] == "*":
            i1 = line.find('[') + 1
            i2 = line.find(']')
            if i1 != 0:
                return line[i1:i2]
            else:
                return "-"

    return "-"

def get_branch_name(dir : Path) -> str:
    output = Popen(
        ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
        cwd=dir,
        encoding='utf-8',
        stdout=PIPE, stderr=PIPE
    ).communicate()

    return (output[0].strip() + output[1].strip())


def is_git_repo(dir : Path) -> bool:
    output : str = Popen(
        ['git', 'branch'],
        cwd=dir,
        encoding='utf-8',
        stdout=PIPE, stderr=PIPE
    ).communicate()
    output = output[0] + "\n" + output[1]

    if ("not a git repository" in output) or \
       ("no es un repositorio git" in output):
        return False
    else:
        return True


def git_fetch(dir : Path) -> bool:
    output : str = Popen(
        ['git', 'fetch', '-avp'],
        cwd=dir,
        encoding='utf-8',
        stdout=PIPE, stderr=PIPE
    ).communicate()
    output = (output[0].strip() + "\n" + output[1].strip()).strip()
    
    error : bool = False
    if output == "":
        printColor("    - NO REMOTE -", stdcolors["brightgreen"])
        error = True
    elif ("Could not read from remote repository" in output) or \
         ("TODO: ESPANOL" in output):
        printColor("    -- ERROR: Remote repository could not be reached.", stdcolors["brightred"])
        error = True
    elif "fatal" in output:
        printColor("    -- ERROR: Unknown error in fetch:", stdcolors["brightred"])
        printColor(output, stdcolors["brightred"])
        error = True

    if not error:
        all_up_to_date : bool = True
        for out in output:
            for line in out.split("\n")[2:-1]:
                if not ("[up to date]" in line or "[actualizado]" in line):
                    all_up_to_date = False
                    printColor(f"    {line}", stdcolors["brightred"])
        if (all_up_to_date):
            printColor("    - REMOTE UP TO DATE -", stdcolors["brightgreen"])
    
    return error


def git_check_repo(dir : Path, options : GitOptions) -> bool:

    msg : str = "-- Checking directory: " + str(dir) + " --"
    print("\n" + "-" * len(msg))
    print(msg)
    print("-" * len(msg), flush=True)

    # Check if it is a repository #
    if not is_git_repo(dir):
        printColor("    -- ERROR: Directory is not a git repository.", stdcolors["brightred"])
        return False

    # Branch names #
    local_branch : str = get_branch_name(dir)
    remote_branch : str = get_remote_branch_name(dir)
    has_upstream : bool
    print(f"    Local branch:  {local_branch}")
    if remote_branch == "-":
        print("    No remote branch")
        has_upstream = False
    else:
        print(f"    Remote branch: {remote_branch}")
        has_upstream = True
    
    # Fetch #
    fetch_error = git_fetch(dir)
    
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
        if ("nothing to commit" in total_output) or \
           ("nada para hacer commit" in total_output):
            branch_clean = True
        if ("Your branch is behind" in total_output):
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
        if not (branch_diverged or fetch_error or not has_upstream):
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
