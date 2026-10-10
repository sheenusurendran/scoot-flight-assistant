import os
import json
from datetime import date

from dotenv import load_dotenv
from google import genai

from flight_models import (
    FlightSearchRequest,
    ConfirmationResponse,
    get_missing_fields
)


# ---------------------------------------------------------
# ENVIRONMENT
# ---------------------------------------------------------

load_dotenv()


GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)


if not GEMINI_API_KEY:

    raise ValueError(
        "GEMINI_API_KEY is not set in .env file"
    )


# ---------------------------------------------------------
# GEMINI CLIENT
# ---------------------------------------------------------

client = genai.Client(
    api_key=GEMINI_API_KEY
)


MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)


# =========================================================
# FLIGHT REQUEST SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = """
You are SkyAssist, an AI flight search assistant.

Your job is to understand the user's current message and
update the existing flight-search information.

The flight information fields are:

- intent
- origin
- destination
- departure_date
- adults
- children
- infants

Rules:

1. Never guess missing information.

2. Preserve information that is already known from the
   previous conversation.

3. If the user provides new information, update the
   corresponding field.

4. If the user gives only a number, interpret that number
   according to the previous assistant question.

   Example:
   Assistant: "How many adults are travelling?"
   User: "2"
   Then adults = 2.

5. If the user says "just me", adults = 1.

6. If children are not mentioned, do NOT assume children = 0.

7. If infants are not mentioned, do NOT assume infants = 0.

8. Convert common city names to IATA airport codes when
   you are confident.

   Singapore -> SIN
   London -> LHR
   Bangkok -> BKK
   Kuala Lumpur -> KUL
   Chennai -> MAA
   Mumbai -> BOM
   Delhi -> DEL

9. Convert dates into YYYY-MM-DD format.

10. For relative dates such as "tomorrow", "today", or
    "next Monday", use the current date provided in the context.

11. Do not overwrite existing information with null.

12. Return only valid JSON.

For flight-search requests:
- intent must always be "search_flight"
- origin must be the IATA airport code
- destination must be the IATA airport code
- departure_date must be YYYY-MM-DD
- adults must contain the number of adults if provided
- children must contain the number of children if provided
- infants must contain the number of infants if provided

Never invent missing passenger information.
Never use "search_flights" as the intent. Use exactly "search_flight".

The JSON must contain:

{
    "intent": "...",
    "origin": "...",
    "destination": "...",
    "departure_date": "...",
    "adults": ...,
    "children": ...,
    "infants": ...
}
"""


# =========================================================
# UNDERSTAND FLIGHT REQUEST
# =========================================================

def understand_request(
    user_message,
    previous_request=None,
    conversation_history=None
):

    # -----------------------------------------------------
    # Previous structured information
    # -----------------------------------------------------

    previous_data = {}


    if previous_request:

        previous_data = (
            previous_request.model_dump()
        )


    # -----------------------------------------------------
    # Conversation history
    # -----------------------------------------------------

    history_text = ""


    if conversation_history:

        history_text = "\n".join(
            [
                f"{message['role']}: {message['content']}"
                for message in conversation_history
            ]
        )


    # -----------------------------------------------------
    # Current date
    # -----------------------------------------------------

    today = date.today().isoformat()


    # -----------------------------------------------------
    # Gemini prompt
    # -----------------------------------------------------

    prompt = f"""
{SYSTEM_PROMPT}

Today's date is: {today}

Current known flight information:

{json.dumps(previous_data, indent=2)}

Previous conversation:

{history_text}

Current user message:

{user_message}

Return the UPDATED flight information as JSON.
"""


    # -----------------------------------------------------
    # Gemini call
    # -----------------------------------------------------

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )


    # -----------------------------------------------------
    # Read response
    # -----------------------------------------------------

    response_text = response.text.strip()


    # -----------------------------------------------------
    # Remove markdown code fences
    # -----------------------------------------------------

    if response_text.startswith("```"):

        response_text = response_text.replace(
            "```json",
            ""
        )

        response_text = response_text.replace(
            "```",
            ""
        )

        response_text = response_text.strip()


    # -----------------------------------------------------
    # Parse JSON
    # -----------------------------------------------------

    data = json.loads(
        response_text
    )


    # -----------------------------------------------------
    # Validate with Pydantic
    # -----------------------------------------------------

    request = FlightSearchRequest.model_validate(
        data
    )


    return request


# =========================================================
# CHECK FLIGHT REQUEST
# =========================================================

def check_flight_request(request):

    missing = get_missing_fields(
        request
    )


    if missing:

        return {
            "ready": False,
            "missing": missing
        }


    return {
        "ready": True,
        "missing": []
    }


# =========================================================
# QUESTION FOR MISSING INFORMATION
# =========================================================

def get_question_for_missing_fields(
    missing_fields
):

    questions = {

        "origin":
            "Where will you be flying from?",

        "destination":
            "Where would you like to fly to?",

        "departure_date":
            "What date would you like to travel?",

        "adults":
            "How many adults are travelling?",

        "children":
            "How many children are travelling? "
            "Please enter 0 if none.",

        "infants":
            "How many infants are travelling? "
            "Please enter 0 if none."
    }


    for field in missing_fields:

        if field in questions:

            return questions[field]


    return (
        "Please provide the missing flight information."
    )


# =========================================================
# UNDERSTAND CONFIRMATION
# =========================================================

def understand_confirmation(
    user_message
):

    prompt = f"""
You are classifying a user's response to a flight-search
confirmation request.

The assistant has already shown the user the complete
flight details and asked whether it should proceed.

Classify the user's response into exactly ONE of:

YES
NO
MODIFY
UNCLEAR

Examples:

"yes" -> YES
"yeah, go ahead" -> YES
"good to go" -> YES
"sure, proceed" -> YES
"that's correct" -> YES
"looks good" -> YES
"okay proceed" -> YES

"no" -> NO
"don't search" -> NO
"cancel" -> NO
"not now" -> NO

"change the date" -> MODIFY
"actually make it 3 adults" -> MODIFY
"I want to change the destination" -> MODIFY
"change the passenger count" -> MODIFY

"maybe" -> UNCLEAR
"I think so" -> UNCLEAR
"what was the date again?" -> UNCLEAR
"how much is it?" -> UNCLEAR

Important:

- Never guess.
- If the user's intention is ambiguous, return UNCLEAR.
- Return ONLY valid JSON.

Required JSON format:

{{
    "confirmation": "YES"
}}

User response:

{user_message}
"""


    # -----------------------------------------------------
    # Gemini call
    # -----------------------------------------------------

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )


    # -----------------------------------------------------
    # Read response
    # -----------------------------------------------------

    response_text = response.text.strip()


    # -----------------------------------------------------
    # Remove markdown code fences
    # -----------------------------------------------------

    if response_text.startswith("```"):

        response_text = response_text.replace(
            "```json",
            ""
        )

        response_text = response_text.replace(
            "```",
            ""
        )

        response_text = response_text.strip()


    # -----------------------------------------------------
    # Parse JSON
    # -----------------------------------------------------

    data = json.loads(
        response_text
    )


    # -----------------------------------------------------
    # Validate response
    # -----------------------------------------------------

    confirmation = (
        ConfirmationResponse.model_validate(
            data
        )
    )


    # -----------------------------------------------------
    # Safety validation
    # -----------------------------------------------------

    allowed_values = {
        "YES",
        "NO",
        "MODIFY",
        "UNCLEAR"
    }


    if confirmation.confirmation not in allowed_values:

        return "UNCLEAR"


    return confirmation.confirmation