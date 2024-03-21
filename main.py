from datetime import datetime

import streamlit as st
from pytz import timezone

from api_calendar import create_event
from api_llm import query_llm


def main():
    st.set_page_config(
        page_title="AI Agent Demo app",
        page_icon=":robot:"
    )
    st.header("AI Agent Demo app")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Let me help you !"):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner(text="processing..."):

            try:
                llm_response = query_llm(query=prompt)
                ai_response = f"DEBUG: {llm_response}"
                ai_response = f"Thanks ! Will be creating an event on Google Calendar with " \
                              f"Title: {llm_response['meeting_name']} on " \
                              f"{llm_response['start_date']} at {llm_response['start_time']} "

            except KeyError as ke:
                ai_response = "Failed to process your request..."

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(ai_response)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": ai_response})

        with st.spinner("creating event"):
            start_datetime_str = f"{llm_response['start_date']} {llm_response['start_time']}"
            end_datetime_str = f"{llm_response['end_date']} {llm_response['end_time']}"

            kolkata_timezone = timezone('Asia/Kolkata')

            # Convert to ISO datetime format
            start_event = datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M")
            start_event = kolkata_timezone.localize(start_event).isoformat()
            end_event = datetime.strptime(end_datetime_str, "%Y-%m-%d %H:%M")
            end_event = kolkata_timezone.localize(end_event).isoformat()

            event_obj = {
                'summary': llm_response['meeting_name'],
                'start_datetime': start_event,  # Replace with desired start datetime (ISO 8601 format)
                'end_datetime': end_event,  # Replace with desired end datetime (ISO 8601 format)
            }

            status, cal_link = create_event(event_obj)
            if status:
                agent_response = f"Event created, {cal_link}"
            else:
                agent_response = "Event not created !"

        with st.chat_message("assistant"):
            st.markdown(agent_response)
        st.session_state.messages.append({"role": "assistant", "content": agent_response})


if __name__ == "__main__":
    main()
