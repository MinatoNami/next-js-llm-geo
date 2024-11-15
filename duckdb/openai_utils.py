import os
from openai import OpenAI

from dotenv import load_dotenv
load_dotenv()


# Function to send a prompt to OpenAI's API
def get_openai_response(prompt):
    api_docs = """
    Available API Endpoints:
    
    1. **/volcanoes/nearest** (GET): Retrieve the n nearest volcanoes to a specified point.
       - Parameters: latitude (float), longitude (float), nearest (int, optional; defaults to 5)
       - Example JSON input: { "latitude": 1.264, "longitude": 103.840, "nearest": 5 }

    2. **/volcanoes/radius** (GET): Retrieve all volcanoes within a radius (km) from a specified point.
       - Parameters: latitude (float), longitude (float), radius (float; defaults to 500)
       - Example JSON input: { "latitude": 1.264, "longitude": 103.840, "radius": 500 }

    3. **/volcanoes/bounding-box** (GET): Retrieve all volcanoes within a bounding box.
       - Parameters: min_lat (float), min_lon (float), max_lat (float), max_lon (float)
       - Example JSON input: { "min_lat": 35, "min_lon": 10, "max_lat": 45, "max_lon": 20 }
    
    Return a JSON response with the required fields under "parameters", a proper text reply to the user under "text" and have a key "choice",
      to indicate which endpoint would be used.
    Give a definitive answer to the user's query and provide the results in a clear and direct manner.
    """

    if "OPENAI_API_KEY" in os.environ:
        client = OpenAI(
                api_key=os.environ.get("OPENAI_API_KEY")
            )
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "You are a geospatiel chatbot that assist users with locating volcanoes. When asked for information, respond with the results in a clear and direct manner." + api_docs},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" },
            max_tokens=100
        )
        # print("Open ai response", response)
        return response.choices[0].message.content
    else:
        return "{\"error\": \"OpenAI API key not set in environment\"}"