import streamlit as st

from flight_agent import (
    understand_request,
    understand_confirmation,
    check_flight_request,
    get_question_for_missing_fields
)

from flight_api import search_flights


st.set_page_config(
    page_title="SkyAssist - Flight Assistant",
    page_icon="✈️",
    layout="centered"
)


st.title("✈️ SkyAssist")
st.caption("Your AI Flight Assistant")
st.divider()


if "messages" not in st.session_state:

    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! 👋 I'm SkyAssist.\n\n"
                "Tell me where you want to fly from, "
                "where you want to go, your travel date, "
                "and passenger details."
            )
        }
    ]


if "flight_request" not in st.session_state:
    st.session_state.flight_request = None


if "awaiting_confirmation" not in st.session_state:
    st.session_state.awaiting_confirmation = False


for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.write(message["content"])


user_message = st.chat_input(
    "Ask me about your flight..."
)


if user_message:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )


    with st.chat_message("user"):

        st.write(user_message)


    # =====================================================
    # CONFIRMATION FLOW
    # =====================================================

    if st.session_state.awaiting_confirmation:

        with st.chat_message("assistant"):

            with st.spinner(
                "Understanding your response..."
            ):

                try:

                    confirmation = understand_confirmation(
                        user_message
                    )


                    # =================================================
                    # YES
                    # =================================================

                    if confirmation == "YES":

                        st.session_state.awaiting_confirmation = False

                        response = (
                            "Confirmed. ✅\n\n"
                            "I will now search for flights."
                        )

                        st.write(response)

                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": response
                            }
                        )


                        # =============================================
                        # SERPAPI FLIGHT SEARCH
                        # =============================================

                        with st.spinner(
                            "🔎 Searching real flights..."
                        ):

                            try:

                                request = (
                                    st.session_state.flight_request
                                )


                                flight_results = search_flights(
                                    origin=request.origin,
                                    destination=request.destination,
                                    departure_date=request.departure_date,
                                    adults=request.adults,
                                    children=request.children,
                                    infants=request.infants
                                )


                                st.success(
                                    "✈️ Flight search completed!"
                                )


                                best_flights = (
                                    flight_results.get(
                                        "best_flights",
                                        []
                                    )
                                )


                                if not best_flights:

                                    st.warning(
                                        "No flights were found "
                                        "for these details."
                                    )

                                else:

                                    st.write(
                                        f"Found {len(best_flights)} "
                                        f"flight options."
                                    )


                                    for flight_group in best_flights:

                                        first_flight = (
                                            flight_group[
                                                "flights"
                                            ][0]
                                        )


                                        airline = (
                                            first_flight.get(
                                                "airline",
                                                "Unknown airline"
                                            )
                                        )


                                        price = (
                                            flight_group.get(
                                                "price",
                                                "Price unavailable"
                                            )
                                        )


                                        duration = (
                                            flight_group.get(
                                                "total_duration",
                                                "Unknown"
                                            )
                                        )


                                        departure = (
                                            first_flight.get(
                                                "departure_airport",
                                                {}
                                            )
                                        )


                                        arrival = (
                                            first_flight.get(
                                                "arrival_airport",
                                                {}
                                            )
                                        )


                                        departure_time = (
                                            departure.get(
                                                "time",
                                                "Unknown"
                                            )
                                        )


                                        arrival_time = (
                                            arrival.get(
                                                "time",
                                                "Unknown"
                                            )
                                        )


                                        st.markdown(
                                            f"""
                                            ✈️ **{airline}**

                                            **{request.origin} → {request.destination}**

                                            Departure: {departure_time}

                                            Arrival: {arrival_time}

                                            Duration: {duration} minutes

                                            **Price: SGD {price}**
                                            """
                                        )

                                        st.divider()


                            except Exception as e:

                                st.error(
                                    f"Flight search failed: {str(e)}"
                                )

                                print(
                                    "FLIGHT SEARCH ERROR:",
                                    repr(e)
                                )


                    # =================================================
                    # NO
                    # =================================================

                    elif confirmation == "NO":

                        st.session_state.awaiting_confirmation = False

                        response = (
                            "No problem. I won't search "
                            "for flights."
                        )

                        st.write(response)

                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": response
                            }
                        )


                    # =================================================
                    # MODIFY
                    # =================================================

                    elif confirmation == "MODIFY":

                        st.session_state.awaiting_confirmation = False

                        response = (
                            "Sure. What would you like "
                            "to change?"
                        )

                        st.write(response)

                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": response
                            }
                        )


                    # =================================================
                    # UNCLEAR
                    # =================================================

                    else:

                        response = (
                            "I want to make sure I understood "
                            "correctly. Would you like me to "
                            "proceed with the flight search?"
                        )

                        st.write(response)

                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": response
                            }
                        )


                except Exception as e:

                    error_message = f"Error: {str(e)}"

                    st.error(error_message)

                    print(
                        "ERROR:",
                        repr(e)
                    )


    # =====================================================
    # NORMAL FLIGHT INFORMATION FLOW
    # =====================================================

    else:

        with st.chat_message("assistant"):

            with st.spinner(
                "Understanding your request..."
            ):

                try:

                    previous_request = (
                        st.session_state.flight_request
                    )


                    request = understand_request(
                        user_message=user_message,
                        previous_request=previous_request,
                        conversation_history=(
                            st.session_state.messages
                        )
                    )


                    st.session_state.flight_request = request


                    result = check_flight_request(
                        request
                    )


                    # =================================================
                    # MISSING INFORMATION
                    # =================================================

                    if not result["ready"]:

                        question = (
                            get_question_for_missing_fields(
                                result["missing"]
                            )
                        )

                        st.write(question)

                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": question
                            }
                        )


                    # =================================================
                    # ALL INFORMATION AVAILABLE
                    # =================================================

                    else:

                        confirmation_message = (
                            "I have the following flight details. "
                            "Please confirm before I search for flights.\n\n"

                            f"**From:** {request.origin}\n\n"

                            f"**To:** {request.destination}\n\n"

                            f"**Date:** {request.departure_date}\n\n"

                            f"**Adults:** {request.adults}\n\n"

                            f"**Children:** {request.children}\n\n"

                            f"**Infants:** {request.infants}\n\n"

                            "**Shall I search for flights? "
                            "Please answer naturally, for example "
                            "\"Yes, proceed\" or \"Yeah, good to go\".**"
                        )


                        st.write(
                            confirmation_message
                        )


                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": confirmation_message
                            }
                        )


                        st.session_state.awaiting_confirmation = True


                except Exception as e:

                    error_message = f"Error: {str(e)}"

                    st.error(error_message)

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": error_message
                        }
                    )

                    print(
                        "ERROR:",
                        repr(e)
                    )