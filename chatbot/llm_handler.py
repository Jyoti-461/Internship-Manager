"""
Handles calls to the Google Gemini API (free tier, no credit card required)
for chatbot queries that the rule-based FAQ matcher in faq_data.py couldn't
confidently answer.

Why Gemini instead of Claude/OpenAI here: Gemini's free tier (via Google AI
Studio) gives a generous daily request quota at zero cost, which fits a
student/college project much better than paid-only APIs. Get a free key at
https://aistudio.google.com/apikey — no card needed.

The system prompt scopes Gemini tightly to internship-related topics, asks
it to gather missing details when needed, and asks it to return structured
JSON so the Flask route knows whether to just reply, or escalate the
conversation to a human teacher.
"""

import json
import os
from google import genai
from google.genai import types

_client = None


def get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    return _client


SYSTEM_PROMPT = """You are "InternBot", a friendly virtual assistant for the internship \
program at our firm. Your job is to help prospective interns with basic questions about \
the internship process: eligibility, duration, stipend, required documents, available \
domains, certificates, remote/onsite options, and how to apply.

Rules you MUST follow:
1. Stay strictly on the topic of internships at this firm. If asked something unrelated \
(general chit-chat is fine briefly, but off-topic requests like coding help, homework, or \
anything unrelated to the internship program should be politely redirected).
2. If you don't have enough information to confidently answer, or the question is about \
something specific to the student's individual application (status, special case, dispute, \
complaint, or anything requiring human judgment), do NOT make up an answer. Instead, \
indicate this should be escalated to a human teacher/coordinator.
3. Keep answers concise (3-5 sentences max), warm, and professional.
4. Always respond with ONLY a JSON object, no other text, no markdown fences, in this exact \
shape:
{
  "reply": "<the message to show the student>",
  "escalate": true or false,
  "category": "<short category like 'Eligibility', 'Application Status', 'Complaint', 'Other'>",
  "summary": "<one-line summary of what the student needs, for the teacher's dashboard>"
}

If escalate is true, the "reply" should tell the student their query has been forwarded to \
the team and they'll be contacted soon. If escalate is false, the "reply" should directly \
and helpfully answer their question.
"""


def ask_gemini(conversation_history, model="gemini-2.0-flash"):
    """
    conversation_history: list of {"role": "user"/"assistant", "content": "..."}
    representing the chat so far (most recent message last).

    Returns a dict: {"reply": str, "escalate": bool, "category": str, "summary": str}
    Falls back to a safe escalation response if the API call fails or the
    response isn't valid JSON.
    """
    try:
        client = get_client()

        # Gemini's SDK uses "model"/"user" roles (not "assistant") and a
        # `contents` list of Content objects, so we translate our internal
        # history format here.
        contents = []
        for turn in conversation_history:
            role = "model" if turn["role"] == "assistant" else "user"
            contents.append(types.Content(role=role, parts=[types.Part(text=turn["content"])]))

        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                max_output_tokens=500,
                response_mime_type="application/json",
            ),
        )
        raw_text = response.text.strip()

        # Defensive cleanup in case the model wraps JSON in code fences anyway
        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`")
            if raw_text.startswith("json"):
                raw_text = raw_text[4:].strip()

        parsed = json.loads(raw_text)

        return {
            "reply": parsed.get("reply", "Let me get a team member to help with that."),
            "escalate": bool(parsed.get("escalate", True)),
            "category": parsed.get("category", "Other"),
            "summary": parsed.get("summary", conversation_history[-1]["content"][:150]),
        }

    except Exception as e:
        # Fail safe: if the Gemini API errors out, hits a rate limit, or
        # returns bad JSON, escalate to a human rather than risk giving the
        # student a broken/empty reply.
        print(f"[chatbot/llm_handler] Gemini API error: {e}")
        return {
            "reply": (
                "Thanks for your question! I want to make sure you get the "
                "most accurate answer, so I've forwarded this to our team — "
                "they'll get in touch with you shortly."
            ),
            "escalate": True,
            "category": "Other",
            "summary": conversation_history[-1]["content"][:150] if conversation_history else "",
        }
