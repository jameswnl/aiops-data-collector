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
        page1.json.return_value = dict(
            page=1,
            total=3,
            per_page=5,
            results=[{'id': '0'}, {'id': '1'}, {'id': '2'}, {'id': '3'}],
        )
        profiles = mocker.MagicMock()
        profiles.json.return_value = dict(results=[1, 2, 3])
        retryable = mocker.patch.object(
            collector.utils, 'retryable', side_effect=[page1, profiles]
        )

        headers = {"x-rh-identity": 'identity_b64'}
        results = collector.host_inventory._retrieve_hosts(headers)

        assert results['results'] == [1, 2, 3]
        calls = [
            mocker.call(
                'get',
                'http://inventory:8080/api/inventory/vX/hosts?page=1',
                headers={'x-rh-identity': 'identity_b64'},
            ),
            mocker.call(
                'get',
                'http://inventory:8080/api/inventory/vX/hosts/'
                '0,1,2,3/system_profile',
                headers={'x-rh-identity': 'identity_b64'}
            ),
        ]
        assert retryable.call_args_list == calls

    def test_get_multiple_pages(self, mocker):
        """When results are in multiple pages."""
        responses = (
            dict(
                page=1,
                total=9,
                per_page=5,
                results=[{'id': '0'}, {'id': '1'}, {'id': '2'}, {'id': '3'}],
            ),
            dict(
                page=2,
                total=9,
                per_page=5,
                results=[{'id': '4'}, {'id': '5'}, {'id': '6'}, {'id': '7'}],
            ),
            dict(results=[0, 1, 2, 3]),
            dict(results=[4, 5, 6, 7]),
        )
        page1 = mocker.MagicMock()
        page2 = mocker.MagicMock()
        page1.json.return_value = responses[0]
        page2.json.return_value = responses[1]
        profile1 = mocker.MagicMock()
        profile2 = mocker.MagicMock()
        profile1.json.return_value = responses[2]
        profile2.json.return_value = responses[3]
        retryable = mocker.patch.object(
            collector.utils, 'retryable', side_effect=[
                page1, profile1, page2, profile2]
        )

        headers = {"x-rh-identity": 'identity_b64'}
        results = collector.host_inventory._retrieve_hosts(headers)

        assert results['results'] == list(range(8))
        calls = [
            mocker.call(
                'get',
                'http://inventory:8080/api/inventory/vX/hosts?page=1',
                headers={'x-rh-identity': 'identity_b64'},
            ),
            mocker.call(
                'get',
                'http://inventory:8080/api/inventory/vX/hosts/'
                '0,1,2,3/system_profile',
                headers={'x-rh-identity': 'identity_b64'}
            ),
            mocker.call(
                'get',
                'http://inventory:8080/api/inventory/vX/hosts?page=2',
                headers={'x-rh-identity': 'identity_b64'},
            ),
            mocker.call(
                'get',
                'http://inventory:8080/api/inventory/vX/hosts/'
                '4,5,6,7/system_profile',
                headers={'x-rh-identity': 'identity_b64'}
            ),
        ]
        assert retryable.call_args_list == calls
