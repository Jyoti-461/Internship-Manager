"""
Main chatbot decision engine. This is what routes/chatbot_routes.py calls.

Flow for every incoming student message:
  1. Try fast rule-based FAQ match (no API cost, instant).
  2. If no FAQ match -> call the Gemini API with the recent conversation
     history for a context-aware answer or an escalation decision.
  3. Return a normalized dict the route can save to the DB and send back.
"""

from chatbot.faq_data import match_faq
from chatbot.llm_handler import ask_gemini


def get_bot_response(user_message: str, recent_messages: list, model="gemini-2.0-flash"):
    """
    user_message: the latest message text from the student
    recent_messages: list of Message model rows (or dicts) for context,
                      oldest first. Used to build Gemini's conversation history.

    Returns dict: {"reply": str, "escalate": bool, "category": str, "summary": str, "source": "faq"|"gemini"}
    """
    # --- Step 1: try rule-based FAQ first (cheap, instant, no API call) ---
    faq_match = match_faq(user_message)
    if faq_match:
        return {
            "reply": faq_match["answer"],
            "escalate": False,
            "category": faq_match["category"],
            "summary": "",
            "source": "faq",
        }

    # --- Step 2: build conversation history for Gemini ---
    history = []
    for m in recent_messages:
        role = "assistant" if m["sender_type"] in ("bot", "teacher") else "user"
        history.append({"role": role, "content": m["message_text"]})

    # Make sure the very latest user message is included
    if not history or history[-1]["content"] != user_message:
        history.append({"role": "user", "content": user_message})

    # The conversation should start with a "user" message
    while history and history[0]["role"] != "user":
        history.pop(0)

    result = ask_gemini(history, model=model)
    result["source"] = "gemini"
    return result
