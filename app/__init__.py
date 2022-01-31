from flask import Flask


def init_app():
    """Construct core Flask application with embedded Dash app."""
    app = Flask(__name__)

    if app.config["ENV"] == "production":

        app.config.from_object("config.ProductionConfig")

    elif app.config["ENV"] == "development":

        app.config.from_object("config.DevelopmentConfig")

    else:

        app.config.from_object("config.ProductionConfig")

    with app.app_context():
        # Import parts of our core Flask app
        from . import routes
        # Import Dash application
        from app.dash.baa import dash_app
        from app.dash.home import dash_pp

        app = dash_app(app)
        app = dash_pp(app)

        return app

