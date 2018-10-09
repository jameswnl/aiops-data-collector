import logging
import os

from flask import Flask, jsonify, request

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

    return app


APP = create_application()


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
    APP.run()
