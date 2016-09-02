import json
import os
import sys
import yaml

JUST_DOCKERFILES_CONFIG_PATH = os.getenv("JUST_DOCKERFILES_CONFIG", "./just-dockerfiles.json")
PROJECT_DIRECTORY = os.path.dirname(JUST_DOCKERFILES_CONFIG_PATH)
DEFAULT_RECIPE_DIRECTORY = os.path.join(PROJECT_DIRECTORY, "recipes")
RECIPE_DIRECTORY = os.environ.get("JUST_DOCKERFILES_RECIPES", DEFAULT_RECIPE_DIRECTORY)

with open("%s/%s/def.yml" % (RECIPE_DIRECTORY, sys.argv[1])) as ins:
    with open("%s/%s/def.json" % (RECIPE_DIRECTORY, sys.argv[1]), "w") as outs:
        json.dump(yaml.load(ins), outs)
