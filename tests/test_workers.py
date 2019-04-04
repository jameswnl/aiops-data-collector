import workers

# R0201 = Method could be a function Used when a method doesn't use its bound
# instance, and so could be written as a function.
# pylint: disable=R0201


class TestRetrieveHosts:
    """Test. `worker_host` function."""

    def test_get_single_pages(self, mocker):
        """When results are in one page."""
        page1 = mocker.MagicMock()
        page1.json.return_value = \
            dict(page=1, total=4, per_page=5, results=[0, 1, 2, 3])
        retryable = mocker.patch.object(
            workers, '_retryable', side_effect=[page1]
        )

        results = workers.retrieve_hosts('inv.svc', 'identity_b64')

        assert results['results'] == list(range(4))
        retryable.assert_called_once_with(
            'get',
            'inv.svc&page=1',
            headers={"x-rh-identity": 'identity_b64'},
            verify=False,
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
            workers, '_retryable', side_effect=[page1, page2]
        )

        results = workers.retrieve_hosts('inv.svc', 'identity_b64')

        assert results['results'] == list(range(9))
        assert retryable.call_count == 2
        retryable.assert_any_call(
            'get',
            'inv.svc&page=1',
            headers={"x-rh-identity": 'identity_b64'},
            verify=False,
        )
        retryable.assert_any_call(
            'get',
            'inv.svc&page=2',
            headers={"x-rh-identity": 'identity_b64'},
            verify=False,
        )
