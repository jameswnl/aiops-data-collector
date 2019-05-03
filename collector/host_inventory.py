import logging
import math
from threading import current_thread

import prometheus_metrics
from . import utils
from .env import HOST_INVENTORY_HOST, HOST_INVENTORY_PATH

LOGGER = logging.getLogger()
URL = f'{HOST_INVENTORY_HOST}/{HOST_INVENTORY_PATH}'


def _retrieve_hosts(headers: dict) -> dict:
    """Collect all hosts for account.

    Parameters
    ----------
    headers (dict)
        HTTP Headers that will be used to request data

    Returns
    -------
    dict
        Host collection

    """
    url = URL + '/hosts?page={}'
    url_profile = URL + '/hosts/{}/system_profile'

    # Perform initial request
    prometheus_metrics.METRICS['gets'].inc()
    resp = utils.retryable('get', url.format(1), headers=headers)
    prometheus_metrics.METRICS['get_successes'].inc()
    resp = resp.json()
    total = resp['total']
    # Iterate next pages if any
    pages = math.ceil(total / resp['per_page'])

    ids = ','.join([x['id'] for x in resp['results']])
    prometheus_metrics.METRICS['gets'].inc()
    resp = utils.retryable('get', url_profile.format(ids), headers=headers)
    prometheus_metrics.METRICS['get_successes'].inc()
    results = resp.json()['results']
    for page in range(2, pages+1):
        prometheus_metrics.METRICS['gets'].inc()
        resp = utils.retryable('get', url.format(page), headers=headers)
        prometheus_metrics.METRICS['get_successes'].inc()
        ids = ','.join([x['id'] for x in resp.json()['results']])
        prometheus_metrics.METRICS['gets'].inc()
        resp = utils.retryable('get', url_profile.format(ids), headers=headers)
        prometheus_metrics.METRICS['get_successes'].inc()
        results += resp.json()['results']

    return dict(results=results, total=total)


def worker(_: str, source_id: str, dest: str, misc: dict) -> None:
    """Worker for host inventory.

    Parameters
    ----------
    _ (str)
        Skipped
    source_id (str)
        Job identifier
    dest (str)
        URL where to pass data
    misc (dict)
        contains e.g. Red Hat Identity base64 string and account_id

    """
    thread = current_thread()
    LOGGER.debug('%s: Worker started', thread.name)

    b64_identity = misc['b64_identity']
    account_id = misc['account_id']

    LOGGER.debug('to retrieve hosts of account_id: %s', account_id)

    headers = {"x-rh-identity": b64_identity}

    try:
        out = _retrieve_hosts(headers)
    except utils.RetryFailedError as exception:
        prometheus_metrics.METRICS['get_errors'].inc()
        LOGGER.error(
            '%s: Unable to fetch source data for "%s": %s',
            thread.name, source_id, exception
        )
        return
    LOGGER.debug(
        'Received data for account_id=%s has total=%s',
        account_id, out.get('total')
    )

    # Build the POST data object
    data = {
        'account': account_id,
        'data': out,
    }

    # Pass to next service
    prometheus_metrics.METRICS['posts'].inc()
    try:
        utils.retryable('post', dest, json=data, headers=headers)
        utils.set_processed(account_id)
        prometheus_metrics.METRICS['post_successes'].inc()
    except utils.RetryFailedError as exception:
        LOGGER.error(
            '%s: Failed to pass data for "%s": %s',
            thread.name, source_id, exception
        )
        prometheus_metrics.METRICS['post_errors'].inc()

    LOGGER.debug('%s: Done, exiting', thread.name)
