from flask import Flask, request, jsonify
import duckdb

app = Flask(__name__)
# For an in-memory database
conn = duckdb.connect(database=':memory:')
# Load spatial extension
# Install and load the spatial extension
conn.execute("INSTALL spatial;")
conn.execute("LOAD spatial;")

@app.route('/point_in_polygon', methods=['POST'])
def point_in_polygon():
    # Example: {'point': 'POINT(30 10)', 'polygon': 'POLYGON((...))'}
    data = request.get_json()
    point = data['point']
    polygon = data['polygon']

    query = f"""
        SELECT ST_Within(ST_GeomFromText('{point}'), ST_GeomFromText('{polygon}')) AS within
    """
    result = conn.execute(query).fetchall()
    return jsonify(result[0][0])

@app.route('/buffer', methods=['POST'])
def buffer():
    data = request.get_json()
    geometry = data['geometry']
    distance = data.get('distance', 1000)  # Default 1 km buffer

    query = f"""
        SELECT ST_AsText(ST_Buffer(ST_GeomFromText('{geometry}'), {distance})) AS buffered_geometry
    """
    result = conn.execute(query).fetchall()
    return jsonify(result[0][0])

@app.route('/nearest_neighbors', methods=['POST'])
def nearest_neighbors():
    data = request.get_json()
    point = data['point']
    limit = data.get('limit', 5)  # Default 5 neighbors

    query = f"""
        SELECT ST_AsText(geometry) AS geometry, ST_Distance(geometry, ST_GeomFromText('{point}')) AS distance
        FROM points_table
        ORDER BY distance
        LIMIT {limit}
    """
    result = conn.execute(query).fetchall()
    return jsonify(result)

@app.route('/create_points', methods=['POST'])
def create_point_table():
    data = request.get_json()
    points = data['points']

    conn.execute("CREATE TABLE points_table (geometry GEOMETRY);")
    for point in points:
        conn.execute(f"INSERT INTO points_table VALUES (ST_GeomFromText('{point}'));")
    return jsonify('Points table created')

@app.route('/get_all_points', methods=['GET'])
def get_all_points():
    query = "SELECT ST_AsText(geometry) FROM points_table;"
    result = conn.execute(query).fetchall()
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)

# Create tables for points and polygons
conn.execute("""
    CREATE TABLE points_table (geometry GEOMETRY);
    CREATE TABLE polygons_table (geometry GEOMETRY);
""")

# Insert sample data
conn.execute("""
    INSERT INTO points_table VALUES (ST_GeomFromText('POINT(30 10)'));
    INSERT INTO polygons_table VALUES (ST_GeomFromText('POLYGON((29 9, 31 9, 31 11, 29 11, 29 9))'));
""")

# # When exit, close the connection
# conn.close()