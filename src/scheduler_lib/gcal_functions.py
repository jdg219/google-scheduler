from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/tasks.readonly']

path_to_file = os.path.abspath(__file__)
resource_dir = os.path.join(os.path.dirname(os.path.dirname(path_to_file)), 'scheduler_resources')


def _update_token():
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

def get_10_task_lists():
    """Shows basic usage of the Tasks API.
    Prints the title and ID of the first 10 task lists.
    """
    creds = _update_token()
    try:
        service = build('tasks', 'v1', credentials=creds)

        # Call the Tasks API
        results = service.tasklists().list(maxResults=10).execute()
        items = results.get('items', [])

        if not items:
            return ['No task lists found.']

        return [(item['title'], item['id']) for item in items]

    except HttpError as err:
        return err

def get_main_task_list():
    """Shows basic usage of the Tasks API.
    Prints the title and ID of the first 10 task lists.
    """
    creds = _update_token()
    try:
        service = build('tasks', 'v1', credentials=creds)

        # Call the Tasks API
        results = service.tasklists().list(maxResults=1).execute()
        items = results.get('items', [])

        if not items:
            print("No task lists found")
            return None

        return items[0]['title'], items[0]['id']

    except HttpError as err:
        print(err)
        return None

def get_a_task():
    creds = _update_token()

    tasklist_details = get_main_task_list()
    if tasklist_details is None:
        print("Error finding the tasklist")

    else:
        tasklist_id = tasklist_details[0]

        try:
            service = build('tasks', 'v1', credentials=creds)

            results = service.tasks().list(tasklist=tasklist_id, maxResults=1).execute()
            items = results.get('items', [])

            if not items:
                print("No task lists found")
                return None

            return items[0]['title'], items[0]['id']

        except HttpError as err:
            print(err)
            return None
