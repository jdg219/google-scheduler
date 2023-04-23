"""
This class holds relevant classes for operation of the gcal functions
"""
from pydantic import BaseModel
from typing import Dict, List
from copy import deepcopy
import datetime


class Task(BaseModel):
    """
    This class is the format for a Google Task
    to be added to a tasklist
    """
    title: str
    notes: str
    due: str

def prettify_tasks(tasks: List[Task]) -> List[str]:
    """
    This method converts a list of tasks to a nicely formatted string

    :param tasks: the tasks to put into a nice format
    :return: a string representation of all tasks
    """

    final_string_set = []
    for ind, task in enumerate(tasks):

        # the task set of lines
        task_strings = [f"**Task Number** : _{ind+1}_", f"**Task Title** : _{task.title}_", f"**Task Notes** :"]

        # parse out the notes
        for line in task.notes.split('||'):
            task_strings += [f"_{line.replace('|', '').strip()}_"]

        # finally parse the due date
        task_strings += [f"**Task Due Date** : _{task.due.split('T')[0].strip()}_"]

        final_string_set.append(task_strings)

    return final_string_set


def raw_app_data_to_tasks(user_generated_data: Dict) -> List:
    """
    This method handles converting from the raw data extracted from the streamlit
    app to the Task classes to be uploaded via the Google Tasks API

    :param user_generated_data: a dictionary containing details from the user (notes field) and a key "time_events"
                                which are all the time and name details for tasks
    :return: a list of Task classes
    """
    # the notes will be the same for each, drawn from all fields besides time_events
    notes = ""
    for key, data in user_generated_data.items():
        if key != 'time_events' and key != 'start_date_input':
            notes += f"| {key} : {data} |"

    # now we handle the actual task generation for each time_event
    tasks = []
    for ind, time_event in enumerate(user_generated_data['time_events']):
        # final setup for notes
        custom_notes = deepcopy(notes)
        custom_notes += f"| Start Date : {user_generated_data['start_date_input']} |"
        custom_notes += f"| Days from Start Date : {time_event['day_offset']} |"
        custom_notes += f"| Task Number {ind+1} of {len(user_generated_data['time_events'])} in Series |"

        # setup for correct date string
        due = datetime.datetime.combine(user_generated_data['start_date_input'], datetime.datetime.min.time()).astimezone() + \
                        datetime.timedelta(days=time_event['day_offset'])
        due = due.isoformat()

        tasks.append(Task(title=time_event['title'], due=due, notes=custom_notes))

    return tasks
