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
        'queries': {
            'container_nodes': {
                'main_collection': 'container_nodes',
                'query_string': 'archived_at'
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
                'main_collection': 'volumes',
                'query_string': 'archived_at'
            },
            'volume_types': {
                'main_collection': 'volume_types',
                'query_string': ''
            },
            'vms': {
                'main_collection': 'vms',
                'query_string': 'archived_at'
            },
            'sources': {
                'main_collection': 'sources',
                'query_string': ''
            }
        }
    }


else:
    logger.info('Target Worker is Clustering')

    NAME = 'worker_clustering'
    INFO = {}


__all__ = ['NAME', 'INFO']
