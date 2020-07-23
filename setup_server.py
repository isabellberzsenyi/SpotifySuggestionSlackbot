from flask import Flask

def create_flask_app():
    # This `app` represents your existing Flask app
    app = Flask(__name__)


    # An example of one of your Flask app's routes
    @app.route("/")
    def hello():
        return "Hello there!"

    return app