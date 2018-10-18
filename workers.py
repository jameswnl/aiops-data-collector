import logging
from threading import Thread

import requests

import s3

logger = logging.getLogger(__name__)
HEADERS = {'Content-type': 'application/json'}


def download_and_pass_data_thread(filesystem, bucket, uri, next_service):
    """Spawn a thread worker for data downloading task.

    Requests the data to be downloaded and pass it to the next service
    """
    def worker():
        logger.debug('Worker started')
        try:
            # Fetch data
            data = s3.fetch(filesystem, bucket, uri)
            # Pass to next service
            requests.post(
                f'http://{next_service}',
                data=data.to_json(),
                headers=HEADERS
            )
        except FileNotFoundError as exception:
            logger.warning(exception)
        except requests.HTTPError as exception:
            logger.error('Unable to pass data: %s', exception)
        logger.debug('Worker is done, exiting')

    thread = Thread(target=worker, name=f'Worker for {uri}')
    thread.start()
