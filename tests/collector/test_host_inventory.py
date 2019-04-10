import collector

# R0201 = Method could be a function Used when a method doesn't use its bound
# instance, and so could be written as a function.
# W0212 = Access to a protected member _retrieve_hosts of a client class

# pylint: disable=R0201,W0212


class TestRetrieveHosts:
    """Test `worker_host` function."""

    def test_get_single_pages(self, mocker):
        """When results are in one page."""
        page1 = mocker.MagicMock()
        page1.json.return_value = \
            dict(page=1, total=4, per_page=5, results=[0, 1, 2, 3])
        retryable = mocker.patch.object(
            collector.utils, 'retryable', side_effect=[page1]
        )

        headers = {"x-rh-identity": 'identity_b64'}
        results = collector.host_inventory._retrieve_hosts(headers)

        assert results['results'] == list(range(4))
        retryable.assert_called_once_with(
            'get',
            'http://inventory:8080/api/inventory/vX/hosts?page=1',
            headers={"x-rh-identity": 'identity_b64'}
        )

    def test_get_multiple_pages(self, mocker):
        """When results are in multiple pages."""
        responses = (
            dict(page=1, total=9, per_page=5, results=[0, 1, 2, 3, 4]),
            dict(page=2, total=9, per_page=5, results=[5, 6, 7, 8]),
        )
        page1 = mocker.MagicMock()
        page2 = mocker.MagicMock()
        page1.json.return_value = responses[0]
        page2.json.return_value = responses[1]
        retryable = mocker.patch.object(
            collector.utils, 'retryable', side_effect=[page1, page2]
        )

        headers = {"x-rh-identity": 'identity_b64'}
        results = collector.host_inventory._retrieve_hosts(headers)

        assert results['results'] == list(range(9))
        assert retryable.call_count == 2
        retryable.assert_any_call(
            'get',
            'http://inventory:8080/api/inventory/vX/hosts?page=1',
            headers={"x-rh-identity": 'identity_b64'}
        )
        retryable.assert_any_call(
            'get',
            'http://inventory:8080/api/inventory/vX/hosts?page=2',
            headers={"x-rh-identity": 'identity_b64'}
        )
