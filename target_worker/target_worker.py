import os


def clustering():
    """Return Clustering info."""
    return 'worker_clustering', {}


def topology():
    """Return Topology Inventory info."""
    username = os.environ.get('USERNAME')
    password = os.environ.get('PASSWORD')
    endpoint = os.environ.get('TOPOLOGY_INVENTORY_ENDPOINT')

    return 'worker_topology',\
           {
               'username': username,
               'password': password,
               'endpoint': endpoint
           }
