
# Copyright (C) 2023-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# neuro-san-studio SDK Software in commercial settings.
#
# END COPYRIGHT

import logging
from typing import Any

from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from openai import OpenAIError

from neuro_san.interfaces.coded_tool import CodedTool

DEFAULT_OPENAI_MODEL = "gpt-4o-2024-08-06"


class OpenaiTool(CodedTool):
    """
    A CodedTool implementation for invoking OpenAI built-in tools using LangChain's ChatOpenAI.

    Supported tools include (but are not limited to):
        - "code_interpreter"
        - "web_search_preview"
        - "file_search"
        - "image_generation"
        - "mcp"

    Only "code_interpreter" and "web_search_preview" have been tested.

    See: https://platform.openai.com/docs/guides/tools?api-mode=responses
    """

    async def async_invoke(self, args: dict[str, Any], sly_data: dict[str, Any]) -> list[dict[str, Any]] | str:
        """
        :param args: An argument dictionary whose keys are the parameters
                to the coded tool and whose values are the values passed for them
                by the calling agent.  This dictionary is to be treated as read-only.

                The argument dictionary expects the following keys:
                    "query"

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
                A list of dictionary of search results
            otherwise:
                a text string an error message in the format:
                "Error: <error message>"
        """

        # Get query from args
        query: str = args.get("query")
        if not query:
            return "Error: No query provided."

        # User-defined arguments

        # # The name of the built-in OpenAI tool to invoke (Required).
        builtin_tool: str = args.get("builtin_tool")
        if not builtin_tool:
            return "Error: No builtin tool specified."

        # The OpenAI model to use when calling the tool.
        # Defaults to "gpt-4o-2024-08-06" if not provided.
        openai_model: str = args.get("openai_model", DEFAULT_OPENAI_MODEL)

        # Additional keyword arguments to pass to the selected tool.
        # Tool-specific requirements:
        #   - "web_search_preview": no additional kwargs needed.
        #   - "code_interpreter": requires "container" to be set.
        # Refer to:
        # https://python.langchain.com/docs/integrations/chat/openai/#code-interpreter
        additional_kwarg: dict[str, Any] = args.get("additional_kwarg", {})

        logger = logging.getLogger(self.__class__.__name__)
        logger.info(">>>>>>>>>> Invoking OpenAI Tool <<<<<<<<<<")
        logger.info("Query: %s", query)
        logger.info("OpenAI Model: %s", openai_model)
        logger.info("Built-in Tool: %s", builtin_tool)
        logger.info("Additional Keyword Arguments: %s", additional_kwarg)

        try:
            # Instantiate the chat model using specified model.
            # The "output_version" key format output from built-in tool invocations into
            # the message’s content field, rather than additional_kwargs.
            openai_llm = ChatOpenAI(model=openai_model, output_version="responses/v1")
            tool: dict[str, Any] = {"type": builtin_tool} | additional_kwarg

            # Invoke with the provided query and tool, "tool_choice" is set to "required" to force the model to use tool.
            result: AIMessage = await openai_llm.ainvoke(query, tools=[tool], tool_choice="required")
            content: list[dict[str, Any]] = result.content
            logger.info("Result from OpenAI Tool: %s", content)
            return content

        except OpenAIError as openai_error:
            logger.error("OpenAI Error: %s", openai_error)
            return f"OpenAI Error: {openai_error}"
