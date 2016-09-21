"""Utility for dumping recipe information for scripting."""
from __future__ import print_function

import json
import os
import sys
import yaml

JUST_DOCKERFILES_CONFIG_PATH = os.getenv("JUST_DOCKERFILES_CONFIG", "./just-dockerfiles.yml")
PROJECT_DIRECTORY = os.path.dirname(JUST_DOCKERFILES_CONFIG_PATH)
DEFAULT_RECIPE_DIRECTORY = os.path.join(PROJECT_DIRECTORY, "recipes")
RECIPE_DIRECTORY = os.environ.get("JUST_DOCKERFILES_RECIPES", DEFAULT_RECIPE_DIRECTORY)
DEFAULT_TIMEOUT = 3600


def main():
    """Entry point for dump function."""
    with open("%s/%s/def.yml" % (RECIPE_DIRECTORY, sys.argv[1])) as ins:
        config = yaml.load(ins)

    action = sys.argv[2]
    if action == "--description":
        with open("%s/%s/def.json" % (RECIPE_DIRECTORY, sys.argv[1]), "w") as outs:
            json.dump(config, outs)
    elif action == "--timeout":
        if "timeout" in config:
            print(config["timeout"])
        else:
            with open(JUST_DOCKERFILES_CONFIG_PATH, "r") as f:
                global_config = yaml.load(f)
                print(global_config.get("defaultTimeout", DEFAULT_TIMEOUT))


if __name__ == "__main__":
    main()
