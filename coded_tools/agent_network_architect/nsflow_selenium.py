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

import asyncio
import time
from typing import Any
from typing import Dict

from neuro_san.interfaces.coded_tool import CodedTool
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

TIME_TO_FIND_ELEMENT = 120.0
TIME_BEFORE_CLICK_SEND = 2.0
TIME_AFTER_RESPONSE_BEFORE_CLOSE = 10.0


class NsflowSelenium(CodedTool):
    """
    CodedTool implementation which opens nsflow in Chrome, enters text input,
    submits the input, waits for the response, and closes the browser.
    """

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> str:
        """
        :param args: An argument dictionary whose keys are the parameters
            to the coded tool and whose values are the values passed for
            them by the calling agent.  This dictionary is to be treated as
            read-only.

            The argument dictionary expects the following keys:
                "agent_name"

        :param sly_data: A dictionary whose keys are defined by the agent
            hierarchy, but whose values are meant to be kept out of the
            chat stream.

            This dictionary is largely to be treated as read-only.
            It is possible to add key/value pairs to this dict that do not
            yet exist as a bulletin board, as long as the responsibility
            for which coded_tool publishes new entries is well understood
            by the agent chain implementation and the coded_tool
            implementation adding the data is not invoke()-ed more than
            once.

            Keys expected for this implementation are:
                None
        :return: successful sent message ID or error message
        """

        # Extract arguments from the input dictionary

        # Required arguments
        agent_name: str = args.get("agent_name")
        query: str = args.get("query")
        url: str = args.get("url")

        # Validate presence of required inputs
        if not agent_name:
            return "Error: No agent_name provided."
        if not query:
            return "Error: No query provided."
        if not url:
            return "Error: No url provided"

        # Optional arguments
        time_to_find_element: float = args.get("time_to_find_element", TIME_TO_FIND_ELEMENT)
        time_before_click_send: float = args.get("time_before_click_send", TIME_BEFORE_CLICK_SEND)
        time_after_response_before_close: float = args.get("time_after_response_before_close", TIME_AFTER_RESPONSE_BEFORE_CLOSE)

        # Optional: set up headless Chrome
        options = Options()
        options.add_argument("--start-maximized")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        try:
            driver.get(url)

            wait = WebDriverWait(driver, time_to_find_element)

            # Wait and click the sidebar button with text {agent_name}
            button = wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//button[contains(@class, 'sidebar-btn') and text()='{agent_name}']"))
            )
            button.click()

            # Type a message into the chat input
            chat_input = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "chat-input-box")))
            chat_input.click()
            chat_input.clear()
            chat_input.send_keys(query)

            # Wait before clicking send
            time.sleep(time_before_click_send)

            # Click the Send button
            send_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "chat-send-btn")))
            send_button.click()

            # Wait for the response box (<span>{agent_name}</span>) to appear
            wait.until(
                EC.presence_of_element_located((By.XPATH, f"//div[contains(@class, 'font-bold')]/span[text()='{agent_name}']"))
            )
            # Find all texts in the text boxes
            # The agent responses should be the last one
            elements = driver.find_elements(By.CSS_SELECTOR, "div.chat-markdown > p")
            response = elements[-1].text if elements else "No agent response found"

            print(f"Agent response: {response}")
            print(f"Agent {agent_name} response detected, waiting {time_after_response_before_close} seconds before closing the browser.")

            time.sleep(time_after_response_before_close)

            return f"Query: {query}\nResponse: {response}"

        except TimeoutException as timeout_error:
            timeout_error_msg = "Timed out waiting for page to load or element to appear."
            print(f"{timeout_error_msg}")
            print(timeout_error)
            return timeout_error_msg
        except WebDriverException as webdriver_error:
            webdriver_error_msg = "WebDriver encountered an issue."
            print(f"{webdriver_error_msg}")
            print(webdriver_error)
            return webdriver_error_msg

        finally:
            # Close browser after finish testing
            driver.quit()

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> str:
        """Run invoke asynchronously."""
        return await asyncio.to_thread(self.invoke, args, sly_data)
