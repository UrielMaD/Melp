from flask import request, Response, jsonify

from app import create_app
from app.dbservice import get_restaurants, get_restaurant_by_id, post_restaurant, \
    delete_restaurant_by_id, update_restaurant, get_restaurants_inside_circle

app = create_app()


@app.route('/restaurants', methods=['GET'])
def get_all_restaurants():
    response = get_restaurants()
    if response:
        return response
    else:
        response = Response("No restaurants", status=200, mimetype='application/json')
        return response


@app.route('/restaurants/<id>', methods=['GET'])
def restaurant_by_id(id):
    response = get_restaurant_by_id(id)
    if response:
        return response
    else:
        response = Response("Restaurant not found", status=200, mimetype='application/json')
        return response


@app.route('/restaurants', methods=['POST'])
def add_restaurant():
    request_data = request.get_json()
    if post_restaurant(request_data):
        return get_restaurant_by_id(request_data['id'])
    else:
        response = Response("Restaurant not added", status=200, mimetype='application/json')
        return response


@app.route('/restaurants/<id>', methods=['DELETE'])
def remove_restaurant(id):
    if delete_restaurant_by_id(id):
        response = Response("Restaurant deleted", status=200, mimetype='application/json')
        return response
    else:
        response = Response("Restaurant not deleted", status=200, mimetype='application/json')
        return response


@app.route('/restaurants/<id>', methods=['PUT'])
def update_restaurant_by_id(id):
    request_data = request.get_json()
    response = update_restaurant(id, request_data)
    if response:
        return response
    else:
        response = Response("Restaurant not updated", status=200, mimetype='application/json')
        return response


@app.route('/restaurants/statistics', methods=['GET'])
def get_restaurants_by_radius():
    lat = request.arg.get('latitude')
    lng = request.arg.get('longitude')
    r = request.arg.get('radius')

    print(f'{lat}, {lng}, {r}')

    data = get_restaurants_inside_circle(lat, lng, r)

    data_json = jsonify([x for x in data])

    return data_json


if __name__ == '__main__':
    app.run()

