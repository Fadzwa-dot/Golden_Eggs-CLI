"""Application factory for the Flask web service.

This module provides a `create_app` function that wires configuration,
registers blueprints, and prepares the application for running. The
first iteration uses existing service classes and the current SQLAlchemy
session helpers; a later iteration can migrate to `flask_sqlalchemy`.
"""
from flask import Flask, jsonify
from app.database import db
from app.database import db

def create_app(config_object):
	app = Flask(__name__)
	app.config.from_object(config_object)

	# Register extensions
	db.init_app(app)

	# Register blueprints lazily to avoid import-time DB initialization
	from app.routes.user_routes import user_bp
	from app.routes.portfolio_routes import portfolio_bp
	from app.routes.security_routes import security_bp

	app.register_blueprint(user_bp)
	app.register_blueprint(portfolio_bp)
	app.register_blueprint(security_bp)

	# Simple index route to help users discover the API
	@app.route("/")
	def index():
		return jsonify({
			"message": "Golden Eggs API is running",
			"endpoints": {
				"users": "/api/users/",
				"portfolios": "/api/portfolios/",
				"securities": "/api/securities/"
			}
		})

	@app.route("/db-info")
	def db_info():
		# Provide non-sensitive DB info to verify configuration
		url = db.engine.url
		return jsonify({
			"dialect": getattr(url, "drivername", str(url)).split(":")[0],
			"driver": getattr(url, "drivername", ""),
			"database": getattr(url, "database", None),
			"host": getattr(url, "host", None),
		})

	return app
