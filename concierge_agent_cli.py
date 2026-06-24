import os
import datetime
from google import genai
from google.genai import types
from google.genai.errors import APIError

# API key retrieved from history
client = genai.Client(api_key=api_key)


def calculate_days_until_deadline(target_date_str: str) -> str:
    """Calculates the number of days left from today until a target deadline date.

    Args:
        target_date_str: The target deadline date in 'YYYY-MM-DD' format.
    """
    try:
        today = datetime.date.today()
        target_date = datetime.datetime.strptime(target_date_str, "%Y-%m-%d").date()
        days_left = (target_date - today).days
        if days_left < 0:
            return f"[TOOL OUTPUT] The date {target_date_str} has already passed."
        return f"[TOOL OUTPUT] There are exactly {days_left} days left until {target_date_str}."
    except Exception as e:
        return f"[TOOL OUTPUT] Error parsing date: {str(e)}. Please use YYYY-MM-DD format."


my_agent_tools = [calculate_days_until_deadline]

system_prompt = """
You are a helpful Project Concierge Agent. Your job is to help the user manage their timeline.
Always use the 'calculate_days_until_deadline' tool whenever the user mentions a specific future date or asks about a deadline.
Be concise, polite, and confirm your actions clearly.
"""


def main():
    print("--- Project Concierge Agent CLI Started ---")
    query = "Hey agent, the deadline is 2026-07-06. How much time do I have?"
    print(f"User: {query}")
    print("Thinking... Calling Gemini and executing tools...\n")

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=query,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                tools=my_agent_tools,
                temperature=0.3,
            ),
        )
        print("--- Agent Response ---")
        print(response.text)
    except APIError as e:
        print(f"API Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
