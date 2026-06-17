from geopy.geocoders import Nominatim


# =========================
# COORDINATES -> LOCATION
# =========================
async def get_location_from_coordinates(
    latitude: float,
    longitude: float
):

    geolocator = Nominatim(
        user_agent="news_app"
    )

    location = geolocator.reverse(
        f"{latitude}, {longitude}",
        language="en"
    )

    if not location:
        return None

    address = location.raw.get(
        "address",
        {}
    )

    return {
        "country": address.get("country"),
        "state": address.get("state"),
        "district": (
            address.get("state_district")
            or address.get("county")
            or address.get("district")
        ),
        "city": (
            address.get("city")
            or address.get("town")
            or address.get("village")
        )
    }


# =========================
# LOCATION -> COORDINATES
# =========================
async def get_coordinates_from_location(
    state: str,
    district: str,
    mandal: str
):

    geolocator = Nominatim(
        user_agent="news_app"
    )

    location_string = (
        f"{mandal}, {district}, {state}, India"
    )

    location = geolocator.geocode(
        location_string
    )

    if not location:
        return None, None

    return (
        location.latitude,
        location.longitude
    )