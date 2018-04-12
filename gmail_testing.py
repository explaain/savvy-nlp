# From this: https://developers.google.com/gmail/api/quickstart/python
# Help from this: https://developers.google.com/identity/sign-in/web/server-side-flow

from __future__ import print_function
import httplib2, http
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from oauth2client.client import GoogleCredentials
from oauth2client import GOOGLE_TOKEN_URI

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
# CLIENT_SECRET_FILE = 'client_secret_704974264220-8vgafqpun36lhcvs82kgbs9dvuu4ohb5.apps.googleusercontent.com.json'
CLIENT_SECRET_FILE = 'google_connect_client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    code = '4/AADMtTHvSid6mkUIt9KOc9y9JPO8n4Ec2UeBO_wHwVMm0yqISpVgzEuMUk0iOE_i4vebEysREpHbapdQsCB6r7Y'
    print('code')
    print(code)

    client_id = '704974264220-lmbsg98tj0f3q09lv4tk6ha46flit4f0.apps.googleusercontent.com'
    client_secret = '7fU16P8yZL-MHzMItnOw-SR0'
    access_token = 'ya29.GluVBRlpHCkhVdbtiACvXWCjbnOtfjlZ49QYQbpCxNVy3ONsnHziLzxgul_nNh4pjFWajsD_fizh2FpZMlpzXTA7zjGeFQ2SrWWEkluK3PvMmdH_Nz3Wf9RwIANQ'
    token_expiry = '2018-04-06 17:41:56.773950'
    refresh_token = '1/sbwfQRDru3Kd4E5IsvmW0zBiPBBX5XKK7shcwzKM6SKpBCQCLL-unY484vlZwCGm'
    token_uri = GOOGLE_TOKEN_URI
    user_agent = 'Python client library'
    revoke_uri = None

    gCreds = GoogleCredentials(
      access_token,
      client_id,
      client_secret,
      refresh_token,
      token_expiry,
      token_uri,
      user_agent,
      revoke_uri=revoke_uri
    )
    print('token_uri')
    print(token_uri)
    print('gCreds')
    print(gCreds)
    return gCreds

    # Exchange auth code for access token, refresh token, and ID token
    credentials = client.credentials_from_clientsecrets_and_code(CLIENT_SECRET_FILE, [SCOPES], code)
    print('credentials 123')
    print(credentials)
    print(dir(credentials))
    print('credentials.client_id', credentials.client_id)
    print('credentials.client_secret', credentials.client_secret)
    print('credentials.access_token', credentials.access_token)
    print('credentials.refresh_token', credentials.refresh_token)

    http_auth = credentials.authorize(httplib2.Http())
    print('credentials.retrieve_scopes()', credentials.retrieve_scopes(http=http_auth))
    print('credentials.id_token', credentials.id_token)
    print('credentials.token_expiry', credentials.token_expiry)
    print('credentials.get_access_token()', credentials.get_access_token(http=http_auth))

    drive_service = discovery.build('drive', 'v3', http=http_auth)
    print('drive_service')
    print(drive_service)

    appfolder = drive_service.files().list().execute()
    print('appfolder')
    print(appfolder)

    #
    #
    # home_dir = os.path.expanduser('~')
    # credential_dir = os.path.join(home_dir, '.credentials')
    # if not os.path.exists(credential_dir):
    #   os.makedirs(credential_dir)
    # credential_path = os.path.join(credential_dir,
    #                                'gmail-python-quickstart.json')
    #
    # store = Storage(credential_path)
    # credentials = store.get()
    # print('credentials')
    # print(credentials)
    # if not credentials or credentials.invalid:
    #   flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
    #   print('flow')
    #   print(flow)
    #   flow.user_agent = APPLICATION_NAME
    #   if flags:
    #     credentials = tools.run_flow(flow, store, flags)
    #     print('credentials')
    #     print(credentials)
    #   else: # Needed only for compatibility with Python 2.6
    #     credentials = tools.run(flow, store)
    #   print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """Shows basic usage of the Gmail API.

    Creates a Gmail API service object and outputs a list of label names
    of the user's Gmail account.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    print('http')
    print(http)
    service = discovery.build('gmail', 'v1', http=http)

    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    if not labels:
        print('No labels found.')
    else:
      print('Labels:')
      for label in labels:
        print(label['name'])


if __name__ == '__main__':
    main()
