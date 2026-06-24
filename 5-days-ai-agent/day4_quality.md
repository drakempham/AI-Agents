# Day 4: Agent Quality & Evaluation

Day 4 addresses ensuring agent reliability and performance using automated evaluations and quality metrics.

---

## 1. Pytest vs. Agent Evaluation

It is critical to distinguish between traditional code testing and agent quality evaluation:

*   **`pytest` (Code Correctness)**: Verifies imports, functions, API contracts, and that your code runs without crashing. Does **NOT** check if the LLM's persona, tone, or answers are correct.
*   **`agents-cli eval` (Agent Quality)**: Verifies model-driven behavior, tool-selection accuracy, persona compliance, safety, and goal-achievement quality.

*Never write pytest tests that assert on LLM text responses, as LLM output is non-deterministic. Use eval with LLM-as-a-judge criteria instead.*

---

## 2. The Quality Flywheel

Improving agent quality is an iterative loop:

1.  **Prepare Data**: Write or generate a dataset of test cases in `tests/eval/datasets/basic-dataset.json` containing inputs (user prompts).
2.  **Run Inference (`eval generate`)**: Execute the agent over the dataset. Traces (user queries, intermediate tool calls, agent responses) are written to disk.
3.  **Grade Traces (`eval grade`)**: Evaluate and score the traces against defined metrics (rubrics or Python logic).
4.  **Analyze Failures (`eval analyze`)**: Examine low scores and LLM judge explanations to categorize bugs.
5.  **Optimize & Fix**: Adjust system instructions, tool signatures, configuration, or datasets, and rerun the loop.

---

## 3. Built-In Evaluation Metrics

Google ADK provides pre-configured metrics:

*   `multi_turn_task_success`: Measures if the agent successfully resolved the user's primary goal.
*   `multi_turn_trajectory_quality`: Evaluates if the agent's path was direct, logical, and efficient (no redundant tool calls).
*   `multi_turn_tool_use_quality`: Evaluates if the agent chose the correct tools and passed correct arguments.
*   `final_response_quality`: Grades the final text output for completeness, helpfulness, and tone.
*   `hallucination`: Checks if the agent claims facts that are not present in the tool outputs (critical for RAG agents).
*   `safety`: Audits safety policies and content policies.

---

## 4. Evaluation CLI Commands

The `agents-cli` provides commands to drive the evaluation loop:

*   **Single-Turn Smoke Test**: `agents-cli run "prompt"`
*   **Execute Inference**: `agents-cli eval generate`
*   **Grade Traces**: `agents-cli eval grade`
*   **Run Complete Eval (Generate + Grade)**: `agents-cli eval run`
*   **Compare two runs (Regressions check)**: `agents-cli eval compare baseline.json candidate.json`
*   **Failure Category Clustering**: `agents-cli eval analyze --eval-result artifacts/grade_results/results.json`
*   **Synthesize Scenarios via Simulation**: `agents-cli eval dataset synthesize` (plays simulations against your agent to automatically build datasets)

---

## 5. Custom Metrics Configuration

Custom metrics are defined in `tests/eval/eval_config.yaml`:

```yaml
metrics_to_run:
  - custom_response_quality

custom_metrics:
  - name: custom_response_quality
    prompt_template: |
      You are a quality assurance evaluator. Check if the agent's response is polite and accurate.
      User Prompt: {prompt}
      Final Response: {response}
      Agent Trace: {agent_data}
      Return JSON: {"score": <1-5>, "explanation": "<rationale>"}
```
