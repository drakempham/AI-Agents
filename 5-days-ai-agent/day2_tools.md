# Day 2: Tools & Interoperability (MCP & A2A)

Day 2 focuses on giving agents "hands" — enabling them to interface with the external world via APIs, custom tools, and open standards like the Model Context Protocol (MCP).

---

## 1. Custom Tools in ADK

In Google ADK, tools are defined as standard Python functions. The agent model reads the function's **docstring** and **type hints** to understand how and when to invoke it.

### Rules for Writing Tools:
1.  **Clear Docstring**: The docstring is sent directly to the LLM as the tool description. It must clearly explain what the tool does and what each argument means.
2.  **Type Hints**: Required for all arguments.
3.  **No Default Values**: Arguments must not have default values in the function signature.
4.  **JSON Return**: Returns should be JSON-serializable (typically dicts).

### Code Example:
```python
from google.adk.tools import ToolContext

def query_shipping_rates(
    weight_lbs: float, 
    destination: str,
    tool_context: ToolContext  # Optional, injected for session state access
) -> dict:
    """Calculates shipping rates for a package.

    Args:
        weight_lbs: Weight of the package in pounds.
        destination: Destination city or zip code.
    """
    # Tool logic here
    cost = weight_lbs * 1.50
    return {"status": "success", "rate": cost, "currency": "USD"}
```

---

## 2. Model Context Protocol (MCP)

**Model Context Protocol (MCP)** is an open standard designed to decouple applications, LLM engines, and data/tool sources. Instead of writing custom API integration code for every tool, you connect your agent to an **MCP Server**.

### Key Server Types:
*   **stdio (Local Development)**: Communication happens over standard input/output. Useful for running local npm/python packages (e.g. filesystem access, SQLite query tool).
*   **SSE (Production)**: Communication happens via HTTP Server-Sent Events. Useful for connecting to remote APIs and databases.

### ADK MCP Connection Example:
```python
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", "/Users/minhpd/Downloads"],
        )
    ),
    tool_filter=["read_file", "list_directory"] # Optional: expose only these tools
)
```

---

## 3. Agent-to-Agent (A2A) Collaboration

The A2A protocol allows an agent to coordinate with other specialized remote agents. The parent agent registers sub-agents via their **Agent Cards** (well-known metadata endpoint) and delegates tasks to them automatically when needed.

### Exposing an Agent as an A2A service:
```python
from google.adk.a2a.utils.agent_to_a2a import to_a2a
to_a2a(root_agent, port=8001)
```

### Consuming a Remote A2A Agent:
```python
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH

remote_billing_agent = RemoteA2aAgent(
    name="billing_agent",
    description="Processes invoices, returns, and refunds.",
    agent_card=f"http://billing-service:8001{AGENT_CARD_WELL_KNOWN_PATH}",
)

# Pass it to root coordinator agent
coordinator = Agent(..., sub_agents=[remote_billing_agent])
```
