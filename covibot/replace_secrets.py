import json
import os
from pathlib import Path

config_path = Path(__name__).parent.absolute() / '.chalice' / 'config.json'
print(config_path)
with open(config_path, 'r+') as f:
    config = json.load(f)

# Replace env vars
token = os.environ['SLACK_BOT_TOKEN']
secret = os.environ['SLACK_SIGNING_SECRET']
testing = os.environ['TESTING']

config['stages']['dev']['environment_variables']['SLACK_BOT_TOKEN'] = token
config['stages']['dev']['environment_variables']['SLACK_SIGNING_SECRET'] = secret
config['stages']['dev']['environment_variables']['TESTING'] = testing
with open(Path('.chalice/config.json'), 'r+') as f:
    config = json.dump(config, f, indent=4, ensure_ascii=False)
