import logging
import os
from json import dumps

from flask import Flask, jsonify, request
import requests

import s3

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def create_application():
    """Create Flask application instance with AWS client enabled."""
    app = Flask(__name__)
    aws_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret = os.environ.get('AWS_SECRET_ACCESS_KEY')

    app.config['AWS_S3_CLIENT'] = s3.connect(aws_key, aws_secret)
    app.config['AWS_S3_BUCKET_NAME'] = os.environ.get('AWS_S3_BUCKET_NAME')
    app.config['NEXT_MICROSERVICE_HOST'] = \
        os.environ.get('NEXT_MICROSERVICE_HOST')

    return app


APP = create_application()


def hit_next_in_pipepine(payload: dict) -> None:
    """Pass the data to next service in line."""
    # Do not wait for response now, so we can keep listening
    # FIXME: Convert to aiohttp or some other async requests alternative
    host = APP.config['NEXT_MICROSERVICE_HOST']

    try:
        data = dumps(payload, default=str)
        requests.post(f'http://{host}', json=data, timeout=10)
    except requests.exceptions.ReadTimeout:
        pass
    except requests.exceptions.ConnectionError as e:
        logger.warning('Call to next service failed: %s', str(e))


@APP.route("/", methods=['POST', 'PUT'])
def index():
    """Endpoint servicing data collection."""
    input_data = request.get_json(force=True)
    client = APP.config['AWS_S3_CLIENT']
    bucket = APP.config['AWS_S3_BUCKET_NAME']

    # Collect data
    response = dict()
    try:
        logger.info('Collecting data on url: %s', input_data['url'])
        response['data'] = s3.fetch(client, bucket, input_data['url'])

        logger.info('Done')
        response['status'] = 'Collected'

        hit_next_in_pipepine(response)

    except s3.S3Exception as exception:
        logger.warning(exception)
        return jsonify(status="FAILED", exception=str(exception)), 400

    return jsonify(status="OK")


if __name__ == "__main__":
    APP.run()
