from flask import Flask
APP = Flask(__name__)


@APP.route("/", methods=['POST', 'PUT'])
def index():
    """Wake up and collect data endpoint."""
    return "OK"


if __name__ == "__main__":
    APP.run()
