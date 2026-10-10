import os
import requests
from dotenv import load_dotenv


load_dotenv()


API_KEY = os.getenv("SERPAPI_API_KEY")


if not API_KEY:
    raise ValueError(
        "SERPAPI_API_KEY is not set in .env file"
    )


def search_flights(
    origin,
    destination,
    departure_date,
    adults=1,
    children=0,
    infants=0
):

    url = "https://serpapi.com/search"


    params = {

        "engine": "google_flights",

        "api_key": API_KEY,

        "departure_id": origin,

        "arrival_id": destination,

        "outbound_date": departure_date,

        # 2 = one-way
        "type": "2",

        "currency": "SGD",

        "hl": "en",

        "gl": "sg",

        "adults": adults,

        "children": children,

        # SerpApi requires us to distinguish
        # infants in seat vs infants on lap.
        # For our first version, treat them as lap infants.
        "infants_on_lap": infants
    }


    response = requests.get(
        url,
        params=params
    )


    print(
        "SerpApi HTTP Status:",
        response.status_code
    )


    if response.status_code != 200:

        print(
            "SerpApi Error:",
            response.text
        )


    response.raise_for_status()


    return response.json()


# ---------------------------------------------------------
# TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    result = search_flights(
        origin="SIN",
        destination="LHR",
        departure_date="2026-09-25",
        adults=2,
        children=1,
        infants=1
    )


    print("\nFlight search completed.")

    print(
        "Best flights found:",
        len(result.get("best_flights", []))
    )


    for flight_group in result.get(
        "best_flights",
        []
    ):

        print(
            "\nAirline:",
            flight_group["flights"][0]["airline"]
        )

        print(
            "Price:",
            flight_group.get("price")
        )

        print(
            "Duration:",
            flight_group.get("total_duration"),
            "minutes"
        )