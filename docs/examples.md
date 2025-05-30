# Examples

Here are a few examples ordered by level of complexity.

<!-- TOC -->
* [Examples](#examples)
  * [🔰 Basic Examples](#-basic-examples)
    * [Music Nerd](#music-nerd)
    * [Music Nerd Pro](#music-nerd-pro)
    * [Music Nerd Local](#music-nerd-local)
    * [Music Nerd Pro Local](#music-nerd-pro-local)
    * [Music Nerd Pro Sly](#music-nerd-pro-sly)
    * [Music Nerd Pro Sly Local](#music-nerd-pro-sly-local)
  * [🧰 Tool Integration Examples](#-tool-integration-examples)
    * [Agentforce](#agentforce)
    * [Agentspace](#agentspace)
    * [MCP BMI SSE](#mcp-bmi-sse)
    * [A2A RESEARCH REPORT](#a2a-research-report)
    * [PDF RAG Assistant](#pdf-rag-assistant)
    * [Agentic RAG Assistant](#agentic-rag-assistant)
  * [🏢 Industry-Specific Examples](#-industry-specific-examples)
    * [Airline Policy 360 Assistant](#airline-policy-360-assistant)
    * [Intranet Agents](#intranet-agents)
    * [Intranet Agents With Tools](#intranet-agents-with-tools)
    * [Real Estate Agent](#real-estate-agent)
    * [Consumer Decision Assistant Agents](#consumer-decision-assistant-agents)
    * [Therapy Vignette Supervision](#therapy-vignette-supervision)
  * [🧪 Experimental and Research](#-experimental-and-research)
    * [Agent Network Designer](#agent-network-designer)
    * [KWIK Agents](#kwik-agents)
    * [Conscious Assistant](#conscious-assistant)
    * [Log Analyzer](#log-analyzer)
<!-- TOC -->

## 🔰 Basic Examples

Introductory examples designed to help users get started with Neuro SAN.

### Music Nerd

[Music Nerd](./examples/music_nerd.md) is a basic agent network with a single agent,
used as a "Hello world!" example. It can also be used to test for follow-up questions and deterministic answers.

### Music Nerd Pro

[Music Nerd Pro](./examples/music_nerd_pro.md) is a simple agent network with a frontman agent and a "Coded Tool."
This is a good way to learn about how to call Python code from an agent.

### Music Nerd Local

[Music Nerd Local](./examples/music_nerd_local.md) is an exact copy of
[Music Nerd](./examples/music_nerd.md) that uses an LLM that runs locally with Ollama.

### Music Nerd Pro Local

[Music Nerd Pro Local](./examples/music_nerd_pro_local.md) is an exact copy of
[Music Nerd Pro](./examples/music_nerd_pro.md) that uses
a **tool-calling** LLM that runs locally with Ollama.

### Music Nerd Pro Sly

[Music Nerd Pro Sly](./examples/music_nerd_pro_sly.md) is a copy of
[Music Nerd Pro](./examples/music_nerd_pro.md) that uses `sly_data` to keep track of a variable.
This is a good way to learn about how to manage a state in a conversation.

### Music Nerd Pro Sly Local

[Music Nerd Pro Sly Local](./examples/music_nerd_pro_sly_local.md) is a copy of
[Music Nerd Pro Sly](./examples/music_nerd_pro_sly.md) that uses
a **tool-calling** LLM that runs locally with Ollama.

## 🧰 Tool Integration Examples

Examples that demonstrate how to integrate external tools and services.

### Agentforce

[Agentforce](./examples/agentforce.md) is an agent network that delegates to a Salesforce Agentforce agent
to interact with a CRM system.

### Agentspace

[Agentspace](./examples/agentspace_adapter.md) is an agent network that delegates to a Google Agentspace agent to
interact with different datastore connectors on Google Cloud.

### MCP BMI SSE

[MCP BMI SSE](./examples/mcp_bmi_sse.md) is an agent that calls a tool in MCP server via server-sent events (sse) to
calculate BMI. It serves as an example of how to connect to MCP servers in coded tools.

### A2A RESEARCH REPORT

[A2A RESEARCH REPORT](./examples/a2a_research_report.md) is an agent that uses a coded tool as an A2A client to connect
to crewAI agents in an A2A server to write a report on a provided topic. This is an example of how to link
neuro-san with other agentic frameworks.

### PDF RAG Assistant

[PDF RAG Assistant](./examples/pdf_rag.md) is an agent-based system that answers user queries by retrieving information
from specified PDF files using Retrieval-Augmented Generation (RAG). It processes input through a frontman agent and a
PDF retrieval tool, enabling accurate responses from static documents.

### Agentic RAG Assistant

[Agentic RAG Assistant](./examples/agentic_rag.md) is a modular multi-agent system that answers user queries by
retrieving information from the web, PDF documents, and Slack channels. It mimics a smart assistant that delegates tasks
to specialized tools and compiles responses into clear, helpful answers.

## 🏢 Industry-Specific Examples

Examples tailored to specific industry applications.

### Airline Policy 360 Assistant

[Airline Policy 360 Assistant](./examples/airline_policy.md) is a sophisticated multi-agent system designed to manage
and respond to customer inquiries by referring to related airline policies with structured delegation. It mimics a
real-world helpdesk with specialized teams, each handling a specific domain of airline policies such as baggage,
flights, international travel, and more.

### Intranet Agents

[Intranet Agents](examples/intranet_agents.md) is a multi-agent system that mimics the intranet of a major corporation.
It allows you to interact and get information from various departments such as IT, Finance, Legal, HR, etc.

### Intranet Agents With Tools

[Intranet Agents With Tools](examples/intranet_agents_with_tools.md) is a multi-agent system that mimics the intranet of
a major corporation. It allows you to interact and get information from various departments such as IT, Finance, Legal,
HR, etc. Some of the down-chain agents call coded tools.

### Real Estate Agent

[Real Estate Agent](examples/real_estate.md) is a multi-agent system that provides help with real estate transaction
inquiries. The top-level "front-man" agent receives a question, and in coordination with down-chain agents, provides an
answer. Some of the down-chain agents call coded tools.

### Consumer Decision Assistant Agents

[consumer_decision_assistant.md](examples/consumer_decision_assistant.md) is a multi-agent system that calls other (B2C)
multi-agent systems that are not necessarily aligned.

### Therapy Vignette Supervision

[Therapy_Vignette_Supervision.md](examples/therapy_vignette_supervision) is an agentic therapy supervision group. Give
it a therapy vignette, and it will produce a consensus treatment plan after the various therapy experts offer their
opinion.

## 🧪 Experimental and Research

Cutting-edge examples for research and experimentation.

### Agent Network Designer

[Agent Network Designer](examples/agent_network_designer.md) is a multi-agent system to create multi-agent systems.
Enter the name of an organization or describe the use-case and will create an agent network hocon for you and save it to
your registries directory and give you some usage examples.

### KWIK Agents

[kwik_agents.md](examples/kwik_agents.md) is a basic multi-agent system with memory.

### Conscious Assistant

[conscious_agent.md](examples/conscious_agent.md) is a multi-agent system used within the conscious assistant and
serves as a good example of how to run an agent permanently.

### Log Analyzer

[log_analyzer.md](examples/log_analyzer.md) is a multi-agent system used within the log analyzer app and serves as a
good example of how to run an agent network on an agent network log for various validations.
