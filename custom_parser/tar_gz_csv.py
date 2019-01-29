import tarfile
from io import BytesIO

BUFFER_SIZE = 10240


def _only_csv_file(member: tarfile.TarInfo) -> bool:
    """Selector for CSV files only in a TAR file."""
    return member.name.endswith('.csv')


def csv_parser(file_obj: BytesIO) -> bytes:
    """Extract CSV data from TAR.GZ file.

    Extracts all CSV files from a TAR.GZ archive and combines them into a list
    of dictionary objects.
    :param filename: Name of the filename to parse
    """
    with tarfile.open(fileobj=file_obj) as tar:
        # Read just the first CSV available
        member = next(filter(_only_csv_file, tar.members), None)
        # Return if no CSV file was found
        if not member:
            return

        # Extract CSV file object
        csv_data = tar.extractfile(member)
        # Read the CSV content in chunks
        yield from iter(lambda: csv_data.read(BUFFER_SIZE), b'')
