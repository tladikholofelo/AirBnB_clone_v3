#!/usr/bin/python3
"""This module defines the RestFul API Endpoints for managing places.

Endpoints:
    GET /cities/<city_id>/places: Retrieves the list of all Place objects
    of a City.
    GET /places/<place_id>: Retrieves a Place object.
    DELETE /places/<place_id>: Deletes a Place object.
    POST /cities/<city_id>/places: Creates a new Place object.
    PUT /places/<place_id>: Updates a Place object.
    POST /places_search: Retrieves all Place objects depending on the
    JSON in the body of the request.
"""
from models.state import State
from models.city import City
from models.place import Place
from models.user import User
from models.amenity import Amenity
from models import storage
from api.v1.views import app_views
from flask import abort, jsonify, make_response, request
from flasgger.utils import swag_from


@app_views.route('/cities/<city_id>/places', methods=['GET'],
                 strict_slashes=False)
@swag_from('documentation/place/get_places.yml', methods=['GET'])
def get_places(city_id):
    """
    Retrieve the list of all Place objects for a City.

    Args:
        city_id (str): The ID of the City object to retrieve Place objects for.

    Returns:
        A JSON response containing a list of dictionaries, where each
        dictionary represents a Place object for the City.

    Raises:
        404: If the City object with the given ID does not exist.
    """
    city = storage.get(City, city_id)
    if not city:
        abort(404)
    places = [place.to_dict() for place in city.places]
    return jsonify(places)


@app_views.route('/places/<place_id>', methods=['GET'], strict_slashes=False)
@swag_from('documentation/place/get_place.yml', methods=['GET'])
def get_place(place_id):
    """
    Retrieves a Place object.

    Args:
        place_id (str): The id of the Place object to retrieve.

    Returns:
        A JSON representation of the Place object.

    Raises:
        404: If the Place object with the given id doesn't exist.
    """
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    return jsonify(place.to_dict())


@app_views.route('/places/<place_id>', methods=['DELETE'],
                 strict_slashes=False)
@swag_from('documentation/place/delete_place.yml', methods=['DELETE'])
def delete_place(place_id):
    """
    Deletes a Place object.

    Args:
        place_id (str): The ID of the Place object to be deleted.

    Returns:
        A JSON response with an empty dictionary and a status
        code of 200 if the Place object was successfully deleted.

    Raises:
        404: If no Place object with the given place_id is found.
    """
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    storage.delete(place)
    storage.save()
    return make_response(jsonify({}), 200)


@app_views.route('/cities/<city_id>/places', methods=['POST'],
                 strict_slashes=False)
@swag_from('documentation/place/post_place.yml', methods=['POST'])
def post_place(city_id):
    """
    Creates a new Place object.

    Args:
        city_id (str): The ID of the City object that matches the Place object.

    Returns:
        A JSON response with the new Place object and a 201 status code.

    Raises:
        404: If the City object with the given city_id doesn't exist.
        400: If the request doesn't contain a JSON object or if the JSON object
             doesn't have a 'user_id' or 'name' field.
             If the User object with the 'user_id' specified in the JSON object
             doesn't exist in the storage.
    """
    city = storage.get(City, city_id)
    if not city:
        abort(404)
    if not request.get_json():
        abort(400, description="Not a JSON")
    if 'user_id' not in request.get_json():
        abort(400, description="Missing user_id")
    data = request.get_json()
    user = storage.get(User, data['user_id'])
    if not user:
        abort(404)
    if 'name' not in request.get_json():
        abort(400, description="Missing name")
    data["city_id"] = city_id
    instance = Place(**data)
    instance.save()
    return make_response(jsonify(instance.to_dict()), 201)


@app_views.route('/places/<place_id>', methods=['PUT'], strict_slashes=False)
@swag_from('documentation/place/put_place.yml', methods=['PUT'])
def put_place(place_id):
    """
    Updates a Place.

    Args:
        place_id (str): The ID of the Place to update.

    Returns:
        A JSON response with the updated Place object.

    Raises:
        404: If the Place with the specified ID does not exist.
        400: If the request body is not a valid JSON or if it
             contains invalid data.
    """
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    data = request.get_json()
    if not data:
        abort(400, description="Not a JSON")
    ignore = ['id', 'user_id', 'city_id', 'created_at', 'updated_at']
    for key, value in data.items():
        if key not in ignore:
            setattr(place, key, value)
    storage.save()
    return make_response(jsonify(place.to_dict()), 200)


@app_views.route('/places_search', methods=['POST'], strict_slashes=False)
@swag_from('documentation/place/post_search.yml', methods=['POST'])
def places_search():
    """
    Retrieves all Place objects depending on the JSON in the body of
    the request.

    Args:
        None

    Returns:
        A list of dictionaries containing the details of all Place objects
        that match the search criteria specified in the request body.

    Raises:
        400 error: If the request body is not in JSON format or is empty.
    """
    if request.get_json() is None:
        abort(400, description="Not a JSON")

    data = request.get_json()

    if data and len(data):
        states = data.get('states', None)
        cities = data.get('cities', None)
        amenities = data.get('amenities', None)

    if not data or not len(data) or (
            not states and
            not cities and
            not amenities):
        places = storage.all(Place).values()
        list_places = []
        for place in places:
            list_places.append(place.to_dict())
        return jsonify(list_places)

    list_places = []
    if states:
        states_obj = [storage.get(State, s_id) for s_id in states]
        for state in states_obj:
            if state:
                for city in state.cities:
                    if city:
                        for place in city.places:
                            list_places.append(place)

    if cities:
        city_obj = [storage.get(City, c_id) for c_id in cities]
        for city in city_obj:
            if city:
                for place in city.places:
                    if place not in list_places:
                        list_places.append(place)

    if amenities:
        if not list_places:
            list_places = storage.all(Place).values()
        amenities_obj = [storage.get(Amenity, a_id) for a_id in amenities]
        list_places = [place for place in list_places
                       if all([am in place.amenities
                               for am in amenities_obj])]

    places = []
    for p in list_places:
        d = p.to_dict()
        d.pop('amenities', None)
        places.append(d)

    return jsonify(places)
