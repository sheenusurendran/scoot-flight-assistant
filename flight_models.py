from pydantic import BaseModel
from typing import Optional


# ---------------------------------------------------------
# FLIGHT SEARCH REQUEST
# ---------------------------------------------------------

class FlightSearchRequest(BaseModel):

    intent: Optional[str] = None

    origin: Optional[str] = None

    destination: Optional[str] = None

    departure_date: Optional[str] = None

    adults: Optional[int] = None

    children: Optional[int] = None

    infants: Optional[int] = None


# ---------------------------------------------------------
# CONFIRMATION RESPONSE
# ---------------------------------------------------------

class ConfirmationResponse(BaseModel):

    confirmation: str


# ---------------------------------------------------------
# CHECK MISSING FLIGHT INFORMATION
# ---------------------------------------------------------

def get_missing_fields(request: FlightSearchRequest):

    missing = []


    if not request.origin:
        missing.append("origin")


    if not request.destination:
        missing.append("destination")


    if not request.departure_date:
        missing.append("departure_date")


    if request.adults is None:
        missing.append("adults")


    if request.children is None:
        missing.append("children")


    if request.infants is None:
        missing.append("infants")


    return missing
