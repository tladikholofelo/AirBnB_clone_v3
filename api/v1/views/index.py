#!/usr/bin/python3
"""
Defines API Endpoints for status and statistics.

This module defines two API endpoints for the Flask application:
    - /status: Returns the API status as a JSON object with the key "status"
               and value "OK"
    - /stats: Returns the number of objects in the database for each of the
              classes in the classes list as a JSON object.
"""
from models.amenity import Amenity
from models.city import City
from models.place import Place
from models.review import Review
from models.state import State
from models.user import User
from models import storage
from api.v1.views import app_views
from flask import jsonify


@app_views.route('/status', methods=['GET'], strict_slashes=False)
def status():
    """Returns the API status"""
    return jsonify({"status": "OK"})


@app_views.route('/stats', methods=['GET'], strict_slashes=False)
def number_objects():
    """Returns the number of objects in the database for each class.

    Returns:
        A JSON object with the number of objects for each class.
        The keys are the class names in the 'names' list, and the values are
        the number of objects.

    Raises:
        None.
    """
    classes = [Amenity, City, Place, Review, State, User]
    names = ["amenities", "cities", "places", "reviews", "states", "users"]
    num_objs = {}
    for i in range(len(classes)):
        num_objs[names[i]] = storage.count(classes[i])
    return jsonify(num_objs)
