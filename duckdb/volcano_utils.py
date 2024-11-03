from utils import process_result

def nearest_volcanoes(conn, data):
    # Get latitude, longitude, and number of nearest volcanoes from the request
        latitude = float(data.get('latitude', 1.264))
        longitude = float(data.get('longitude', 103.840))
        n = int(data.get('nearest', '5'))  # Default to 5 nearest volcanoes
        # Query to find the n nearest volcanoes
        query = """
        SELECT V_Name, Country, Latitude, Longitude, 
               ST_Distance(geometry, ST_Point(?, ?)) AS distance_km
        FROM volcano_data
        ORDER BY distance_km
        LIMIT ?;
        """
        
        # Execute the query with the given parameters
        result = conn.execute(query, [longitude, latitude, n]).fetchall()
        
        # Format the results as JSON
        volcanoes = process_result(longitude, latitude, result)
        
        return volcanoes

def volcanoes_within_radius (conn, data):
        latitude = float(data.get('latitude', 1.264))
        longitude = float(data.get('longitude', 103.840))
        radius_km = float(data.get('radius', 500))
        # print("Latitude", latitude)
        
        query = """
        SELECT V_Name, Country, Latitude, Longitude, 
               ST_Distance(geometry, ST_Point(?, ?)) / 1000 AS distance
        FROM volcano_data
        ORDER BY distance
        LIMIT 5;
        """

        # query = """
        # SELECT V_Name, Country, Latitude, Longitude, 
        #        ST_Distance(geometry, ST_Point(?, ?)) / 1000 AS distance
        # FROM volcano_data
        #     WHERE ST_DWithin(geometry, ST_Point(?, ?), ?)
        # ORDER BY distance
        # LIMIT 5;
        # """
        # SELECT ST_DWithin(ST_Point(101.840, 1.264), ST_Buffer(ST_Point(103.8198, 1.3521), 10000), 10000);

        # query = """
        # SELECT ST_Distance_Sphere(ST_Point(100.473, -0.381), ST_Point(?, ?))/1000 AS distance_k
        # """
        # Need to figure how to filter by spatial distance and return the distance in km

        # Convert radius to meters (since ST_DWithin uses meters)
        radius_m = radius_km * 1000
        result = conn.execute(query, [longitude, latitude]).fetchall()
        # Format results as JSON
        volcanoes = process_result(longitude, latitude, result, radius_km)

        return volcanoes

def volcanoes_within_bounding_box (conn, data):
    min_lat = float(data.get('min_lat', 35))
    min_lon = float(data.get('min_lon', 10))
    max_lat = float(data.get('max_lat', 45))
    max_lon = float(data.get('max_lon', 20))

    # Define bounding box coordinates (min_lon, min_lat, max_lon, max_lat)
    # min_lon, min_lat = 10, 35
    # max_lon, max_lat = 20, 45


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

    return volcanoes