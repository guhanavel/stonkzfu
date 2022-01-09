from flask import Flask


def init_app():
    """Construct core Flask application with embedded Dash app."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')

    with app.app_context():
        # Import parts of our core Flask app

        # Import Dash application
        from stonk.dash.main import dash_app
        app = dash_app(app)

        return app
