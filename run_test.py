"""Entry point for defining py.test tests for this project."""
from __future__ import print_function

import functools
import yaml
import os
import subprocess
import uuid

JUST_DOCKERFILES_CONFIG_PATH = os.getenv("JUST_DOCKERFILES_CONFIG", "./just-dockerfiles.json")
PROJECT_DIRECTORY = os.path.abspath(os.path.dirname(JUST_DOCKERFILES_CONFIG_PATH))
DEFAULT_RECIPE_DIRECTORY = os.path.join(PROJECT_DIRECTORY, "recipes")
RECIPE_DIRECTORY = os.environ.get("JUST_DOCKERFILES_RECIPES", DEFAULT_RECIPE_DIRECTORY)


with open(JUST_DOCKERFILES_CONFIG_PATH, "r") as f:
    JUST_DOCKERFILES_CONFIG = yaml.load(f)


def _create_function_for_recipe(recipe_name):
    recipe_path = os.path.join(RECIPE_DIRECTORY, recipe_name)
    the_t_function = functools.partial(_t_function, recipe_path)
    the_t_function.__name__ = "test_%s" % recipe_name
    the_t_function.__description__ = "Auto-generated test for %s" % recipe_name
    return the_t_function


def _t_function(path):
    recipe_config_path = os.path.join(path, "def.yml")
    if os.path.exists(recipe_config_path):
        with open(recipe_config_path, "r") as f:
            recipe_config = yaml.load(f)
    else:
        recipe_config = {}

    target_path = _get_defaultable_option(recipe_config, "targetPath", "/app")
    target_root = os.getenv("TARGET_ROOT", os.path.join(PROJECT_DIRECTORY, ".."))

    docker_image_id = str(uuid.uuid4())
    recipe_type = _recipe_type(path, recipe_config)
    if recipe_type == "dockerfile":
        _check_call(["docker", "build", "-t", docker_image_id, "."], cwd=path)
        _check_call(["docker", "run", "-u", str(os.getuid()), "-v", "%s:%s" % (target_root, target_path), "--rm", "-t", docker_image_id], cwd=path)
    else:
        compose_args = []
        common_docker_compose_path = os.path.join(path, "common-docker-compose.yml")
        docker_compose_path = os.path.join(path, "docker-compose.yml")
        if os.path.exists(common_docker_compose_path):
            compose_args.extend(["-f", common_docker_compose_path])

        compose_args.extend(["-f", docker_compose_path])
        compose_args.extend(["-p", docker_image_id])

        compose_kwd = {
            'cwd': path,
            'env': {
                'TARGET_PATH': target_path,
                'TARGET_ROOT': target_root,
            }
        }

        try:
            try:
                _check_call_flattened(["docker-compose", compose_args, "build", "test"], **compose_kwd)
                _check_call_flattened(["docker-compose", compose_args, "run", "test"], **compose_kwd)
            finally:
                _check_call_flattened(["docker-compose", compose_args, "kill"], **compose_kwd)
        finally:
            _check_call_flattened(["docker-compose", compose_args, "rm", "-f"], **compose_kwd)


def _recipe_type(path, recipe_config):
    recipe_type = recipe_config.get("recipe_type", None)
    if recipe_type is None:
        docker_compose_path = os.path.join(path, "docker-compose.yml")
        docker_file_path = os.path.join(path, "Dockerfile")
        if os.path.exists(docker_compose_path):
            recipe_type = "docker-compose"
        elif os.path.exists(docker_file_path):
            recipe_type = "dockerfile"
        elif "docker_image" in recipe_config:
            recipe_type = "docker-image"
        else:
            raise Exception("Unable to determine recipe type for [%s]" % path)

    if recipe_type not in ["docker-compose", "dockerfile", "docker-image"]:
        raise Exception("Unknown recipe type [%s]" % recipe_type)

    return recipe_type


def _check_call_flattened(cmd, *args, **kwd):
    flat_cmd = []
    for cmd_part in cmd:
        if isinstance(cmd_part, list):
            add = flat_cmd.extend
        else:
            add = flat_cmd.append
        add(cmd_part)
    _check_call(flat_cmd, *args, **kwd)


def _check_call(cmd, cwd, env={}):
    print("Executing test command [%s]" % " ".join(cmd))
    new_env = os.environ.copy()
    new_env.update(env)
    ret = subprocess.check_call(cmd, cwd=cwd, shell=False, env=new_env)
    print("Command exited with return code [%s]" % ret)


def _get_defaultable_option(recipe_config, key, default):
    default_key = "default" + key[0].upper() + key[1:]
    if key in recipe_config:
        return recipe_config.get(key)
    elif default_key in JUST_DOCKERFILES_CONFIG:
        return JUST_DOCKERFILES_CONFIG.get(default_key)
    else:
        return default


for recipe_name in os.listdir(RECIPE_DIRECTORY):
    the_t_function = _create_function_for_recipe(recipe_name)
    globals()[the_t_function.__name__] = the_t_function
