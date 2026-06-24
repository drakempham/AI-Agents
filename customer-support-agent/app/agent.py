# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from typing import Any
import google.auth
from google.auth.exceptions import DefaultCredentialsError

from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.workflow import Workflow, START, node
from google.adk.events.event import Event
from google.adk.events.event_actions import EventActions
from google.adk.agents.context import Context
from google.genai import types
from pydantic import BaseModel, Field

# Authenticate with Vertex AI / Google GenAI
try:
    _, project_id = google.auth.default()
    if project_id:
        os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
    os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
except DefaultCredentialsError:
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"
    if "GEMINI_API_KEY" in os.environ and "GOOGLE_API_KEY" not in os.environ:
        os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]


class Classification(BaseModel):
    is_related: bool = Field(
        description="True if the user's query is related to shipping (rates, tracking, delivery, returns). False if the query is unrelated."
    )
    reason: str = Field(
        description="A short explanation of why the query was classified as related or unrelated."
    )


@node
def store_user_query(node_input: Any) -> Event:
    """Extracts and stores the initial user query text in the workflow session state."""
    text = ""
    if isinstance(node_input, str):
        text = node_input
    elif hasattr(node_input, "parts") and node_input.parts:
        text = node_input.parts[0].text or ""
    elif isinstance(node_input, dict) and "parts" in node_input:
        parts = node_input["parts"]
        if parts and isinstance(parts, list):
            text = parts[0].get("text", "") or ""
    return Event(output=text, actions=EventActions(state_delta={"user_query": text}))


classifier_agent = LlmAgent(
    name="classifier_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are an AI assistant for a shipping company. "
        "Your task is to classify whether the user's query is related to shipping or unrelated. "
        "Shipping-related topics include shipping rates, price quotes, package tracking, delivery status, "
        "shipping options/methods, shipping addresses/schedules, returns, refunds, or package pickups. "
        "Unrelated topics include general greetings (unless immediately followed by a shipping query), "
        "math, coding, jokes, politics, or any other topic not about shipping. "
        "Respond with a structured Classification object where is_related is True if related to shipping, and False otherwise."
    ),
    output_schema=Classification,
)


@node
def route_query(ctx: Context, node_input: Any) -> Event:
    """Inspects classification results and routes the workflow accordingly."""
    is_related = False
    if isinstance(node_input, Classification):
        is_related = node_input.is_related
    elif isinstance(node_input, dict):
        is_related = node_input.get("is_related", False)

    user_query = ctx.state.get("user_query", "")
    if is_related:
        return Event(output=user_query, actions=EventActions(route="shipping_related"))
    return Event(output=user_query, actions=EventActions(route="unrelated"))


shipping_faq_agent = LlmAgent(
    name="shipping_faq_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are an expert shipping company customer support agent. "
        "Answer the user's questions about shipping rates, tracking, delivery, or returns politely and accurately."
    ),
)


@node
def decline_node(node_input: Any) -> Event:
    """Politely declines to answer non-shipping queries."""
    message = (
        "I'm sorry, but I can only assist with shipping-related inquiries "
        "(such as rates, tracking, delivery, and returns). Please let me know if you have any shipping questions!"
    )
    return Event(
        content=types.Content(role="model", parts=[types.Part.from_text(text=message)]),
        output=message,
    )


root_agent = Workflow(
    name="customer_support_workflow",
    edges=[
        ("START", store_user_query),
        (store_user_query, classifier_agent),
        (classifier_agent, route_query),
        (
            route_query,
            {"shipping_related": shipping_faq_agent, "unrelated": decline_node},
        ),
    ],
    description="Routes user queries to a shipping FAQ agent if they are shipping-related, or politely declines them otherwise.",
)

app = App(
    root_agent=root_agent,
    name="app",
)
