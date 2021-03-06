from flask import request, Response, jsonify
import numpy as np

from app import create_app
from app.dbservice import get_restaurants, get_restaurant_by_id, post_restaurant, \
    delete_restaurant_by_id, update_restaurant, get_restaurants_inside_circle

app = create_app()


# Route for the GET method that returns all restaurants
@app.route('/restaurants', methods=['GET'])
def get_all_restaurants():
    response = get_restaurants()
    if response:
        return response
    else:
        response = Response("No restaurants", status=200, mimetype='application/json')
        return response


# Route for the GET method that returns a restaurant that matches
# with given id
@app.route('/restaurants/<id>', methods=['GET'])
def restaurant_by_id(id):
    response = get_restaurant_by_id(id)
    if response:
        return response
    else:
        response = Response("Restaurant not found", status=200, mimetype='application/json')
        return response


# Route for posting a restaurant
@app.route('/restaurants', methods=['POST'])
def add_restaurant():
    request_data = request.get_json()
    if post_restaurant(request_data):
        return get_restaurant_by_id(request_data['id'])
    else:
        response = Response("Restaurant not added", status=200, mimetype='application/json')
        return response


# Route for deleting a restaurant
@app.route('/restaurants/<id>', methods=['DELETE'])
def remove_restaurant(id):
    if delete_restaurant_by_id(id):
        response = Response("Restaurant deleted", status=200, mimetype='application/json')
        return response
    else:
        response = Response("Restaurant not deleted", status=200, mimetype='application/json')
        return response


# Route for update information about a restaurant
@app.route('/restaurants/<id>', methods=['PUT'])
def update_restaurant_by_id(id):
    request_data = request.get_json()
    response = update_restaurant(id, request_data)
    if response:
        return response
    else:
        response = Response("Restaurant not updated", status=200, mimetype='application/json')
        return response


# Route for the statistical data about restaurants within a circle
@app.route('/restaurants/statistics', methods=['GET'])
def get_restaurants_by_radius():
    lat = request.args.get('latitude')
    lng = request.args.get('longitude')
    r = request.args.get('radius')

    data = get_restaurants_inside_circle(lat, lng, r)
    data = [x[0] for x in data]

    stats = {
        "count": len(data),
        "avg": np.mean(data),
        "std": np.std(data),
    }

    return stats


if __name__ == '__main__':
    app.run()

