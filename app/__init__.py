from flask import Flask

def create_app():
    app = Flask(__name__)

    # Import the routes
    from .routes import scraper_bp
    app.register_blueprint(scraper_bp)

    return app
