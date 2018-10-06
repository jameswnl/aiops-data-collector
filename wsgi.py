import logging

from flask import Flask, request

import s3

APP = Flask(__name__)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@APP.route("/", methods=['POST', 'PUT'])
def index():
    """Endpoint servicing data collection."""
    input_data = request.get_json(force=True)

    try:
        s3.fetch(input_data['url'])
    except s3.S3Exception as exception:
        logger.warning(exception)
        return str(exception), 400

    return "OK"


if __name__ == "__main__":
    APP.run()
