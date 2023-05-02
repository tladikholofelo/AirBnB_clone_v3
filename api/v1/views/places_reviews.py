#!/usr/bin/python3
"""
This module defines RESTful API endpoints for managing Reviews
associated with Places.

Endpoints:
    GET /places/<place_id>/reviews: Retrieves a list of all Review objects.
    GET /reviews/<review_id>: Retrieves a Review object with the specified ID.
    POST /places/<place_id>/reviews: Creates a new Review object for a Place.
    PUT /reviews/<review_id>: Updates a Review object with the specified ID.
    DELETE /reviews/<review_id>: Deletes a Review object with the specified ID.
"""
from models.review import Review
from models.place import Place
from models.user import User
from models import storage
from api.v1.views import app_views
from flask import abort, jsonify, make_response, request
from flasgger.utils import swag_from


@app_views.route('/places/<place_id>/reviews', methods=['GET'],
                 strict_slashes=False)
@swag_from('documentation/reviews/get_reviews.yml', methods=['GET'])
def get_reviews(place_id):
    """
    Retrieve a list of Review objects associated with a Place.

    Args:
        place_id (str): The ID of the Place to retrieve Reviews for.

    Returns:
        A JSON response containing a list of Review objects associated
        with the specified Place.

    Raises:
        404 error: If the Place with the specified ID does not exist.
    """
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    reviews = [review.to_dict() for review in place.reviews]
    return jsonify(reviews)


@app_views.route('/reviews/<review_id>', methods=['GET'], strict_slashes=False)
@swag_from('documentation/reviews/get_review.yml', methods=['GET'])
def get_review(review_id):
    """
    Retrieve a Review object by ID.

    Args:
        review_id (str): The ID of the Review to retrieve.

    Returns:
        A JSON response containing the Review object.

    Raises:
        404 error: If the Review with the specified ID does not exist.
    """
    review = storage.get(Review, review_id)
    if not review:
        abort(404)
    return jsonify(review.to_dict())


@app_views.route('/reviews/<review_id>', methods=['DELETE'],
                 strict_slashes=False)
@swag_from('documentation/reviews/delete_reviews.yml', methods=['DELETE'])
def delete_review(review_id):
    """
    Args:
    review_id (str): The ID of the Review object to delete.

    Returns:
        A JSON response with an empty dictionary and a status
        code of 200 if the deletion was successful.

    Raises:
    404: If the Review object with the specified ID does not exist.
    """
    review = storage.get(Review, review_id)
    if not review:
        abort(404)
    storage.delete(review)
    storage.save()
    return make_response(jsonify({}), 200)


@app_views.route('/places/<place_id>/reviews', methods=['POST'],
                 strict_slashes=False)
@swag_from('documentation/reviews/post_reviews.yml', methods=['POST'])
def post_review(place_id):
    """
    Creates a Review object.

    Args:
        place_id (str): The id of the Place object to which the review belongs.

    Returns:
        A JSON response containing the newly created Review object.

    Raises:
        400 Bad Request: If the request data is not a valid JSON or
            user_id or text are missing from the request data.
        404 Not Found: If the Place object with the given place_id or the
            User object with the given user_id is not found.
    """
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    if not request.get_json():
        abort(400, description="Not a JSON")
    if 'user_id' not in request.get_json():
        abort(400, description="Missing user_id")
    data = request.get_json()
    user = storage.get(User, data['user_id'])
    if not user:
        abort(404)
    if 'text' not in request.get_json():
        abort(400, description="Missing text")
    data['place_id'] = place_id
    instance = Review(**data)
    instance.save()
    return make_response(jsonify(instance.to_dict()), 201)


@app_views.route('/reviews/<review_id>', methods=['PUT'], strict_slashes=False)
@swag_from('documentation/reviews/put_reviews.yml', methods=['PUT'])
def put_review(review_id):
    """
    Update a Review object by ID.

    Args:
        review_id (str): The ID of the Review to update.

    Returns:
        A JSON response containing the updated Review object.

    Raises:
        400: If the request is not a valid JSON or if any of the
        required fields are missing.
    """
    review = storage.get(Review, review_id)
    if not review:
        abort(404)
    if not request.get_json():
        abort(400, description="Not a JSON")
    ignore = ['id', 'user_id', 'place_id', 'created_at', 'updated_at']
    data = request.get_json()
    for key, value in data.items():
        if key not in ignore:
            setattr(review, key, value)
    storage.save()
    return make_response(jsonify(review.to_dict()), 200)
