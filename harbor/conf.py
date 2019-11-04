import json
import os
import logging
import sys
from logging.handlers import RotatingFileHandler

config_root = os.environ.get('HARBOR_ROOT')
config_path = os.path.join(config_root, 'config.json')
config = None

if config is None:
    with open(config_path, encoding='utf8') as json_data_file:
        config = json.load(json_data_file)

logging.basicConfig(
        handlers=[
            RotatingFileHandler(
                os.path.join(config_root, 'harbor.log'),
                maxBytes=100000,
                backupCount=10
            ),
            logging.StreamHandler(sys.stdout)
        ],
        level=logging.DEBUG,
        format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S'
)


DB_CONNECTION_STRING = f'sqlite:////{config_root}/storage.db'
PROVIDERS = config.get('providers', [])
UPDATE_FREQUENCY = config.get('app', {}).get('update_frequency', 30)
MAX_REQUEST_RATE = config.get('app', {}).get('max_request_rate', 5)
REQUESTS_DELAY_SEC = config.get('app', {}).get('delay_sec', 3)
