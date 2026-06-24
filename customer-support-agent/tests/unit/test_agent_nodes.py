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

from app.agent import store_user_query, route_query, Classification
from google.genai import types
from google.adk.agents.context import Context
from unittest.mock import MagicMock


def test_store_user_query_str() -> None:
    event = store_user_query._func(node_input="Where is my package?")
    assert event.output == "Where is my package?"
    assert event.actions.state_delta == {"user_query": "Where is my package?"}


def test_store_user_query_content() -> None:
    content = types.Content(
        role="user",
        parts=[types.Part.from_text(text="How much for express shipping?")],
    )
    event = store_user_query._func(node_input=content)
    assert event.output == "How much for express shipping?"
    assert event.actions.state_delta == {
        "user_query": "How much for express shipping?"
    }


def test_route_query_related() -> None:
    ctx = MagicMock(spec=Context)
    ctx.state = {"user_query": "How much for express shipping?"}

    # Test Pydantic model input
    classification = Classification(is_related=True, reason="shipping question")
    event = route_query._func(ctx, node_input=classification)
    assert event.output == "How much for express shipping?"
    assert event.actions.route == "shipping_related"


def test_route_query_unrelated() -> None:
    ctx = MagicMock(spec=Context)
    ctx.state = {"user_query": "Tell me a joke."}

    # Test dict input (serialization fallback)
    classification_dict = {"is_related": False, "reason": "unrelated topic"}
    event = route_query._func(ctx, node_input=classification_dict)
    assert event.output == "Tell me a joke."
    assert event.actions.route == "unrelated"
