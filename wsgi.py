import logging
import os

from flask import Flask, jsonify, request

import s3

APP = Flask(__name__)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@APP.route("/", methods=['POST', 'PUT'])
def index():
    """Endpoint servicing data collection."""
    input_data = request.get_json(force=True)
    client = APP.config['AWS_S3_CLIENT']
    bucket = APP.config['AWS_S3_BUCKET_NAME']

    # Collect data
    try:
        s3.fetch(client, bucket, input_data['url'])
    except s3.S3Exception as exception:
        logger.warning(exception)
        return jsonify(status="FAILED", exception=str(exception)), 400

    return jsonify(status="OK")


if __name__ == "__main__":
    # Build AWS S3 client and store it in server runtime
    AWS_KEY = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET = os.environ.get('AWS_SECRET_ACCESS_KEY')

    APP.config['AWS_S3_CLIENT'] = s3.connect(AWS_KEY, AWS_SECRET)
    APP.config['AWS_S3_BUCKET_NAME'] = os.environ.get('AWS_S3_BUCKET_NAME')

    APP.run(port=8080)
