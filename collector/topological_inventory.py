import logging
import os
from threading import current_thread
from collections import defaultdict

import yaml

import prometheus_metrics
from . import utils
from .env import (APP_NAME, SOURCES_HOST, SOURCES_PATH,
                  TOPOLOGICAL_INVENTORY_HOST, TOPOLOGICAL_INVENTORY_PATH)

LOGGER = logging.getLogger()
CFG_DIR = '{}/configs'.format(os.path.dirname(__file__))

# Provide mapping for all available services, default to TOPOLOGICAL
SERVICES_URL = defaultdict(
    lambda: dict(
        host=TOPOLOGICAL_INVENTORY_HOST,
        path=TOPOLOGICAL_INVENTORY_PATH
    ),
    SOURCES=dict(
        host=SOURCES_HOST,
        path=SOURCES_PATH
    )
)


def _load_yaml(filename: str) -> dict:
    """Yaml filename loader helper.

    Parameters
    ----------
    filename (str)
        Yaml file to load

    Returns
    -------
    dict
        YAML content as Pythonic dict

    """
    with open(filename) as yaml_file:
        return yaml.full_load(yaml_file)


APP_CONFIG = _load_yaml(f'{CFG_DIR}/topological_app_config.yml').get(APP_NAME)
QUERIES = _load_yaml(f'{CFG_DIR}/topological_queries.yml')


def _update_fk(page_data: list, fk_name: str, fk_id: str) -> dict:
    """Mutate Rows with Foreign key info.

    Updates foreign key values for each entry in given page_data

    Parameters
    ----------
    page_data (list)
        Data on a page which should be modified
    fk_name (str)
        Column where the Foreign Key is located
    fk_id (str)
        Foreign Key value

    Returns
    -------
    list
        Updated page_data

    """
    if not (fk_name and fk_id):
        return page_data

    for row in page_data:
        row[fk_name] = fk_id
    return page_data


def _collect_data(host: dict, url: str, fk_name: str = None,
                  fk_id: str = None, headers: dict = None) -> dict:
    """Aggregate data from all pages.

    Returns data aggregated from all pages together

    Parameters
    ----------
    host (str)
        Service host
    url (str)
        URI to the first page, where to start the traverse
    fk_name (str)
        Foreign key column to update if needed
    fk_id (str)
        Foreign key value to update if needed

    Returns
    -------
    dict
        All data aggregated across all pages

    Raises
    ------
    utils.RetryFailedError
        Connection failed, data is not complete

    """
    # Collect data from the first page
    url = f'{host["host"]}/{host["path"]}/{url}'
    prometheus_metrics.METRICS['gets'].inc()
    resp = utils.retryable('get', url, headers=headers)
    prometheus_metrics.METRICS['get_successes'].inc()
    resp = resp.json()
    all_data = resp['data']

    # Walk all pages
    while resp['links'].get('next'):
        prometheus_metrics.METRICS['gets'].inc()
        resp = utils.retryable(
            'get',
            f'{host["host"]}{resp["links"]["next"]}',
            headers=headers
        )
        resp = resp.json()
        prometheus_metrics.METRICS['get_successes'].inc()
        all_data += resp['data']

    return _update_fk(all_data, fk_name, fk_id)


def _query_main_collection(entity: dict, headers: dict = None) -> dict:
    """Query a Collection.

    Parameters
    ----------
    entity (dict)
        A query_spec entity to download

    Returns
    -------
    dict
        All data aggregated across all pages

    Raises
    ------
    utils.RetryFailedError
        Connection failed, data is not complete

    """
    collection = entity['main_collection']
    service = SERVICES_URL[entity.get('service')]

    return _collect_data(service, collection, headers=headers)


def _query_sub_collection(entity: dict, data: dict,
                          headers: dict = None) -> dict:
    """Query a SubCollection for all records in the main collection.

    Parameters
    ----------
    entity (dict)
        A query_spec entity to download
    data (dict)
        Already available data for reference
    foreign_key (str)
        Foreign key column to be populated in sub-collection records

    Returns
    -------
    dict
        All data aggregated across all pages

    Raises
    ------
    utils.RetryFailedError
        Connection failed, data is not complete

    """
    main_collection = entity['main_collection']
    sub_collection = entity['sub_collection']
    foreign_key = entity['foreign_key']
    service = SERVICES_URL[entity.get('service')]

    url = f'{main_collection}/{{}}/{sub_collection}'
    all_data = []
    for item in data[main_collection]:
        all_data += _collect_data(service, url.format(item['id']),
                                  foreign_key, item['id'], headers=headers)
    return all_data


def worker(_: str, source_id: str, dest: str, b64_identity: str) -> None:
    """Worker for topological inventory.

    Parameters
    ----------
    _ (str)
        Skipped
    source_id (str)
        Job identifier
    dest (str)
        URL where to pass data
    b64_identity (str)
        Red Hat Identity base64 string

    """
    thread = current_thread()
    LOGGER.debug('%s: Worker started', thread.name)

    # Build the POST data object
    data = {
        'id': source_id,
        'data': {}
    }
    headers = {"x-rh-identity": b64_identity}

    for entity in APP_CONFIG:
        query_spec = QUERIES[entity]

        if query_spec.get('sub_collection'):
            try:
                all_data = _query_sub_collection(
                    query_spec,
                    data['data'],
                    headers=headers
                )
            except utils.RetryFailedError as exception:
                prometheus_metrics.METRICS['get_errors'].inc()
                LOGGER.error(
                    '%s: Unable to fetch source data for "%s": %s',
                    thread.name, source_id, exception
                )
                return
        else:
            try:
                all_data = _query_main_collection(query_spec, headers=headers)
            except utils.RetryFailedError as exception:
                prometheus_metrics.METRICS['get_errors'].inc()
                LOGGER.error(
                    '%s: Unable to fetch source data for "%s": %s',
                    thread.name, source_id, exception
                )
                return

        LOGGER.info(
            '%s: %s: %s\t%s',
            thread.name, source_id, entity, len(all_data)
        )
        data['data'][entity] = all_data

    # Pass to next service
    prometheus_metrics.METRICS['posts'].inc()
    try:
        utils.retryable('post', dest, json=data, headers=headers)
        prometheus_metrics.METRICS['post_successes'].inc()
    except utils.RetryFailedError as exception:
        LOGGER.error(
            '%s: Failed to pass data for "%s": %s',
            thread.name, source_id, exception
        )
        prometheus_metrics.METRICS['post_errors'].inc()

    LOGGER.debug('%s: Done, exiting', thread.name)
