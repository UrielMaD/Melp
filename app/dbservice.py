import psycopg2
from psycopg2 import Error
import json

try:
    conn = psycopg2.connect(
        user="ojarcsdtkmvrpo",
        password="668dcc1854b8c19e66faa5c744eabfff5824ec62158430eb9770184df646c5be",
        host="ec2-3-222-11-129.compute-1.amazonaws.com",
        port=5432,
        database="da6kivfej96opc"
    )
except Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")

cur = conn.cursor()


def _check_if_table_exists(name):
    cur.execute(f"""
        select * from information_schema.tables where table_name = '{name}'
        """)
    result = cur.fetchone()
    if result:
        return True
    else:
        return False


def _create_table():
    cur.execute("""CREATE TABLE Restaurants( 
        id VARCHAR(36) NOT NULL PRIMARY KEY,
        rating INT,
        name TEXT,
        site TEXT,
        email TEXT,
        phone TEXT,
        street TEXT,
        city TEXT,
        state TEXT,
        lat FLOAT,
        lng FLOAT
    )
    """)


def get_restaurants():
    table_exists = _check_if_table_exists('Restaurants')
    if table_exists:
        cur.execute("""SELECT * FROM Restaurants""")
        headers = [x[0] for x in cur.description]
        rv = cur.fetchall()
        restaurants = []
        for result in rv:
            restaurants.append(dict(zip(headers, result)))
        if len(restaurants) > 0:
            return json.dumps(restaurants)
        else:
            return None
    else:
        _create_table()
        return None


def get_restaurant_by_id(id):
    table_exists = _check_if_table_exists('Restaurants')
    if table_exists:
        cur.execute(f"SELECT * FROM Restaurants WHERE id = '{id}'")
        headers = [x[0] for x in cur.description]
        rv = cur.fetchall()
        json_data = []

        for result in rv:
            json_data.append(dict(zip(headers, result)))
        if len(json_data) > 0:
            return json.dumps(json_data)
        else:
            return None
    else:
        return None


def post_restaurant(rest):
    if _check_if_table_exists('Restaurants') and get_restaurant_by_id(rest['id']) is None:
        query = """INSERT INTO Restaurants VALUES (%s, %d, %s, %s, %s, %s, %s, %s, %s, %d, %d)"""
        cur.execute(query, (
            rest['id'], rest['rating'], rest['name'], rest['site'], rest['email'],
            rest['phone'], rest['street'], rest['city'], rest['state'], rest['lat'],
            rest['lng']
        ))
        conn.commit()
        result = get_restaurant_by_id(rest['id'])
        if result is not None:
            return result
        else:
            return None
    else:
        return None


def update_restaurant(id, rest):
    if _check_if_table_exists('Restaurants') and get_restaurant_by_id(id) is not None:
        query = """UPDATE Restaurants SET rating = %d, name = %s, site = %s, email = %s,
                phone = %s, street = %s, city = %s, state = %s, lat = %d, lng = %d WHERE
                id = %s"""
        cur.execute(query, (
            rest['rating'], rest['name'], rest['site'], rest['email'], rest['phone'],
            rest['street'], rest['city'], rest['state'], rest['lat'], rest['lng'],
            id,
        ))
        conn.commit()
        result = get_restaurant_by_id(id)
        if result is not None:
            return result
        else:
            return None
    else:
        return None


def delete_restaurant_by_id(id):
    if get_restaurant_by_id(id):
        cur.execute(f"DELETE FROM Restaurants WHERE id = '{id}'")
        conn.commit()
        return True
    else:
        return None


print(get_restaurants())