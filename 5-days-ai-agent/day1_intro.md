# Day 1: Introduction to Agents & Vibe Coding

Day 1 introduces the foundational architecture of AI Agents and the concept of "Vibe Coding" — using natural language as the primary software interface.

---

## 1. What is an AI Agent?

Traditional LLM applications are stateless and single-turn (input -> output). In contrast, **AI Agents** are active, stateful, and autonomous systems that execute a loop of reasoning, planning, and actions:

*   **Reasoning & Planning**: Deciding how to solve a user's request.
*   **Memory**: Recalling past turns, sessions, or user preferences.
*   **Tool Calling**: Executing code, searching databases, or calling APIs.
*   **Action Execution**: Changing states in the physical or digital world.

---

## 2. The Vibe Coding SDLC

"Vibe Coding" refers to writing prompts, requirements, and instructions in natural language, and using AI coding assistants to automatically generate, modify, and manage the underlying code. The Software Development Life Cycle (SDLC) shifts to:

1.  **Plan**: Draft specifications in plain English (or Markdown specs).
2.  **Build**: Use CLI tools (`agents-cli`) and AI agents to scaffold and implement features.
3.  **Evaluate**: Run systematic, automated evaluation runs over a dataset rather than asserting keywords in pytest.
4.  **Deploy**: Push to lightweight environments (like Vertex AI Agent Runtime or Cloud Run) for rapid prototyping.
5.  **Observe**: Watch session logs and traces to detect hallucinations or routing errors.
6.  **Iterate**: Tune the system instructions, templates, or tools based on observed results.

---

## 3. Google Agent Development Kit (ADK) Basics

The course centers on **Google ADK** (Agent Development Kit), which provides Python libraries and CLI tools for building enterprise-grade agent apps.

### Project Setup Commands
*   **Install CLI**: `uv tool install google-agents-cli`
*   **Check Info**: `agents-cli info`
*   **Scaffold Project**: `agents-cli scaffold create my-agent --agent adk --prototype`
*   **Install Dependencies**: `agents-cli install` (runs `uv sync` locally)
*   **Run Local Server / Playground**: `agents-cli playground` (launches local web console at `http://127.0.0.1:8080`)
*   **Terminal Smoke Test**: `agents-cli run "What can you do?"`

---

## 4. Coding a Simple Agent
ADK uses the `LlmAgent` class to define agents. The agent requires a name, a model configuration, and system instructions:

```python
from google.adk.agents import Agent
from google.adk.apps import App

root_agent = Agent(
    name="my_agent",
    model="gemini-2.5-flash",
    instruction="You are a polite receptionist. Guide visitors using the tools provided.",
)

app = App(
    root_agent=root_agent,
    name="app",
)
```
