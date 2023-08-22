'''
Executes webhook requests
'''
import json
from datetime import datetime
from typing import Any, List, Dict
from hashlib import md5
from os import environ
from string import Template
import requests
from loguru import logger as log

# WEBHOOKS_LAST_NOTIFIED is a dictionary with each webhook config hashed as the key and the last notify time as the value
# This allows us to store the last notified time per webhook and ensure each webhook is tracked properly since it's
# possible to have multiple webhooks with matching attributes and there's no need to ask the user for a name/id
WEBHOOKS_LAST_NOTIFIED = {}


def sanitize_webhook(webhook: Dict, template_strs: Dict) -> Dict:
    '''
    Replace url/header template strings.
    From:
    { Authorization: Bearer $API_TOKEN }
    To:
    { Authorization: Bearer eyJ0e... }
    '''
    # Ensure we don't overwrite the existing templates webhook str in memory
    sanitized_webhook = {}
    sanitized_headers = {}

    for key, value in webhook['headers'].items():
        sanitized_headers[key] = Template(value).substitute(template_strs)

    sanitized_webhook['url'] = Template(webhook['url']).substitute(template_strs)
    sanitized_webhook['method'] = Template(webhook['method']).substitute(template_strs)
    sanitized_webhook['headers'] = sanitized_headers
    sanitized_webhook['body'] = Template(webhook['body']).substitute(template_strs)
    sanitized_webhook['timeout'] = webhook['timeout']
    sanitized_webhook['notifyInterval'] = webhook['notifyInterval']
    sanitized_webhook['objects'] = webhook['objects']

    return sanitized_webhook


def process(webhooks: List[Dict], object_name: str, object_confidence: str) -> None:
    '''
    Determine if webhooks needed to be processed, if so, process
    '''
    # KV pairs that can be replaced in the URL/headers/data
    template_strs = {
        **environ,
        'object_name': object_name,
        'object_confidence': object_confidence
    }

    for webhook in webhooks:
        # Subsitute url, headers, body with object data, environment variables for secrets
        webhook = sanitize_webhook(webhook, template_strs)
        # Create opts to send request and hash to render an immutable ID to track last notification
        # Opts for requests library
        request_opts = {
            'url': webhook['url'],
            'method': webhook['method'],
            'headers': webhook['headers'],
            'data': webhook['body'],
            'timeout': webhook['timeout']
        }
        # Get the webhook's ID and check when webhook was last notified
        webhook_hash = dict_hash(webhook)
        if webhook_hash in WEBHOOKS_LAST_NOTIFIED:
            time_since_last_notified = datetime.now() - WEBHOOKS_LAST_NOTIFIED[webhook_hash]
            # If notified within the last configured interval, in seconds, skip
            seconds_since_last_notified = time_since_last_notified.total_seconds()
            if seconds_since_last_notified < webhook['notifyInterval']:
                log.debug(f"Notified {webhook['url']} {seconds_since_last_notified} seconds ago. Skipping...")
                return

        # Otherwise continue and notify
        try:
            log.info(f"Object {object_name} detected with confidence of {object_confidence}. Notifying {webhook['url']}")
            response = requests.request(**request_opts)
            # Raise an error in the event of a non 2XX response code
            response.raise_for_status()
            # Request was successful, so we store last notified time
            WEBHOOKS_LAST_NOTIFIED[webhook_hash] = datetime.now()
            log.success(f"Notified {webhook['url']} successfully")
            log.debug(f"{webhook['url']} response code: {response.status_code}, body: {response.text}")
        except requests.exceptions.HTTPError as e:
            log.debug(f"{webhook['url']} response code: {response.status_code}, body: {response.text}")
            log.error(f"{e}.{webhook['url']} response code: {response.status_code}, reason: {response.reason}")
        except Exception as e:
            log.error(e)


def dict_hash(dictionary: Dict[str, Any]) -> str:
    '''MD5 hash of a dictionary.'''
    dhash = md5()
    # We need to sort arguments so {'a': 1, 'b': 2} is the same as {'b': 2, 'a': 1}
    encoded = json.dumps(dictionary, sort_keys=True).encode()
    dhash.update(encoded)
    return dhash.hexdigest()
