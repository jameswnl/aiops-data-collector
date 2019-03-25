import logging
import os

from flask import Flask, jsonify, request
from flask.logging import default_handler

import workers
import prometheus_metrics

from collect_json_schema import CollectJSONSchema


def create_application():
    """Create Flask application instance with AWS client enabled."""
    app = Flask(__name__)
    app.config['NEXT_MICROSERVICE_HOST'] = \
        os.environ.get('NEXT_MICROSERVICE_HOST')

    return app


APP = create_application()
ROOT_LOGGER = logging.getLogger()
ROOT_LOGGER.setLevel(APP.logger.level)
ROOT_LOGGER.addHandler(default_handler)

API_VERSION = '0.1'

ROUTE_PREFIX = ''
PATH_PREFIX = os.environ.get('PATH_PREFIX')
if PATH_PREFIX:
    APP_NAME = os.environ.get('APP_NAME', '')
    ROUTE_PREFIX = f'/{PATH_PREFIX}/{APP_NAME}'

# Schema for the Collect API
SCHEMA = CollectJSONSchema()


@APP.route(f'{ROUTE_PREFIX}/', methods=['GET'])
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
    input_data = request.get_json(force=True)
    validation = SCHEMA.load(input_data)
    prometheus_metrics.METRICS['jobs_total'].inc()

    if validation.errors:
        prometheus_metrics.METRICS['jobs_denied'].inc()
        return jsonify(
            status='Error',
            errors=validation.errors,
            version=API_VERSION,
            message='Input payload validation failed'
        ), 400

    next_service = APP.config['NEXT_MICROSERVICE_HOST']
    source_id = input_data.get('payload_id')

    b64_identity = request.headers.get('x-rh-identity')

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


if __name__ == "__main__":
    # pylama:ignore=C0103
    port = int(os.environ.get("PORT", 8004))
    APP.run(port=port)
