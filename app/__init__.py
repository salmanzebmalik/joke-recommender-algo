from flask import Flask

def create_app():
    # Initialize the Flask app
    app = Flask(__name__)

    # Optionally, load configuration from a separate config.py file
    app.config.from_object('config.Config')

    # Import and register API routes
    from . import routes
    app.register_blueprint(routes.bp)

    return app
