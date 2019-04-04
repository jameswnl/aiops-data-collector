import tarfile
import logging

from threading import current_thread
from io import BytesIO

import prometheus_metrics
from . import utils

BUFFER_SIZE = 10240
LOGGER = logging.getLogger()


def _only_csv_file(member: tarfile.TarInfo) -> bool:
    """Selector for CSV files only in a TAR file."""
    return member.name.endswith('.csv')


def _csv_parser(file_obj: BytesIO) -> bytes:
    """Extract CSV data from TAR.GZ file.

    Extracts all CSV files from a TAR.GZ archive and combines them into a list
    of dictionary objects.
    :param filename: Name of the filename to parse
    """
    with tarfile.open(fileobj=file_obj) as tar:
        # Read just the first CSV available
        member = next(filter(_only_csv_file, tar.members), None)
        # Return if no CSV file was found
        if not member:
            return

        # Extract CSV file object
        csv_data = tar.extractfile(member)
        # Read the CSV content in chunks
        yield from iter(lambda: csv_data.read(BUFFER_SIZE), b'')


def worker(source_url, source_id, dest_url, b64_identity):
    """Worker for Insights Client uploads.

    Args:
        source_url (str): URL of the source
        source_id (str): Job identifier
        dest (str): URL where to pass data
        b64_identity (str): Red Hat Identity base64 string

    """
    thread = current_thread()
    LOGGER.debug('%s: Worker started', thread.name)

    # Fetch data
    prometheus_metrics.METRICS['gets'].inc()
    try:
        resp = utils.retryable('get', source_url, stream=True)
    except utils.RetryFailedError as exception:
        LOGGER.error(
            '%s: Unable to fetch source data for "%s": %s',
            thread.name, source_id, exception
        )
        prometheus_metrics.METRICS['get_errors'].inc()
        return
    prometheus_metrics.METRICS['get_successes'].inc()

    file_obj = BytesIO(resp.content)

    # Store payload ID in a header
    headers = {
        'source_id': source_id,
        'x-rh-identity': b64_identity,
    }

    # Pass to next service
    prometheus_metrics.METRICS['posts'].inc()
    try:
        resp = utils.retryable(
            'post',
            dest_url,
            data=_csv_parser(file_obj),
            headers=headers
        )
        prometheus_metrics.METRICS['post_successes'].inc()
    except utils.RetryFailedError as exception:
        LOGGER.error(
            '%s: Failed to pass data for "%s": %s',
            thread.name, source_id, exception
        )
        prometheus_metrics.METRICS['post_errors'].inc()

    LOGGER.debug('%s: Done, exiting', thread.name)
