"""
This file is the main streamlit app used for interacting with Google Calendar's API
Details of setup can be found in the Readme of the repository
"""

import streamlit as st
import oyaml, os, datetime
from src.scheduler_lib.gcal_functions import get_a_task, add_tasks
from src.scheduler_lib import raw_app_data_to_tasks, prettify_tasks

# load in the resource data
with open(os.path.abspath('src/scheduler_resources/default_events.yaml'), 'r') as rid:
    resource_data = oyaml.safe_load(rid)

# set up the basic layout of the App
st.title("Colie's Google Calendar Interface")
st.markdown("Use the **Sidebar** on the **Left** to setup the relevant details.")
st.sidebar.title("Calendar Event(s) Details")

# provide the user the default schedules to use
general_choice = st.sidebar.radio('Select a Base Option or Customize from Scratch',
                                  [*[event for event in resource_data['events'].keys()], "Custom"])
st.sidebar.header(f"Current Configuration for {general_choice}")

# handle the details for a given experiment
time_points = st.sidebar.number_input("Number of Time Events:", min_value=1, max_value=10, value=len(resource_data['events'][general_choice]['time_events']), step=1)
with st.sidebar.form("Experiment Details"):

    # dict to store all user inputs
    user_inputs_results = {'time_events': [{} for i in range(time_points)], "Experiment Selection": general_choice}

    # display the user input options
    st.header("User Inputs")
    for user_input in resource_data['events'][general_choice]['user_inputs']:

        # number inputs
        if user_input['type'] == 'number':
            user_inputs_results[user_input['name']] = st.number_input(user_input['name'], min_value=user_input['min'],
                                                                      max_value=user_input['max'], step=user_input['step'])

        # selectbox inputs
        elif user_input['type'] == 'single_select':
            user_inputs_results[user_input['name']] = st.selectbox(user_input['name'], options=user_input['options'])

        # string inputs
        elif user_input['type'] == 'string':
            user_inputs_results[user_input['name']] = st.text_input(user_input['name'])

        # date inputs
        elif user_input['type'] == 'date':
            if user_input['is_start']:
                user_inputs_results['start_date_input'] = st.date_input(user_input['name'] + " (YYYY/MM/DD)", value=datetime.date.today())
            else:
                user_inputs_results[user_input['name']] = st.date_input(user_input['name'] + " (YYYY/MM/DD)", value=datetime.date.today())

    # display the time events
    st.header("Time Events")
    for ind in range(time_points):
        event_name = resource_data['events'][general_choice]['time_events'][ind]['title'] if ind < len(resource_data['events'][general_choice]['time_events']) else "Event Name"
        event_days = resource_data['events'][general_choice]['time_events'][ind]['days'] if ind < len(resource_data['events'][general_choice]['time_events']) else 30

        user_inputs_results['time_events'][ind]['title'] = st.text_input(f"Name of Event {ind}", value=event_name)
        user_inputs_results['time_events'][ind]['day_offset'] = st.number_input(f"Days to Event {ind}", value=event_days,
                                                                           min_value=0, max_value=360, step=1)

    # submit
    submit_spec = st.form_submit_button("Verify My Choices")
    if submit_spec:
        st.session_state['user_genned_data'] = user_inputs_results

# display the generated details in the main panel
# for user final review before submitting and
# provide final submit button
if st.session_state.get('user_genned_data') is not None:
    # convert the raw data to a list of tasks
    tasks = raw_app_data_to_tasks(st.session_state['user_genned_data'])

    # display for the user
    st.header("Events Specified")
    for task_set in prettify_tasks(tasks):
        st.markdown("""---""")
        for line in task_set:
            st.markdown(line)
    st.markdown("""---""")

    # final submit activity
    final_submit = st.button("Submit to Google Calendar!")
    if final_submit:
        st.write("Submitting...")

        #actual calling of the google api
        results = add_tasks(tasks)

        # now remove the genned data
        st.session_state['user_genned_data'] = None
        tasks = None

        # output the results
        st.write("Submitted!")
        st.header("Results:")
        if results:
            for result in results:
                st.write(result)
        else:
            st.write("No Results Obtained")





