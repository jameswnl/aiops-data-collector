from prometheus_client import Counter, generate_latest   #noqa

# Prometheus Metrics
aiops_data_collector_jobs_total = Counter(   #noqa
    'aiops_data_collector_jobs_total',
    'The total number of data collector jobs'
)
aiops_data_collector_jobs_initiated = Counter(   #noqa
    'aiops_data_collector_jobs_initiated',
    'The total number of successfully initiated data collector jobs'
)
aiops_data_collector_jobs_denied = Counter(   #noqa
    'aiops_data_collector_jobs_denied',
    'The total number of denied data collector jobs'
)
aiops_data_collector_data_download_requests_total = Counter(   #noqa
    'aiops_data_collector_data_download_requests_total',
    'The total number of data download requests'
)
aiops_data_collector_data_download_successful_requests_total = Counter(   #noqa
    'aiops_data_collector_data_download_successful_requests_total',
    'The total number of successful data download requests'
)
aiops_data_collector_data_download_request_exceptions = Counter(   #noqa
    'aiops_data_collector_data_download_request_exceptions',
    'The total number of data download request exceptions'
)
aiops_data_collector_post_data_requests_total = Counter(   #noqa
    'aiops_data_collector_post_data_requests_total',
    'The total number of post data requests'
)
aiops_data_collector_post_data_successful_requests_total = Counter(   #noqa
    'aiops_data_collector_post_data_successful_requests_total',
    'The total number of successful post data requests'
)
aiops_data_collector_post_data_request_exceptions = Counter(   #noqa
    'aiops_data_collector_post_data_request_exceptions',
    'The total number of post data request exceptions'
)
