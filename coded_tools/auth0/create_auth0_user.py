import os
import sys
import random
import string
import requests
from auth0.management import Auth0

# Configuration
AUTH0_DOMAIN = "cognizant-ai.auth0.com"
CLIENT_ID = "KhDbuFds86TZVGCbz8JUHsgROZyMXIkq"
CONNECTION_NAME = "Username-Password-Authentication"
MANAGEMENT_AUDIENCE = f"https://{AUTH0_DOMAIN}/api/v2/"
EXTENSION_AUDIENCE = "urn:auth0-authz-api"
GROUP_NAME = "unileaf-user"
GROUP_API_URL = "https://cognizant-ai.us12.webtask.io/adf6e2f2b84784b57522e3b19dfc9201/api/groups"

# Get the client secret from the environment variable
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

if not CLIENT_SECRET:
    print("Error: CLIENT_SECRET environment variable is not set.")
    sys.exit(1)


# Function to fetch a fresh API token
def get_api_token(audience):
    """Function to fetch a fresh API token"""
    url = f"https://{AUTH0_DOMAIN}/oauth/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "audience": audience,
        "grant_type": "client_credentials",
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json().get("access_token")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching API token for audience {audience}: {e}")
        sys.exit(1)


def generate_random_password(length=20):
    """Function to generate a random password"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*()-_"
    return "".join(random.choice(characters) for _ in range(length))


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
        sys.exit(1)


def add_user_to_group(user_id, group_id, token):
    """Function to add a user to a group which
       uses the Authorization Extension api"""
    url = f"{GROUP_API_URL}/{group_id}/members"
    headers = {"Authorization": f"Bearer {token}"}
    payload = [user_id]

    try:
        response = requests.patch(url, json=payload, headers=headers)
        response.raise_for_status()
        print(f"User {user_id} successfully added to group {group_id}.")
    except requests.exceptions.RequestException as e:
        print(f"Error adding user to group: {e}")
        sys.exit(1)


def fetch_tokens():
    """
    Fetches tokens for the Management API and Authorization Extension API.

    Returns:
        tuple: (management_token, extension_token)
    """
    try:
        management_token = get_api_token(MANAGEMENT_AUDIENCE)
        extension_token = get_api_token(EXTENSION_AUDIENCE)
        return management_token, extension_token
    except Exception as e:
        print(f"Error fetching tokens: {e}")
        sys.exit(1)


def process_emails(email_list):
    """
    Process a list of emails: create users and add them to a group.

    Args:
        email_list (list): List of email addresses.
    Returns:
        list: Emails that failed to process.
    """
    # Fetch tokens
    token_management, token_extension = fetch_tokens()

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
            add_user_to_group(user_id, group_id, token_extension)
            print(f"User {email} successfully added to group {GROUP_NAME}.")

        except Exception as error:
            print(f"An error occurred while processing {email}: {error}")
            failures.append(email)

    return failures


def parse_email_list(raw_email_string):
    """
    Parses and cleans a comma-separated string of emails.

    Args:
        raw_email_string (str): Comma-separated string of email addresses.

    Returns:
        list: Cleaned list of email addresses.
    """
    return [email.strip() for email in raw_email_string.split(",") if email.strip()]


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

