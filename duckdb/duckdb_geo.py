from flask import Flask, request, jsonify
import duckdb
import geopandas as gpd

app = Flask(__name__)

# Source: https://data.gov.sg/datasets/d_cac2c32f01960a3ad7202a99c27268a0/view
geojson_file = 'C:/Users/chong/OneDrive/Desktop/Git Repositories/next-js-llm-geo/duckdb/geojson/supermarkets.geojson'
gdf = gpd.read_file(geojson_file)
print(gdf.head())	# Print the first 5 rows of the GeoDataFrame


# Preprocessing the GeoDataFrame
# Rename columns to align with DuckDB schema
gdf = gdf.rename(columns={'Name': 'name', 'Description': 'description'})

# Convert geometries to WKT format
gdf['geometry_wkt'] = gdf['geometry'].apply(lambda x: x.wkt)

# Drop the original 'geometry' column (if you don't need it directly in GeoDataFrame)
gdf = gdf.drop(columns=['geometry']) 

# For an in-memory database
conn = duckdb.connect(database=':memory:')
# Load spatial extension
# Install and load the spatial extension
conn.execute("INSTALL spatial;")
conn.execute("LOAD spatial;")

create_table_query = """
CREATE TABLE supermarkets (
    name TEXT,
    description TEXT,
    geometry_wkt TEXT
);
"""
conn.execute("DROP TABLE IF EXISTS countries;")
conn.execute(create_table_query)

# Insert data into the DuckDB table
# Convert GeoDataFrame to DuckDB-compatible format
# Here we assume that 'gdf' has 'id', 'name', 'population' fields and a 'geometry' field
# Adjust column names as needed

# Write GeoDataFrame to DuckDB, using DuckDB's support for spatial data
conn.register('temp_gdf', gdf)

conn.execute("INSERT INTO supermarkets SELECT * FROM temp_gdf")

# query_result = conn.execute("SELECT * FROM supermarkets").fetchall()
# print(query_result)

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

@app.route('/get_all_supermarkets', methods=['GET'])
def get_all_countries():
    query = "SELECT name, ST_AsText(geom) FROM supermarkets;"
    result = conn.execute(query).fetchall()
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)

# Define the schema for the 'countries' table
# This will create a table with columns based on the GeoDataFrame's properties

# Create tables for points and polygons
# conn.execute("""
#     CREATE TABLE points_table (geometry GEOMETRY);
#     CREATE TABLE polygons_table (geometry GEOMETRY);
# """)

# # Insert sample data
# conn.execute("""
#     INSERT INTO points_table VALUES (ST_GeomFromText('POINT(30 10)'));
#     INSERT INTO polygons_table VALUES (ST_GeomFromText('POLYGON((29 9, 31 9, 31 11, 29 11, 29 9))'));
# """)

# # When exit, close the connection
# conn.close()