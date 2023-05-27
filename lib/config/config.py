'''
Parses and validates app confguration files
'''
import json
from typing import List
import yaml
from loguru import logger as log
from schema import Optional, Or, Regex, Schema
from ultralytics import YOLO

# TIME_REGEX is used to validate start/end times in the scheduling configuration
TIME_REGEX = r'\d{2}:\d{2}'

# We'll use this map to store all objects to be recognized per webhook
# then store the index of the webhooks that need to be called when a configured object is detected.
# This keeps us from having to loop all webhooks/objects every time an object is detecteced.
OBJECT_TO_WEBHOOK_MAP = {}

config_schema = Schema(
    {
        'config': {
            'source': str,
            Optional('confidence', default=0.6): float,
            Optional('model', default='yolov8n.pt'): str,
            Optional('loglevel', default='info'): Or(
             'trace',
             'debug',
             'info',
             'success',
             'warning',
             'error',
             'critical',
             error='loglevel must be one of: "trace", "debug", "info", "success", "warning", "error", "critical"',
            ),
            Optional('schedule'): {
                'startTime': Regex(TIME_REGEX, error='Start time must be in the format of 00:00'),
                'endTime': Regex(TIME_REGEX, error='End time must be in the format of 00:00'),
            },
            Optional('webhooks'): [
                {
                    'url': lambda x: x.startswith(('http', 'https')),
                    'objects': [
                        str
                    ],
                    Optional('notifyInterval', default=0): int,
                    Optional('method', default='post'): str,
                    Optional('headers'): object,
                    Optional('body'): str,
                    Optional('timeout', default=5): int
                }
            ]
        }
    }, ignore_extra_keys=True
)


class InvalidObjectException(Exception):
    '''
    Exception raised when object name in configuration is not suppored by the model.
    '''


def validate_objects(model_names: dict, objects: List[str]):
    '''
    Validates list of objects in config are supported by the model
    '''
    supported_class_names = model_names.values()
    for object_name in objects:
        object_name = object_name.lower()
        if object_name not in supported_class_names:
            error_str = f"Object {object_name} not supported by model"
            log.error(f"{error_str}. Supported objects: {list(supported_class_names)}")
            raise InvalidObjectException(error_str)


def parse(config_file: str) -> dict:
    '''
    Reads in the config file and returns a dictionary that has been validated
    '''

    # Empty config object to unmarshal yaml/json data to before validating it
    config = {}

    # Attempt to unmarshal config
    with open(config_file, 'r', encoding='UTF-8') as file:
        if config_file.endswith(('.yml', '.yaml')):
            config = yaml.safe_load(file)
        elif config_file.endswith('.json'):
            config = json.load(file)
        else:
            log.warning('Only YAML/JSON supported. You may not be using the appropriate configuration file format.')

        # Use config object returned for defaults
        config = config_schema.validate(config)
        model = YOLO(config['config']['model'])

        # If we made it this far, the config is valid, let's populate OBJECT_TO_WEBHOOK_MAP for fast lookup later
        # Set up our map for tracking which webhooks need to be called when an object is detected
        for webhook in config['config']['webhooks']:
            for object_name in webhook['objects']:
                if object_name not in OBJECT_TO_WEBHOOK_MAP:
                    OBJECT_TO_WEBHOOK_MAP[object_name] = []
                OBJECT_TO_WEBHOOK_MAP[object_name].append(webhook)

        # Validate objects in config are supported by model
        validate_objects(model.names, OBJECT_TO_WEBHOOK_MAP.keys())

    return config
