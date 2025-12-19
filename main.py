"""Switch main entrypoint to start the Flask web service.

To run the CLI, use its module directly (e.g., `py -m app.cli.menu_printer`),
but for Assignment 3 the main entrypoint starts the web server.
"""
from app import create_app
from app.config import Config

app = create_app(Config)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=Config.DEBUG)
