import json
import os
import sys
from pathlib import Path


chalice_config_path = Path(__file__).parent.absolute() / '.chalice'
config_path = chalice_config_path / 'config.json'


def replace():
    config = read_config()
    dump_env_vars(config)
    replace_config(config)


def read_config():
    with open(config_path, 'r+') as f:
        config = json.load(f)

    return config


def dump_env_vars(config):
    # Replace env vars
    token = os.environ['SLACK_BOT_TOKEN']
    secret = os.environ['SLACK_SIGNING_SECRET']
    testing = os.environ['TESTING']
    config['stages']['dev']['environment_variables']['SLACK_BOT_TOKEN'] = token
    config['stages']['dev']['environment_variables']['SLACK_SIGNING_SECRET'] = secret
    config['stages']['dev']['environment_variables']['TESTING'] = testing

    return config


def replace_config(config):
    with open(config_path, 'w+') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


def unreplace():
    config = read_config()
    config['stages']['dev']['environment_variables']['SLACK_BOT_TOKEN'] = '$SBT'
    config['stages']['dev']['environment_variables']['SLACK_SIGNING_SECRET'] = '$SSS'
    config['stages']['dev']['environment_variables']['TESTING'] = '$TESTING'
    replace_config(config)


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        replace()
    else:
        unreplace()
