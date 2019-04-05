from imp import reload

import pytest

import collector


@pytest.fixture(autouse=True)
def patch_env(monkeypatch):
    """Set up environment."""
    # Set Test variables
    setenv = dict(
        TOPOLOGICAL_INVENTORY_HOST='http://topological:8080',
        TOPOLOGICAL_INVENTORY_PATH='api/topo/vX',
        HOST_INVENTORY_HOST='http://inventory:8080',
        HOST_INVENTORY_PATH='api/inventory/vX'
    )
    for item, value in setenv.items():
        monkeypatch.setenv(item, value)

    # Drop extra variables
    monkeypatch.delenv('SSL_VERIFY')

    # Reload modules
    reload(collector.env)
    reload(collector.host_inventory)
    reload(collector.topological_inventory)
