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
            },
            'container_groups': {
                'main_collection': 'container_groups',
                'query_string': 'archived_at'
            },
            'containers': {
                'main_collection': 'container_groups',
                'sub_collection': 'containers',
                'query_string': 'archived_at'
            },
            'container_resource_quotas': {
                'main_collection': 'container_resource_quotas',
                'query_string': 'archived_at'
            },
            'container_projects': {
                'main_collection': 'container_projects',
                'query_string': 'archived_at'
            },
            'flavors': {
                'main_collection': 'flavors',
                'query_string': ''
            }
        }
    }


else:
    logger.info('Target Worker is Clustering')

    NAME = 'worker_clustering'
    INFO = {}


__all__ = ['NAME', 'INFO']
