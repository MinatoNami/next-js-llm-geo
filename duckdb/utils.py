import math

def haversine(lat1, lon1, lat2, lon2):
    # Radius of Earth in kilometers
    R = 6371.0
    
    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Distance in kilometers
    distance = R * c
    return distance

# Helper function to process results
def process_result(longitude, latitude, result, radius_km=0):
    volcanoes = []
    for row in result:
        result_lat = row[2]
        result_long = row[3]

        # Use haversine formula to calculate distance between two points
        distance_km = haversine(latitude, longitude, result_lat, result_long)
        obj = {
        "name": row[0],
        "country": row[1],
        "latitude": row[2],
        "longitude": row[3],
        "distance_km": distance_km
        }
        #Explicitly check if distance is within radius (issue with st_dwithin or st_within)
        if radius_km == 0:
            volcanoes.append(obj)
        elif distance_km <= radius_km:
            volcanoes.append(obj)
    return volcanoes
