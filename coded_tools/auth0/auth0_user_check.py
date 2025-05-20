from typing import Any
from typing import Dict
from typing import Union
from auth0.management import Auth0

from neuro_san.interfaces.coded_tool import CodedTool

import os
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

# # Get the client secret from the environment variable
# CLIENT_SECRET = os.getenv("CLIENT_SECRET")
#
# if not CLIENT_SECRET:
#     print("Error: CLIENT_SECRET environment variable is not set.")
#     sys.exit(1)


class Auth0UserCheck(CodedTool):
    """
    A tool that looks up Auth0 user by his id, and then checks and returns his status.
    """

    def __init__(self):
        self.group_name: str = GROUP_NAME
        self.group_api_url: str = GROUP_API_URL

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Looks up user status in the Auth0 system and returns it to the caller.
        :param args: A dictionary with the following keys:
                    "user_id": Auth0 user id.

        :param sly_data: A dictionary containing parameters that should be kept out of the chat stream.
                         Keys expected for this implementation are:
                         None

        :return: A dictionary containing:
                 "user_id": the passed in Auth0 user id,
                 "valid": status of this user, which could be:
                          "true" or "false"
                 "group_valid": status of this user group, which could be:
                          "true" or "false"
                 "message": a string which could be empty
                          or could contain additional information about user status.
        """
        _ = sly_data
        client_secret: str = os.environ.get("CLIENT_SECRET", None)
        tool_name = self.__class__.__name__
        print(f"========== Calling {tool_name} ==========")
        user_id: str = args.get("user_id", None)

        token: str = self.get_api_token(client_secret, MANAGEMENT_AUDIENCE)
        if token.startswith("Error"):
            tool_response = {
                "user_id": user_id,
                "valid": "false",
                "group_valid": "false",
                "message": token}
            return tool_response

        response_dict: Dict[str, Any] = self.check_auth0_user(user_id, token)
        user_found: bool = response_dict.get("found", False)
        err_msg: str = response_dict.get("error", "")
        user_in_group: bool = False
        if user_found:
            user_id: str = response_dict["user_id"]
            token: str = self.get_api_token(client_secret, EXTENSION_AUDIENCE)
            if token.startswith("Error"):
                tool_response = {
                    "user_id": user_id,
                    "valid": "true",
                    "group_valid": "false",
                    "message": token}
                return tool_response
            result_dict: Dict[str, Any] = self.is_user_in_target_group(user_id, token, GROUP_NAME)
            user_in_group = result_dict.get("in_group", False)

        tool_response = {"user_id": user_id,
                         "valid": "true" if user_found else "false",
                         "group_valid": "true" if user_in_group else "false",
                         "message": err_msg
                        }
        print("-----------------------")
        print(f"{tool_name} response: ", tool_response)
        print(f"========== Done with {tool_name} ==========")
        return tool_response

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

    def check_auth0_user(self, email, token):
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
                    return {"found": False, "error": "social login only"}
            else:
                print("❌ No user found in Auth0 with that email.")
                return {"found": False}

        except Exception as error:
            print(f"🚨 An error occurred while processing {email}: {error}")
            return {"found": False, "error": str(error)}

    def get_user_groups_from_extension(self, user_id: str, token: str):
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

    def is_user_in_target_group(self, user_id: str, token: str, target_group: str) -> dict:
        groups = self.get_user_groups_from_extension(user_id, token)

        if target_group in groups:
            print(f"✅ User IS in target group: {target_group}")
            return {"in_group": True, "groups": groups}
        else:
            print(f"❌ User is NOT in target group: {target_group}")
            return {"in_group": False, "groups": groups}

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """
        Delegates to the synchronous invoke method because it's quick, non-blocking.
        """
        return self.invoke(args, sly_data)




#
#
#
#
#
#
#
# # Function to fetch a fresh API token
# def get_api_token(audience):
#     """Function to fetch a fresh API token"""
#     url = f"https://{AUTH0_DOMAIN}/oauth/token"
#     payload = {
#         "client_id": CLIENT_ID,
#         "client_secret": CLIENT_SECRET,
#         "audience": audience,
#         "grant_type": "client_credentials",
#     }
#
#     try:
#         response = requests.post(url, json=payload)
#         response.raise_for_status()
#         return response.json().get("access_token")
#
#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching API token for audience {audience}: {e}")
#         sys.exit(1)
#
#
#
# def check_auth0_user(email, token):
#     """Function to check whether an Auth0 user (non-social) exists"""
#     auth0 = Auth0(AUTH0_DOMAIN, token)
#
#     try:
#         users = auth0.users.list(q=f'email:"{email}"', search_engine='v3')
#
#         if users['total'] > 0:
#             found_auth0_user = False
#             user_info = None
#
#             for user in users['users']:
#                 for identity in user.get('identities', []):
#                     if identity.get('provider') == 'auth0':
#                         found_auth0_user = True
#                         user_info = {
#                             "user_id": user['user_id'],
#                             "email_verified": user.get('email_verified', False),
#                             "source": "auth0"
#                         }
#                         break  # exit identities loop
#
#                 if found_auth0_user:
#                     break  # exit users loop
#
#             if found_auth0_user:
#                 print("✅ Auth0 user found")
#                 print(f"  user id        : {user_info['user_id']}")
#                 print(f"  email verified : {user_info['email_verified']}")
#                 print(f"  source         : {user_info['source']}")
#                 return {"found": True, **user_info}
#             else:
#                 print("⚠️ User exists, but only via social provider (e.g. GitHub)")
#                 return {"found": False, "note": "social login only"}
#         else:
#             print("❌ No user found in Auth0 with that email.")
#             return {"found": False}
#
#     except Exception as error:
#         print(f"🚨 An error occurred while processing {email}: {error}")
#         return {"found": False, "error": str(error)}
#
#
# def get_user_groups_from_extension(user_id: str, token: str):
#     EXTENSION_DOMAIN="https://cognizant-ai.us12.webtask.io/adf6e2f2b84784b57522e3b19dfc9201"
#     url = f"{EXTENSION_DOMAIN}/api/users/{user_id}/groups"
#     headers = {
#         "Authorization": f"Bearer {token}"
#     }
#     try:
#         resp = requests.get(url, headers=headers)
#         resp.raise_for_status()
#         groups = resp.json()
#         group_names = [g["name"] for g in groups]
#         print(f"🔍 Groups from Extension for user {user_id}: {group_names}")
#         return group_names
#     except Exception as e:
#         print(f"🚨 Error fetching groups from extension: {e}")
#         return []
#
# def is_user_in_target_group(user_id: str, token: str, target_group: str) -> dict:
#     groups = get_user_groups_from_extension(user_id, token)
#
#     if target_group in groups:
#         print(f"✅ User IS in target group: {target_group}")
#         return {"in_group": True, "groups": groups}
#     else:
#         print(f"❌ User is NOT in target group: {target_group}")
#         return {"in_group": False, "groups": groups}
#
#
#
#
#
# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Check Auth0 user group membership.")
#     parser.add_argument("email", help="Email address of the user to check")
#     args = parser.parse_args()
#
#     email = args.email
#
#     user_check = check_auth0_user(email, get_api_token(MANAGEMENT_AUDIENCE))
#     if user_check.get("found"):
#         user_id = user_check["user_id"]
#         result = is_user_in_target_group(user_id, get_api_token(EXTENSION_AUDIENCE), GROUP_NAME)
#
