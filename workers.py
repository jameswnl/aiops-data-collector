from contextlib import suppress
import logging
import os
from threading import Thread, current_thread
from tempfile import NamedTemporaryFile
from uuid import uuid4

import requests

logger = logging.getLogger()


try:
    # Try to import a provided parser. This can be AI service specific.
    from parser import parse
except ImportError:
    logger.warning('No parser provided, fallback used!')

    def parse(_):
        """Fallback parser.

        Used when no data preprocessor is provided.
        """
        return {}

logger = logging.getLogger()
CHUNK = 10240
MAX_RETRIES = 3


def download_job(source_url: str, source_id: str, dest_url: str) -> None:
    """Spawn a thread worker for data downloading task.

    Requests the data to be downloaded and pass it to the next service
    :param source_url: Data source location
    :param source_id: Data identifier
    :param dest_url: Location where the collected data should be received
    """
    # When source_id is missing, create our own
    source_id = source_id or str(uuid4())

    def worker() -> None:
        """Download, extract data and forward the content."""
        thread = current_thread()
        logger.debug('%s: Worker started', thread.name)

        # Fetch data
        try:
            resp = requests.get(source_url, stream=True)

            with NamedTemporaryFile(delete=False) as tmp_file:
                file_name = tmp_file.name

                for chunk in filter(None, resp.iter_content(chunk_size=CHUNK)):
                    tmp_file.write(chunk)

        except requests.HTTPError as exception:
            logger.error(
                '%s: Unable to fetch source data for "%s": %s',
                thread.name, source_id, exception
            )
            return
        except IOError as exception:
            logger.error(
                '%s: Unable to create temp file for "%s": %s',
                thread.name, source_id, exception
            )
            return

        # Unpack data and stream it

        # Build the POST data object
        data = {
            'id': source_id,
            'data': parse(file_name),
        }

        # Pass to next service
        with requests.Session() as session:
            for attempt in range(MAX_RETRIES):
                try:
                    resp = session.post(f'http://{dest_url}', json=data)

                    resp.raise_for_status()
                except requests.HTTPError as e:
                    logging.warning(
                        '%s: Request failed (attempt #%d), retrying: %s',
                        thread.name, attempt, str(e)
                    )
                    continue
                else:
                    break

                logger.error(
                    '%s: All attempts failed for "%s"', thread.name, source_id
                )

        with suppress(IOError):
            os.remove(file_name)

        logger.debug('%s: Done, exiting', thread.name)

    thread = Thread(target=worker)
    thread.start()
