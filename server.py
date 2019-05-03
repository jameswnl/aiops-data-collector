import base64
import json
import logging
import os

from flask import Flask, jsonify, request
from flask.logging import default_handler
from jinja2 import Template
import yaml

import collector
import workers
import prometheus_metrics


def create_application():
    """Create Flask application instance with AWS client enabled."""
    app = Flask(__name__)
    app.config['NEXT_SERVICE_URL'] = os.environ.get('NEXT_SERVICE_URL')
    app.config['APP_NAME'] = os.environ.get('APP_NAME')

    return app


APP = create_application()
ROOT_LOGGER = logging.getLogger()
ROOT_LOGGER.setLevel(APP.logger.level)
ROOT_LOGGER.addHandler(default_handler)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

API_VERSION = '1.0'

ROUTE_PREFIX = ''
PATH_PREFIX = os.environ.get('PATH_PREFIX')
if PATH_PREFIX:
    APP_NAME = os.environ.get('APP_NAME', '')
    ROUTE_PREFIX = f'/{PATH_PREFIX}/{APP_NAME}'


@APP.route(f'{ROUTE_PREFIX}/', methods=['GET'], strict_slashes=False)
def get_root():
    """Root Endpoint for 3scale."""
    return jsonify(
        status='OK',
        version=API_VERSION,
        message='Up and Running'
    )


@APP.route(f'{ROUTE_PREFIX}/v{API_VERSION}/version', methods=['GET'])
def get_version():
    """Endpoint for getting the current version."""
    return jsonify(
        status='OK',
        version=API_VERSION,
        message=f'AIOPS Data Collector Version v{API_VERSION}'
    )


@APP.route(f'{ROUTE_PREFIX}/v{API_VERSION}/collect', methods=['POST'])
def post_collect():
    """Endpoint servicing data collection."""
    prometheus_metrics.METRICS['jobs_total'].inc()
    input_data = request.get_json(force=True) if request.get_data() else {}

    b64_identity = request.headers.get('x-rh-identity')
    if not b64_identity:
        prometheus_metrics.METRICS['jobs_denied'].inc()
        return jsonify(
            status='Unauthorized',
            version=API_VERSION,
            message="Missing 'x-rh-identity' header"
        ), 401

    identity = json.loads(base64.b64decode(b64_identity))
    account_id = identity.get('identity', {}).get('account_number')
    APP.logger.debug('Account_id: %s', account_id)

    # Check if this account has been processed within the window
    if account_id and collector.utils.processed(account_id):
        APP.logger.info("Account %s processed before, skipping", account_id)
        return jsonify(
            status="OK",
            version=API_VERSION,
            message="Account processed before"
        )

    next_service = APP.config['NEXT_SERVICE_URL']
    source_id = input_data.get('payload_id')

    workers.download_job(
        input_data.get('url'),
        source_id,
        next_service,
        b64_identity
    )
    APP.logger.info('Job started.')

    prometheus_metrics.METRICS['jobs_initiated'].inc()
    return jsonify(
        status="OK",
        version=API_VERSION,
        message="Job initiated"
    )


@APP.route("/metrics", methods=['GET'])
def get_metrics():
    """Metrics Endpoint."""
    return prometheus_metrics.generate_aggregated_metrics()


@APP.route(f'{ROUTE_PREFIX}/v{API_VERSION}/openapi.json')
def get_openapi():
    """Provide OpenAPI v3 scheme."""
    with open('openapi.yml.j2') as f:
        template = Template(f.read())

    spec = template.render(route_prefix=ROUTE_PREFIX, api_version=API_VERSION)
    return jsonify(yaml.load(spec))


if __name__ == "__main__":
    # pylama:ignore=C0103
    port = int(os.environ.get("PORT", 8004))
    APP.run(port=port)
