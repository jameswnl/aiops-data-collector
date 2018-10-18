import logging
from threading import Thread, current_thread

import requests

import s3

logger = logging.getLogger()
HEADERS = {'Content-type': 'application/json'}


def download_and_pass_data_thread(filesystem, bucket, uri, next_service):
    """Spawn a thread worker for data downloading task.

    Requests the data to be downloaded and pass it to the next service
    """
    def worker():
        thread = current_thread()
        logger.info('%s: Worker started', thread.name)
        try:
            # Fetch data
            data = s3.fetch(filesystem, bucket, uri)
            # Pass to next service
            logger.info('%s: Downloaded records %s', thread.name, data.shape)
            requests.post(
                f'http://{next_service}',
                data=data.to_json(),
                headers=HEADERS
            )
        except FileNotFoundError as exception:
            logger.warning('%s: %s', thread.name, exception)
        except requests.HTTPError as exception:
            logger.error('Unable to pass data: %s', exception)
        logger.debug('%s: Done, exiting', thread.name)

    thread = Thread(target=worker)
    thread.start()
