# Copyright (C) 2023-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# neuro-san-demos SDK Software in commercial settings.
#
import os
import subprocess
import signal
import glob
import sys
import argparse
import threading
from dotenv import load_dotenv

class NeuroSanRunner:
    """Command-line tool to run the Neuro SAN server and web client."""

    def __init__(self):
        """Initialize configuration and parse CLI arguments."""
        self.is_windows = os.name == "nt"

        # Load environment variables from .env file
        self.root_dir = os.getcwd()
        print(f"Root directory: {self.root_dir}")
        self.load_env_variables()

        # Default Configuration
        self.neuro_san_server_host = os.getenv("NEURO_SAN_SERVER_HOST", "localhost")
        self.neuro_san_server_port = int(os.getenv("NEURO_SAN_SERVER_PORT", 30013))
        self.neuro_san_web_client_port = int(os.getenv("NEURO_SAN_WEB_CLIENT_PORT", 5003))
        thinking_file = "C:\\tmp\\agent_thinking.txt" if self.is_windows else "/tmp/agent_thinking.txt"
        self.thinking_file = os.getenv("THINKING_FILE", thinking_file)

        # Parse command-line arguments
        self.config = self.parse_args()

        # Process references
        self.server_process = None
        self.app_process = None

        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)

    def load_env_variables(self):
        """Load .env file from project root and set variables."""
        env_path = os.path.join(self.root_dir, ".env")
        if os.path.exists(env_path):
            load_dotenv(env_path)
            print(f"Loaded environment variables from: {env_path}")
        else:
            print(f"No .env file found at {env_path}. \nUsing defaults.\n")

    def parse_args(self):
        """Parses command-line arguments for configuration."""
        parser = argparse.ArgumentParser(description="Run the Neuro SAN server and web client.")

        parser.add_argument('--server-host', type=str, default=self.neuro_san_server_host, help="Host address for the Neuro SAN server")
        parser.add_argument('--server-port', type=int, default=self.neuro_san_server_port, help="Port number for the Neuro SAN server")
        parser.add_argument('--web-client-port', type=int, default=self.neuro_san_web_client_port, help="Port number for the web client")
        parser.add_argument('--thinking-file', type=str, default=self.thinking_file, help="Path to the agent thinking file")
        parser.add_argument('--no-html', action='store_true', help="Don't generate html for network diagrams")

        return vars(parser.parse_args())

    @staticmethod
    def set_environment_variables():
        """Set required environment variables, optionally using neuro-san defaults."""
        os.environ["PYTHONPATH"] = os.getcwd()
        os.environ["AGENT_MANIFEST_FILE"] = "./registries/manifest.hocon"
        os.environ["AGENT_TOOL_PATH"] = "./coded_tools"

        print(f"PYTHONPATH set to: {os.environ['PYTHONPATH']}\n")
        print(f"AGENT_MANIFEST_FILE set to: {os.environ['AGENT_MANIFEST_FILE']}")
        print(f"AGENT_TOOL_PATH set to: {os.environ['AGENT_TOOL_PATH']}\n")

    @staticmethod
    def generate_html_files():
        """Generate .html files for all registry files except manifest.hocon."""
        for file in glob.glob("./registries/*"):
            if os.path.basename(file) != "manifest.hocon":
                print(f"Generating .html file for: {file}")
                result = subprocess.run(
                    [sys.executable, "-m", "neuro_san_web_client.agents_diagram_builder", "--input_file", file],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
                )
                print(result.stdout)
                if result.stderr:
                    print(result.stderr, file=sys.stderr)

    @staticmethod
    def stream_output(pipe, log_file, prefix):
        """Stream subprocess output to console and log file in real-time."""
        with open(log_file, "a") as log:
            for line in iter(pipe.readline, ''):
                formatted_line = f"{prefix}: {line.strip()}"
                print(formatted_line)  # Print to console
                log.write(formatted_line + "\n")  # Write to log file
        pipe.close()

    def start_process(self, command, process_name, log_file):
        """Start a subprocess and capture logs."""
        creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP if self.is_windows else 0

        with open(log_file, "w") as log:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       text=True, bufsize=1, universal_newlines=True,
                                       preexec_fn=None if self.is_windows else os.setpgrp,
                                       creationflags=creation_flags)

        print(f"Started {process_name} with PID {process.pid}")

        # Start streaming logs in separate threads
        stdout_thread = threading.Thread(target=self.stream_output, args=(process.stdout, log_file, process_name))
        stderr_thread = threading.Thread(target=self.stream_output, args=(process.stderr, log_file, process_name))
        stdout_thread.start()
        stderr_thread.start()

        return process

    def signal_handler(self, signum, frame):
        """Handle termination signals to cleanly exit."""
        print("\nTermination signal received. Stopping all processes...")

        if self.server_process:
            print(f"\nStopping SERVER (PID {self.server_process.pid})...")
            if self.is_windows:
                self.server_process.terminate()
            else:
                os.killpg(os.getpgid(self.server_process.pid), signal.SIGKILL)

        if self.app_process:
            print(f"Stopping WEB CLIENT (PID {self.app_process.pid})...")
            if self.is_windows:
                self.app_process.terminate()
            else:
                os.killpg(os.getpgid(self.app_process.pid), signal.SIGKILL)

        sys.exit(0)

    def run(self):
        """Run the Neuro SAN server and web client."""
        print("\nRun Config:\n" + "\n".join(f"{key}: {value}" for key, value in self.config.items()) + "\n")

        # Set environment variables
        self.set_environment_variables()

        # Generate HTML files unless asked not to
        if not self.config["no_html"]:
            self.generate_html_files()

        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)

        # Set up signal handling for termination
        signal.signal(signal.SIGINT, self.signal_handler)  # Handle Ctrl+C
        if not self.is_windows:
            signal.signal(signal.SIGTERM, self.signal_handler)  # Handle kill command (not available on Windows)

        # Start server (Log to logs/server.log)
        server_command = [
            sys.executable, "-u", "-m", "neuro_san.service.agent_main_loop",
            "--port", str(self.config["server_port"])
        ]
        self.server_process = self.start_process(server_command, "SERVER", "logs/server.log")

        # Start web client (Log to logs/client.log)
        client_command = [
            sys.executable, "-u", "-m", "neuro_san_web_client.app",
            "--server-host", self.config["server_host"],
            "--server-port", str(self.config["server_port"]),
            "--web-client-port", str(self.config["web_client_port"]),
            "--thinking-file", self.config["thinking_file"]
        ]
        self.app_process = self.start_process(client_command, "WEB CLIENT", "logs/client.log")

        # Wait for both processes to finish
        self.server_process.wait()
        self.app_process.wait()


if __name__ == "__main__":
    runner = NeuroSanRunner()
    runner.run()
