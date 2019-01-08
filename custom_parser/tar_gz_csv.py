import csv
import tarfile
from itertools import chain
from io import StringIO


def csv_parser(filename):
    """Extract CSV data from TAR.GZ file.

    Extracts all CSV files from a TAR.GZ archive and combines them into a list
    of dictionary objects.
    :param filename: Name of the filename to parse
    """
    entries = list()
    with tarfile.open(filename) as tar:
        for member in tar:
            # Only CSV files are interesting
            if not member.name.endswith('.csv'):
                continue

            # Read the CSV
            csv_string = tar.extractfile(member).read().decode()
            csv_stream = StringIO(csv_string)
            entries = chain(entries, csv.DictReader(csv_stream))

    return list(entries)
