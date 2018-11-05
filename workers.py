import logging
from threading import Thread, current_thread
from json import dumps

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
            s3_data = s3.fetch(filesystem, bucket, uri)
            logger.info(
                '%s: Downloaded records %s',
                thread.name,
                s3_data.shape
            )

            # Build the POST data object
            data = {
                'data': s3_data.to_dict(),
                # Set data identifier (for now, should be handled better)
                'id': uri.split('/')[0]
            }

            # Pass to next service
            requests.post(
                f'http://{next_service}',
                data=dumps(data),
                headers=HEADERS
            )
        except FileNotFoundError as exception:
            logger.warning('%s: %s', thread.name, exception)
        except requests.HTTPError as exception:
            logger.error('Unable to pass data: %s', exception)
        logger.debug('%s: Done, exiting', thread.name)

    thread = Thread(target=worker)
    thread.start()
