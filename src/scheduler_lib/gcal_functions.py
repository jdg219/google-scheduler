import os
from typing import Tuple, List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.scheduler_lib import Task

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/tasks']

path_to_file = os.path.abspath(__file__)
resource_dir = os.path.join(os.path.dirname(os.path.dirname(path_to_file)), 'scheduler_resources')


def _update_token():
    """
    This method is pulled from Google Task's API docs which describes how to
    create a new credential and token file for interaction with a project API

    :return: a valid credential
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(f'{resource_dir}/token.json'):
        creds = Credentials.from_authorized_user_file(f'{resource_dir}/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                f'{resource_dir}/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(f'{resource_dir}/token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

def task_api_interface(command_to_execute: callable) -> Tuple:
    """
    This method handles the basic interaction setup for the Google Task
    API. In general, the interaction is a consistent form with just the
    action to execute differing

    :param command_to_execute: the task api command
    :return: Tuple (possibly None) of resulting item 0
    """
    try:
        results = command_to_execute.execute()
        items = results.get('items', [])

        if not items:
            print("No task lists found")
            return None

        return items[0]['title'], items[0]['id']

    except HttpError as err:
        print(err)
        return None

def get_main_task_list():
    """Shows basic usage of the Tasks API.
    Returns the main task list title and id
    """
    creds = _update_token()
    service = build('tasks', 'v1', credentials=creds)
    executable_action = service.tasklists().list(maxResults=1)

    return task_api_interface(executable_action)

def get_a_task() -> Tuple:
    """
    A dummy method to demonstrate fetching a single task
    from the main task list, useful for checking if something has been populated

    :return: A single task from the main tasklist
    """
    creds = _update_token()
    tasklist_details = get_main_task_list()
    if tasklist_details is None:
        print("Error finding the tasklist")
    else:
        tasklist_id = tasklist_details[1]
        service = build('tasks', 'v1', credentials=creds)
        executable_command = service.tasks().list(tasklist=tasklist_id, maxResults=1)
        return task_api_interface(executable_command)
    return None


def add_task_to_default_tasklist(task: Task):
    """
    This method handles the addition of a task to the default
    task list of a user.

    :param task: a Task class object with the necessary fields
    :return: the result of insertion of the task
    """
    creds = _update_token()
    tasklist_details = get_main_task_list()
    if tasklist_details is None:
        print("Error finding the tasklist")
    else:
        tasklist_id = tasklist_details[1]
        service = build('tasks', 'v1', credentials=creds)
        executable_command = service.tasks().insert(tasklist=tasklist_id, body=task.dict())
        results = executable_command.execute()
        return results

        # TODO: REVERT BACK TO HELPER LATER
        #return task_api_interface(executable_command)
    return None

def add_tasks(tasks: List[Task]) -> List:
    """
    This is a wrapper to allow for multiple task additions  from a list

    :param tasks: a list of tasks to upload
    :return: a list of results
    """
    results = []
    for task in tasks:
        result = add_task_to_default_tasklist(task)
        results.append(result)
    return results