import unittest
from unittest import mock

from workers import retrieve_hosts


class TestGetHosts(unittest.TestCase):
    """Test. `worker_host` function."""

    def setUp(self):
        """Test setup."""
        self.single_resp = {
            'page': 1,
            'total': 4,
            'per_page': 5,
            'results': [0, 1, 2, 3],
        }
        self.resp1 = {
            **self.single_resp,
            'total': 9,
            'results': [0, 1, 2, 3, 4],
        }
        self.resp2 = {
            **self.resp1,
            'page': 2,
            'results': [5, 6, 7, 8],
        }

    @mock.patch('workers._retryable')
    def test_get_single_pages(self, _retryable):
        """When results are in one page."""
        page1 = mock.MagicMock()
        page1.json.return_value = self.single_resp
        _retryable.side_effect = [page1]
        results = retrieve_hosts('inv.svc', 'identity_b64')
        assert results['results'] == list(range(4))
        _retryable.assert_called_once_with(
            'get',
            'inv.svc?page=1',
            headers={"x-rh-identity": 'identity_b64'},
            verify=False,
        )

    @mock.patch('workers._retryable')
    def test_get_multiple_pages(self, _retryable):
        """When results are in multiple pages."""
        page1 = mock.MagicMock()
        page1.json.return_value = self.resp1
        page2 = mock.MagicMock()
        page2.json.return_value = self.resp2
        _retryable.side_effect = [page1, page2]
        results = retrieve_hosts('inv.svc', 'identity_b64')
        assert results['results'] == list(range(9))
        calls = [
            mock.call(
                'get',
                'inv.svc?page=1',
                headers={"x-rh-identity": 'identity_b64'},
                verify=False,
            ),
            mock.call(
                'get',
                'inv.svc?page=2',
                headers={"x-rh-identity": 'identity_b64'},
                verify=False,
            ),
        ]
        _retryable.assert_has_calls(calls)
