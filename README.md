<h2 align="center">Neuro SAN Studio</h2>
<p align="center">
  A playground for <a href="https://github.com/leaf-ai/neuro-san">Neuro SAN</a> — a customizable Multi-Agent Orchestration Framework.
  <br>
  <strong>Quickstart Friendly:</strong> This repo includes working examples to get started with <strong>Neuro SAN</strong>.<br>
  Explore, extend, and experiment with custom multi-agent networks!
</p>

---

<p align="center">
  Neuro SAN is the open-source library powering the Cognizant Neuro® AI Multi-Agent Accelerator, allowing domain experts, researchers and developers to immediately start prototyping and building agent networks across any industry vertical to transform their business operations with AI.
</p>

---

<p align="center">
  <!-- GitHub Stats -->
  <img src="https://img.shields.io/github/stars/leaf-ai/neuro-san?style=social" alt="GitHub stars">
  <img src="https://img.shields.io/github/forks/leaf-ai/neuro-san-studio?style=social" alt="GitHub forks">
  <img src="https://img.shields.io/github/watchers/leaf-ai/neuro-san-studio?style=social" alt="GitHub watchers">
</p>
<p align="center">
  <!-- Github Info -->
  <img src="https://img.shields.io/github/last-commit/leaf-ai/neuro-san-studio" alt="Last Commit">
  <img src="https://img.shields.io/github/issues/leaf-ai/neuro-san-studio" alt="Issues">
  <img src="https://img.shields.io/github/issues-pr/leaf-ai/neuro-san-studio" alt="Pull Requests">
  <img src="https://img.shields.io/github/commit-activity/m/leaf-ai/neuro-san" alt="commit activity">
</p>

<p align="center">
  <!-- Pypi Stats -->
  <a href="https://github.com/leaf-ai/neuro-san"><img alt="GitHub Repo" src="https://img.shields.io/badge/GitHub-Repo-green.svg" /></a>
  <a href="https://pepy.tech/projects/neuro-san"><img alt="PyPI Downloads" src="https://static.pepy.tech/badge/neuro-san" /></a>
  <a href="https://pypi.org/project/neuro-san/"><img alt="neuro-san@PyPI" src="https://img.shields.io/pypi/v/neuro-san.svg?style=flat-square"></a>
</p>


## What is Neuro SAN?

[**Neuro SAN (System of Agent Networks)**](https://github.com/leaf-ai/neuro-san) is an open-source, data-driven multi-agent orchestration framework designed to simplify and accelerate the development of collaborative AI systems. It allows users—from machine learning engineers to business domain experts—to quickly build sophisticated multi-agent applications without extensive coding, using declarative configuration files (in HOCON format).

Neuro SAN enables multiple large language model (LLM)-powered agents to collaboratively solve complex tasks, dynamically delegating subtasks through adaptive inter-agent communication protocols. This approach addresses the limitations inherent to single-agent systems, where no single model has all the expertise or context necessary for multifaceted problems.

---

### Key Features

* **Data-Driven Configuration**: Entire agent networks are defined declaratively via simple HOCON files, empowering technical and non-technical stakeholders to design agent interactions intuitively.
* **Adaptive Communication (AAOSA Protocol)**: Agents autonomously determine how to delegate tasks, making interactions fluid and dynamic with decentralized decison making.
* **Sly-Data (Protected Data Channels)**: Facilitates safe handling and transfer of sensitive data between agents without exposing it directly to any language models.
* **Dynamic Agent Network Creation**: Includes a meta-agent called the Agent Network Designer – essentially, an agent that creates other agent networks. Provided as an example with Neuro SAN, it can take a high-level description of a use-case as input and generate a new custom agent network for it.
* **Flexible Tool Integration**: Integrate custom Python-based "coded tools," APIs, databases, and even external agent ecosystems (Agentforce, Agentspace, CrewAI agents, langchain tools and more) seamlessly into your agent workflows.
* **Robust Traceability**: Detailed logging, tracing, and session-level metrics enhance transparency, debugging, and operational monitoring.
* **Extensible and Cloud-Agnostic**: Compatible with a wide variety of LLM providers (OpenAI, Anthropic, Azure, Ollama, etc.) and deployable in diverse environments (local machines, containers, or cloud infrastructures).

---

### Use Cases:

* **Customer Support Automation**: Specialized agents answering FAQs, troubleshooting, and escalating complex issues dynamically.
* **Business Intelligence & Analytics**: Agents collaboratively pulling data, generating insights, and producing analytical reports securely.
* **Intelligent Workflow Management**: Coordinating multi-step workflows involving multiple expert agents and automated tool calls.


---

## Getting Started:

To dive into Neuro SAN and start building your own multi-agent networks, this repository contains a collection of demos for the [neuro-san library](https://github.com/leaf-ai/neuro-san).

You'll find comprehensive documentation, example agent networks, and tutorials to guide you through your first steps.

---

### Installation

Clone the repo:

```bash
git clone https://github.com/leaf-ai/neuro-san-demos
```

Go to dir:

```bash
cd neuro-san-demos
```

Ensure you have a supported version of python (3.12 at this time):

```bash
python --version
```

Create a dedicated Python virtual environment:

```bash
python -m venv venv
```

Source it:

- For Windows:

  ```bash
  .\venv\Scripts\activate && export PYTHONPATH=`pwd`
  ```

- For Mac:

  ```bash
  source venv/bin/activate && export PYTHONPATH=`pwd`
  ```

Install the requirements:

```bash
pip install -r requirements.txt
```

**IMPORTANT**: By default the server relies on OpenAI's `gpt-4o` model. Set the OpenAI API key, and add it to your shell configuration so it's available in future sessions.

You can get your OpenAI API key from <https://platform.openai.com/signup>. After signing up, create a new API key in the API keys section in your profile.

**NOTE**: Replace `XXX` with your actual OpenAI API key.  
**NOTE**: This is OS dependent.

- For macOS and Linux:

  ```bash
  export OPENAI_API_KEY="XXX" && echo 'export OPENAI_API_KEY="XXX"' >> ~/.zshrc
  ```

- For Windows:
  - On Command Prompt:

    ```bash
    set OPENAI_API_KEY=XXX
    ```

  - On PowerShell:

    ```bash
    $env:OPENAI_API_KEY="XXX"
    ```

Other providers and models are supported too but will require proper setup.

---

### Run

There are multiple ways in which we can now use the neuro-san server with a client:

#### Option 1: Using [`nsflow`](https://github.com/leaf-ai/nsflow) as a developer-oriented web client

If you want to use neuro-san with a FastAPI-based developer-oriented client, follow these steps:

- Start the server and client with a single command, from project root:

  ```bash
  python -m run
  ```

- As a default
  - Frontend will be available at: `http://127.0.0.1:4173`
  - The client and server logs will be saved to `logs/nsflow.log` and `logs/server.log` respectively.

- To see the various config options for this app, on terminal

  ```bash
  python -m run --help
  ```

Screenshot:

![NSFlow UI Snapshot](https://raw.githubusercontent.com/leaf-ai/nsflow/main/docs/snapshot01.png)

---

#### Option 2: Using a basic web client interface

A [basic web client interface](https://github.com/leaf-ai/neuro-san-web-client) is installed by default.
It's a great, simple example of how to connect to a neuro-san server and interact with it.
Start the server and the client in one single command:

```bash
python -m run --use-flask-web-client
```

The client and server logs will show on the screen,
and will also be saved to `logs/server.log` and `logs/client.log` respectively.
As a default, on a web browser you can now navigate to <http://127.0.0.1:5003/> to start using the application:

![web_client.png](docs/images/web_client.png)

1. Expand the `Configuration` tab at the bottom of the interface
2. Choose an Agent Network Name, e.g. "music_nerd", click Update  
   💡 **Hint**: Check the server logs to see which agent networks are available. For instance:

   ```text
   SERVER: {"message": "tool_registries found: ['hello_world', 'airline_policy', 'advanced_calculator', 'smart_home', 'agent_network_designer', 'agent_network_generator', 'music_nerd', 'music_nerd_pro', 'agentforce', 'banking_ops', 'cpg_agents', 'insurance_agents', 'intranet_agents', 'retail_ops_and_customer_service', 'six_thinking_hats', 'telco_network_support']", "user_id": "None", "Timestamp": "2025-04-11T11:20:22.092078", "source": "Agent Server", "message_type": "Other", "request_id": "None"}
   ```

   They should match the list of agent networks that are activated in the `registries/manifest.hocon` file.
3. Type your message in the chat box and press 'Send' to interact with the agent network.
4. Optional: open the `Agent Network Diagram` tab to visualize the interactions between the agents.
5. Optional: open the `Agent Communications` tab to see the messages exchanged between the agents.

Run this command to see the various config options for the server and client:

```bash
python -m run --help
```

---

#### Option 3: Command Line Interface

You can also use [neuro-san](https://github.com/leaf-ai/neuro-san)'s command line interface (CLI) to start and interact with the server.

- Export the following environment variables:

  ```bash
  # Point the server to the manifest file containing the agent network configurations
  export AGENT_MANIFEST_FILE="./registries/manifest.hocon"
  # Point the server to the directory containing the agent Python tools
  export AGENT_TOOL_PATH="./coded_tools"
  ```

- Start the server:

```bash
python -m neuro_san.service.agent_main_loop --port 30011
```

- Start the client:
  From another terminal window, navigate to the repo's folder and activate the virtual environment:

  ```bash
  source venv/bin/activate && export PYTHONPATH=`pwd`
  ```

Then start the client:

```bash
python -m neuro_san.client.agent_cli --connection service --agent hello_world
```

- Query the client:
  
  When prompted, ask a question to the `hello_world` agent network. For example:

  ```text
  I am travelling to a new planet and wish to send greetings to the orb.
  ```

And it should return something like:

```text
Hello, world.
```

... but you are dealing with LLMs. Your results will vary!

Type `quit` to exit the client.

---

## User guide

Ready to dive in? Check out the [user guide](docs/user_guide.md) for a detailed overview of the neuro-san library
and its features.

---

## Tutorial

For a detailed tutorial, refer to [docs/tutorial.md](docs/tutorial.md).

---

## Examples

For examples of agent networks, check out [docs/examples.md](docs/examples.md).

---

## Developer Guide

For the development guide, check out [docs/dev_guide.md](docs/dev_guide.md).
