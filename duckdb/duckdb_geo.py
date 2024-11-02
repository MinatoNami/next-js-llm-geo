from flask import Flask, request, jsonify
from flask_cors import CORS
import duckdb
import json
import openai

app = Flask(__name__)
CORS(app)
# Set your OpenAI API key here
openai.api_key = "??"

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

# Function to send a prompt to OpenAI's API
def get_openai_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # or "gpt-3.5-turbo"
        messages=[
            {"role": "system", "content": "You are an assistant that can help with volcano data queries."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=100
    )
    return response['choices'][0]['message']['content']

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
        print("Prompt:", user_prompt)
        # Send prompt to OpenAI and get a response
        # ai_response = get_openai_response(user_prompt)
        ai_response = "within"
        
        # Example: If response contains "within" or "radius", perform a spatial query
        if "within" in ai_response or "radius" in ai_response:
            # Extract radius and coordinates from response (assuming AI provides them clearly)
            # For simplicity, assume default values if extraction is not covered yet
            latitude, longitude = 40.821, 14.426  # Default coordinates (e.g., Vesuvius)
            radius_km = 100  # Default radius in km
            
            # Query DuckDB for volcanoes within radius
            query = """
            SELECT V_Name, Country, Latitude, Longitude, ST_Distance(geometry, ST_Point(?, ?)) AS distance_km
            FROM volcano_data
            WHERE ST_DWithin(geometry, ST_Point(?, ?), ?);
            """
            radius_m = radius_km * 1000  # Convert km to meters
            result = conn.execute(query, [longitude, latitude, longitude, latitude, radius_m]).fetchall()
            
            # Format the response for the frontend
            volcanoes = [{
                "name": row[0],
                "country": row[1],
                "latitude": row[2],
                "longitude": row[3],
                "distance_km": row[4]
            } for row in result]
            
            return jsonify({"ai_response": ai_response, "volcanoes": volcanoes}), 200
        
        # If no specific query instruction, return AI response only
        return jsonify({"ai_response": ai_response}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route('/volcanoes/radius', methods=['GET'])
def get_volcanoes_within_radius():
    """Retrieve all volcanoes within a radius (km) from a specified point."""
    try:
        # latitude = float(request.args.get('latitude'))
        # longitude = float(request.args.get('longitude'))
        # radius_km = float(request.args.get('radius'))

        # latitude, longitude = 1.33026764039613, 103.80974175381397  # Example coordinates (e.g., near Vesuvius)
        # radius_km = 10  # Radius in kilometers
        latitude = float(request.args.get('latitude', 1.264))
        longitude = float(request.args.get('longitude', 103.840))
        radius_km = float(request.args.get('radius', 100))
        print("Latitude", latitude)
        
        query = """
        SELECT V_Name, Country, Latitude, Longitude, 
               ST_Distance_Sphere(geometry, ST_Point(?, ?)) / 1000 AS distance_km
        FROM volcano_data
        WHERE ST_DWithin(geometry, ST_Point(?, ?), ?)
        ORDER BY distance_km
        LIMIT 5;
        """

        # query = """
        # SELECT ST_Distance_Sphere(ST_Point(100.473, -0.381), ST_Point(?, ?))/1000 AS distance_k
        # """
        # Need to figure how to filter by spatial distance and return the distance in km

        # Convert radius to meters (since ST_DWithin uses meters)
        radius_m = radius_km * 1000
        result = conn.execute(query, [longitude, latitude, longitude, latitude, radius_m]).fetchall()
        print("Result" , result)
        # Format results as JSON
        volcanoes = [{
            "name": row[0],
            "country": row[1],
            "latitude": row[2],
            "longitude": row[3],
            "distance_km": row[4]
        } for row in result]

        return jsonify(volcanoes), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/volcanoes/bounding-box', methods=['GET'])
def get_volcanoes_within_bounding_box():
    """Retrieve all volcanoes within a bounding box."""
    try:
        # min_lat = float(request.args.get('min_lat'))
        # min_lon = float(request.args.get('min_lon'))
        # max_lat = float(request.args.get('max_lat'))
        # max_lon = float(request.args.get('max_lon'))

        # Define bounding box coordinates (min_lon, min_lat, max_lon, max_lat)
        min_lon, min_lat = 10, 35
        max_lon, max_lat = 20, 45


        query = """
        SELECT V_Name, Country, Latitude, Longitude
        FROM volcano_data
        WHERE ST_Within(geometry, ST_MakeEnvelope(?, ?, ?, ?));
        """

        result = conn.execute(query, [min_lon, min_lat, max_lon, max_lat]).fetchall()

        # Format results as JSON
        volcanoes = [{
            "name": row[0],
            "country": row[1],
            "latitude": row[2],
            "longitude": row[3]
        } for row in result]

        return jsonify(volcanoes), 200

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
