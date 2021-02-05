import psycopg2
from psycopg2 import Error
import json
import pandas as pd
from postgis.psycopg import register

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
register(conn)


# Private function that checks if table exists
def _check_if_table_exists(name):
    cur.execute(f"""
        select * from information_schema.tables where table_name = '{name}'
        """)
    result = cur.fetchone()
    if result:
        return True
    else:
        return False


# Private function that creates the table restaurants
def _create_table():
    cur.execute("""
        CREATE TABLE restaurants ( 
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
    cur.close()
    conn.commit()


COLUMNS = 'id, rating, name, site, email, phone, street, city, state, lat, lng'


# Function that returns an array with all the restaurants in the data base
def get_restaurants():
    table_exists = _check_if_table_exists('restaurants')
    if table_exists:
        cur.execute(f"""SELECT {COLUMNS} FROM restaurants""")
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
        return None


# Function thar returns a restaurant that matches with given id
def get_restaurant_by_id(id):
    table_exists = _check_if_table_exists('restaurants')
    if table_exists:
        cur.execute(f"SELECT {COLUMNS} FROM restaurants WHERE id = '{id}'")
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


# Function that post a restaurant in the database if it does not exists
def post_restaurant(rest):
    if _check_if_table_exists('restaurants') and get_restaurant_by_id(rest['id']) is None:
        query = """INSERT INTO restaurants(id, rating, name, site, email, phone, street,
                                            city, state, lat, lng) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cur.execute(query, (
            rest['id'], rest['rating'], rest['name'], rest['site'], rest['email'],
            rest['phone'], rest['street'], rest['city'], rest['state'], rest['lat'],
            rest['lng']
        ))
        cur.execute(f"""
                UPDATE restaurants SET geom = ST_SetSRID(ST_MakePoint(lng, lat), 4326) 
                WHERE id = '{rest['id']}'
            """)
        conn.commit()
        result = get_restaurant_by_id(rest['id'])
        if result is not None:
            return result
        else:
            return None
    else:
        return None


# Function that updates restaurant information if it exists
def update_restaurant(id, rest):
    if _check_if_table_exists('restaurants') and get_restaurant_by_id(id) is not None:
        query = """UPDATE restaurants SET rating = %s, name = %s, site = %s, email = %s,
                phone = %s, street = %s, city = %s, state = %s, lat = %s, lng = %s,
                geom = ST_SetSRID(ST_MakePoint(%s, %s), 4326) WHERE id = %s"""
        cur.execute(query, (
            rest['rating'], rest['name'], rest['site'], rest['email'], rest['phone'],
            rest['street'], rest['city'], rest['state'], rest['lat'], rest['lng'],
            rest['lng'], rest['lat'], id,
        ))
        cur.execute(f"""
                UPDATE restaurants SET geom = ST_SetSRID(ST_MakePoint(lng, lat), 4326) 
                WHERE id = '{id}'
            """)
        conn.commit()
        result = get_restaurant_by_id(id)
        if result is not None:
            return result
        else:
            return None
    else:
        return None


# Function that deletes a restaurant if it exists
def delete_restaurant_by_id(id):
    if get_restaurant_by_id(id):
        cur.execute(f"DELETE FROM restaurants WHERE id = '{id}'")
        conn.commit()
        return True
    else:
        return None


# Private function that loads all data from a csv file
def _load_data():
    df = pd.read_csv('/app/static/restaurants.csv')

    for index, row in df.iterrows():
        rest = dict(zip(row.index, row.values))
        print(post_restaurant(rest))


# Private function that creates the geom column to handle GEO queries
def _create_geo_column():
    cur.execute("""
        SELECT AddGeometryColumn('restaurants', 'geom', 4326, 'POINT', 2);
    """)
    cur.execute("""
        UPDATE restaurants SET geom = ST_SetSRID(ST_MakePoint(lng, lat), 4326); 
        CREATE INDEX idx_restaurants ON restaurants USING gist(geom);
    """)


# Function that returns a cursor with all restaurants within a circle with
# center given by 'lat' and 'lng' with a radius = r
def get_restaurants_inside_circle(lat, lng, r):
    cur.execute(f"""
        SELECT rating FROM restaurants 
        WHERE ST_DWithin(geom, ST_MakePoint({lng}, {lat})::geography, {r})
    """)
    conn.commit()
    return cur
