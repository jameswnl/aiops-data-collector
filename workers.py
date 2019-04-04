import logging
from threading import Thread
from uuid import uuid4

from target_worker import WORKER

LOGGER = logging.getLogger()

LIVE_THREADS = []


def download_job(
        source_url: str,
        source_id: str,
        dest_url: str,
        b64_identity: str = None
) -> None:
    """Spawn a thread worker for data downloading task.

    Requests the data to be downloaded and pass it to the next service

    Args:
        source_url (str): URL of the source
        source_id (str): Job identifier
        dest (str): URL where to pass data
        b64_identity (str): Red Hat Identity base64 string

    """
    # When source_id is missing, create our own
    source_id = source_id or str(uuid4())

    thread = Thread(
        target=WORKER,
        args=(source_url, source_id, dest_url, b64_identity)
        )
    LIVE_THREADS.append(thread)
    thread.start()

    # Cleanup
    for thread in LIVE_THREADS:
        if not thread.is_alive():
            thread.join()
            LIVE_THREADS.remove(thread)
