import os
import sys
from typing import Any
from typing import Dict
from typing import Union

from neuro_san.interfaces.coded_tool import CodedTool


class URLProvider(CodedTool):
    """
    CodedTool implementation which provides URLs for company's intranet apps.
    """

    def __init__(self):
        """
        Constructs a URL Provider for company's intranet.
        """
        INTRANET = os.environ.get("MI_INTRANET", None)
        print(f"INTRANET: {INTRANET}")

        HCM = os.environ.get("MI_HCM", None)
        print(f"HCM: {HCM}")

        ABSENCE_MANAGEMENT = os.environ.get("MI_ABSENCE_MANAGEMENT", None)
        print(f"ABSENCE_MANAGEMENT: {ABSENCE_MANAGEMENT}")

        TRAVEL_AND_EXPENSE = os.environ.get("MI_TRAVEL_AND_EXPENSE", None)
        print(f"TRAVEL_AND_EXPENSE: {TRAVEL_AND_EXPENSE}")

        GSD = os.environ.get("MI_GSD", None)
        print(f"GSD: {GSD}")

        self.company_urls = {
            "One Cognizant": INTRANET,
            "HCM": HCM,
            "Absence Management": ABSENCE_MANAGEMENT,
            "Travel and Expense": TRAVEL_AND_EXPENSE,
            "GSD": GSD
        }

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """
        :param args: An argument dictionary whose keys are the parameters
                to the coded tool and whose values are the values passed for them
                by the calling agent.  This dictionary is to be treated as read-only.

                The argument dictionary expects the following keys:
                    "app_name" the name of the One Cognizant app for which the URL is needed.

        :param sly_data: A dictionary whose keys are defined by the agent hierarchy,
                but whose values are meant to be kept out of the chat stream.

                This dictionary is largely to be treated as read-only.
                It is possible to add key/value pairs to this dict that do not
                yet exist as a bulletin board, as long as the responsibility
                for which coded_tool publishes new entries is well understood
                by the agent chain implementation and the coded_tool implementation
                adding the data is not invoke()-ed more than once.

                Keys expected for this implementation are:
                    None

        :return:
            In case of successful execution:
                The URL to the app as a string.
            otherwise:
                a text string an error message in the format:
                "Error: <error message>"
        """
        app_name: str = args.get("app_name", None)
        if app_name is None:
            return "Error: No app name provided."
        print(">>>>>>>>>>>>>>>>>>>URL Provider>>>>>>>>>>>>>>>>>>")
        print(f"App name: {app_name}")
        app_url = self.company_urls.get(app_name)
        print(f"URL: {app_url}")
        print(">>>>>>>>>>>>>>>>>>>DONE !!!>>>>>>>>>>>>>>>>>>")
        return app_url
