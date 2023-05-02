#!/usr/bin/python3
"""This module defines the RESTful API Endpoints for managing Amenity objects.

Endpoints:
    GET /api/v1/amenities - Retrieves a list of all amenities.
    GET /api/v1/amenities/{amenity_id} - Retrieves a specific amenity by ID.
    POST /api/v1/amenities - Creates a new amenity.
    PUT /api/v1/amenities/{amenity_id} - Updates an existing amenity by ID.
    DELETE /api/v1/amenities/{amenity_id} - Deletes an amenity by ID.
"""
from models.amenity import Amenity
from models import storage
from api.v1.views import app_views
from flask import abort, jsonify, make_response, request
from flasgger.utils import swag_from


@app_views.route('/amenities', methods=['GET'], strict_slashes=False)
@swag_from('documentation/amenity/all_amenities.yml')
def get_amenities():
    """
    Returns a JSON object containing all amenities.

    Args:
        None

    Returns:
        A JSON object representing all amenities.

    Raises:
        500: If there was a server-side error when fetching amenities.
    """
    all_amenities = storage.all(Amenity).values()
    list_amenities = []
    for amenity in all_amenities:
        list_amenities.append(amenity.to_dict())
    return jsonify(list_amenities)


@app_views.route('/amenities/<amenity_id>/', methods=['GET'],
                 strict_slashes=False)
@swag_from('documentation/amenity/get_amenity.yml', methods=['GET'])
def get_amenity(amenity_id):
    """Retrieve a specific amenity by ID.

    Args:
        amenity_id (str): The ID of the amenity to retrieve.

    Returns:
        A JSON object representing the specified amenity.

    Raises:
        404 error: If the amenity with the specified ID is not found.
    """
    amenity = storage.get(Amenity, amenity_id)
    if not amenity:
        abort(404)
    return jsonify(amenity.to_dict())


@app_views.route('/amenities', methods=['POST'], strict_slashes=False)
@swag_from('documentation/amenity/post_amenity.yml', methods=['POST'])
def post_amenity():
    """
    Args:
        None

    Returns:
        A JSON object containing the newly created amenity with a
        status code of 201 (Created).

    Raises:
        400: If the request body is not in JSON format or the 'name'
        key is missing.
        500: If there was a server-side error while saving the amenity.
    """
    if not request.get_json():
        abort(400, description="Not a JSON")
    if 'name' not in request.get_json():
        abort(400, description="Missing name")
    data = request.get_json()
    instance = Amenity(**data)
    instance.save()
    return make_response(jsonify(instance.to_dict()), 201)


@app_views.route('/amenities/<amenity_id>', methods=['PUT'],
                 strict_slashes=False)
@swag_from('documentation/amenity/put_amenity.yml', methods=['PUT'])
def put_amenity(amenity_id):
    """
    Updates an amenity by ID with data from the request body.

    Args:
        amenity_id (str): The ID of the amenity to update.

    Returns:
        A JSON object representing the updated amenity.

    Raises:
        400: If the request body is not a JSON or if it is
        missing any required fields.
        404: If the amenity with the specified ID does not exist.
    """
    if not request.get_json():
        abort(400, description="Not a JSON")
    ignore = ['id', 'created_at', 'updated_at']

    amenity = storage.get(Amenity, amenity_id)
    if not amenity:
        abort(404)
    data = request.get_json()
    for key, value in data.items():
        if key not in ignore:
            setattr(amenity, key, value)
    storage.save()
    return make_response(jsonify(amenity.to_dict()), 200)


@app_views.route('/amenities/<amenity_id>', methods=['DELETE'],
                 strict_slashes=False)
@swag_from('documentation/amenity/delete_amenity.yml', methods=['DELETE'])
def delete_amenity(amenity_id):
    """
    Deletes an amenity by ID.

    Args:
        amenity_id (str): The ID of the amenity to be deleted.

    Returns:
        A JSON object representing an empty dictionary with a status
        code of 200.

    Raises:
        404: If no amenity is found with the given amenity_id.
    """
    amenity = storage.get(Amenity, amenity_id)
    if not amenity:
        abort(404)
    storage.delete(amenity)
    storage.save()
    return make_response(jsonify({}), 200)
