import os
import sys
import random
import string
import requests
import argparse
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



def check_auth0_user(email, token):
    """Function to check whether an Auth0 user (non-social) exists"""
    auth0 = Auth0(AUTH0_DOMAIN, token)

    try:
        users = auth0.users.list(q=f'email:"{email}"', search_engine='v3')

        if users['total'] > 0: 
            found_auth0_user = False
            user_info = None

            for user in users['users']:
                for identity in user.get('identities', []):
                    if identity.get('provider') == 'auth0':
                        found_auth0_user = True
                        user_info = {
                            "user_id": user['user_id'],
                            "email_verified": user.get('email_verified', False),
                            "source": "auth0"
                        }
                        break  # exit identities loop

                if found_auth0_user:
                    break  # exit users loop

            if found_auth0_user:
                print("✅ Auth0 user found")
                print(f"  user id        : {user_info['user_id']}")
                print(f"  email verified : {user_info['email_verified']}")
                print(f"  source         : {user_info['source']}")
                return {"found": True, **user_info}
            else:
                print("⚠️ User exists, but only via social provider (e.g. GitHub)")
                return {"found": False, "note": "social login only"}
        else:
            print("❌ No user found in Auth0 with that email.")
            return {"found": False}

    except Exception as error:
        print(f"🚨 An error occurred while processing {email}: {error}")
        return {"found": False, "error": str(error)}


def get_user_groups_from_extension(user_id: str, token: str):
    EXTENSION_DOMAIN="https://cognizant-ai.us12.webtask.io/adf6e2f2b84784b57522e3b19dfc9201"
    url = f"{EXTENSION_DOMAIN}/api/users/{user_id}/groups"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    try:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        groups = resp.json()
        group_names = [g["name"] for g in groups]
        print(f"🔍 Groups from Extension for user {user_id}: {group_names}")
        return group_names
    except Exception as e:
        print(f"🚨 Error fetching groups from extension: {e}")
        return []

def is_user_in_target_group(user_id: str, token: str, target_group: str) -> dict:
    groups = get_user_groups_from_extension(user_id, token)

    if target_group in groups:
        print(f"✅ User IS in target group: {target_group}")
        return {"in_group": True, "groups": groups}
    else:
        print(f"❌ User is NOT in target group: {target_group}")
        return {"in_group": False, "groups": groups}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check Auth0 user group membership.")
    parser.add_argument("email", help="Email address of the user to check")
    args = parser.parse_args()

    email = args.email

    user_check = check_auth0_user(email, get_api_token(MANAGEMENT_AUDIENCE))
    if user_check.get("found"):
        user_id = user_check["user_id"]
        result = is_user_in_target_group(user_id, get_api_token(EXTENSION_AUDIENCE), GROUP_NAME)

