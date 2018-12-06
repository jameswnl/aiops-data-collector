import logging
import os

from flask import Flask, jsonify, request
from flask.logging import default_handler

import workers


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


@APP.route("/", methods=['POST'])
def index():
    """Endpoint servicing data collection."""
    input_data = request.get_json(force=True)
    next_service = APP.config['NEXT_MICROSERVICE_HOST']

    try:
        APP.logger.info('Peeking files on uri %s', input_data['url'])

        workers.download_and_pass_data_thread(
            input_data['url'], next_service
        )
        APP.logger.info('Files found, job started.')

    except FileNotFoundError as exception:
        APP.logger.warning(exception)
        return jsonify(status="FAILED", exception=str(exception)), 400

    return jsonify(status="OK", message="Job initiated")


if __name__ == "__main__":
    APP.run()
