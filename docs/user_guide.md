# User guide

## Simple agent network

The `music_nerd` agent network is the simple agent network possible: it contains a single agent
that answers questions about music since the 60s. See its description here: [docs/examples/music_nerd.md](../docs/examples/music_nerd.md).

The steps to start the server and the client are described in the [README](../README.md).
When starting, the first thing the server will do is load the agent network configurations
from the "manifest" file. The manifest file is specified by the `AGENT_MANIFEST_FILE` environment variable:
```
AGENT_MANIFEST_FILE="./registries/manifest.hocon"
```
Open [./registries/manifest.hocon](../registries/manifest.hocon) and look at its contents. It should look something like this:
```hocon
{
    # ... other agent networks ... #
    "music_nerd.hocon": true,
    # ... other agent networks ... #
}
```
This tells the server to load the `music_nerd.hocon` file from the same `/registries` folder.

Setting the value to `false` would make the server ignore this agent network.

Open [./registries/music_nerd.hocon](../registries/hello_world.hocon) and have a look at it.
For now just note that it contains:
- an `llm_config` section that specifies which LLM to use by default for the agents in this file
- a `tools` section that contains a single agent, the "frontman", called `MusicNerd`

Read the instructions of the agent to see what it does.
Feel free to modify the instructions to see how it affects the agent's behavior.
See if you can make it a soccer expert for instance!

We'll describe the structure of agent networks' .hocon files in next section.

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

See next section for more information about how to specify the LLM(s) to use.

## LLM configuration

The `llm_config` section of the agent network configuration file specifies which LLM to use
for the agents in this file. It can be specified:
- at the agent network level, to apply to all agents in this file
- at the agent level, to apply to a specific agent

### OpenAI

To use an OpenAI LLM, set the `OPENAI_API_KEY` environment variable to your OpenAI API key
and specify which model to use in the `model_name` field:
```hocon
    "llm_config": {
        "model_name": "gpt-4o",
    },
```

See [./examples/music_nerd.md](./examples/music_nerd.md) for an example.

### Ollama

To use an LLM that runs locally with [Ollama](https://ollama.com/):
- Make sure the Ollama server is running
- Make sure the model is downloaded and available in the Ollama server. For instance, `ollama run llama3.1`
  will download the model and make it available for use.
- Set the `class` and `model_name` fields in the `llm_config` section of the agent network configuration file:
```hocon
    "llm_config": {
        "class": "ollama",
        "model_name": "llama3.1",
    },
```

See [./examples/music_nerd_pro_local.md](./examples/music_nerd_pro_local.md) for an example.

For more information about how to use Ollama with LangChain,
see [this page](https://python.langchain.com/docs/integrations/chat/ollama/)


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
