"""
This file is the main streamlit app used for interacting with Google Calendar's API
Details of setup can be found in the Readme of the repository
"""

import streamlit as st
import oyaml, os
from src.scheduler_lib.gcal_functions import add_event_to_calendar

# load in the resource data
with open(os.path.abspath('src/scheduler_resources/default_events.yaml'), 'r') as rid:
    resource_data = oyaml.safe_load(rid)

# set up the basic layout of the App
st.title("Colie's Google Calendar Interface")
st.markdown("Use the **Sidebar** on the **Left** to setup the relevant details.")
st.sidebar.title("Calendar Event(s) Details")

# provide the user the default schedules to use
general_choice = st.sidebar.radio('Select a Base Option or Customize from Scratch',
                                  [*[event['name'] for event in resource_data['events']], "Custom"])
st.sidebar.header(f"Current Configuration for {general_choice}")


