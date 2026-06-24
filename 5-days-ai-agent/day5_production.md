# Day 5: Prototype to Production

Day 5 details moving agents from a prototype playground to production deployments, utilizing ADK 2.0 Graph Workflows for complex routing, and prepping for the Capstone Project.

---

## 1. Deployment Targets

When ready to launch into production, you can transition your local prototype using `agents-cli scaffold enhance . --deployment-target <target>`:

| Target | Description | Session Storage |
| :--- | :--- | :--- |
| **`agent_runtime`** | Managed by Vertex AI Agent Runtime. Zero-ops infrastructure. | Managed internally. |
| **`cloud_run`** | Standard container-based deployment. Offers full Docker/web server control. | `in_memory`, `cloud_sql`, or `agent_platform_sessions` |
| **`gke`** | Container-based deployment on GKE Autopilot. Provides full Kubernetes orchestration. | `in_memory`, `cloud_sql`, or `agent_platform_sessions` |

*Note: For the Capstone Project prototype, you can skip deployment configurations by setting `--deployment-target none`.*

---

## 2. ADK 2.0 Graph Workflows

For complex applications, a single ReAct agent is often insufficient. **ADK 2.0** introduces a graph-based `Workflow` engine to coordinate multiple agents, routers, and processing steps with structured paths.

### Core Workflow Blocks:
1.  **Nodes**: Wrapping functions (`FunctionNode`), LLM agents (`_LlmAgentWrapper`), or tools (`_ToolNode`).
2.  **Edges**: Directing connections. Supports:
    *   *Sequential Chains*: `('START', node_a, node_b)`
    *   *Conditional Routing*: `(router, {"route_x": node_x, "route_y": node_y})`
    *   *Fan-out (Parallel)*: `(node_a, (branch_1, branch_2))`
    *   *Fan-in (Join)*: Using a `JoinNode` to collect parallel outputs into a dictionary.

### Graph Validation Rules:
*   `START` must be the unique entry point (has no incoming edges).
*   All nodes must be reachable from `START`.
*   No duplicate node names.
*   No unconditional loops/cycles (any loop must contain at least one routed/conditional edge to prevent infinite loops).

---

## 3. Capstone Project Preparation

The **Capstone Project** is the final assignment to apply everything learned during the 5-day course.

### Requirements:
1.  **Build a Real-World System**: Implement a multi-agent or graph workflow system using the Google Agent Development Kit (ADK) and Gemini.
2.  **Verify & Grade**: Write unit tests (`pytest`) and set up an evaluation suite (`eval_config.yaml` and datasets) to verify the quality and safety of the system.
3.  **No Strict Deployment Required**: You can complete the project as a prototype (using `--deployment-target none`), focusing on core functionality and quality evaluations.
4.  **Submission Deadline**: **July 6, 2026**. Submitting successfully awards a Kaggle badge and certificate.
