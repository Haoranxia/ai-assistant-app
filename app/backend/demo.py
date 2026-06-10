import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Code
CLIENT_FILE = "creds/credentials.json"
SCOPES = ["https://www.googleapis.com/auth/calendar"]

creds = None    # Retrieved credentials (initially none)
if os.path.exists("token.json"):    # If we already have credentials
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

# If our credits dont exist or are not valid
if not creds or not creds.valid:
    # Prepare an OAuth authentication process
    # Flow is an object that holds the "state" for an OAuth process. So we 
    # it contains client id, secret, scopes, etc.. 
    # Note no process has happened yet. Just holds all the required info to start the process
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_FILE, SCOPES)
    # This line goes about the whole process. Starts a local HTTP server, logs into google, etc..
    # Hence its called run_local_server
    creds = flow.run_local_server(port=6767)

if creds.expired and creds.refresh_token:
    creds.refresh_token()

with open("token.json", "w") as token:
    token.write(creds.to_json())