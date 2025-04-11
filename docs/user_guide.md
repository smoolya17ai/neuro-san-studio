# User guide

## Hello World

The `hello_world` agent network is a simple agent network that returns a greeting when prompted.

The steps to start the server and the client are described above.
When starting, the first thing the server will do is load the agent network configurations
from the "manifest" file. The manifest file is specified by the `AGENT_MANIFEST_FILE` environment variable:
```
AGENT_MANIFEST_FILE="./registries/manifest.hocon"
```
Open [./registries/manifest.hocon](../registries/manifest.hocon) and look at its contents. It should look something like this:
```hocon
{
    # Currently we list each hocon file we want to serve as a key with a boolean value.
    # Eventually we might have a dictionary value with server specifications for each.
    "hello_world.hocon": true,
    # ...
}
```
This tells the server to load the `hello_world.hocon` file from the same `/registries` folder.

Open [./registries/hello_world.hocon](../registries/hello_world.hocon) and have a look at it.
For now just note that it contains a "Front Man",
called "announcer", which is the entry point to the agent network.
The "announcer" tool, also known as an "agent", has 1 tool at its disposal (another agent), called "synonymizer".
Read the instructions of these 2 agents to see what they do.
Feel free to modify the instructions to see how the agent network behaves.

We'll come back to the structure of .hocon files later.

## Hello World - custom LLMs

TODO

## Hocon files

### Manifest

A manifest file is a list of agent network configurations that the server will load.

It's simple dictionary where the keys are the names of the agent network configuration files
and the values are booleans. For instance:
```hocon
{
    "agent_network_A.hocon": true,
    "agent_network_B.hocon": false,
    "agent_network_C.hocon": true,
}
```
In this example the server will load agent networks A and C but not B.

When you start the server, you can see which agent networks have been loaded by looking at the logs:
```
> python -m neuro_san.service.agent_main_loop --port 30011

tool_registries found: ['agent_network_A', 'agent_network_C']
```

### Agent network

#### Agent specifications

| **Field**    | **Description**                                                                                                                              |
|--------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| agent_name   | text handle for other agent specs and hosting system to refer to                                                                             |
| function     | Open AI function spec (standard) that formally describes the various inputs that the agent expects                                           |
| instructions | text that sets up the agent in detail for its task                                                                                           |
| command      | text that sets the agent in motion after it receives all its inputs                                                                          |
| tools        | optional list of references to other agents that this agent is allowed to call in the course of working through their input and instructions |
| llm_config   | optional agent-specification for different LLMs for different purposes such as specialization, costs, etc.                                   |

#### Tool specifications

| **Field**     | **Description**                                                                                   |
|---------------|---------------------------------------------------------------------------------------------------|
| agent_name    | text handle for other agent specs to refer to                                                     |
| function      | Open AI function spec (standard) that formally describes the various inputs that the tool expects |
| method        | Code reference to the function that is to be invoked when the tool is called.                     |

#### LLM specifications

| **Field**   | **Description**                                                                                                                       |
|-------------|---------------------------------------------------------------------------------------------------------------------------------------|
| model_name  | name of the model to use (i.e. “gpt-4o”, “claude-3-haiku”)                                                                            |
| *_api_key   | api key value or environment variable to reference to allow access to the LLM provider if different from hosting environment default. |
| temperature | optional level of randomness 0.0-1.0 to use for LLM results                                                                           |

## Multi-agent networks

TODO

## Coded tools

### Simple tool

### API calling tool

### Sly data

Specific data can be passed to CodeTools via the `sly_data` dictionary.
The `sly_data` dictionary can be passed along with the chat_request from the client side.
The LLMs won’t see the `sly_data`, but the coded tools can access it.
Useful to hold onto a user id and tokens for instance.

## Toolbox

RAG
DB connectors

## Logging and debugging

## Advanced

### Subnetworks

### AAOSA

AAOSA stands for **A**daptive **A**gent **O**riented **S**oftware **A**rchitecture.

In this architecture, agents decide if they can answer inquiries or if they need to call other agents to help them.

Reference:
[Iterative Statistical Language Model Generation for Use with an
Agent-Oriented Natural Language Interface ](https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=3004005f1e736815b367be83f2f90cc0fa9e0411)

<!-- (https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=011fb718658d611294613286c0f4b143aed40f43) -->

Look at [./registries/smart_home.onf.hocon](../registries/smart_home_onf.hocon) and in particular:
- aaosa_instructions
- aaosa_call
- aaosa_command

## Connect with other agent frameworks

e.g. crewAI, AutoGen, LangGraph, etc.
Agentforce, ServiceNow, 
