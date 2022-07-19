import shlex
from pathlib import Path
from Levenshtein import distance as levenshtein_distance

from .git_check import git_check, GitOptions
from .json_readwrite import readJSON, writeJSON, getConfigList, listAllConfigs, purgeJSON_Console
from .colors import *
from .config import Config


def help(cmds, config) -> None:
    print("This is the help for gittool.\nStill in construction. Please stand by.")


def addRepo(cmds, config : Config) -> None:
    if len(cmds) == 0:
        print("Missing arguments for ADD REPO")
        return
    for d in cmds:
        p = Path(d)
        if not p.is_dir():
            print(f"Error: {d} is not a directory.")
        else:
            config.addRepo(d)


def addSearch(cmds, config: Config) -> None:
    if len(cmds) == 0:
        print("Missing arguments for ADD SEARCH")
        return
    for d in cmds:
        p = Path(d)
        if not p.is_dir():
            print(f"Error: {d} is not a directory.")
        else:
            config.addSearch(d)


def addIgnore(cmds, config: Config) -> None:
    if len(cmds) == 0:
        print("Missing arguments for ADD IGNORE")
        return
    for d in cmds:
        p = Path(d)
        if not p.is_dir():
            print(f"Error: {d} is not a directory.")
        else:
            config.addIgnore(d)


def delRepo(cmds, config : Config) -> None:
    if len(cmds) == 0:
        print("Missing arguments for DEL REPO")
        return
    for d in cmds:
        p = Path(d)
        if not p in config.repos:
            print(f"Error: {d} is not listed as a repository directory")
        else:
            config.removeRepo(d)


def delSearch(cmds, config : Config) -> None:
    if len(cmds) == 0:
        print("Missing arguments for DEL SEARCH")
        return
    for d in cmds:
        p = Path(d)
        if not p in config.search:
            print(f"Error: {d} is not listed as a search directory")
        else:
            config.removeSearch(d)


def delIgnore(cmds, config : Config) -> None:
    if len(cmds) == 0:
        print("Missing arguments for DEL IGNORE")
        return
    for d in cmds:
        p = Path(d)
        if not p in config.ignore:
            print(f"Error: {d} is not listed as a ignore directory")
        else:
            config.removeIgnore(d)


def add(cmds, config: Config) -> None:
    if len(cmds) == 0:
        print("Missing arguments for ADD. Needs to be REPO, SEARCH or IGNORE")
        return
    
    if cmds[0].upper() == "REPO":
        addRepo(cmds[1:], config)
    elif cmds[0].upper() == "SEARCH":
        addSearch(cmds[1:], config)
    elif cmds[0].upper() == "IGNORE":
        addIgnore(cmds[1:], config)
    else:
        print(f"Error: {cmds[0]} is not a valid argument for ADD")


def delete(cmds, config: Config) -> None:
    if len(cmds) == 0:
        print("Missing arguments for DEL. Needs to be REPO, SEARCH or IGNORE")
        return
    
    if cmds[0].upper() == "REPO":
        delRepo(cmds[1:], config)
    elif cmds[0].upper() == "SEARCH":
        delSearch(cmds[1:], config)
    elif cmds[0].upper() == "IGNORE":
        delIgnore(cmds[1:], config)
    else:
        print(f"Error: {cmds[0]} is not a valid argument for DEL")


def useConfig(cmds, config: Config) -> None:
    if len(cmds) == 0:
        print("Missing arguments for USE")
        return
    
    repos = []
    search = []
    ignore = []
    config_list = []
    json_config_list = getConfigList()
    for name in cmds:
        if not name in json_config_list:
            print(f"Error: {name} is not a configuration")
        else:
            config_list.append(name)
    if (len(config_list) > 0):
        readJSON(config_list, repos, search, ignore)
        for d in repos:
            config.addRepo(d)
        for d in search:
            config.addSearch(d)
        for d in ignore:
            config.addIgnore(d)


def setConfig(cmds, config: Config) -> None:
    if len(cmds) == 0:
        print("Missing arguments for SET")
        return
    if config.isEmpty():
        print("Error: Cannot save empty configuration")
        return
    repos = sorted(config.repos)
    search = sorted(config.search)
    ignore = sorted(config.ignore)
    writeJSON(cmds, repos, search, ignore)


def showConfig(cmd, config: Config) -> None:
    if len(cmd) > 0:
        print("SHOW takes no arguments")
    
    types_str = ["Repository directories", "Search directories", "Ignore directories"]
    for i in range(3):
        if len(config.all[i]) > 0:
            print(f"{types_str[i]}:")
            for d in config.all[i]:
                print(f"    {d}")
            print("")


def listConfigs(cmds, config: Config) -> None:
    if len(cmds) > 0:
        print("LIST takes no arguments")
        return
    print("\n".join(getConfigList()))


def listConfigsVerbose(cmds, config: Config) -> None:
    if len(cmds) == 0:
        print("Missing argument for VERBOSE")
        return
    
    if "all" in cmds:
        listAllConfigs(verbose=True)
    else:
        config_list = []
        json_config_list = getConfigList()
        for name in cmds:
            if not name in json_config_list:
                print(f"Error: {name} is not a configuration")
            else:
                config_list.append(name)
        if (len(config_list) > 0):
            listAllConfigs(config_list, verbose=True)


def purgeConfigs(cmds, config: Config) -> None:
    if len(cmds) > 0:
        print("PURGE takes no arguments")
        return
    
    purgeJSON_Console()


def resetConfig(cmds, config: Config) -> None:
    if len(cmds) > 0:
        print("RESET takes no arguments")
        return
    if config.isEmpty():
        print("Nothing to reset")
        return
    config.reset()
    print ("Configuration resetted")


def run(cmds, config: Config) -> None:
    if config.isEmpty():
        print("Error: Cannot run empty configuration")
        return
    status = True
    commit = False
    push = False
    pull = False
    for c in cmds:
        cmd = c.upper()
        if cmd in ["STATUS", "NOCOMMIT", "NOPUSH", "NOPULL"]:
            pass
        elif cmd == "NO-STATUS":
            status = False
        elif cmd == "COMMIT":
            commit = True
        elif cmd == "PUSH":
            push = True
        elif cmd == "PULL":
            pull = True
        else:
            print(f"Error: {cmd} is not a valid argument for RUN")
            return

    options = GitOptions(status, commit, push, pull)

    try:
        git_check(
            sorted(config.repos),
            sorted(config.search),
            config.ignore,
            options,
            recursive = False,
            recursive_max_level = None
        )
    except KeyboardInterrupt:
        print("\nRun interrupted")


input_method = {
    "EXIT" : lambda _, __: exit(1),
    "HELP" : help,

    "ADD"  : add,
    "DEL"  : delete,

    "USE" : useConfig,
    "SET" : setConfig,

    "SHOW": showConfig,
    "LIST": listConfigs,
    "VERBOSE": listConfigsVerbose,

    "PURGE": purgeConfigs,

    "RESET": resetConfig,

    "RUN": run,
}


def keyError(key: str) -> None:
    print(f"Unknown command: {key}")
    # Find closest matches in input_methods
    matches = [i for i in input_method if levenshtein_distance(i, key) <= 1]
    if len(matches) > 0:
        print("\nDid you mean any of the following?\n    ", end="")
        for k in matches:
            print(k, " ", end="")
        print("")


def interpretInput(input_str: str, config: Config) -> None:
    # Get command from user, that might be a list of commands separated by ";"
    cmd_set = [i.strip() for i in input_str.split(";") if i.strip() != ""]
    for cmd in cmd_set:
        # Split command into command and arguments
        while cmd[-1] == "\\":
            cmd = cmd[:-1]
        cmd_split = shlex.split(cmd)
        for i in range(1, len(cmd_split)):
            while cmd_split[i][-1] == "\\":
                cmd_split[i] = cmd_split[i][:-1]
        
        current_cmd = cmd_split[0].upper()
        key_ok = False
        try:
            # Reach method for each command
            method = input_method[current_cmd]
            key_ok = True
        except KeyError:
            keyError(current_cmd)
        
        if key_ok:
            method(cmd_split[1:], config)


def loop(config: Config) -> None:
    # Loop over all commands except for a Keyboard interrupt
    try:
        while True:
            # Get input from user
            print(">>> ", end="")
            interpretInput(input(), config)
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt")
        exit(1)


def main() -> None:
    # Create an empty config and begin loop
    loop(Config())
    exit(0)
