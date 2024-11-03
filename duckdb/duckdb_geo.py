from flask import Flask, request, jsonify
from flask_cors import CORS
import duckdb
import json

from openai_utils import get_openai_response

from volcano_utils import nearest_volcanoes, volcanoes_within_radius, volcanoes_within_bounding_box

app = Flask(__name__)
CORS(app)

with open('volcano.json', 'r') as file:
    volcano_data = json.load(file)

# For an in-memory database
conn = duckdb.connect(database=':memory:')
# Load spatial extension
conn.execute("INSTALL spatial;")
conn.execute("LOAD spatial;")

# Create database
conn.execute("""
    CREATE TABLE IF NOT EXISTS volcano_data (
        VolcanoID INTEGER,
        V_Name TEXT,
        Country TEXT,
        Region TEXT,
        Subregion TEXT,
        PEI INTEGER,
        H_active INTEGER,
        VEI_Holoce TEXT,
        Latitude DOUBLE,
        Longitude DOUBLE,
        geometry GEOMETRY
    );
""")

# Preprocess and insert each feature into the DuckDB table with spatial data
for feature in volcano_data['features']:
    properties = feature['properties']
    latitude = properties.get('Latitude')
    longitude = properties.get('Longitude')
    
    # Prepare values
    volcano_id = properties.get('VolcanoID')
    v_name = properties.get('V_Name')
    country = properties.get('Country')
    region = properties.get('Region')
    subregion = properties.get('Subregion')
    pei = properties.get('PEI')
    h_active = properties.get('H_active')
    vei_holoce = properties.get('VEI_Holoce')
    
    # Insert data, using ST_Point to create the geometry point
    conn.execute("""
        INSERT INTO volcano_data (
            VolcanoID, V_Name, Country, Region, Subregion, PEI, H_active, VEI_Holoce, Latitude, Longitude, geometry
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ST_Point(?, ?));
    """, [volcano_id, v_name, country, region, subregion, pei, h_active, vei_holoce, latitude, longitude, longitude, latitude])



# Example route to fetch sample data from DuckDB
@app.route('/data', methods=['GET'])
def get_data():
    query = "SELECT * FROM volcano_data LIMIT 10"  # Replace with your DuckDB query
    result = conn.execute(query).fetchall()
    return jsonify(result)

# Endpoint to handle chat and query DuckDB
@app.route('/chat-query', methods=['POST'])
def chat_query():
    """Accepts a user prompt, sends it to OpenAI, and queries DuckDB if needed."""
    try:
        # Get prompt from the request
        user_prompt = request.json.get('prompt')
        # print("Prompt:", user_prompt)

        # Send prompt to OpenAI and get a response
        ai_response = json.loads(get_openai_response(user_prompt))
        # ai_response = {
        #     "choice": "/volcanoes/nearest",
        #     "latitude": 1.3521,
        #     "longitude": 103.8198,
        #     "nearest": 10
        #     }
        volcanoes = None
        endpoint_choice = ai_response['choice'].split('/')[2]
        if not endpoint_choice:
             # If no specific query instruction, return AI response only
            return jsonify({"ai_response": ai_response}), 200
        
        # Example: If response contains "within" or "radius", perform a spatial query
        if ('nearest'== endpoint_choice):
            # Call nearest volcanoes endpoint and return
            volcanoes = nearest_volcanoes(conn, ai_response)

        elif ('radius' == endpoint_choice):
            # Call volcanoes within radius endpoint and return
            volcanoes = volcanoes_within_radius(conn, ai_response)

        elif ('bounding-box' == endpoint_choice):
            # Call volcanoes within bounding box endpoint and return
            volcanoes = volcanoes_within_bounding_box(conn, ai_response)

        if volcanoes:
            # print("Volcanoes:", volcanoes)
            return jsonify(volcanoes), 200
        
        # If no specific query instruction, return AI response only
        return jsonify({"ai_response": ai_response}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Returns the nth closest volcanoes to a given point
@app.route('/volcanoes/nearest', methods=['GET'])
def get_nearest_volcanoes():
    """Retrieve the n nearest volcanoes to a specified point."""
    data = request.get_json()
    try:
        response = nearest_volcanoes(conn, data)
        
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Returns all volcanoes within a given radius from a point  
@app.route('/volcanoes/radius', methods=['GET'])
def get_volcanoes_within_radius():
    """Retrieve all volcanoes within a radius (km) from a specified point."""
    data = request.get_json()
    try:
        response = volcanoes_within_radius(conn, data)

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Returns all volcanoes within a given bounding box
@app.route('/volcanoes/bounding-box', methods=['GET'])
def get_volcanoes_within_bounding_box():
    """Retrieve all volcanoes within a bounding box."""
    data = request.get_json()
    try:
        response = volcanoes_within_bounding_box(conn, data)
    
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400



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

# # Create tables for points and polygons
# conn.execute("""
#     CREATE TABLE points_table (geometry GEOMETRY);
#     CREATE TABLE polygons_table (geometry GEOMETRY);
# """)

# # # Insert sample data
# conn.execute("""
#     INSERT INTO points_table VALUES (ST_GeomFromText('POINT(30 10)'));
#     INSERT INTO polygons_table VALUES (ST_GeomFromText('POLYGON((29 9, 31 9, 31 11, 29 11, 29 9))'));
# """)

if __name__ == '__main__':
    app.run(debug=True)

# When exit, close the connection
conn.close()
