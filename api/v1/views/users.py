#!/usr/bin/python3
"""This module defines the RestFul API Endpoints for managing users.

Endpoints:
    - GET /users: Retrieves a list of all user objects.
    - GET /users/<user_id>: Retrieves a specific user object.
    - POST /users: Creates a new user object.
    - PUT /users/<user_id>: Updates an existing user object.
    - DELETE /users/<user_id>: Deletes an existing user object.
"""
from models.user import User
from models import storage
from api.v1.views import app_views
from flask import abort, jsonify, make_response, request
from flasgger.utils import swag_from


@app_views.route('/users', methods=['GET'], strict_slashes=False)
@swag_from('documentation/user/all_users.yml')
def get_users():
    """
    Retrieves a list of all user objects or a specific user object.

    Returns:
        A JSON object containing a list of user objects.

    Raises:
        404: If the requested user object(s) do not exist.
    """
    all_users = storage.all(User).values()
    list_users = []
    for user in all_users:
        list_users.append(user.to_dict())
    return jsonify(list_users)


@app_views.route('/users/<user_id>', methods=['GET'], strict_slashes=False)
@swag_from('documentation/user/get_user.yml', methods=['GET'])
def get_user(user_id):
    """Retrieve a user object by id.

    Args:
        user_id (str): The id of the user.

    Returns:
        The user object in JSON format.

    Raises:
        404: If no user with the given id is found in storage.
    """
    user = storage.get(User, user_id)
    if not user:
        abort(404)

    return jsonify(user.to_dict())


@app_views.route('/users/<user_id>', methods=['DELETE'],
                 strict_slashes=False)
@swag_from('documentation/user/delete_user.yml', methods=['DELETE'])
def delete_user(user_id):
    """
    Delete a user object by id.

    Args:
        user_id (str): The id of the user.

    Returns:
        An empty JSON response with status code 200.

    Raises:
        404: If no user with the given id is found in storage.
    """
    user = storage.get(User, user_id)

    if not user:
        abort(404)

    storage.delete(user)
    storage.save()

    return make_response(jsonify({}), 200)


@app_views.route('/users', methods=['POST'], strict_slashes=False)
@swag_from('documentation/user/post_user.yml', methods=['POST'])
def post_user():
    """
    Creates a user.

    Args:
        None

    Returns:
        A JSON response containing the newly created user.

    Raises:
        400 error if request is not in JSON format or,
        if email or password is missing.
    """
    if not request.get_json():
        abort(400, description="Not a JSON")

    if 'email' not in request.get_json():
        abort(400, description="Missing email")
    if 'password' not in request.get_json():
        abort(400, description="Missing password")

    data = request.get_json()
    instance = User(**data)
    instance.save()
    return make_response(jsonify(instance.to_dict()), 201)


@app_views.route('/users/<user_id>', methods=['PUT'], strict_slashes=False)
@swag_from('documentation/user/put_user.yml', methods=['PUT'])
def put_user(user_id):
    """
    Updates a user.

    Args:
        user_id (int): ID of the user to be updated.

    Returns:
        A JSON response containing the updated user.

    Raises:
        404 error if the user with the specified ID does not exist.
        400 error if request is not in JSON format.
    """
    user = storage.get(User, user_id)

    if not user:
        abort(404)

    if not request.get_json():
        abort(400, description="Not a JSON")

    ignore = ['id', 'email', 'created_at', 'updated_at']

    data = request.get_json()
    for key, value in data.items():
        if key not in ignore:
            setattr(user, key, value)
    storage.save()
    return make_response(jsonify(user.to_dict()), 200)
