# Copyright (C) 2023-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# neuro-san-demos SDK Software in commercial settings.
#
import argparse
import glob
import os
import signal
import subprocess
import sys
import threading
import time

from dotenv import load_dotenv


# pylint: disable=too-many-instance-attributes
class NeuroSanRunner:
    """Command-line tool to run the Neuro SAN server and web client."""

    def __init__(self):
        """Initialize configuration and parse CLI arguments."""
        self.is_windows = os.name == "nt"

        # Load environment variables from .env file
        self.root_dir = os.path.dirname(os.path.abspath(__file__))

        # self.root_dir = os.getcwd()
        print(f"Root directory: {self.root_dir}")
        self.load_env_variables()

        # Default Configuration
        self.manifest_update_period_seconds = int(os.getenv("AGENT_MANIFEST_UPDATE_PERIOD_SECONDS", "5"))
        self.neuro_san_server_host = os.getenv("NEURO_SAN_SERVER_HOST", "localhost")
        self.neuro_san_server_port = int(os.getenv("NEURO_SAN_SERVER_PORT", "30013"))
        self.nsflow_port = int(os.getenv("NSFLOW_PORT", "4173"))
        self.neuro_san_web_client_port = int(os.getenv("NEURO_SAN_WEB_CLIENT_PORT", "5003"))
        thinking_file = "C:\\tmp\\agent_thinking.txt" if self.is_windows else "/tmp/agent_thinking.txt"
        self.thinking_file = os.getenv("THINKING_FILE", thinking_file)
        self.agent_manifest_file = os.getenv(
            "AGENT_MANIFEST_FILE", os.path.join(self.root_dir, "registries", "manifest.hocon")
        )
        self.agent_tool_path = os.getenv("AGENT_TOOL_PATH", os.path.join(self.root_dir, "coded_tools"))

        # Parse command-line arguments
        self.config = self.parse_args()

        # Process references
        self.server_process = None
        self.flask_webclient_process = None
        self.nsflow_process = None

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
        parser = argparse.ArgumentParser(
            description="Run the Neuro SAN server and web client.",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )

        parser.add_argument(
            "--server-host", type=str, default=self.neuro_san_server_host, help="Host address for the Neuro SAN server"
        )
        parser.add_argument(
            "--server-port", type=int, default=self.neuro_san_server_port, help="Port number for the Neuro SAN server"
        )
        parser.add_argument(
            "--nsflow-port",
            type=int,
            default=self.nsflow_port,
            help="Port number for the nsflow client",
        )
        parser.add_argument(
            "--web-client-port",
            type=int,
            default=self.neuro_san_web_client_port,
            help="Port number for the web client",
        )
        parser.add_argument(
            "--thinking-file", type=str, default=self.thinking_file, help="Path to the agent thinking file"
        )
        parser.add_argument("--no-html", action="store_true", help="Don't generate html for network diagrams")
        parser.add_argument(
            "--client-only", action="store_true", help="Run only the nsflow client without NeuroSan server"
        )
        parser.add_argument(
            "--server-only", action="store_true", help="Run only the NeuroSan server without the default nsflow client"
        )
        parser.add_argument(
            "--use-flask-web-client", action="store_true", help="Use the flask based neuro-san-web-client"
        )

        args, _ = parser.parse_known_args()
        explicitly_passed_args = {arg for arg in sys.argv[1:] if arg.startswith("--")}
        # Check for mutually exclusive arguments
        if args.client_only and (
            "--server-host" in explicitly_passed_args or "--server-port" in explicitly_passed_args
        ):
            parser.error("[x] You cannot specify --server-host or --server-port when using --client-only mode.")
        if args.server_only and (
            "--nsflow-host" in explicitly_passed_args or "--nsflow-port" in explicitly_passed_args
        ):
            parser.error("[x] You cannot specify --nsflow-host or --nsflow-port when using --server-only mode.")
        if args.client_only and args.server_only:
            parser.error("[x] You cannot specify both --client-only and --server-only at the same time.")

        return vars(args)

    def set_environment_variables(self):
        """Set required environment variables, optionally using neuro-san defaults."""
        print("\n" + "=" * 50 + "\n")
        print("Setting environment variables...\n")
        # Common env variables
        os.environ["PYTHONPATH"] = self.root_dir
        os.environ["AGENT_MANIFEST_FILE"] = self.agent_manifest_file
        os.environ["AGENT_TOOL_PATH"] = self.agent_tool_path
        os.environ["AGENT_MANIFEST_UPDATE_PERIOD_SECONDS"] = str(self.manifest_update_period_seconds)
        print(f"PYTHONPATH set to: {os.environ['PYTHONPATH']}\n")
        print(f"AGENT_MANIFEST_FILE set to: {os.environ['AGENT_MANIFEST_FILE']}")
        print(f"AGENT_TOOL_PATH set to: {os.environ['AGENT_TOOL_PATH']}\n")
        print(f"AGENT_MANIFEST_UPDATE_PERIOD_SECONDS set to: {os.environ['AGENT_MANIFEST_UPDATE_PERIOD_SECONDS']}\n")

        # Client-only env variables
        if not self.config["server_only"]:
            if self.config["use_flask_web_client"]:
                os.environ["NEURO_SAN_WEB_CLIENT_PORT"] = str(self.config["web_client_port"])
                print(f"NEURO_SAN_WEB_CLIENT_PORT set to: {os.environ['NEURO_SAN_WEB_CLIENT_PORT']}")
            else:
                os.environ["NSFLOW_PORT"] = str(self.config["nsflow_port"])
                print(f"NSFLOW_PORT set to: {os.environ['NSFLOW_PORT']}")
                # Set env variable for using nsflow in client-only mode
                if self.config["client_only"]:
                    os.environ["NSFLOW_CLIENT_ONLY"] = "True"
                    print(f"NSFLOW_CLIENT_ONLY set to: {os.environ['NSFLOW_CLIENT_ONLY']}")

        # Server-only env variables
        if not self.config["client_only"]:
            os.environ["NEURO_SAN_SERVER_HOST"] = self.config["server_host"]
            os.environ["NEURO_SAN_SERVER_PORT"] = str(self.config["server_port"])

            # Adding these two below only because nsflow depends on these variables that are named differently
            # These should be removed when the nsflow client is updated to use consistent environment variable names
            os.environ["NS_SERVER_HOST"] = self.config["server_host"]
            os.environ["NS_SERVER_PORT"] = str(self.config["server_port"])

            print(f"NEURO_SAN_SERVER_HOST set to: {os.environ['NEURO_SAN_SERVER_HOST']}")
            print(f"NEURO_SAN_SERVER_PORT set to: {os.environ['NEURO_SAN_SERVER_PORT']}\n")

        print("\n" + "=" * 50 + "\n")

    @staticmethod
    def generate_html_files():
        """Generate .html files for all registry files except manifest.hocon."""
        for file in glob.glob("./registries/*"):
            if os.path.basename(file) != "manifest.hocon":
                print(f"Generating .html file for: {file}")
                result = subprocess.run(
                    [sys.executable, "-m", "neuro_san_web_client.agents_diagram_builder", "--input_file", file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    check=True,
                )
                print(result.stdout)
                if result.stderr:
                    print(result.stderr, file=sys.stderr)

    @staticmethod
    def stream_output(pipe, log_file, prefix):
        """Stream subprocess output to console and log file in real-time."""
        with open(log_file, "a", encoding="utf-8") as log:
            for line in iter(pipe.readline, ""):
                formatted_line = f"{prefix}: {line.strip()}"
                print(formatted_line)  # Print to console
                log.write(formatted_line + "\n")  # Write to log file
        pipe.close()

    def start_process(self, command, process_name, log_file):
        """Start a subprocess and capture logs."""
        creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP if self.is_windows else 0

        # Initialize/clear the log file before starting
        with open(log_file, "w", encoding="utf-8") as log:
            log.write(f"Starting {process_name}...\n")

        # pylint: disable=consider-using-with
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
            start_new_session=not self.is_windows,
            creationflags=creation_flags,
        )

        print(f"Started {process_name} with PID {process.pid}")

        # Start streaming logs in separate threads
        stdout_thread = threading.Thread(target=self.stream_output, args=(process.stdout, log_file, process_name))
        stderr_thread = threading.Thread(target=self.stream_output, args=(process.stderr, log_file, process_name))
        stdout_thread.start()
        stderr_thread.start()

        return process

    def start_neuro_san(self):
        """Start the Neuro SAN server."""
        print("Starting Neuro SAN server...")
        command = [
            sys.executable,
            "-u",
            "-m",
            "neuro_san.service.agent_main_loop",
            "--port",
            str(self.config["server_port"]),
        ]
        self.server_process = self.start_process(command, "NeuroSan", "logs/server.log")
        print("NeuroSan server started on port: ", self.config["server_port"])

    def start_nsflow(self):
        """Start nsflow client."""
        print("Starting nsflow slient...")
        command = [
            sys.executable,
            "-u",
            "-m",
            "uvicorn",
            "nsflow.backend.main:app",
            "--port",
            str(self.config["nsflow_port"]),
            "--reload",
        ]

        self.nsflow_process = self.start_process(command, "nsflow", "logs/nsflow.log")
        print("nsflow client started on port: ", self.config["nsflow_port"])

    def start_flask_web_client(self):
        """Start the Flask web client."""
        print("Starting Flask web client...")
        command = [
            sys.executable,
            "-u",
            "-m",
            "neuro_san_web_client.app",
            "--server-host",
            self.config["server_host"],
            "--server-port",
            str(self.config["server_port"]),
            "--web-client-port",
            str(self.config["web_client_port"]),
            "--thinking-file",
            self.config["thinking_file"],
        ]
        self.flask_webclient_process = self.start_process(command, "FlaskWebClient", "logs/webclient.log")
        print("Flask web client started on port: ", self.config["web_client_port"])

    # pylint: disable=unused-argument
    def signal_handler(self, signum, frame):
        """Handle termination signals to cleanly exit."""
        print("\nTermination signal received. Stopping all processes...")

        if self.server_process:
            print(f"\nStopping SERVER (PID {self.server_process.pid})...")
            if self.is_windows:
                self.server_process.terminate()
            else:
                os.killpg(os.getpgid(self.server_process.pid), signal.SIGKILL)

        if self.flask_webclient_process:
            print(f"Stopping WEB CLIENT (PID {self.flask_webclient_process.pid})...")
            if self.is_windows:
                self.flask_webclient_process.terminate()
            else:
                os.killpg(os.getpgid(self.flask_webclient_process.pid), signal.SIGKILL)

        if self.nsflow_process:
            print(f"Stopping NSFLOW (PID {self.nsflow_process.pid})...")
            if self.is_windows:
                self.nsflow_process.terminate()
            else:
                os.killpg(os.getpgid(self.nsflow_process.pid), signal.SIGKILL)

        sys.exit(0)

    def run(self):
        """Run the Neuro SAN server and a client."""
        print("\nRun Config:\n" + "\n".join(f"{key}: {value}" for key, value in self.config.items()) + "\n")

        # Set environment variables
        self.set_environment_variables()

        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)

        # Set up signal handling for termination
        signal.signal(signal.SIGINT, self.signal_handler)  # Handle Ctrl+C
        if not self.is_windows:
            signal.signal(signal.SIGTERM, self.signal_handler)  # Handle kill command (not available on Windows)

        # Handle mutually exclusive modes
        client_only = self.config["client_only"]
        server_only = self.config["server_only"]

        if client_only and server_only:
            print("[x] You cannot specify both --client-only and --server-only at the same time.")
            sys.exit(1)

        if not server_only:
            if self.config["use_flask_web_client"]:
                # Generate HTML files unless asked not to
                if not self.config["no_html"]:
                    self.generate_html_files()
                self.start_flask_web_client()
            else:
                self.start_nsflow()

        if not client_only:
            self.start_neuro_san()
            time.sleep(3)  # Give the server some time to start

        print("\n" + "=" * 50 + "\n")
        print("All processes now running.")
        print("Press Ctrl+C to stop the server.")
        print("\n" + "=" * 50 + "\n")

        # Wait on active processes to finish
        if self.nsflow_process:
            self.nsflow_process.wait()
        if self.server_process:
            self.server_process.wait()
        if self.flask_webclient_process:
            self.flask_webclient_process.wait()


if __name__ == "__main__":
    runner = NeuroSanRunner()
    runner.run()
