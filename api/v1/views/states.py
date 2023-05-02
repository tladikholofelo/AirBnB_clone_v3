#!/usr/bin/python3
"""
This module defines the RESTful API actions for managing State objects.

Routes:
    GET /states: Retrieve a list of all states.
    GET /states/<state_id>: Retrieve a specific state.
    POST /states: Create a new state.
    PUT /states/<state_id>: Update an existing state.
    DELETE /states/<state_id>: Delete a state.
"""
from flask import abort, jsonify, make_response, request
from flasgger.utils import swag_from
from models.state import State
from models import storage
from api.v1.views import app_views


@app_views.route('/states', methods=['GET'], strict_slashes=False)
@swag_from('documentation/state/get_state.yml', methods=['GET'])
def get_states():
    """
    Retrieve the list of all State objects.

    Returns:
        HTTP response containing a JSON list of all states.
    """
    all_states = storage.all(State).values()
    list_states = []
    for state in all_states:
        list_states.append(state.to_dict())
    return jsonify(list_states)


@app_views.route('/states/<state_id>', methods=['GET'], strict_slashes=False)
@swag_from('documentation/state/get_id_state.yml', methods=['get'])
def get_state(state_id):
    """
    Retrieve a specific State.

    Args:
        state_id (str): the ID of the State to retrieve.

    Returns:
        HTTP response containing a JSON representation of the State.

    Raises:
        404: If no State with the given ID exists."""
    state = storage.get(State, state_id)
    if not state:
        abort(404)
    return jsonify(state.to_dict())


@app_views.route('/states/<state_id>', methods=['DELETE'],
                 strict_slashes=False)
@swag_from('documentation/state/delete_state.yml', methods=['DELETE'])
def delete_state(state_id):
    """
    Delete a State Object.

    Args:
        state_id (str): the ID of the State to delete.

    Returns:
        HTTP response with an empty JSON payload.

    Raises:
        404: If no State with the given ID exists.
    """
    state = storage.get(State, state_id)
    if not state:
        abort(404)
    storage.delete(state)
    storage.save()
    return make_response(jsonify({}), 200)


@app_views.route('/states', methods=['POST'], strict_slashes=False)
@swag_from('documentation/state/post_state.yml', methods=['POST'])
def post_state():
    """
    Create a State.

    Returns:
        HTTP response containing a JSON representation of the newly
        created State.

    Raises:
        400: If the request body is not a valid JSON or if the required
        "name" attribute is missing.
    """
    if not request.get_json():
        abort(400, description="Not a JSON")
    data = request.get_json()
    if 'name' not in request.get_json():
        abort(400, description="Missing name")
    instance = State(**data)
    instance.save()
    return make_response(jsonify(instance.to_dict()), 201)


@app_views.route('/states/<state_id>', methods=['PUT'], strict_slashes=False)
@swag_from('documentation/state/put_state.yml', methods=['PUT'])
def put_state(state_id):
    """
    Update a State object.

    Args:
        state_id (str): the ID of the State to update.

    Returns:
        HTTP response containing a JSON representation of the updated State.

    Raises:
        404: If no State with the given ID exists.
        400: If the request body is not a valid JSON.
    """
    state = storage.get(State, state_id)
    if not state:
        abort(404)
    if not request.get_json():
        abort(400, description="Not a JSON")
    ignore = ['id', 'created_at', 'updated_at']
    data = request.get_json()
    for key, value in data.items():
        if key not in ignore:
            setattr(state, key, value)
    storage.save()
    return make_response(jsonify(state.to_dict()), 200)
