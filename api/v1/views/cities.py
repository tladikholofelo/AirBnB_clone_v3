#!/usr/bin/python3
"""This module defines RESTful API Endpoints for managing City objects.

This module defines various API endpoints for handling CRUD operations
(create, read, update, and delete) on City objects.

Endpoints:
    GET /states/<state_id>/cities: Retrieves a list of cities for a state.
    GET /cities/<city_id>/: Retrieves a specific city based on its ID.
    DELETE /cities/<city_id>: Deletes a city based on its ID.
    POST /states/<state_id>/cities: Creates a new city object for a state.
    PUT /cities/<city_id>: Updates a city based on the given city_id.
"""
from models.city import City
from models.state import State
from models import storage
from api.v1.views import app_views
from flask import abort, jsonify, make_response, request
from flasgger.utils import swag_from


@app_views.route('/states/<state_id>/cities', methods=['GET'],
                 strict_slashes=False)
@swag_from('documentation/city/cities_by_state.yml', methods=['GET'])
def get_cities(state_id):
    """
    Retrieves a list of cities for a specific state.

    Args:
        state_id (str): The ID of the state.

    Returns:
        A JSON representation of the list of all cities for the state.

    Raises:
        404 (HTTPException): If the state with the specified ID does
        not exist.
    """
    list_cities = []
    state = storage.get(State, state_id)
    if not state:
        abort(404)
    for city in state.cities:
        list_cities.append(city.to_dict())
    return jsonify(list_cities)


@app_views.route('/cities/<city_id>/', methods=['GET'], strict_slashes=False)
@swag_from('documentation/city/get_city.yml', methods=['GET'])
def get_city(city_id):
    """
    Retrieves a specific city based on its ID.

    Args:
        city_id (str): The ID of the city to retrieve.

    Returns:
        A JSON representation of the city object.

    Raises:
        404 (HTTPException): If the city with the specified
        ID does not exist.
    """
    city = storage.get(City, city_id)
    if not city:
        abort(404)
    return jsonify(city.to_dict())


@app_views.route('/cities/<city_id>', methods=['DELETE'], strict_slashes=False)
@swag_from('documentation/city/delete_city.yml', methods=['DELETE'])
def delete_city(city_id):
    """
    Deletes a city based on its ID.

    Args:
        city_id (str): The ID of the city to delete.

    Returns:
        An empty JSON response with status code 200.

    Raises:
        404 (HTTPException): If the city with the specified ID does
        not exist.
    """
    city = storage.get(City, city_id)

    if not city:
        abort(404)
    storage.delete(city)
    storage.save()
    return make_response(jsonify({}), 200)


@app_views.route('/states/<state_id>/cities', methods=['POST'],
                 strict_slashes=False)
@swag_from('documentation/city/post_city.yml', methods=['POST'])
def post_city(state_id):
    """
    Creates a new city object for a given state.

    Args:
        state_id (str): The ID of the state object for the new city object.

    Returns:
        A JSON response containing the newly created city object with
        status code 201.

    Raises:
        404: If the state object of the ID does not exist.
        400: If the request data is not in JSON format, or if the
        'name' field is missing.
    """
    state = storage.get(State, state_id)
    if not state:
        abort(404)
    if not request.get_json():
        abort(400, description="Not a JSON")
    if 'name' not in request.get_json():
        abort(400, description="Missing name")
    data = request.get_json()
    instance = City(**data)
    instance.state_id = state.id
    instance.save()
    return make_response(jsonify(instance.to_dict()), 201)


@app_views.route('/cities/<city_id>', methods=['PUT'], strict_slashes=False)
@swag_from('documentation/city/put_city.yml', methods=['PUT'])
def put_city(city_id):
    """
    Update a City object with the specified city_id.

    Args:
        city_id (str): The ID of the city object to be updated.

    Returns:
        A JSON representation of the updated city object with status code 200.

    Raises:
        404 (HTTPException): If the city object with the specified
        ID does not exist.
        400 (HTTPException): If the request data is not in JSON format.
    """
    city = storage.get(City, city_id)
    if not city:
        abort(404)
    if not request.get_json():
        abort(400, description="Not a JSON")
    ignore = ['id', 'state_id', 'created_at', 'updated_at']
    data = request.get_json()
    for key, value in data.items():
        if key not in ignore:
            setattr(city, key, value)
    storage.save()
    return make_response(jsonify(city.to_dict()), 200)
