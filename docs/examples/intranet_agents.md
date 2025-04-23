# Intranet Agents

The **Intranet Agents** is a multi-agent system that mimics the intranet of a major corporation. It allows you to interact with and get information from various departments such as IT, Finance, Legal, HR, etc. The top-level "front-man" agent receives a question, and in coordination with down-chain agents,
provides an answer.

## File

[intranet_agents.hocon](../../registries/intranet_agents.hocon)

---

## Description

Provide the top-level "front-man" agent a question and it will call down-chain agents to determine if they are responsible for all or part of question.
It will then ask those down-chain agents what they need in order to handle their part of the inquiry. Once the requirements are gathered, the top agent
delegates the inquiry and the fulfilled requirements to the appropriate down-chain agents. Once all down-chain agents respond, the top agent will compile
their responses and return the final response.

The "front-man" agent can call IT, Finance, Procurement, Legal, and HR agents. Those agents, in turn, can call other, more specific agents. For example,
the HR agent can call Benefits or Payroll agents. The agent network has the sahpe of a tree that is two layers deep.

---

## Example Conversation

### Human:
```
I recently got married
```

### AI (intranet_agents):
```
Congratulations on your recent marriage! Here are some ways I can assist you across different areas:

IT and Security:

If you have specific concerns related to digital security, data privacy, or shared digital accounts with your spouse, please let me know so I can provide guidance.
Finance:

Budgeting and Financial Planning: I can help create a budget plan and offer financial advice. Please share details such as your current income, expenses, financial goals, and any debts or investments.
Tax Implications: Marriage can affect your tax status. Updating tax forms like the W-4 might be necessary.
Procurement:

If there are specific procurement or contract-related questions, such as name changes on contracts or vendor management, please provide more context.
Legal:

I can assist with legal considerations like name changes, marriage certificates, and estate planning. Please specify any particular legal concerns or areas where you need assistance.
HR and Benefits:

Employee Benefits: If you need to update benefits like health insurance or retirement plans, or if you're interested in adding your spouse to your coverage, I can guide you through the process.
Please let me know which specific areas or questions you would like to explore further, and I will be happy to provide more detailed assistance!
```

---

## Architecture Overview

### Frontman Agent: **intranet_agents**
- Acts as the entry point for all user commands
- Can call IT, Finance, Procurement, Legal, and HR agents

### Agents called by the Frontman:

1. **IT_agent**
   - Responsible for IT-related inquiries
   - Can call Security_agent or Networking_agent
   - Security_agent: Handles security-related tasks, including system protection, cybersecurity, and data security
   - Networking_agent: Handles network-related tasks, including network setup, maintenance, and troubleshooting

2. **instruction_refiner**
   - Retrieves the agent network definition using the [get_agent_network.py](../../coded_tools/agent_network_designer/get_agent_network.py) tool.
   - Iterates through the agents in the retrieved definition and refines each agent's instructions using the [set_agent_instructions.py](../../coded_tools/agent_network_designer/set_agent_instructions.py) tool

3. **query_generator**
   - Retrieves the agent network definition using the [get_agent_network.py](../../coded_tools/agent_network_designer/get_agent_network.py) tool.
   - Generates and returns a few usage examples for the new agent network.

---

## Functional Tools

These are coded tools called by various policy agents:

- **add_agent**
  - Adds the name, instructions, and list of down-chains of an agent to a data structure stored in sly_data. It also determines of the agent is the top agent.

- **get_agent_network**
  - Retrieves the agent network data structure from sly_data and returns a string representation of it.

- **set_agent_instructions**
  - Replaces the instructions for a given agent in the list of agents in the agent network data structure in sly_data.

- **get_agent_network_hocon**
  - Retrieves the agent network data structure from sly_data.
  - Formats the agent network as a hocon definition config.
  - Appends a header.
  - Saves the hocon file under the local registries directory.
  - Adds an entry to the local manifest.hocon file.

**Note**: it is assumed that the agent coordination mechanism is AAOSA, and the LLM is GPT-4o.

---
