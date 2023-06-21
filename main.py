#!/usr/bin/env python3
'''
cv-notifier recognizes objects using YOLOv8 and calls configurable webhooks
'''

from datetime import datetime
from sys import stdout
from time import sleep
from loguru import logger as log
from ultralytics import YOLO
from lib.config.args import args
from lib.config import config
from lib.utils import time as time_utils
from lib.webhooks import requests


def main():
    '''
    main
    '''
    arguments = args()

    # Read config from local file
    configuration = config.parse(arguments.config)['config']

    # Set up a logger based on configured log level
    log.remove()
    log.add(stdout, level=configuration['loglevel'].upper())

    # Maintain state of whether we logged when detections will resume
    logged_scheduling_message = False
    # Maintain results to keep from spawning zombie threads
    results = None

    # Start processing
    while True:
        # Determine if we need to run on a schedule or not
        start_time, end_time = time_utils.parse_schedule_times(configuration)
        schedule_set = start_time and end_time

        if schedule_set and not time_utils.in_between(datetime.now(), start_time, end_time):
            if not logged_scheduling_message:
                log.info(f"Outside of scheduled hours. Skipping detections until {start_time.strftime('%I:%M %p')}")
                # Prevent unnecessary logs
                logged_scheduling_message = True
                sleep(60)

        if (schedule_set and time_utils.in_between(datetime.now(), start_time, end_time)) or not schedule_set:
            # Reset logger message
            logged_scheduling_message = False
            log.info('Inside scheduled hours or scheduling is disabled. Detecting objects...')

            model = YOLO(configuration['model'])
            # Only assign results if it hasn't been before (start of the program) so that we don't create any zombie threads (according to tini)
            results = results or model.predict(source=configuration['source'],
                                               conf=configuration['confidence'],
                                               stream=True,
                                               verbose=False)

            for result in results:
                if result.boxes:
                    box = result.boxes[-1]
                    class_id = int(box.cls)
                    detected_object_name = model.names[class_id]
                    detected_object_confidence = round(float(box.conf), 2)
                    log.debug(f'Detected object: {detected_object_name} with confidence score of {detected_object_confidence}')
                    if detected_object_name in config.OBJECT_TO_WEBHOOK_MAP:
                        webhooks_to_process = config.OBJECT_TO_WEBHOOK_MAP[detected_object_name]
                        requests.process(webhooks_to_process, detected_object_name, detected_object_confidence)

                # If we're outside scheduled hours, let's break the loop which will then reset model and results
                if schedule_set and not time_utils.in_between(datetime.now(), start_time, end_time):
                    break


if __name__ == '__main__':
    main()
