import json
import tarfile
from io import BytesIO

import pandas as pd


def csv_parser(file_obj: BytesIO) -> bytes:
    """Extract CSV data from TAR.GZ file.

    Extracts all CSV files from a TAR.GZ archive and combines them into a list
    of dictionary objects.
    :param filename: Name of the filename to parse
    """
    # Start data stream
    yield b'['

    with tarfile.open(fileobj=file_obj) as tar:
        for member in tar:
            # Only CSV files are interesting
            if not member.name.endswith('.csv'):
                continue

            # Read the CSV
            csv_data = pd.read_csv(tar.extractfile(member))

            for item in csv_data.itertuples(index=False):
                out_str = json.dumps(item._asdict())
                yield f'{out_str},'.encode()

    # End data stream
    yield b']'
