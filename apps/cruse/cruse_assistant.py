import os

from pyhocon import ConfigFactory

from neuro_san.client.agent_session_factory import AgentSessionFactory
from neuro_san.client.streaming_input_processor import StreamingInputProcessor

AGENT_NETWORK_NAME = "cruse_agent"


def set_up_cruse_assistant(selected_agent):
    """Configure these as needed."""
    agent_name = AGENT_NETWORK_NAME
    connection = "direct"
    host = "localhost"
    port = 30011
    local_externals_direct = False
    metadata = {"user_id": os.environ.get("USER")}

    # Create session factory and agent session
    factory = AgentSessionFactory()
    session = factory.create_session(connection, agent_name, host, port, local_externals_direct, metadata)
    sly_data = {"selected_agent": selected_agent, "agent_session": session}

    # Initialize any conversation state here
    cruse_thread = {
        "last_chat_response": None,
        "prompt": "Please enter your response ('quit' to terminate):\n",
        "timeout": 5000.0,
        "num_input": 0,
        "user_input": None,
        "sly_data": sly_data,
        "chat_filter": {"chat_filter_type": "MAXIMAL"},
    }
    return session, cruse_thread


def cruse(cruse_session, cruse_thread, user_input):
    """
    Processes a single turn of user input within the cruse agent's session.

    This function simulates a conversational turn by:
    1. Initializing a StreamingInputProcessor to handle the input.
    2. Updating the agent's internal thread state with the user's input (`thoughts`).
    3. Passing the updated thread to the processor for handling.
    4. Extracting and returning the agent's response for this turn.

    Parameters:
        cruse_session: An active session object for the cruse agent.
        cruse_thread (dict): The agent's current conversation thread state.
        user_input (str): The user's input or query to be processed.

    Returns:
        tuple:
            - last_chat_response (str or None): The agent's response to the input.
            - cruse_thread (dict): The updated thread state after processing.
    """
    # Use the processor (like in agent_cli.py)
    input_processor = StreamingInputProcessor(
        "DEFAULT",
        "/tmp/agent_thinking.txt",  # Or wherever you want
        cruse_session,
        None,  # Not using a thinking_dir for simplicity
    )
    # Update the conversation state with this turn's input
    cruse_thread["user_input"] = user_input
    cruse_thread = input_processor.process_once(cruse_thread)
    # Get the agent response for this turn
    last_chat_response = cruse_thread.get("last_chat_response")
    return last_chat_response, cruse_thread


def tear_down_cruse_assistant(cruse_session):
    """Tear down the assistant.

    :param cruse_session: The pointer to the session.
    """
    print("tearing down cruse assistant...")
    cruse_session.close()
    # client.assistants.delete(cruse_assistant_id)
    print("cruse assistant torn down.")

def get_available_systems():
    config = ConfigFactory.parse_file(os.environ["AGENT_MANIFEST_FILE"])
    return [key for key, enabled in config.items() if enabled]

