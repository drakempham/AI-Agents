# Day 3: Context Engineering (Sessions & Memory)

Day 3 covers managing state and context in multi-turn conversations, including sessions, short-term memory, long-term memory, context caching, and context compaction.

---

## 1. Session & State Management

Conversations in Google ADK are grouped into **Sessions**. The state is maintained in a key-value dictionary.

### Session Storage backends:
*   `InMemorySessionService`: Used during local development. Session data is wiped on server restart.
*   `DatabaseSessionService` / `CloudSQL`: Persistent storage.
*   `VertexAiSessionService`: Automatically managed session lifecycle.

### State Scope Prefixes
State variables can be scoped differently by prepending specific prefixes to the key:
*   **Session-scoped (Default)**: `state["step"] = 1` (Only available in the current conversation thread).
*   **User-scoped**: `state["user:language"] = "vi"` (Persisted across different sessions for the same user).
*   **App-scoped**: `state["app:total_users"] = 10` (Shared across all users of the app).
*   **Temp-scoped**: `state["temp:cache"] = data` (Wiped clean after the current invocation turn).

---

## 2. Memory Bank (Long-Term Memory)

While user-scoped state stores structured settings, **Memory Bank** stores unstructured text memories and learnings gathered from previous sessions. It uses vector semantic retrieval to recall memories.

### Saving Session to Memory:
We use a callback function at the end of the conversation to synthesize and write new learnings into the Memory Bank:

```python
from google.adk.agents.callback_context import CallbackContext

async def generate_memories_callback(callback_context: CallbackContext):
    """Summarizes current conversation events and saves them to Memory Bank."""
    await callback_context.add_session_to_memory()
    return None

root_agent = Agent(
    ...,
    after_agent_callback=generate_memories_callback
)
```

### Recalling Memories:
*   **Preloaded Memory**: Use the built-in `PreloadMemoryTool` to search and inject relevant memories directly into the system instructions at the start of every turn.
*   **On-Demand Memory**: Use `LoadMemoryTool` so the agent can actively choose to query memory when it needs to retrieve past information.

---

## 3. Context Optimization

As conversations grow, they consume more input tokens, leading to higher latency and costs. ADK provides two built-in solutions:

### Context Caching
Caches the static portion of the context (system instruction, tools definition, and static documents) on Gemini servers when the token count exceeds a threshold.
```python
from google.adk.apps import App
from google.adk.agents.context_cache_config import ContextCacheConfig

app = App(
    name="app",
    root_agent=root_agent,
    context_cache_config=ContextCacheConfig(
        min_tokens=2048,     # Cache only if context size exceeds 2048 tokens
        ttl_seconds=1800,    # Cache lasts for 30 minutes
    )
)
```

### Context Compaction
Automatically summarizes older conversation turns when a session gets too long, keeping only the recent turns in full.
```python
from google.adk.apps import App
from google.adk.apps.app import EventsCompactionConfig
from google.adk.apps.llm_event_summarizer import LlmEventSummarizer

app = App(
    name="app",
    root_agent=root_agent,
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=20,  # Summarize older events every 20 turns
        overlap_size=3,          # Keep last 3 events in full for continuity
    )
)
```
