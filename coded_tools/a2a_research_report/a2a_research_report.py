"""Example of how to use coded tool from a2a server"""

# Copyright (C) 2023-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# neuro-san SDK Software in commercial settings.
#
# END COPYRIGHT

from typing import Any
from typing import Dict

from a2a.client import A2AClient
import httpx
from uuid import uuid4

from neuro_san.interfaces.coded_tool import CodedTool


class A2aResearchReport(CodedTool):
    """
    CodedTool implementation which calculate BMI using a tool from mcp server
    """

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> str:
        """
        Calculate BMI.

        :param args: Dictionary containing 'weight' and 'height'.
        :param sly_data: A dictionary whose keys are defined by the agent
            hierarchy, but whose values are meant to be kept out of the
            chat stream.

            This dictionary is largely to be treated as read-only.
            It is possible to add key/value pairs to this dict that do not
            yet exist as a bulletin board, as long as the responsibility
            for which coded_tool publishes new entries is well understood
            by the agent chain implementation and the coded_tool implementation
            adding the data is not invoke()-ed more than once.

            Keys expected for this implementation are:
                None
        :return: BMI or error message
        """
        # Extract arguments from the input dictionary
        topic: str = args.get("topic")

        if not topic:
            return "Error: No weight provided."

        # Adjust the timeout according to how long you expect the server needs to run
        # before return the response.
        async with httpx.AsyncClient(timeout=60.0) as httpx_client:
            client = await A2AClient.get_client_from_agent_card_url(
                httpx_client, 'http://localhost:9999'
            )
            send_message_payload: dict[str, Any] = {
                "message": {
                    "role": "user",
                    "parts": [
                        {"type": "text", 'text': f"{topic}"}
                    ],
                    "messageId": uuid4().hex,
                },
            }

            response = await client.send_message(payload=send_message_payload)
            result: Dict[str, Any] = response.model_dump(exclude_none=True)
            return result["result"]["parts"][-1]["text"]

        # neuro-san uses langchain-mcp-adapter to create mcp client
        # In this example, there is only 1 server at localhost:8000
        # however, client can be connected to multiple servers,
        # and a server can also have multiple tools.
        # Note that mcp server can contain tools, resources, and prompts
        # but langchain-mcp-adapter only works with **tools**.
        # async with MultiServerMCPClient(
        #     {
        #         # This key only used as a reference here and may be different
        #         # from the actual name in mcp server.
        #         "bmi": {
        #             # sse is prefered over stdio as transport method.
        #             # make sure the port here matches the one in  your server.
        #             "url": "http://localhost:8000/sse",
        #             "transport": "sse",
        #         }
        #     }
        # ) as client:
        #     # `get_tools` method returns a list of StructuredTool ordered by
        #     # server and tool's order in the server, respectively.
        #     # Note that to `invoke` or `ainvoke` for StructureTool require
        #     # dictionary input.
        #     return await client.get_tools()[0].ainvoke({"weight": weight, "height": height})
