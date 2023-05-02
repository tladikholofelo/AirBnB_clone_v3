#!/usr/bin/python3
"""
This module defines API Endpoints for managing the relationship between
Place and Amenity objects.

Endpoints:
    GET /places/<place_id>/amenities - Retrieves a list of all Amenity-Place.
    POST /places/<place_id>/amenities/<amenity_id> - Creates a Place-Amenity.
    DELETE /places/<place_id>/amenities/<amenity_id> - Deletes a Place-Amenity.

Dependencies:
    - flask: a micro web framework for building APIs with Python.
    - flasgger: a Swagger documentation generator for Flask APIs.
    - models: a module containing the Place and Amenity models.
    - storage: a module providing an interface to a database.
"""
from models.amenity import Amenity
from models import storage
from api.v1.views import app_views
from os import environ
from flask import abort, jsonify, make_response, request
from flasgger.utils import swag_from


@app_views.route('places/<place_id>/amenities', methods=['GET'],
                 strict_slashes=False)
@swag_from('documentation/place_amenity/get_places_amenities.yml',
           methods=['GET'])
def get_place_amenities(place_id):
    """
    Retrieves the list of all Amenity objects of a Place.

    Args:
        place_id (str): The ID of the Place object to retrieve amenities for.

    Returns:
        A JSON representation of a list of Amenity objects
        associated with the Place.

    Raises:
        404: If the Place object with the given ID doesn't exist.
    """
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    if environ.get('HBNB_TYPE_STORAGE') == "db":
        amenities = [amenity.to_dict() for amenity in place.amenities]
    else:
        amenities = [storage.get(Amenity, amenity_id).to_dict()
                     for amenity_id in place.amenity_ids]
    return jsonify(amenities)


@app_views.route('/places/<place_id>/amenities/<amenity_id>',
                 methods=['DELETE'], strict_slashes=False)
@swag_from('documentation/place_amenity/delete_place_amenities.yml',
           methods=['DELETE'])
def delete_place_amenity(place_id, amenity_id):
    """
    Deletes an Amenity object of a Place.

    Args:
        place_id (str): The id of the Place object.
        amenity_id (str): The id of the Amenity object.

    Returns:
        Response: An empty JSON response with status code 200.

    Raises:
        404 error: If the Place or Amenity object with the
        given id is not found.
    """
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    amenity = storage.get(Amenity, amenity_id)
    if not amenity:
        abort(404)
    if environ.get('HBNB_TYPE_STORAGE') == "db":
        if amenity not in place.amenities:
            abort(404)
        place.amenities.remove(amenity)
    else:
        if amenity_id not in place.amenity_ids:
            abort(404)
        place.amenity_ids.remove(amenity_id)
    storage.save()
    return make_response(jsonify({}), 200)


@app_views.route('/places/<place_id>/amenities/<amenity_id>', methods=['POST'],
                 strict_slashes=False)
@swag_from('documentation/place_amenity/post_place_amenities.yml',
           methods=['POST'])
def post_place_amenity(place_id, amenity_id):
    """
    Link an Amenity object to a Place.

    Args:
        place_id (str): The ID of the Place to link the Amenity to.
        amenity_id (str): The ID of the Amenity to link to the Place.

    Returns:
        A JSON response containing the details of the linked Amenity object and
        a HTTP status code of 201.

    Raises:
        404: If either the Place or Amenity with the gives IDs do not exist.
    """
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    amenity = storage.get(Amenity, amenity_id)
    if not amenity:
        abort(404)
    if environ.get('HBNB_TYPE_STORAGE') == "db":
        if amenity in place.amenities:
            return make_response(jsonify(amenity.to_dict()), 200)
        else:
            place.amenities.append(amenity)
    else:
        if amenity_id in place.amenity_ids:
            return make_response(jsonify(amenity.to_dict()), 200)
        else:
            place.amenity_ids.append(amenity_id)
    storage.save()
    return make_response(jsonify(amenity.to_dict()), 201)
