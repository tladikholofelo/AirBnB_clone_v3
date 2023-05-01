#!/usr/bin/python3
"""
This module creates a Flask application instance for the AirBnB Clone
RESTful API.

The API provides HTTP endpoints for managing AirBnB Clone resources
such as users, places, amenities, and reviews.

Functions:
    close_db: Function to close the database connection.
    not_found: Function to handle 404 errors and return a JSON response.

Usage:
    To run the application:
        $ python3 -m api.v1.app
"""
from models import storage
from api.v1.views import app_views
from os import environ
from flask import Flask, render_template, make_response, jsonify
from flask_cors import CORS
from flasgger import Swagger
from flasgger.utils import swag_from

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.register_blueprint(app_views)
cors = CORS(app, resources={r"/*": {"origins": "0.0.0.0"}})

app.config['SWAGGER'] = {
    'title': 'AirBnB clone Restful API',
    'uiversion': 3
}
Swagger(app)


@app.teardown_appcontext
def close_db(error):
    """Close the database connection."""
    storage.close()


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors andd return JSON response.

    Responses:
      404:
        Description: a resource was not found
    """
    return make_response(jsonify({'error': "Not found"}), 404)


if __name__ == "__main__":
    """Run the application."""
    host = environ.get('HBNB_API_HOST')
    port = environ.get('HBNB_API_PORT')
    if not host:
        host = '0.0.0.0'
    if not port:
        port = '5000'
    app.run(host=host, port=port, threaded=True)