import os
import logging
from typing import Any
from typing import Dict
from typing import Union

from neuro_san.client.agent_session_factory import AgentSessionFactory
from neuro_san.client.streaming_input_processor import StreamingInputProcessor
from neuro_san.interfaces.coded_tool import CodedTool

CONNECTION_TYPE = "direct"
HOST = "localhost"
PORT = 30011


class CallAgent(CodedTool):
    """
    CodedTool implementation which provides a way to utilize different websites' search feature
    """

    def __init__(self):
        self.top_n = 5

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
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
                by the agent chain implementation, and the coded_tool implementation
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
        inquiry: str = args.get("inquiry", "")
        if inquiry == "":
            return "Error: No inquiry provided."
        mode: str = args.get("mode", "")
        if mode == "":
            return "Error: No mode provided."
        agent_name: str = sly_data.get("selected_agent", "")
        if agent_name == "":
            return "Error: No select_agent in sly_data."

        print(f"inquiry: {inquiry}")
        print(f"mode: {mode}")
        print(f"agent_name: {agent_name}")

        logger = logging.getLogger(self.__class__.__name__)
        logger.info(">>>>>>>>>>>>>>>>>>>CallAgent>>>>>>>>>>>>>>>>>>")
        logger.info("inquiry: %s", str(inquiry))
        logger.info("mode: %s", str(mode))
        logger.info("agent_name: %s", str(agent_name))

        agent_session = sly_data.get("agent_session", None)
        agent_thread = sly_data.get("agent_thread", None)
        if not agent_thread or not agent_session:
            agent_session, agent_thread = set_up_agent(agent_name)
        response, agent_thread = call_agent(agent_session, agent_thread, inquiry + mode)
        sly_data["agent_session"] = agent_session
        sly_data["agent_thread"] = agent_thread

        logger.info(">>>>>>>>>>>>>>>>>>>DONE !!!>>>>>>>>>>>>>>>>>>")
        return response

def set_up_agent(agent_name):
    """Configure these as needed."""
    connection = CONNECTION_TYPE
    host = HOST
    port = PORT
    local_externals_direct = False
    metadata = {"user_id": os.environ.get("USER")}

    # Create session factory and agent session
    factory = AgentSessionFactory()
    agent_session = factory.create_session(connection, agent_name, host, port, local_externals_direct, metadata)
    # Initialize any conversation state here
    agent_thread = {
        "last_chat_response": None,
        "prompt": "Please enter your response ('quit' to terminate):\n",
        "timeout": 5000.0,
        "num_input": 0,
        "user_input": None,
        "sly_data": None,
        "chat_filter": {"chat_filter_type": "MAXIMAL"},
    }
    return agent_session, agent_thread

def call_agent(agent_session, agent_thread, user_input):
    """
    Processes a single turn of user input within the selected agent's session.

    This function simulates a conversational turn by:
    1. Initializing a StreamingInputProcessor to handle the input.
    2. Updating the agent's internal thread state with the user's input (`thoughts`).
    3. Passing the updated thread to the processor for handling.
    4. Extracting and returning the agent's response for this turn.

    Parameters:
        agent_session: An active session object for the selected agent.
        agent_thread (dict): The agent's current conversation thread state.
        user_input (str): The user's input or query to be processed.

    Returns:
        tuple:
            - last_chat_response (str or None): The agent's response to the input.
            - agent_thread (dict): The updated thread state after processing.
    """
    # Use the processor (like in agent_cli.py)
    input_processor = StreamingInputProcessor(
        "DEFAULT",
        "/tmp/agent_thinking.txt",  # Or wherever you want
        agent_session,
        None,  # Not using a thinking_dir for simplicity
    )
    # Update the conversation state with this turn's input
    agent_thread["user_input"] = user_input
    agent_thread = input_processor.process_once(agent_thread)
    # Get the agent response for this turn
    last_chat_response = agent_thread.get("last_chat_response")
    return last_chat_response, agent_thread
