"""Target Worker library.

With the help of this library a target worker can be assigned on-the-fly
The library also provides all necessary information to the worker to process
the GET requests
"""

import logging
import os
import sys

from host_inventory import worker as host
from topological_inventory import worker as topology
from client_upload import worker as upload


LOGGER = logging.getLogger()

# Load constants from environment
TOPOLOGICAL_INVENTORY_HOST = os.environ.get('TOPOLOGICAL_INVENTORY_HOST ')
TOPOLOGICAL_INVENTORY_PATH = os.environ.get('TOPOLOGICAL_INVENTORY_PATH')
HOST_INVENTORY_HOST = os.environ.get('HOST_INVENTORY_HOST')
HOST_INVENTORY_PATH = os.environ.get('HOST_INVENTORY_PATH')
INPUT_DATA_FORMAT = os.environ.get('INPUT_DATA_FORMAT', '').upper()

# Decide which worker should be used
if INPUT_DATA_FORMAT == 'TOPOLOGY':
    LOGGER.info('Target Worker is Topology')
    WORKER = topology

    if not(TOPOLOGICAL_INVENTORY_HOST and  TOPOLOGICAL_INVENTORY_PATH):
        LOGGER.error('Environment not set properly, for topological worker')
        sys.exit(1)

elif INPUT_DATA_FORMAT == 'HOST':
    LOGGER.info('Target Worker is Host')
    WORKER = host

    if not (HOST_INVENTORY_HOST and HOST_INVENTORY_PATH):
        LOGGER.error('Environment not set properly, for host inventory worker')
        sys.exit(1)

    PER_PAGE = os.environ.get('HOST_INVENTORY_PER_PAGE', 50)
    URL = f'{HOST_INVENTORY_HOST}/{HOST_INVENTORY_PATH}?per_page=' + PER_PAGE

elif INPUT_DATA_FORMAT == 'CLIENT':
    LOGGER.info('Target Worker is Client upload')
    WORKER = upload

else:
    LOGGER.warning('No worker set. Exiting.')
    sys.exit(1)
