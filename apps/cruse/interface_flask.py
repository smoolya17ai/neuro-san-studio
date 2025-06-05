import atexit
import os
import queue
import re
import time

# pylint: disable=import-error
import cv2
import schedule
from flask import Flask
from flask import render_template
from flask_socketio import SocketIO

from apps.cruse.cruse_assistant import cruse
from apps.cruse.cruse_assistant import set_up_cruse_assistant
from apps.cruse.cruse_assistant import tear_down_cruse_assistant

os.environ["AGENT_MANIFEST_FILE"] = "registries/manifest.hocon"
os.environ["AGENT_TOOL_PATH"] = "coded_tools"
app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)
thread_started = False  # pylint: disable=invalid-name

user_input_queue = queue.Queue()
gui_context_queue = queue.Queue()

cruse_session, cruse_thread = set_up_cruse_assistant()


def cruse_thinking_process():
    """Main permanent agent-calling loop."""
    with app.app_context():
        global cruse_thread
        user_input = ""

        while True:
            socketio.sleep(1)
            if user_input:
                try:
                    gui_context = gui_context_queue.get_nowait()
                except queue.Empty:
                    gui_context = ""

                response, cruse_thread = cruse(cruse_session, cruse_thread, user_input + gui_context)
                print(response)

                gui_to_emit = []
                speeches_to_emit = []

                pattern = re.compile(
                    r"(?m)^(gui|say):[ \t]*(.*?)(?=^\s*(?:gui|say):|\Z)", re.S
                )

                for kind, raw in pattern.findall(response):
                    content = raw.lstrip()
                    if not content:
                        continue
                    if kind == "gui":
                        gui_to_emit.append(f"gui: {content}")
                    else:
                        speeches_to_emit.append(content)

                if gui_to_emit:
                    socketio.emit("update_gui", {"data": "\n".join(gui_to_emit)}, namespace="/chat")

                if speeches_to_emit:
                    socketio.emit("update_speech", {"data": "\n".join(speeches_to_emit)}, namespace="/chat")

            try:
                user_input = user_input_queue.get_nowait()
                if user_input == "exit":
                    break
            except queue.Empty:
                user_input = ""
                time.sleep(0.1)
                continue


@socketio.on("connect", namespace="/chat")
def on_connect():
    """Start background task on connect."""
    global thread_started  # pylint: disable=global-statement
    if not thread_started:
        thread_started = True
        # let socketio manage the green-thread
        socketio.start_background_task(cruse_thinking_process)


@app.route("/")
def index():
    """Return the html."""
    return render_template("index.html")


@socketio.on("user_input", namespace="/chat")
def handle_user_input(json, *_):
    """
    Handles user input.

    :param json: A json object
    """
    user_input = json["data"]
    user_input_queue.put(user_input)
    socketio.emit("update_user_input", {"data": user_input}, namespace="/chat")


def cleanup():
    """Tear things down on exit."""
    print("Bye!")
    tear_down_cruse_assistant(cruse_session)
    socketio.stop()


@app.route("/shutdown")
def shutdown():
    """Shut down process."""
    cleanup()
    cv2.destroyAllWindows()
    return "Capture ended"


@app.after_request
def add_header(response):
    """Add the header."""
    response.headers["Cache-Control"] = "no-store"
    return response


def run_scheduled_tasks():
    """Run the scheduled tasks."""
    while True:
        schedule.run_pending()
        time.sleep(1)


# Register the cleanup function
atexit.register(cleanup)

if __name__ == "__main__":
    socketio.run(app, debug=False, port=5001, allow_unsafe_werkzeug=True, log_output=True, use_reloader=False)
