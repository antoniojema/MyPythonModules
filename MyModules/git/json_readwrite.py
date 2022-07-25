from typing import List, Set
import json
from pathlib import Path

from .colors import *


def createIfNotExists(path : Path, dir_error : bool = True) -> None:
    json_path = Path(__file__).parent / "config.json"
    if not json_path.exists():
        with open(json_path, "w") as fout:
            json.dump(dict(), fout)
    elif dir_error and json_path.is_dir():
        exitOnError(f"YOU SHOULD NEVER SEE THIS: {path} is a directory.")


def getConfigList() -> List[str]:
    json_path : Path = Path(__file__).parent / "config.json"
    createIfNotExists(json_path)
    
    with json_path.open() as fin:
        data = json.load(fin)
    if not type(data) is dict:
        exitOnError("YOU SHOULD NEVER SEE THIS: json.load() did not return dictionary.")
    
    return [key for key in data]


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


def listAllConfigs(specific : List[str] = [], verbose : bool = False) -> None:
    json_path : Path = Path(__file__).parent / "config.json"
    createIfNotExists(json_path)
    
    with json_path.open() as fin:
        data = json.load(fin)
    if not type(data) is dict:
        print("YOU SHOULD NEVER SEE THIS: json.load() did not return dictionary.")
        return
    
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
                print(f"Error: Configuration {key} does not exist.")
        print("\nConfigurations:")
        for key in specific:
            print(f"\n    {key}")
            listOneConfig(data, key)


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
    del_configs = []
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
        del_config : bool = True
        for t in config:
            if len(config[t]) > 0:
                del_config = False
                break
        if del_config:
            something_done = True
            del_configs.append(label)
    
    if len(del_configs) > 0:
        printColor("\nThe following configurations do not hold valid directories anymore and will be deleted:", stdcolors["yellow"])
        for label in del_configs:
            printColor(f"    {label}", stdcolors["yellow"])
            del data[label]

    with json_path.open("w") as fout:
        json.dump(data, fout, indent=4)
    
    if not something_done:
        print("Nothing to purge")
    else:
        printColor("\n-- Purge complete --", stdcolors["green"])
    
    exit(0)


# Used to delete any directory in the JSON that does not exist anymore #
def purgeJSON_Console() -> None:
    json_path : Path = Path(__file__).parent / "config.json"
    createIfNotExists(json_path)
    
    with json_path.open() as fin:
        data = json.load(fin)
    if not type(data) is dict:
        exitOnError("YOU SHOULD NEVER SEE THIS: json.load() did not return dictionary.")
    
    del_configs = []
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
        del_config : bool = True
        for t in config:
            if len(config[t]) > 0:
                del_config = False
                break
        if del_config:
            something_done = True
            del_configs.append(label)
    
    if len(del_configs) > 0:
        printColor("\nThe following configurations do not hold valid directories anymore and will be deleted:", stdcolors["yellow"])
        for label in del_configs:
            printColor(f"    {label}", stdcolors["yellow"])
            del data[label]

    with json_path.open("w") as fout:
        json.dump(data, fout, indent=4)
    
    if not something_done:
        print("Nothing to purge")
    else:
        printColor("\n-- Purge complete --", stdcolors["green"])
