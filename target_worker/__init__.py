"""Target Worker library.

With the help of this library a target worker can be assigned on-the-fly
The library also provides authentication information to process the GET
requests, if applicable
"""

import logging
import os

logger = logging.getLogger()

if os.environ.get('INPUT_DATA_FORMAT') == 'TOPOLOGY':
    logger.info('Target Worker is Topology')
    from .target_worker import topology as name

else:
    logger.info('Target Worker is Clustering')
    from .target_worker import clustering as name


__all__ = ['name']
