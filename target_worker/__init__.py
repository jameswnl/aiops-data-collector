"""Target Worker library.

With the help of this library a target worker can be assigned on-the-fly
The library also provides all necessary information to the worker to process
the GET requests
"""

import logging
import os
import sys

logger = logging.getLogger()

if os.environ.get('INPUT_DATA_FORMAT') == 'TOPOLOGY':
    logger.info('Target Worker is Topology')

    HOST = os.environ.get('TOPOLOGY_INVENTORY_HOST')
    ENDPOINT = os.environ.get('TOPOLOGY_INVENTORY_ENDPOINT')

    if not ENDPOINT:
        logger.error('Environment not set properly, '
                     'missing TOPOLOGY_INVENTORY_ENDPOINT')
        sys.exit(1)

    NAME = 'worker_topology'
    INFO = {
        'host': HOST,
        'endpoint': ENDPOINT,
        'queries_by_app': {
            'aiops-volume-type-validation': [
                'container_nodes',
                'container_nodes_tags',
                'vms',
                'sources',
                'volume_attachments',
                'volumes',
                'volume_types'
            ],
            'aiops-idle-cost-savings': [
                'container_nodes',
                'container_nodes_tags',
                'vms',
                'sources',
                'container_groups',
                'containers',
                'container_resource_quotas',
                'container_projects',
                'flavors'
            ]
        },
        'queries': {
            'container_nodes': {
                'main_collection': 'container_nodes?filter[archived_at][nil]',
                'query_string': ''
            },
            'container_nodes_tags': {
                'main_collection': 'container_nodes',
                'sub_collection': 'tags',
                'foreign_key': 'container_node_id',
                'query_string': ''
            },
            'volume_attachments': {
                'main_collection': 'volume_attachments',
                'query_string': ''
            },
            'volumes': {
                'main_collection': 'volumes?filter[archived_at][nil]',
                'query_string': ''
            },
            'volume_types': {
                'main_collection': 'volume_types',
                'query_string': ''
            },
            'vms': {
                'main_collection': 'vms?filter[archived_at][nil]',
                'query_string': ''
            },
            'sources': {
                'main_collection': 'sources',
                'query_string': ''
            },
            'container_groups': {
                'main_collection': 'container_groups?filter[archived_at][nil]',
                'query_string': ''
            },
            'containers': {
                'main_collection': 'container_groups?filter[archived_at][nil]',
                'sub_collection': 'containers',
                'query_string': ''
            },
            'container_resource_quotas': {
                'main_collection': 'container_resource_quotas?filter[archived_at][nil]',
                'query_string': ''
            },
            'container_projects': {
                'main_collection': 'container_projects?filter[archived_at][nil]',
                'query_string': ''
            },
            'flavors': {
                'main_collection': 'flavors',
                'query_string': ''
            }
        }
    }


elif os.environ.get('INPUT_DATA_FORMAT') == 'HOST':
    logger.info('Target Worker is Host')
    HOST_INVENTORY_HOST = os.environ.get('HOST_INVENTORY_HOST')
    HOST_INVENTORY_PATH = os.environ.get('HOST_INVENTORY_PATH')
    PER_PAGE = os.environ.get('HOST_INVENTORY_PER_PAGE', 50)

    if not HOST_INVENTORY_HOST and HOST_INVENTORY_PATH:
        logger.error('Environment not set properly, '
                     'missing HOST_INVENTORY_HOST and/or HOST_INVENTORY_PATH')
        sys.exit(1)
    NAME = 'worker_host'

    url = f'{HOST_INVENTORY_HOST}/{HOST_INVENTORY_PATH}?per_page=' + PER_PAGE
    INFO = {'host_inventory_url': url}


else:
    logger.info('Target Worker is Clustering')

    NAME = 'worker_clustering'
    INFO = {}


__all__ = ['NAME', 'INFO']
