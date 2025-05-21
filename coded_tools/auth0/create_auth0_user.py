from typing import Any
from typing import Dict
from typing import Union
from auth0.management import Auth0

from neuro_san.interfaces.coded_tool import CodedTool
import os
import sys
import random
import string
import requests

# Configuration
AUTH0_DOMAIN = "cognizant-ai.auth0.com"
CLIENT_ID = "KhDbuFds86TZVGCbz8JUHsgROZyMXIkq"
CONNECTION_NAME = "Username-Password-Authentication"
MANAGEMENT_AUDIENCE = f"https://{AUTH0_DOMAIN}/api/v2/"
EXTENSION_AUDIENCE = "urn:auth0-authz-api"
GROUP_NAME = "unileaf-user"
GROUP_API_URL = "https://cognizant-ai.us12.webtask.io/adf6e2f2b84784b57522e3b19dfc9201/api/groups"

def generate_random_password(length=20):
    """Function to generate a random password"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*()-_"
    return "".join(random.choice(characters) for _ in range(length))

def parse_email_list(raw_email_string):
    """
    Parses and cleans a comma-separated string of emails.

    Args:
        raw_email_string (str): Comma-separated string of email addresses.

    Returns:
        list: Cleaned list of email addresses.
    """
    return [email.strip() for email in raw_email_string.split(",") if email.strip()]

def create_auth0_user(email, password, token):
    """Function to create a user"""
    auth0 = Auth0(AUTH0_DOMAIN, token)
    user_data = {
        "email": email,
        "password": password,
        "connection": CONNECTION_NAME,
        "email_verified": True,
    }

    try:
        user = auth0.users.create(user_data)
        # We need the user_id in order to add them to the group
        user_id = user['user_id']
        print(f"User created successfully. User ID: {user_id}")
        return user_id
    except Exception as e:
        print(f"Error creating user: {e}")
        return None

def get_group_id(group_name, token):
    """Fetch group ID by name which uses the
       Authorization Extension api"""
    url = f"{GROUP_API_URL}"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        # Access the list of groups under the "groups" key
        groups = data.get("groups", [])
        if not groups:
            print("No groups found.")
            return None

        for group in groups:
            if group["name"] == group_name:
                return group["_id"]
        print(f"Group '{group_name}' not found.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching groups: {e}")
        return None

def add_user_to_group(user_id, group_id, token) -> bool:
    """Function to add a user to a group which
       uses the Authorization Extension api"""
    url = f"{GROUP_API_URL}/{group_id}/members"
    headers = {"Authorization": f"Bearer {token}"}
    payload = [user_id]

    try:
        response = requests.patch(url, json=payload, headers=headers)
        response.raise_for_status()
        print(f"User {user_id} successfully added to group {group_id}.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error adding user to group: {e}")
        return False


class CreateAuth0User(CodedTool):
    """
    A tool that adds a list of users to Auth0 system,
    given a list of their e-mails.
    """

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Looks up user status in the Auth0 system and returns it to the caller.
        :param args: A dictionary with the following keys:
                    "users": a string containing comma-delimited list of users e-mails.

        :param sly_data: A dictionary containing parameters that should be kept out of the chat stream.
                         Keys expected for this implementation are:
                         None

        :return: A dictionary containing:
                 "failed": a sequence of strings with user e-mails that failed to be processed successfully.
                 "message": a string which could be empty
                          or could contain additional information about user status.
        """
        _ = sly_data
        client_secret: str = os.environ.get("CLIENT_SECRET", None)
        tool_name = self.__class__.__name__
        print(f"========== Calling {tool_name} ==========")

        # Parse and clean the email list
        emails_to_process = parse_email_list(args.get("users", ""))

        if not emails_to_process:
            return {"failed": []}

        # Process the emails
        failed_emails = self.process_emails(client_secret, emails_to_process)

        # Check for failures
        if failed_emails:
            print("\nThe following emails failed:")
            for failed_email in failed_emails:
                print(f"- {failed_email}")
            return failed_emails
        else:
            print("\nAll users processed successfully.")
            return []

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """
        Delegates to the synchronous invoke method because it's quick, non-blocking.
        """
        return self.invoke(args, sly_data)

    # Function to fetch a fresh API token
    def get_api_token(self, client_secret: str, audience: str) -> str:
        """Function to fetch a fresh API token"""
        url = f"https://{AUTH0_DOMAIN}/oauth/token"
        payload = {
            "client_id": CLIENT_ID,
            "client_secret": client_secret,
            "audience": audience,
            "grant_type": "client_credentials",
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json().get("access_token")
        except requests.exceptions.RequestException as e:
            err_msg: str = f"Error fetching API token for audience {audience}: {e}"
            print(err_msg)
            return err_msg

    def fetch_tokens(self, client_secret: str):
        """
        Fetches tokens for the Management API and Authorization Extension API.

        Returns:
            tuple: (management_token, extension_token)
        """
        try:
            management_token = self.get_api_token(client_secret, MANAGEMENT_AUDIENCE)
            extension_token = self.get_api_token(client_secret, EXTENSION_AUDIENCE)
            return management_token, extension_token
        except Exception as e:
            err_msg: str = f"Error fetching tokens: {e}"
            print(err_msg)
            return err_msg, err_msg

    def process_emails(self, client_secret, email_list):
        """
        Process a list of emails: create users and add them to a group.

        Args:
            email_list (list): List of email addresses.
        Returns:
            list: Emails that failed to process.
        """
        # Fetch tokens
        token_management, token_extension = self.fetch_tokens(client_secret)
        if token_management.startswith("Error"):
            return email_list

        failures = []
        group_id = get_group_id(GROUP_NAME, token_extension)
        if not group_id:
            print(f"Failed to find group '{GROUP_NAME}'. Cannot proceed.")
            return email_list  # All emails fail if the group isn't found

        for email in email_list:
            print(f"Processing user: {email}")
            try:
                # Generate password
                password = generate_random_password()
                print(f"Generated password for {email}: <redacted>")

                # Create user
                user_id = create_auth0_user(email, password, token_management)
                if not user_id:
                    print(f"User creation failed for {email}.")
                    failures.append(email)
                    continue

                # Add user to group
                if add_user_to_group(user_id, group_id, token_extension):
                    print(f"User {email} successfully added to group {GROUP_NAME}.")
                else:
                    failures.append(email)
            except Exception as error:
                print(f"An error occurred while processing {email}: {error}")
                failures.append(email)
        return failures


if __name__ == "__main__":
    # Check for emails as a command-line argument
    if len(sys.argv) != 2:
        print("Usage: python create_auth0_user.py <email1,email2,email3,...>")
        sys.exit(1)

    # Parse and clean the email list
    raw_email_string = sys.argv[1]
    emails_to_process = parse_email_list(raw_email_string)

    if not emails_to_process:
        print("No valid emails provided. Exiting.")
        sys.exit(1)

    # Process the emails
    failed_emails = process_emails(emails_to_process)

    # Check for failures
    if failed_emails:
        print("\nThe following emails failed:")
        for failed_email in failed_emails:
            print(f"- {failed_email}")
        sys.exit(1)  # Exit with failure status
    else:
        print("\nAll users processed successfully.")

