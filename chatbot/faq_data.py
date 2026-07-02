"""
Predefined FAQ entries for instant, zero-cost answers to extremely common
internship questions. The bot engine checks these BEFORE calling the Gemini
API, so frequent questions don't burn API calls / add latency.

Each entry: keywords (any match triggers it) -> canned answer.
Keep answers short, friendly, and specific to your firm's actual policies —
edit the placeholder text below to match reality.
"""

FAQ_ENTRIES = [
    {
        "keywords": ["eligibility", "eligible", "who can apply", "criteria"],
        "category": "Eligibility",
        "answer": (
            "To be eligible for our internship program, you should be currently "
            "enrolled in a Bachelor's or Master's degree program (any relevant "
            "stream) with a minimum CGPA of 6.5 or equivalent. Final-year students "
            "and recent graduates (within 1 year) are also welcome to apply."
        ),
    },
    {
        "keywords": ["duration", "how long", "weeks", "months"],
        "category": "Duration",
        "answer": (
            "Our internships typically run for 8 to 12 weeks, with flexibility "
            "for part-time arrangements during the academic semester. Exact "
            "duration depends on the domain and project you're assigned to."
        ),
    },
    {
        "keywords": ["stipend", "salary", "paid", "payment", "money"],
        "category": "Stipend",
        "answer": (
            "Yes, our internships are paid. Stipend amounts vary by role and "
            "experience level and will be confirmed during your offer discussion "
            "with the team."
        ),
    },
    {
        "keywords": ["document", "documents required", "what to submit", "resume", "cv"],
        "category": "Documents",
        "answer": (
            "You'll need: an updated resume/CV, a copy of your college ID, your "
            "latest academic transcript, and a short statement of purpose (why "
            "you want to intern with us). You can upload your resume from your "
            "student dashboard after registering."
        ),
    },
    {
        "keywords": ["domain", "department", "tracks", "roles available", "fields"],
        "category": "Domains",
        "answer": (
            "We currently offer internships in: Web Development, Data Science / "
            "ML, Cloud & DevOps, UI/UX Design, and Digital Marketing. You can "
            "select your preferred domain when you apply from your dashboard."
        ),
    },
    {
        "keywords": ["certificate", "certification"],
        "category": "Certificate",
        "answer": (
            "Yes, all interns who successfully complete the program receive a "
            "Certificate of Completion, and top performers may receive a "
            "Letter of Recommendation as well."
        ),
    },
    {
        "keywords": ["remote", "work from home", "wfh", "online", "in office", "onsite"],
        "category": "Work Mode",
        "answer": (
            "We offer both remote and in-office internship options depending on "
            "the role and your location. You can mention your preference when "
            "you apply, and our team will confirm what's available."
        ),
    },
    {
        "keywords": ["how to apply", "apply", "application process", "register"],
        "category": "Application Process",
        "answer": (
            "Great, here's how to apply: 1) Register for a student account, "
            "2) Complete your profile with college details, 3) Upload your "
            "resume, 4) Select your preferred internship domain, and 5) Submit "
            "your application from the dashboard. You'll be notified once it's "
            "reviewed."
        ),
    },
]


def match_faq(user_message: str):
    """
    Returns a matching FAQ dict if the user's message contains any of its
    keywords, else None. Simple substring matching, case-insensitive.
    """
    text = user_message.lower()
    for entry in FAQ_ENTRIES:
        for kw in entry["keywords"]:
            if kw in text:
                return entry
    return None
