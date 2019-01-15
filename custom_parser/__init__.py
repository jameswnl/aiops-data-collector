"""Parser library.

Each format of the input data should be parsed in different manner. This
library provides custom parsers for each such usecase. The "parse"
function used by data-collector is decided by env variable INPUT_DATA_FORMAT.
"""

import logging
import os

logger = logging.getLogger()

if os.environ.get('INPUT_DATA_FORMAT') == 'CSV':
    logger.info('Selected parser for "CSV files in TAR.GZ"')
    from .tar_gz_csv import csv_parser as parse

else:
    logger.warning('No parser provided, fallback used!')

    def parse(_):
        """Fallback parser.

        Used when no data preprocessor is provided.
        """
        return {}

__all__ = ['parse']
